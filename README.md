# 🎬 CINELOG

Sistema simples de gerenciamento de catálogo de filmes e séries via terminal, desenvolvido em Python.

## Funcionalidades

- Cadastrar filmes/séries (com título, gênero, ano, status e nota)
- Listar todo o catálogo
- Marcar/desmarcar como assistido
- Avaliar títulos (nota de 0 a 10)
- Buscar por gênero
- Excluir títulos do catálogo
- Calcular estatísticas (média das notas, total assistido, gênero mais frequente)
- Persistência automática em arquivo `catalogo.json`

## Requisitos

- Python 3.7 ou superior
- Nenhuma biblioteca externa necessária (usa apenas `json` e `os`)

## Como executar

1. Salve o código em um arquivo, por exemplo: `cinelog.py`
2. No terminal, execute:

```bash
python cinelog.py
```

## Menu de opções

```
╔══════════════════════════════╗
║           CINELOG            ║
╠══════════════════════════════╣
║ 1. Cadastrar filme/série     ║
║ 2. Listar catálogo           ║
║ 3. Marcar como assistido     ║
║ 4. Avaliar (0 a 10)          ║
║ 5. Buscar por gênero         ║
║ 6. Excluir filme/série       ║
║ 7. Calcular estatísticas     ║
║ 8. Sair                      ║
╚══════════════════════════════╝
```

## Persistência de dados

- Ao sair (opção **8**), o catálogo é salvo automaticamente em `catalogo.json`.
- Ao iniciar, o programa tenta carregar esse arquivo.
- Caso o arquivo não exista ou esteja corrompido, o programa inicia com o catálogo vazio.

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
        "nota": 8.5
    }
]
```

## Observações

- Os títulos são armazenados sem duplicatas (comparação não diferencia maiúsculas/minúsculas).
- A nota deve estar entre **0** e **10**.
- A limpeza da tela é automática em cada operação (compatível com Windows e Linux/macOS).

## Licença

Projeto livre para uso e estudo.
