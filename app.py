from flask import Flask, jsonify, request

from cinelog_core import (
    GENEROS,
    ORDENACOES_VALIDAS,
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

app = Flask(__name__)
app.json.ensure_ascii = False


@app.errorhandler(ErroValidacao)
def _err_validacao(e):
    return jsonify({"erro": str(e), "tipo": "validacao"}), 400


@app.errorhandler(NaoEncontrado)
def _err_nao_encontrado(e):
    return jsonify({"erro": str(e), "tipo": "nao_encontrado"}), 404


@app.errorhandler(Conflito)
def _err_conflito(e):
    return jsonify({"erro": str(e), "tipo": "conflito"}), 409


@app.errorhandler(404)
def _err_rota(e):
    return jsonify({"erro": "Rota não encontrada.", "tipo": "rota"}), 404


@app.errorhandler(405)
def _err_metodo(e):
    return jsonify({"erro": "Método não permitido.", "tipo": "metodo"}), 405


@app.get("/")
def home():
    return jsonify({
        "nome": "CINELOG API",
        "versao": "1.0",
        "generos": GENEROS,
        "endpoints": [
            "GET    /api/generos",
            "GET    /api/filmes",
            "GET    /api/filmes/<titulo>",
            "POST   /api/filmes",
            "PUT    /api/filmes/<titulo>",
            "PATCH  /api/filmes/<titulo>/assistido",
            "DELETE /api/filmes/<titulo>",
            "GET    /api/estatisticas",
        ],
    })


@app.get("/api/generos")
def rota_generos():
    return jsonify(GENEROS)


@app.get("/api/filmes")
def rota_listar():
    genero = request.args.get("genero")

    assistido_raw = request.args.get("assistido")
    assistido = None
    if assistido_raw is not None:
        v = assistido_raw.lower()
        if v in ("true", "1", "sim"):
            assistido = True
        elif v in ("false", "0", "nao", "não"):
            assistido = False
        else:
            raise ErroValidacao("'assistido' deve ser true ou false.")

    busca = request.args.get("busca")
    ordenar = request.args.get("ordenar", "titulo")

    if ordenar not in ORDENACOES_VALIDAS:
        raise ErroValidacao(f"'ordenar' deve ser um de: {sorted(ORDENACOES_VALIDAS)}")

    if genero and genero not in GENEROS:
        raise ErroValidacao(f"'genero' deve ser um de: {GENEROS}")

    itens = listar(genero=genero, assistido=assistido, ordenar=ordenar, busca=busca)
    return jsonify({"total": len(itens), "itens": itens})


@app.get("/api/filmes/<path:titulo>")
def rota_obter(titulo):
    return jsonify(obter(titulo))


@app.post("/api/filmes")
def rota_cadastrar():
    dados = request.get_json(silent=True)
    if dados is None:
        raise ErroValidacao("Envie JSON no corpo da requisição.")
    novo = cadastrar(dados)
    return jsonify(novo), 201


@app.put("/api/filmes/<path:titulo>")
def rota_atualizar(titulo):
    dados = request.get_json(silent=True)
    if dados is None:
        raise ErroValidacao("Envie JSON no corpo da requisição.")
    item = atualizar(titulo, dados)
    return jsonify(item)


@app.patch("/api/filmes/<path:titulo>/assistido")
def rota_toggle_assistido(titulo):
    return jsonify(alternar_assistido(titulo))


@app.delete("/api/filmes/<path:titulo>")
def rota_excluir(titulo):
    removido = excluir(titulo)
    return jsonify({"mensagem": "Removido com sucesso.", "item": removido})


@app.get("/api/estatisticas")
def rota_estatisticas():
    return jsonify(estatisticas())


if __name__ == "__main__":
    app.run(debug=True, port=5000)
