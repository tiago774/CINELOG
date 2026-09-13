import json
import shutil

import pytest

import cinelog_core
from cinelog_core import (
    Conflito,
    ErroValidacao,
    NaoEncontrado,
    alternar_assistido,
    atualizar,
    cadastrar,
    carregar,
    estatisticas,
    excluir,
    listar,
    obter,
    salvar,
)


def test_carregar_json_nao_e_lista(catalogo_tmp):
    """JSON válido mas não é lista → []."""
    catalogo_tmp.write_text('{"nao": "e lista"}', encoding="utf-8")
    assert carregar() == []


def test_carregar_normaliza_nota_string(catalogo_tmp):
    """nota como string deve virar float."""
    catalogo_tmp.write_text(json.dumps([
        {"titulo": "X", "genero": "Ação", "ano": 2000,
         "nota": "7.5", "assistido": False}
    ]), encoding="utf-8")

    dados = carregar()
    assert dados[0]["nota"] == 7.5
    assert isinstance(dados[0]["nota"], float)


def test_carregar_nota_invalida_vira_zero(catalogo_tmp):
    """nota não conversível → 0.0."""
    catalogo_tmp.write_text(json.dumps([
        {"titulo": "X", "genero": "Ação", "ano": 2000,
         "nota": "abc", "assistido": False}
    ]), encoding="utf-8")

    dados = carregar()
    assert dados[0]["nota"] == 0.0


def test_carregar_completa_campos_ausentes(catalogo_tmp):
    """Itens legados sem campos → setdefault preenche."""
    catalogo_tmp.write_text(json.dumps([
        {"titulo": "Antigo", "nota": 5}
    ]), encoding="utf-8")

    item = carregar()[0]
    assert item["genero"] == "Outro"
    assert item["ano"] == 0
    assert item["assistido"] is False
    assert item["comentario"] == ""
    assert item["data_cadastro"] == "1970-01-01T00:00:00"


def test_carregar_item_sem_titulo_recebe_default(catalogo_tmp):
    """Item sem titulo → 'Sem título'."""
    catalogo_tmp.write_text(json.dumps([
        {"nota": 5}  # sem titulo
    ]), encoding="utf-8")
    assert carregar()[0]["titulo"] == "Sem título"


def test_salvar_faz_backup_do_anterior(catalogo_tmp, filme_valido):
    """Depois de salvar 2x, o .bak contém o primeiro estado."""
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)

    backup = catalogo_tmp.parent / "catalogo.json.bak"
    assert backup.exists()
    conteudo = json.loads(backup.read_text(encoding="utf-8"))
    assert len(conteudo) == 1
    assert conteudo[0]["titulo"] == "Matrix"


def test_salvar_erro_de_escrita_vira_runtime_error(monkeypatch, catalogo_tmp, filme_valido):
    """Se open() falhar, levanta RuntimeError."""
    import builtins
    real_open = builtins.open

    def fake_open(path, *args, **kwargs):
        if str(path) == str(catalogo_tmp) and "w" in (args[0] if args else kwargs.get("mode", "")):
            raise OSError("disco cheio")
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", fake_open)

    with pytest.raises(RuntimeError, match="Erro ao salvar"):
        salvar([filme_valido])


def test_salvar_backup_falha_nao_impede_gravacao(monkeypatch, catalogo_tmp, filme_valido):
    """Se o copy2 falhar, o json ainda é salvo (except OSError: pass)."""
    catalogo_tmp.write_text("[]", encoding="utf-8")

    def fake_copy(*a, **k):
        raise OSError("sem permissão")

    monkeypatch.setattr(shutil, "copy2", fake_copy)

    salvar([filme_valido])  # não deve levantar
    assert json.loads(catalogo_tmp.read_text(encoding="utf-8"))[0]["titulo"] == "Matrix"



@pytest.mark.parametrize("payload_extra", [
    {},
])
def test_cadastrar_genero_ausente(catalogo_tmp, filme_valido, payload_extra):
    filme_valido.pop("genero", None)
    filme_valido.update(payload_extra)
    with pytest.raises(ErroValidacao):
        cadastrar(filme_valido)


def test_cadastrar_nota_none(catalogo_tmp, filme_valido):
    filme_valido["nota"] = None
    with pytest.raises(ErroValidacao):
        cadastrar(filme_valido)


