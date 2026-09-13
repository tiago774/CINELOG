import datetime
import json
import pathlib
import shutil

PASTA_SCRIPT = pathlib.Path(__file__).resolve().parent
ARQUIVO_JSON = PASTA_SCRIPT / "catalogo.json"
ARQUIVO_BACKUP = PASTA_SCRIPT / "catalogo.json.bak"

GENEROS = ["Ação", "Comédia", "Drama", "Ficção", "Romance", "Terror"]

ORDENACOES_VALIDAS = {"titulo", "ano", "nota", "data", "cadastro"}


class ErroValidacao(Exception):
    """Entrada inválida → HTTP 400."""


class NaoEncontrado(Exception):
    """Recurso não existe → HTTP 404."""


class Conflito(Exception):
    """Título duplicado, etc → HTTP 409."""

def carregar():
    """Lê catalogo.json. Se ausente ou corrompido, devolve lista vazia."""
    if not ARQUIVO_JSON.exists():
        return []

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    for item in data:
        if not isinstance(item.get("nota"), (int, float)):
            try:
                item["nota"] = float(item["nota"])
            except (ValueError, TypeError):
                item["nota"] = 0.0
        item.setdefault("titulo", "Sem título")
        item.setdefault("genero", "Outro")
        item.setdefault("ano", 0)
        item.setdefault("assistido", False)
        item.setdefault("comentario", "")
        item.setdefault("data_cadastro", "1970-01-01T00:00:00")

    return data


def salvar(catalogo):
    """Grava catalogo.json fazendo backup do anterior."""
    try:
        if ARQUIVO_JSON.exists():
            try:
                shutil.copy2(ARQUIVO_JSON, ARQUIVO_BACKUP)
            except OSError:
                pass

        with open(ARQUIVO_JSON, "w", encoding="utf-8") as f:
            json.dump(catalogo, f, ensure_ascii=False, indent=4)
    except OSError as e:
        raise RuntimeError(f"Erro ao salvar catálogo: {e}") from e



def encontrar_por_titulo(catalogo, titulo):
    """Case-insensitive exato. Retorna (indice, item) ou (None, None)."""
    alvo = titulo.strip().lower()
    for i, item in enumerate(catalogo):
        if item["titulo"].lower() == alvo:
            return i, item
    return None, None


def _validar_cadastro(dados):
    """Valida e normaliza o payload de criação. Levanta ErroValidacao."""
    if not isinstance(dados, dict):
        raise ErroValidacao("Corpo deve ser um objeto JSON.")

    titulo = (dados.get("titulo") or "").strip()
    if not titulo:
        raise ErroValidacao("Campo 'titulo' é obrigatório.")

    genero = dados.get("genero")
    if genero not in GENEROS:
        raise ErroValidacao(f"'genero' deve ser um de: {GENEROS}")

    try:
        ano = int(dados.get("ano"))
    except (TypeError, ValueError):
        raise ErroValidacao("'ano' deve ser um número inteiro.")

    ano_max = datetime.datetime.now().year + 5
    if not (1900 <= ano <= ano_max):
        raise ErroValidacao(f"'ano' deve estar entre 1900 e {ano_max}.")

    try:
        nota = float(dados.get("nota"))
    except (TypeError, ValueError):
        raise ErroValidacao("'nota' deve ser um número.")

    if not (0 <= nota <= 10):
        raise ErroValidacao("'nota' deve estar entre 0 e 10.")

    assistido = bool(dados.get("assistido", False))
    comentario = (dados.get("comentario") or "").strip()

    return {
        "titulo": titulo,
        "genero": genero,
        "ano": ano,
        "assistido": assistido,
        "nota": nota,
        "comentario": comentario,
    }

def listar(genero=None, assistido=None, ordenar="titulo", busca=None):
    itens = carregar()

    if genero:
        itens = [i for i in itens if i["genero"] == genero]

    if assistido is not None:
        itens = [i for i in itens if i["assistido"] == assistido]

    if busca:
        termo = busca.lower()
        itens = [i for i in itens if termo in i["titulo"].lower()]

    if ordenar == "titulo":
        itens.sort(key=lambda i: i["titulo"].lower())
    elif ordenar == "ano":
        itens.sort(key=lambda i: i["ano"])
    elif ordenar == "nota":
        itens.sort(key=lambda i: i["nota"], reverse=True)
    elif ordenar == "data":
        itens.sort(key=lambda i: i.get("data_cadastro", ""), reverse=True)

    return itens


