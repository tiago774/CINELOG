import json
import os
import pathlib
import shutil

import pytest

import cinelog_core
from cinelog_core import (
    cadastrar,
    carregar,
    listar,
    salvar,
)


def test_arquivo_e_criado_apos_primeiro_cadastro(catalogo_tmp, filme_valido):
    assert not catalogo_tmp.exists()
    cadastrar(filme_valido)
    assert catalogo_tmp.exists()


def test_arquivo_e_json_valido_e_utf8(catalogo_tmp, filme_valido):
    filme_valido["titulo"] = "Ação & Ficção"
    cadastrar(filme_valido)

    bruto = catalogo_tmp.read_text(encoding="utf-8")
    dados = json.loads(bruto)

    assert dados[0]["titulo"] == "Ação & Ficção"
    assert "ç" in bruto or "ã" in bruto


def test_arquivo_indentado_com_4_espacos(catalogo_tmp, filme_valido):
    """json.dump(indent=4): 4 espaços por nível de aninhamento.

    Lista → 4 espaços antes de '{'
    Chaves do dict → 8 espaços antes de '"titulo"'
    """
    cadastrar(filme_valido)
    bruto = catalogo_tmp.read_text(encoding="utf-8")

    assert "\n    {" in bruto
    assert '\n        "' in bruto
    assert "\n  {" not in bruto


def test_backup_criado_apos_segunda_gravacao(catalogo_tmp, filme_valido):
    backup = catalogo_tmp.parent / "catalogo.json.bak"

    cadastrar(filme_valido)
    assert not backup.exists()

    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)
    assert backup.exists()

    conteudo_bak = json.loads(backup.read_text(encoding="utf-8"))
    assert len(conteudo_bak) == 1
    assert conteudo_bak[0]["titulo"] == "Matrix"


def test_backup_e_sobrescrito_a_cada_gravacao(catalogo_tmp, filme_valido):
    backup = catalogo_tmp.parent / "catalogo.json.bak"

    cadastrar(filme_valido)
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Terceiro"
    cadastrar(filme_valido)

    conteudo_bak = json.loads(backup.read_text(encoding="utf-8"))
    assert len(conteudo_bak) == 2


def test_backup_preserva_metadados_do_arquivo(catalogo_tmp, filme_valido):
    """shutil.copy2 preserva mtime; o .bak deve ter mtime <= do arquivo real."""
    cadastrar(filme_valido)
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)

    backup = catalogo_tmp.parent / "catalogo.json.bak"
    mtime_real = os.path.getmtime(catalogo_tmp)
    mtime_bak = os.path.getmtime(backup)
    assert mtime_bak <= mtime_real


def test_data_cadastro_tem_microseconds(catalogo_tmp, filme_valido):
    """Garante que o fix de ordenação está em vigor."""
    item = cadastrar(filme_valido)
    assert "." in item["data_cadastro"]
    partes = item["data_cadastro"].split(".")
    assert len(partes) == 2
    assert len(partes[1]) == 6  # exatamente 6 dígitos


def test_datas_consecutivas_sao_estritamente_crescentes(catalogo_tmp, filme_valido):
    """Duas gravações seguidas → datas distintas (não empata)."""
    a = cadastrar(filme_valido)["data_cadastro"]
    filme_valido["titulo"] = "Segundo"
    b = cadastrar(filme_valido)["data_cadastro"]
    assert a < b


def test_ordenar_por_data_com_tres_itens(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)                        # 1º
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)                        # 2º
    filme_valido["titulo"] = "Terceiro"
    cadastrar(filme_valido)                        # 3º

    resultado = listar(ordenar="data")
    assert [i["titulo"] for i in resultado] == ["Terceiro", "Segundo", "Matrix"]


def test_carregar_arquivo_com_json_truncado(catalogo_tmp):
    catalogo_tmp.write_text('{"titulo": "x"', encoding="utf-8")
    assert carregar() == []


def test_carregar_arquivo_vazio(catalogo_tmp):
    catalogo_tmp.write_text("", encoding="utf-8")
    assert carregar() == []


def test_carregar_arquivo_com_lista_vazia(catalogo_tmp):
    catalogo_tmp.write_text("[]", encoding="utf-8")
    assert carregar() == []


def test_carregar_ignora_arquivo_inexistente(catalogo_tmp):
    assert not catalogo_tmp.exists()
    assert carregar() == []


def test_carregar_ignora_item_nao_dict(catalogo_tmp):
    """Itens que não são dict são ignorados silenciosamente."""
    catalogo_tmp.write_text(json.dumps([1, 2, {"titulo": "Válido", "nota": 5}]),
                            encoding="utf-8")
    dados = carregar()
    assert len(dados) == 1
    assert dados[0]["titulo"] == "Válido"



def test_round_trip_com_caracteres_especiais(catalogo_tmp, filme_valido):
    filme_valido["titulo"] = "Amélie & Cia."
    filme_valido["comentario"] = "Coração ❤"
    cadastrar(filme_valido)

    lido = carregar()[0]
    assert lido["titulo"] == "Amélie & Cia."
    assert lido["comentario"] == "Coração ❤"


def test_round_trip_preserva_tipos(catalogo_tmp, filme_valido):
    cadastrar(filme_valido)
    lido = carregar()[0]

    assert isinstance(lido["titulo"], str)
    assert isinstance(lido["genero"], str)
    assert isinstance(lido["ano"], int)
    assert isinstance(lido["nota"], float)
    assert isinstance(lido["assistido"], bool)


def test_salvar_substitui_arquivo_inteiro(catalogo_tmp, filme_valido):
    """Salvar não faz append — substitui."""
    cadastrar(filme_valido)              # 1 item
    filme_valido["titulo"] = "Segundo"
    cadastrar(filme_valido)              # 2 itens

    # Agora sobrescreve com lista de 1
    salvar([filme_valido])
    assert len(carregar()) == 1
