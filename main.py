import datetime
import json
import os
import pathlib
import shutil
import sys

generos = ["Ação", "Comédia", "Drama", "Ficção", "Romance", "Terror"]
catalogo = []

PASTA_SCRIPT = pathlib.Path(__file__).resolve().parent
ARQUIVO_JSON = PASTA_SCRIPT / "catalogo.json"
ARQUIVO_BACKUP = PASTA_SCRIPT / "catalogo.json.bak"


class Cor:
    RESET    = "\033[0m"
    NEGRITO  = "\033[1m"
    VERMELHO = "\033[91m"
    VERDE    = "\033[92m"
    AMARELO  = "\033[93m"
    AZUL     = "\033[94m"
    MAGENTA  = "\033[95m"
    CIANO    = "\033[96m"
    CINZA    = "\033[90m"


if os.name == "nt":
    os.system("")


def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')


def cabecalho(texto):
    print(f"{Cor.CIANO}{Cor.NEGRITO}{texto}{Cor.RESET}")


def sucesso(texto):
    print(f"{Cor.VERDE}{texto}{Cor.RESET}")


def aviso(texto):
    print(f"{Cor.AMARELO}{texto}{Cor.RESET}")


def erro(texto):
    print(f"{Cor.VERMELHO}{texto}{Cor.RESET}")


def info(texto):
    print(f"{Cor.CINZA}{texto}{Cor.RESET}")


def nota_para_estrelas(nota):
    try:
        nota = float(nota)
    except (ValueError, TypeError):
        return "—"

    if nota < 1:
        return "☆"
    elif nota < 2:
        return "⯨"
    elif nota < 3:
        return "★"
    elif nota < 4:
        return "★⯨"
    elif nota < 5:
        return "★★"
    elif nota < 6:
        return "★★⯨"
    elif nota < 7:
        return "★★★"
    elif nota < 8:
        return "★★★⯨"
    elif nota < 9:
        return "★★★★"
    elif nota < 10:
        return "★★★★⯨"
    else:
        return "★★★★★"


def colorir_nota(nota):
    estrelas = nota_para_estrelas(nota)
    try:
        n = float(nota)
    except (ValueError, TypeError):
        return f"{Cor.CINZA}{estrelas}{Cor.RESET}"

    if n >= 8:
        cor = Cor.VERDE
    elif n >= 5:
        cor = Cor.AMARELO
    else:
        cor = Cor.VERMELHO
    return f"{cor}{estrelas}{Cor.RESET}"


def cor_status(assistido):
    if assistido:
        return f"{Cor.VERDE}Assistido{Cor.RESET}"
    return f"{Cor.AMARELO}Pendente{Cor.RESET}"



def _snapshot_catalogo():
    return json.dumps(catalogo, ensure_ascii=False, sort_keys=True)


def gravar_json(silencioso=False, criar_backup=True):
    try:
        if len(catalogo) == 0 and ARQUIVO_JSON.exists():
            try:
                with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
                    antigo = json.load(f)
                if isinstance(antigo, list) and len(antigo) > 0:
                    aviso(
                        f"⚠  Atenção: sobrescrevendo {len(antigo)} título(s) "
                        f"do JSON por uma lista vazia!"
                    )
            except (json.JSONDecodeError, OSError):
                pass

        if criar_backup and ARQUIVO_JSON.exists():
            try:
                shutil.copy2(ARQUIVO_JSON, ARQUIVO_BACKUP)
            except OSError as e:
                aviso(f"Não foi possível criar backup: {e}")

        with open(ARQUIVO_JSON, "w", encoding="utf-8") as arquivo:
            json.dump(catalogo, arquivo, ensure_ascii=False, indent=4)

        if not silencioso:
            sucesso(f"Catálogo salvo em {ARQUIVO_JSON}")
        return True

    except OSError as e:
        erro(f"Erro ao salvar o catálogo: {e}")
        return False


def salvar_auto():
    gravar_json(silencioso=True)