def obter(titulo):
    catalogo = carregar()
    _, item = encontrar_por_titulo(catalogo, titulo)
    if item is None:
        raise NaoEncontrado(f"Título '{titulo}' não encontrado.")
    return item


def cadastrar(dados):
    payload = _validar_cadastro(dados)
    catalogo = carregar()

    _, existente = encontrar_por_titulo(catalogo, payload["titulo"])
    if existente is not None:
        raise Conflito(f"'{payload['titulo']}' já está cadastrado.")

    payload["data_cadastro"] = datetime.datetime.now().isoformat(timespec="seconds")
    catalogo.append(payload)
    salvar(catalogo)
    return payload


def atualizar(titulo, dados):
    catalogo = carregar()
    i, item = encontrar_por_titulo(catalogo, titulo)
    if item is None:
        raise NaoEncontrado(f"Título '{titulo}' não encontrado.")

    if "titulo" in dados:
        novo = (dados["titulo"] or "").strip()
        if not novo:
            raise ErroValidacao("'titulo' não pode ser vazio.")
        _, dup = encontrar_por_titulo(catalogo, novo)
        if dup is not None and dup is not item:
            raise Conflito(f"Já existe outro título '{novo}'.")
        item["titulo"] = novo

    if "genero" in dados:
        if dados["genero"] not in GENEROS:
            raise ErroValidacao(f"'genero' deve ser um de: {GENEROS}")
        item["genero"] = dados["genero"]

    if "ano" in dados:
        try:
            ano = int(dados["ano"])
        except (TypeError, ValueError):
            raise ErroValidacao("'ano' deve ser um número inteiro.")
        if not (1900 <= ano <= datetime.datetime.now().year + 5):
            raise ErroValidacao("'ano' fora do intervalo permitido.")
        item["ano"] = ano

    if "nota" in dados:
        try:
            nota = float(dados["nota"])
        except (TypeError, ValueError):
            raise ErroValidacao("'nota' deve ser um número.")
        if not (0 <= nota <= 10):
            raise ErroValidacao("'nota' deve estar entre 0 e 10.")
        item["nota"] = nota

    if "assistido" in dados:
        item["assistido"] = bool(dados["assistido"])

    if "comentario" in dados:
        item["comentario"] = (dados["comentario"] or "").strip()

    catalogo[i] = item
    salvar(catalogo)
    return item


def alternar_assistido(titulo):
    catalogo = carregar()
    i, item = encontrar_por_titulo(catalogo, titulo)
    if item is None:
        raise NaoEncontrado(f"Título '{titulo}' não encontrado.")
    item["assistido"] = not item["assistido"]
    catalogo[i] = item
    salvar(catalogo)
    return item


def excluir(titulo):
    catalogo = carregar()
    i, item = encontrar_por_titulo(catalogo, titulo)
    if item is None:
        raise NaoEncontrado(f"Título '{titulo}' não encontrado.")
    removido = catalogo.pop(i)
    salvar(catalogo)
    return removido


def estatisticas():
    catalogo = carregar()
    if not catalogo:
        return {
            "total": 0,
            "media_notas": 0.0,
            "assistidos": 0,
            "pendentes": 0,
            "genero_top": None,
            "por_genero": {},
            "com_comentario": 0,
        }

    notas = [i["nota"] for i in catalogo]
    media = sum(notas) / len(notas)
    assistidos = sum(1 for i in catalogo if i["assistido"])
    pendentes = len(catalogo) - assistidos

    por_genero = {}
    for i in catalogo:
        por_genero[i["genero"]] = por_genero.get(i["genero"], 0) + 1

    genero_top = max(por_genero, key=por_genero.get)  # type: ignore[arg-type]
    com_comentario = sum(1 for i in catalogo if i.get("comentario", "").strip())

    return {
        "total": len(catalogo),
        "media_notas": round(media, 2),
        "assistidos": assistidos,
        "pendentes": pendentes,
        "genero_top": genero_top,
        "por_genero": por_genero,
        "com_comentario": com_comentario,
    }
