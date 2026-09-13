import importlib
import json

import pytest

import cinelog_core


@pytest.fixture
def catalogo_tmp(tmp_path, monkeypatch):
    """Redireciona ARQUIVO_JSON/ARQUIVO_BACKUP para tmp_path."""
    arquivo = tmp_path / "catalogo.json"
    backup = tmp_path / "catalogo.json.bak"

    monkeypatch.setattr(cinelog_core, "ARQUIVO_JSON", arquivo)
    monkeypatch.setattr(cinelog_core, "ARQUIVO_BACKUP", backup)

    return arquivo


@pytest.fixture
def filme_valido():
    return {
        "titulo": "Matrix",
        "genero": "Ficção",
        "ano": 1999,
        "assistido": True,
        "nota": 9.5,
        "comentario": "Clássico absoluto",
    }


@pytest.fixture
def client(catalogo_tmp):
    """Cliente Flask com o core apontando para arquivo temporário."""
    # Recarrega o app para pegar a config limpa
    import app as app_module
    importlib.reload(app_module)

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c
