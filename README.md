# CINELOG

Sistema de gerenciamento de catálogo de filmes e séries via terminal (CLI), desenvolvido em Python.

## Funcionalidades

- Cadastrar filmes/séries com título, gênero, ano, status, nota, comentário e data de cadastro
- Listar o catálogo com ordenação por título, ano, nota ou data de cadastro
- Filtrar a listagem por status (todos, apenas assistidos, apenas pendentes)
- Marcar/desmarcar títulos como assistidos
- Avaliar títulos com nota de 0 a 10 (exibida também em formato de estrelas)
- Adicionar ou atualizar comentários/resenhas por título
- Buscar por gênero
- Buscar por parte do título (busca parcial)
- Excluir títulos do catálogo com confirmação
- Calcular estatísticas: total de títulos, média das notas, total assistido, total pendente, gênero mais frequente e quantidade de títulos com comentário
- Interface colorida no terminal (com códigos ANSI, sem dependências externas)
- Persistência automática em arquivo `catalogo.json`
- Backup automático do catálogo anterior em `catalogo.json.bak`
- Salvamento automático após cada alteração

## Requisitos

- Python 3.7 ou superior
- Nenhuma biblioteca externa necessária (usa apenas a biblioteca padrão)

## Como executar

1. Clone o repositório ou baixe os arquivos do projeto.
2. No terminal, dentro da pasta do projeto, execute:

```bash
python main.py
```

Opcionalmente, é recomendado usar um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate       # Windows
```

## Menu de opções

```
+------------------------------+
|           CINELOG            |
+------------------------------+
| 1. Cadastrar filme/série     |
| 2. Listar catálogo           |
| 3. Marcar como assistido     |
| 4. Avaliar (0 a 10)          |
| 5. Buscar por gênero         |
| 6. Excluir filme/série       |
| 7. Calcular estatísticas     |
| 8. Buscar por título         |
| 9. Sair                      |
+------------------------------+
```

## Persistência de dados

- O catálogo é salvo automaticamente em `catalogo.json` após cada alteração (cadastro, edição, avaliação, exclusão ou mudança de status).
- Ao sair, o programa verifica se houve alterações antes de gravar novamente, evitando sobrescritas desnecessárias.
- Ao iniciar, o programa tenta carregar o arquivo `catalogo.json`. Caso não exista ou esteja corrompido, inicia com o catálogo vazio.
- Antes de cada gravação, é criado um backup do catálogo anterior em `catalogo.json.bak`.
- O arquivo `catalogo.json` está listado no `.gitignore` e não é versionado.

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

## Observações

- Os títulos são armazenados sem duplicatas (comparação não diferencia maiúsculas/minúsculas).
- A nota deve estar entre 0 e 10.
- O ano deve estar entre 1900 e o ano atual + 5.
- A limpeza de tela é automática em cada operação (compatível com Windows e Linux/macOS).
- Interrupções com Ctrl+C são tratadas e o catálogo é salvo antes de sair.
- Recomenda-se adicionar `catalogo.json.bak` ao `.gitignore` caso o backup não deva ser versionado.

## Estrutura do projeto

```
.
├── main.py
├── README.md
├── .gitignore
└── catalogo.json   (gerado em tempo de execução, não versionado)
```

## Licença

Projeto livre para uso e estudo.
