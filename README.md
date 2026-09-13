# CINELOG API

API REST para catalogar filmes e séries, construída com **Flask** e persistência em **JSON**.

O projeto começou como um CLI de terminal e foi refatorado para uma API REST.
A lógica de negócio ficou isolada em `cinelog_core.py` (sem `print`, sem `input`),
e a camada HTTP em `app.py` consome essas funções e expõe endpoints REST.

## Funcionalidades

- Cadastrar filmes/séries com título, gênero, ano, status, nota, comentário e data de cadastro
- Listar o catálogo com ordenação por título, ano, nota ou data de cadastro
- Filtrar a listagem por status (todos, apenas assistidos, apenas pendentes)
- Buscar por gênero
- Buscar por parte do título (busca parcial)
- Marcar/desmarcar títulos como assistidos
- Avaliar títulos com nota de 0 a 10
- Adicionar ou atualizar comentários/resenhas por título
- Excluir títulos do catálogo
- Calcular estatísticas: total de títulos, média das notas, total assistido,
  total pendente, gênero mais frequente e quantidade de títulos com comentário
- Persistência automática em arquivo `catalogo.json`
- Backup automático do catálogo anterior em `catalogo.json.bak`

## Requisitos

- Python 3.10 ou superior
- Flask 3.0 ou superior

## Como executar

### 1. Clonar o repositório

```bash
git clone https://github.com/tiago774/CLI-CINELOG.git
cd CLI-CINELOG
```

### 2. Criar e ativar ambiente virtual

```bash
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# .venv\Scripts\activate      # Windows
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Rodar a API

```bash
python app.py
```

A API estará disponível em `http://localhost:5000`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Informações da API |
| `GET` | `/api/generos` | Lista os gêneros disponíveis |
| `GET` | `/api/filmes` | Lista o catálogo (aceita filtros) |
| `GET` | `/api/filmes/<titulo>` | Obtém um título específico |
| `POST` | `/api/filmes` | Cadastra um novo título |
| `PUT` | `/api/filmes/<titulo>` | Atualiza campos de um título |
| `PATCH` | `/api/filmes/<titulo>/assistido` | Alterna o status "assistido" |
| `DELETE` | `/api/filmes/<titulo>` | Remove um título |
| `GET` | `/api/estatisticas` | Estatísticas do catálogo |

### Filtros disponíveis em `GET /api/filmes`

| Query param | Valores aceitos | Exemplo |
|-------------|-----------------|---------|
| `genero` | um dos gêneros válidos | `?genero=Ação` |
| `assistido` | `true` / `false` | `?assistido=false` |
| `busca` | texto livre (busca parcial) | `?busca=matrix` |
| `ordenar` | `titulo`, `ano`, `nota`, `data`, `cadastro` | `?ordenar=nota` |

## Exemplos de uso

### Cadastrar um filme

```bash
curl -X POST http://localhost:5000/api/filmes \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Matrix",
    "genero": "Ficção",
    "ano": 1999,
    "assistido": true,
    "nota": 9.5,
    "comentario": "Clássico absoluto"
  }'
```

### Listar todos, ordenados por nota

```bash
curl -s "http://localhost:5000/api/filmes?ordenar=nota" | jq
```

### Filtrar por gênero e status

```bash
curl -s 'http://localhost:5000/api/filmes?genero=Ficção&assistido=true' | jq
```

> ⚠️ Use **aspas simples** ao redor da URL quando ela tiver acentos ou `&`.

### Buscar por parte do título

```bash
curl -s "http://localhost:5000/api/filmes?busca=mat" | jq
```

### Obter um título específico

```bash
curl -s http://localhost:5000/api/filmes/Matrix | jq
```

### Atualizar a nota e o comentário

```bash
curl -X PUT http://localhost:5000/api/filmes/Matrix \
  -H "Content-Type: application/json" \
  -d '{"nota": 10, "comentario": "Melhor que eu lembrava"}'
```

### Alternar status "assistido"

```bash
curl -X PATCH http://localhost:5000/api/filmes/Matrix/assistido
```

### Excluir um título

```bash
curl -X DELETE http://localhost:5000/api/filmes/Matrix
```

### Ver estatísticas

```bash
curl -s http://localhost:5000/api/estatisticas | jq
```

## Códigos de erro

| Status | Quando acontece |
|--------|-----------------|
| `400 Bad Request` | Payload inválido (nota fora de 0–10, gênero inexistente, ano inválido) |
| `404 Not Found` | Título não cadastrado |
| `409 Conflict` | Título já cadastrado |

Todas as respostas de erro seguem o formato:

```json
{
  "erro": "mensagem descritiva",
  "tipo": "validacao"
}
```

Os valores possíveis para `tipo` são: `validacao`, `nao_encontrado`, `conflito`, `rota` e `metodo`.

## Gêneros disponíveis

- Ação
- Comédia
- Drama
- Ficção
- Romance
- Terror

## Estrutura do `catalogo.json`

```json
[
    {
        "titulo": "Exemplo",
        "genero": "Ação",
        "ano": 2024,
        "assistido": true,
        "nota": 8.5,
        "comentario": "Ótimo filme",
        "data_cadastro": "2025-01-15T14:30:00"
    }
]
```

## Persistência de dados

- O catálogo é salvo automaticamente em `catalogo.json` após cada alteração
  (cadastro, edição, avaliação, exclusão ou mudança de status).
- Ao iniciar, a aplicação tenta carregar o arquivo `catalogo.json`. Caso não exista
  ou esteja corrompido, inicia com o catálogo vazio.
- Antes de cada gravação, é criado um backup do catálogo anterior em `catalogo.json.bak`.
- Tanto `catalogo.json` quanto `catalogo.json.bak` estão no `.gitignore` e não
  são versionados.

## Observações

- Os títulos são armazenados sem duplicatas (comparação não diferencia maiúsculas/minúsculas).
- A nota deve estar entre 0 e 10.
- O ano deve estar entre 1900 e o ano atual + 5.
- Interrupções com `Ctrl+C` são tratadas e o catálogo é salvo antes de sair.

## Estrutura do projeto

```
.
├── app.py                    # API Flask (rotas + tratamento de erros)
├── cinelog_core.py           # Lógica de negócio pura (JSON + validação)
├── requirements.txt          # Dependências (Flask)
├── catalogo.exemplo.json     # Exemplo de estrutura do catálogo
├── README.md
├── .gitignore
└── catalogo.json             # Gerado em tempo de execução, não versionado
```

## Licença

Projeto livre para uso e estudo.