def validar_json():
    info(f"Lendo arquivo: {ARQUIVO_JSON}")

    if not ARQUIVO_JSON.exists():
        aviso(f"Arquivo '{ARQUIVO_JSON.name}' não existe. Iniciando catálogo vazio.")
        return []

    try:
        with open(ARQUIVO_JSON, "r", encoding="utf-8") as arquivo:
            data = json.load(arquivo)

        if not isinstance(data, list):
            erro("Conteúdo do JSON não é uma lista. Iniciando vazio.")
            return []

        # Normaliza cada registro
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

        sucesso(f"{len(data)} título(s) carregado(s) do JSON.")
        return data

    except json.JSONDecodeError as e:
        erro(f"JSON inválido ({e}). Iniciando vazio.")
        if ARQUIVO_JSON.exists():
            aviso(f"O arquivo corrompido NÃO foi apagado. Corrija manualmente:")
            info(f"   {ARQUIVO_JSON}")
        return []
    except OSError as e:
        erro(f"Erro ao ler o arquivo: {e}")
        return []


def cadastrar_filme_serie():
    limpar_tela()
    cabecalho("=== Cadastro de filme/série ===\n")
    titulo = input("Digite o título do filme/série: ").strip()

    if not titulo:
        erro("Título não pode ser vazio.")
        return

    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            aviso(f"'{titulo}' já está cadastrado.")
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
            erro("Número fora do intervalo. Tente novamente.")
        except ValueError:
            erro("Digite um número válido.")

    while True:
        try:
            ano = int(input("Digite o ano: "))
            if 1900 <= ano <= datetime.datetime.now().year + 5:
                break
            erro("Ano inválido. Tente novamente.")
        except ValueError:
            erro("Digite um ano válido.")

    assistido = input("Já assistiu? (S/N): ").strip().upper() == "S"

    while True:
        try:
            nota = float(input("Digite a nota (0 a 10): "))
            if 0 <= nota <= 10:
                break
            erro("A nota deve estar entre 0 e 10.")
        except ValueError:
            erro("Digite uma nota válida.")

    comentario = input("Comentário/resenha (opcional, Enter para pular): ").strip()

    catalogo.append({
        "titulo": titulo,
        "genero": genero,
        "ano": ano,
        "assistido": assistido,
        "nota": nota,
        "comentario": comentario,
        "data_cadastro": datetime.datetime.now().isoformat(timespec="seconds")
    })
    salvar_auto()
    sucesso(f"\n'{titulo}' cadastrado com sucesso!")


def _aplicar_filtro_status(itens):
    print(f"\n{Cor.CINZA}Filtrar por status:{Cor.RESET}")
    print("1. Todos")
    print("2. Apenas assistidos")
    print("3. Apenas pendentes")

    escolha = input("Escolha (Enter = 1): ").strip() or "1"

    if escolha == "2":
        return [i for i in itens if i["assistido"]], "Apenas assistidos"
    elif escolha == "3":
        return [i for i in itens if not i["assistido"]], "Apenas pendentes"
    return itens, "Todos"


def listar_catalogo():
    limpar_tela()
    if not catalogo:
        aviso("Nenhum filme/série cadastrado.")
        return

    print("Ordenar por:")
    print("1. Título (A-Z)")
    print("2. Ano (crescente)")
    print("3. Nota (maior → menor)")
    print("4. Data de cadastro (mais recente primeiro)")
    print("5. Sem ordenação (ordem de cadastro)")

    opcao = input("Escolha uma opção (Enter = 1): ").strip() or "1"

    itens = list(catalogo)

    if opcao == "1":
        itens.sort(key=lambda i: i["titulo"].lower())
        criterio = "Título (A-Z)"
    elif opcao == "2":
        itens.sort(key=lambda i: i["ano"])
        criterio = "Ano (crescente)"
    elif opcao == "3":
        itens.sort(key=lambda i: i["nota"], reverse=True)
        criterio = "Nota (maior → menor)"
    elif opcao == "4":
        itens.sort(key=lambda i: i.get("data_cadastro", ""), reverse=True)
        criterio = "Data de cadastro (mais recente primeiro)"
    elif opcao == "5":
        criterio = "Ordem de cadastro"
    else:
        aviso("Opção inválida. Usando ordem de cadastro.")
        criterio = "Ordem de cadastro"

    itens, filtro = _aplicar_filtro_status(itens)

    limpar_tela()
    cabecalho(f"=== Catálogo | Ordenado por: {criterio} | Filtro: {filtro} ===\n")

    if not itens:
        aviso("Nenhum título corresponde ao filtro escolhido.")
        return

    print(f"{Cor.NEGRITO}{'TÍTULO'.ljust(30)} {'GÊNERO'.ljust(12)} {'ANO'.ljust(6)} "
          f"{'STATUS'.ljust(20)} {'DATA'.ljust(20)} NOTA{Cor.RESET}")
    print("-" * 115)

    for item in itens:
        status = cor_status(item["assistido"])
        estrelas = colorir_nota(item["nota"])
        data = item.get("data_cadastro", "—").replace("T", " ")

        status_plain = "Assistido" if item["assistido"] else "Pendente"
        padding = " " * (20 - len(status_plain))
        status_col = status + padding

        print(f"{item['titulo'][:30].ljust(30)} {item['genero'].ljust(12)} "
              f"{str(item['ano']).ljust(6)} {status_col} "
              f"{data.ljust(20)} {estrelas} ({item['nota']:.1f})")

        comentario = item.get("comentario", "").strip()
        if comentario:
            print(f"   {Cor.CINZA}{comentario}{Cor.RESET}")


