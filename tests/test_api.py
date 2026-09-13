def test_home(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.get_json()["nome"] == "CINELOG API"


def test_generos(client):
    r = client.get("/api/generos")
    assert r.status_code == 200
    assert "Ação" in r.get_json()


def test_cadastrar_e_listar(client, filme_valido):
    r = client.post("/api/filmes", json=filme_valido)
    assert r.status_code == 201
    assert r.get_json()["titulo"] == "Matrix"

    r = client.get("/api/filmes")
    corpo = r.get_json()
    assert corpo["total"] == 1
    assert corpo["itens"][0]["titulo"] == "Matrix"


def test_cadastrar_json_ausente(client):
    r = client.post("/api/filmes", data="nao-e-json",
                    content_type="text/plain")
    assert r.status_code == 400
    assert r.get_json()["tipo"] == "validacao"


def test_cadastrar_duplicado_retorna_409(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.post("/api/filmes", json=filme_valido)
    assert r.status_code == 409
    assert r.get_json()["tipo"] == "conflito"


def test_obter_inexistente_retorna_404(client):
    r = client.get("/api/filmes/Nada")
    assert r.status_code == 404
    assert r.get_json()["tipo"] == "nao_encontrado"


def test_alternar_assistido(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.patch("/api/filmes/Matrix/assistido")
    assert r.status_code == 200
    assert r.get_json()["assistido"] is False


def test_excluir(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.delete("/api/filmes/Matrix")
    assert r.status_code == 200

    r = client.get("/api/filmes/Matrix")
    assert r.status_code == 404


def test_filtro_assistido_invalido(client):
    r = client.get("/api/filmes?assistido=talvez")
    assert r.status_code == 400
    assert r.get_json()["tipo"] == "validacao"


def test_filtro_ordenar_invalido(client):
    r = client.get("/api/filmes?ordenar=aleatorio")
    assert r.status_code == 400


def test_rota_inexistente_retorna_404(client):
    r = client.get("/api/nada")
    assert r.status_code == 404
    assert r.get_json()["tipo"] == "rota"


def test_metodo_nao_permitido(client):
    r = client.delete("/api/generos")
    assert r.status_code == 405
    assert r.get_json()["tipo"] == "metodo"


def test_estatisticas(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.get("/api/estatisticas")
    assert r.status_code == 200
    assert r.get_json()["total"] == 1
