def test_listar_com_busca(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.get("/api/filmes?busca=mat")
    assert r.status_code == 200
    assert r.get_json()["total"] == 1


def test_listar_genero_invalido(client):
    r = client.get("/api/filmes?genero=Musical")
    assert r.status_code == 400
    assert r.get_json()["tipo"] == "validacao"


def test_listar_assistido_true(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.get("/api/filmes?assistido=true")
    assert r.get_json()["total"] == 1


def test_listar_assistido_false(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.get("/api/filmes?assistido=false")
    assert r.get_json()["total"] == 0


def test_listar_assistido_1_e_0(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    assert client.get("/api/filmes?assistido=1").get_json()["total"] == 1
    assert client.get("/api/filmes?assistido=0").get_json()["total"] == 0


def test_listar_assistido_sim_nao(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    assert client.get("/api/filmes?assistido=sim").get_json()["total"] == 1
    assert client.get("/api/filmes?assistido=nao").get_json()["total"] == 0
    assert client.get("/api/filmes?assistido=não").get_json()["total"] == 0


def test_put_atualiza_filme(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.put("/api/filmes/Matrix", json={"nota": 10, "comentario": "top"})
    assert r.status_code == 200
    assert r.get_json()["nota"] == 10


def test_put_sem_json(client):
    r = client.put("/api/filmes/Matrix", data="texto",
                   content_type="text/plain")
    assert r.status_code == 400
    assert r.get_json()["tipo"] == "validacao"


def test_put_inexistente(client):
    r = client.put("/api/filmes/Nada", json={"nota": 5})
    assert r.status_code == 404
    assert r.get_json()["tipo"] == "nao_encontrado"


def test_patch_inexistente(client):
    r = client.patch("/api/filmes/Nada/assistido")
    assert r.status_code == 404


def test_delete_inexistente(client):
    r = client.delete("/api/filmes/Nada")
    assert r.status_code == 404


def test_home_lista_endpoints(client):
    r = client.get("/")
    assert "GET    /api/filmes" in r.get_json()["endpoints"]
    assert r.get_json()["versao"] == "1.0"


def test_get_filme_especifico(client, filme_valido):
    client.post("/api/filmes", json=filme_valido)
    r = client.get("/api/filmes/Matrix")
    assert r.status_code == 200
    assert r.get_json()["genero"] == "Ficção"