def test_cadastrar_ano_none(catalogo_tmp, filme_valido):
    filme_valido["ano"] = None
    with pytest.raises(ErroValidacao):
        cadastrar(filme_valido)


def test_cadastrar_comentario_none(catalogo_tmp, filme_valido):
    """comentario=None deve virar ''."""
    filme_valido["comentario"] = None
    item = cadastrar(filme_valido)
    assert item["comentario"] == ""


def test_cadastrar_assistido_ausente_default_false(catalogo_tmp, filme_valido):
    filme_valido.pop("assistido")
    item = cadastrar(filme_valido)
    assert item["assistido"] is False


def test_cadastrar_ano_string_numerica(catalogo_tmp, filme_valido):
    filme_valido["ano"] = "1999"
    item = cadastrar(filme_valido)
    assert item["ano"] == 1999


def test_listar_ordenar_por_ano(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)  # 1999
    filme_valido["titulo"] = "Novo"
    filme_valido["ano"] = 2024
    cadastrar(filme_valido)

    resultado = listar(ordenar="ano")
    assert [i["ano"] for i in resultado] == [1999, 2024]


def test_listar_ordenar_por_data(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)

    resultado = listar(ordenar="data")
    assert resultado[0]["titulo"] == "Segundo"


def test_listar_ordenar_cadastro(catalogo_tmp, filme_valido):
    """'cadastro' é valor válido mas não casa com nenhum branch → ordem original."""
    cadastrar(filme_valido)
    assert len(listar(ordenar="cadastro")) == 1



def test_atualizar_genero_invalido(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"genero": "Musical"})


def test_atualizar_ano_invalido(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"ano": "abc"})

    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"ano": 1800})


def test_atualizar_nota_invalida(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"nota": "abc"})

    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"nota": 11})


def test_atualizar_titulo_vazio(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    with pytest.raises(ErroValidacao):
        atualizar("Matrix", {"titulo": "   "})


def test_atualizar_assistido_e_comentario(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)  # assistido=True
    item = atualizar("Matrix", {"assistido": False, "comentario": "novo"})
    assert item["assistido"] is False
    assert item["comentario"] == "novo"


def test_atualizar_comentario_none(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    item = atualizar("Matrix", {"comentario": None})
    assert item["comentario"] == ""


def test_atualizar_genero_ano_nota_validos(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    item = atualizar("Matrix", {
        "genero": "Drama", "ano": 2000, "nota": 7.0,
    })
    assert item["genero"] == "Drama"
    assert item["ano"] == 2000
    assert item["nota"] == 7.0


def test_alternar_assistido_inexistente(catalogo_tmp):
    with pytest.raises(NaoEncontrado):
        alternar_assistido("Nada")


def test_excluir_inexistente(catalogo_tmp):
    with pytest.raises(NaoEncontrado):
        excluir("Nada")


def test_estatisticas_empate_genero(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)  # Ficção
    filme_valido["titulo"] = "Comedia"
    filme_valido["genero"] = "Comédia"
    cadastrar(filme_valido)

    stats = estatisticas()
    assert stats["genero_top"] in ("Ficção", "Comédia")
    assert stats["por_genero"] == {"Ficção": 1, "Comédia": 1}


def test_atualizar_titulo_valido(catalogo_tmp, filme_valido):
    """Renomear um filme para um título novo (caminho feliz)."""
    cadastrar(filme_valido)  # Matrix

    item = atualizar("Matrix", {"titulo": "Matrix Reloaded"})

    assert item["titulo"] == "Matrix Reloaded"
    # Confirma que persistiu
    assert obter("Matrix Reloaded")["titulo"] == "Matrix Reloaded"
    # O título antigo não existe mais
    with pytest.raises(NaoEncontrado):
        obter("Matrix")


def test_atualizar_titulo_para_si_mesmo(catalogo_tmp, filme_valido):
    """Renomear para o mesmo título não deve dar conflito (dup is item)."""
    cadastrar(filme_valido)

    item = atualizar("Matrix", {"titulo": "Matrix"})
    assert item["titulo"] == "Matrix"


def test_atualizar_titulo_muda_case(catalogo_tmp, filme_valido):
    """Trocar apenas o case do título deve funcionar (dup is item)."""
    cadastrar(filme_valido)

    item = atualizar("Matrix", {"titulo": "MATRIX"})
    assert item["titulo"] == "MATRIX"
