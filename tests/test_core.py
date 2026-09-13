import pytest

from cinelog_core import (
    Conflito,
    ErroValidacao,
    NaoEncontrado,
    alternar_assistido,
    atualizar,
    cadastrar,
    estatisticas,
    excluir,
    listar,
    obter,
)


def test_cadastrar_sucesso(catalogo_tmp, filme_valido):
    novo = cadastrar(filme_valido)
    assert novo["titulo"] == "Matrix"
    assert novo["nota"] == 9.5
    assert "data_cadastro" in novo
    assert catalogo_tmp.exists()


def test_cadastrar_titulo_duplicado(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    with pytest.raises(Conflito):
        cadastrar(filme_valido)


def test_cadastrar_titulo_duplicado_case_insensitive(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "MATRIX"
    with pytest.raises(Conflito):
        cadastrar(filme_valido)


@pytest.mark.parametrize("campo, valor, msg", [
    ("titulo", "   ", "titulo"),
    ("genero", "Musical", "genero"),
    ("ano", "abc", "ano"),
    ("ano", 1800, "ano"),
    ("nota", "x", "nota"),
    ("nota", 11, "nota"),
    ("nota", -1, "nota"),
])
def test_cadastrar_validacoes(catalogo_tmp, filme_valido, campo, valor, msg):
    filme_valido[campo] = valor
    with pytest.raises(ErroValidacao) as exc:
        cadastrar(filme_valido)
    assert msg in str(exc.value).lower()


def test_cadastrar_corpo_nao_dict(catalogo_tmp):
    with pytest.raises(ErroValidacao):
        cadastrar(["nao", "e", "dict"])


def test_obter_case_insensitive(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    assert obter("matrix")["titulo"] == "Matrix"


def test_obter_inexistente(catalogo_tmp):
    with pytest.raises(NaoEncontrado):
        obter("Nada")


def test_listar_filtro_genero(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Toy Story"
    filme_valido["genero"] = "Comédia"
    cadastrar(filme_valido)

    acao = listar(genero="Ação")
    assert acao == []

    ficcao = listar(genero="Ficção")
    assert len(ficcao) == 1
    assert ficcao[0]["titulo"] == "Matrix"


def test_listar_busca_parcial(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    assert len(listar(busca="mat")) == 1
    assert listar(busca="zzz") == []


def test_listar_ordenar_por_nota(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Pior"
    filme_valido["nota"] = 3.0
    cadastrar(filme_valido)

    resultado = listar(ordenar="nota")
    assert [i["titulo"] for i in resultado] == ["Matrix", "Pior"]


def test_atualizar_campos(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    item = atualizar("Matrix", {"nota": 10, "comentario": "Top"})
    assert item["nota"] == 10
    assert item["comentario"] == "Top"


def test_atualizar_para_titulo_existente(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Outro"
    cadastrar(filme_valido)

    with pytest.raises(Conflito):
        atualizar("Matrix", {"titulo": "Outro"})


def test_atualizar_inexistente(catalogo_tmp):
    with pytest.raises(NaoEncontrado):
        atualizar("Nada", {"nota": 5})


def test_alternar_assistido(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)  # assistido=True
    item = alternar_assistido("Matrix")
    assert item["assistido"] is False
    item = alternar_assistido("Matrix")
    assert item["assistido"] is True


def test_excluir(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    removido = excluir("Matrix")
    assert removido["titulo"] == "Matrix"
    with pytest.raises(NaoEncontrado):
        obter("Matrix")


def test_estatisticas_vazio(catalogo_tmp):
    stats = estatisticas()
    assert stats["total"] == 0
    assert stats["genero_top"] is None


def test_estatisticas_com_dados(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Toy Story"
    filme_valido["genero"] = "Comédia"
    filme_valido["nota"] = 8.0
    filme_valido["assistido"] = False
    filme_valido["comentario"] = ""
    cadastrar(filme_valido)

    stats = estatisticas()
    assert stats["total"] == 2
    assert stats["media_notas"] == 8.75
    assert stats["assistidos"] == 1
    assert stats["pendentes"] == 1
    assert stats["com_comentario"] == 1


def test_carregar_arquivo_corrompido(catalogo_tmp):
    catalogo_tmp.write_text("{isso nao e json}", encoding="utf-8")
    assert listar() == []
