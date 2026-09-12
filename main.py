import json
import os

generos = ["Ação", "Comédia", "Drama", "Ficção", "Romance", "Terror"]
catalogo = []


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def cadastrar_filme_serie():
    limpar_tela()
    print("=== Cadastro de filme/série ===\n")
    titulo = input("Digite o título do filme/série: ").strip()

    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            print(f"'{titulo}' já está cadastrado.")
            return

    print("\nGêneros disponíveis:")
    for i, genero in enumerate(generos, start=1):
        print(f"{i}. {genero}")

    while True:
        try:
            opcao_genero = int(input("Escolha o gênero (número): ")) - 1
            if 0 <= opcao_genero < len(generos):
                genero = generos[opcao_genero]
                break
            print("Número fora do intervalo. Tente novamente.")
        except ValueError:
            print("Digite um número válido.")

    while True:
        try:
            ano = int(input("Digite o ano: "))
            break
        except ValueError:
            print("Digite um ano válido.")

    assistido = input("Já assistiu? (S/N): ").strip().upper() == "S"

    while True:
        try:
            nota = float(input("Digite a nota (0 a 10): "))
            if 0 <= nota <= 10:
                break
            print("A nota deve estar entre 0 e 10.")
        except ValueError:
            print("Digite uma nota válida.")

    catalogo.append({
        "titulo": titulo,
        "genero": genero,
        "ano": ano,
        "assistido": assistido,
        "nota": nota
    })
    print(f"\n'{titulo}' cadastrado com sucesso!")


def listar_catalogo():
    limpar_tela()
    if not catalogo:
        print("Nenhum filme/série cadastrado.")
        return

    print(f"{'TÍTULO'.ljust(30)} {'GÊNERO'.ljust(12)} {'ANO'.ljust(6)} "
          f"{'STATUS'.ljust(12)} NOTA")
    print("-" * 80)
    for item in catalogo:
        status = "Assistido" if item["assistido"] else "Pendente"
        print(f"{item['titulo'].ljust(30)} {item['genero'].ljust(12)} "
              f"{str(item['ano']).ljust(6)} {status.ljust(12)} {item['nota']:.1f}")


def marcar_assistido():
    limpar_tela()
    titulo = input("Digite o título do filme/série: ").strip()
    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            item["assistido"] = not item["assistido"]
            estado = "Assistido" if item["assistido"] else "Não assistido"
            print(f"Status atualizado para '{estado}'.")
            return
    print("Filme/Série não encontrado.")


def avaliar():
    limpar_tela()
    titulo = input("Digite o título do filme/série: ").strip()
    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            while True:
                try:
                    nova_nota = float(input("Digite a nova nota (0 a 10): "))
                    if 0 <= nova_nota <= 10:
                        item["nota"] = nova_nota
                        print("Nota atualizada.")
                        return
                    print("A nota deve estar entre 0 e 10.")
                except ValueError:
                    print("Digite uma nota válida.")
    print("Filme/Série não encontrado.")


def buscar_por_genero():
    limpar_tela()
    print("Gêneros disponíveis:")
    for i, genero in enumerate(generos, start=1):
        print(f"{i}. {genero}")

    try:
        opcao_genero = int(input("Escolha o gênero (número): ")) - 1
        genero_escolhido = generos[opcao_genero]
    except (ValueError, IndexError):
        print("Opção inválida.")
        return

    encontrados = [i for i in catalogo if i["genero"] == genero_escolhido]
    if encontrados:
        print(f"\nFilmes/Séries do gênero {genero_escolhido}:")
        for item in encontrados:
            print(f"- {item['titulo']} ({item['ano']})")
    else:
        print(f"Nenhum título encontrado para o gênero {genero_escolhido}.")


def excluir_filme_serie():
    limpar_tela()
    titulo = input("Digite o título a ser excluído: ").strip()
    for i, item in enumerate(catalogo):
        if item["titulo"].lower() == titulo.lower():
            del catalogo[i]
            print("Filme/Série excluído do catálogo.")
            return
    print("Filme/Série não encontrado.")


def calcular_estatisticas():
    limpar_tela()
    if not catalogo:
        print("Nenhum filme/série cadastrado.")
        return

    notas = [i["nota"] for i in catalogo if isinstance(i.get("nota"), (int, float))]
    media = sum(notas) / len(notas) if notas else 0
    total_assistido = sum(1 for i in catalogo if i["assistido"])

    contagem = {}
    for item in catalogo:
        contagem[item["genero"]] = contagem.get(item["genero"], 0) + 1
    genero_top = max(contagem, key=contagem.get) # type: ignore

    print(f"Média das notas: {media:.2f}")
    print(f"Total assistido: {total_assistido}")
    print(f"Gênero mais frequente: {genero_top}")


def gravar_json():
    try:
        with open("catalogo.json", "w", encoding="utf-8") as arquivo:
            json.dump(catalogo, arquivo, ensure_ascii=False, indent=4)
        print("Catálogo salvo em catalogo.json.")
    except OSError as e:
        print(f"Erro ao salvar o catálogo: {e}")


def validar_json():
    try:
        with open("catalogo.json", "r", encoding="utf-8") as arquivo:
            data = json.load(arquivo)
            if isinstance(data, list):
                return data
            print("Erro: conteúdo do JSON não é uma lista. Iniciando vazio.")
            return []
    except FileNotFoundError:
        print("Arquivo catalogo.json não encontrado. Iniciando vazio.")
        return []
    except json.JSONDecodeError:
        print("Erro ao decodificar o JSON. Iniciando vazio.")
        return []


def exibir_menu():
    print("""
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
""")


def main():
    global catalogo
    catalogo = validar_json()

    while True:
        exibir_menu()
        opcao = input("Digite o número da opção desejada: ").strip()

        if opcao == "1":
            cadastrar_filme_serie()
        elif opcao == "2":
            listar_catalogo()
        elif opcao == "3":
            marcar_assistido()
        elif opcao == "4":
            avaliar()
        elif opcao == "5":
            buscar_por_genero()
        elif opcao == "6":
            excluir_filme_serie()
        elif opcao == "7":
            calcular_estatisticas()
        elif opcao == "8":
            gravar_json()
            print("Saindo do CINELOG. Até a próxima! 🎬")
            break
        else:
            print("Opção inválida. Tente novamente.")

        input("\nPressione Enter para continuar...")


if __name__ == "__main__":
    main()