def marcar_assistido():
    limpar_tela()
    cabecalho("=== Marcar como assistido ===")
    titulo = input("Digite o título do filme/série: ").strip()
    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            item["assistido"] = not item["assistido"]
            salvar_auto()
            estado = "Assistido" if item["assistido"] else "Não assistido"
            sucesso(f"Status atualizado para '{estado}'.")
            return
    erro("Filme/Série não encontrado.")


def avaliar():
    limpar_tela()
    cabecalho("=== Avaliar ===")
    titulo = input("Digite o título do filme/série: ").strip()
    for item in catalogo:
        if item["titulo"].lower() == titulo.lower():
            while True:
                try:
                    nova_nota = float(input("Digite a nova nota (0 a 10): "))
                    if 0 <= nova_nota <= 10:
                        item["nota"] = nova_nota
                        estrelas = colorir_nota(nova_nota)
                        sucesso(f"Nota atualizada: {estrelas} ({nova_nota:.1f})")

                        atualizar = input("Deseja atualizar o comentário? (S/N): ").strip().upper()
                        if atualizar == "S":
                            novo_comentario = input("Novo comentário/resenha: ").strip()
                            item["comentario"] = novo_comentario
                            sucesso("Comentário atualizado.")

                        salvar_auto()
                        return
                    erro("A nota deve estar entre 0 e 10.")
                except ValueError:
                    erro("Digite uma nota válida.")
    erro("Filme/Série não encontrado.")


def buscar_por_titulo():
    limpar_tela()
    cabecalho("=== Buscar por título (busca parcial) ===")
    termo = input("Digite parte do título: ").strip().lower()

    if not termo:
        erro("Digite ao menos um caractere.")
        return

    encontrados = [i for i in catalogo if termo in i["titulo"].lower()]

    if not encontrados:
        aviso(f"Nenhum título contém '{termo}'.")
        return

    print(f"\n{Cor.CINZA}{len(encontrados)} resultado(s) para '{termo}':{Cor.RESET}\n")
    for item in encontrados:
        status = cor_status(item["assistido"])
        estrelas = colorir_nota(item["nota"])
        print(f"  {Cor.NEGRITO}{item['titulo']}{Cor.RESET} ({item['ano']}) "
              f"- {item['genero']} - {status} - {estrelas} ({item['nota']:.1f})")
        if item.get("comentario"):
            print(f"     {Cor.CINZA}{item['comentario']}{Cor.RESET}")


def buscar_por_genero():
    limpar_tela()
    cabecalho("=== Buscar por gênero ===")
    print("Gêneros disponíveis:")
    for i, genero in enumerate(generos, start=1):
        print(f"{i}. {genero}")

    try:
        opcao_genero = int(input("Escolha o gênero (número): ")) - 1
        if not 0 <= opcao_genero < len(generos):
            erro("Opção inválida.")
            return
        genero_escolhido = generos[opcao_genero]
    except ValueError:
        erro("Opção inválida.")
        return

    encontrados = [i for i in catalogo if i["genero"] == genero_escolhido]
    if encontrados:
        print(f"\n{Cor.CINZA}Filmes/Séries do gênero {genero_escolhido}:{Cor.RESET}\n")
        for item in encontrados:
            estrelas = colorir_nota(item["nota"])
            print(f"  {Cor.NEGRITO}{item['titulo']}{Cor.RESET} ({item['ano']}) {estrelas}")
            if item.get("comentario"):
                print(f"     {Cor.CINZA}{item['comentario']}{Cor.RESET}")
    else:
        aviso(f"Nenhum título encontrado para o gênero {genero_escolhido}.")


def excluir_filme_serie():
    limpar_tela()
    cabecalho("=== Excluir filme/série ===")
    titulo = input("Digite o título a ser excluído: ").strip()

    for i, item in enumerate(catalogo):
        if item["titulo"].lower() == titulo.lower():
            print(f"\n{Cor.NEGRITO}Título:{Cor.RESET} {item['titulo']}")
            print(f"{Cor.NEGRITO}Gênero:{Cor.RESET} {item['genero']} | "
                  f"{Cor.NEGRITO}Ano:{Cor.RESET} {item['ano']} | "
                  f"{Cor.NEGRITO}Status:{Cor.RESET} "
                  f"{'Assistido' if item['assistido'] else 'Pendente'}")
            print(f"{Cor.NEGRITO}Nota:{Cor.RESET} "
                  f"{colorir_nota(item['nota'])} ({item['nota']:.1f})")

            confirmacao = input(
                f"\n{Cor.VERMELHO}Tem certeza que deseja excluir? (S/N): {Cor.RESET}"
            ).strip().upper()

            if confirmacao == "S":
                del catalogo[i]
                salvar_auto()
                sucesso("Filme/Série excluído do catálogo.")
            else:
                aviso("Exclusão cancelada.")
            return

    erro("Filme/Série não encontrado.")


def calcular_estatisticas():
    limpar_tela()
    if not catalogo:
        aviso("Nenhum filme/série cadastrado.")
        return

    notas = [i["nota"] for i in catalogo if isinstance(i.get("nota"), (int, float))]
    media = sum(notas) / len(notas) if notas else 0
    total_assistido = sum(1 for i in catalogo if i["assistido"])
    total_pendente = len(catalogo) - total_assistido

    contagem = {}
    for item in catalogo:
        contagem[item["genero"]] = contagem.get(item["genero"], 0) + 1
    genero_top = max(contagem, key=contagem.get) # type: ignore

    com_comentario = sum(1 for i in catalogo if i.get("comentario", "").strip())

    cabecalho("=== Estatísticas do CINELOG ===\n")
    print(f"Total de títulos:        {Cor.NEGRITO}{len(catalogo)}{Cor.RESET}")
    print(f"Média das notas:         {media:.2f} {colorir_nota(media)}")
    print(f"Total assistido:         {Cor.VERDE}{total_assistido}{Cor.RESET}")
    print(f"Total pendente:          {Cor.AMARELO}{total_pendente}{Cor.RESET}")
    print(f"Gênero mais frequente:   {Cor.CIANO}{genero_top}{Cor.RESET} "
          f"({contagem[genero_top]} títulos)")
    print(f"Com comentário/resenha:  {Cor.MAGENTA}{com_comentario}{Cor.RESET}")


def exibir_menu():
    print(f"""{Cor.CIANO}{Cor.NEGRITO}
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
║ 8. Buscar por título         ║
║ 9. Sair                      ║
╚══════════════════════════════╝
{Cor.RESET}""")


def main():
    global catalogo
    catalogo = validar_json()

    estado_inicial = _snapshot_catalogo()

    try:
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
                buscar_por_titulo()
            elif opcao == "9":
                sucesso("Saindo do CINELOG. Até a próxima!")
                break
            else:
                erro("Opção inválida. Tente novamente.")

            input(f"\n{Cor.CINZA}Pressione Enter para continuar...{Cor.RESET}")

    except KeyboardInterrupt:
        print()
        aviso("\nInterrompido pelo usuário.")
    except Exception as e:
        print()
        erro(f"\nErro inesperado: {e}")
    finally:
        # Só grava se o catálogo foi realmente alterado
        estado_final = _snapshot_catalogo()
        if estado_final != estado_inicial:
            gravar_json(silencioso=True)
            info(f"Alterações salvas em {ARQUIVO_JSON.name}")
        else:
            info("Nenhuma alteração — JSON preservado.")


if __name__ == "__main__":
    main()
