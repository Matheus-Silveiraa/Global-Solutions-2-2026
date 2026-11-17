"""Citizen Assist AI - interface de texto.

Execução (a partir da pasta do projeto):
    python src/sistema.py
    python src/sistema.py caminho/para/outra_base.json   (opcional)
"""
import sys

import base as base_mod
import busca
import respostas

MAX_RELACIONADOS = 5


def ler(prompt):
    """Lê uma linha; trata Ctrl+C / fim de entrada saindo com mensagem educada."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print("\nAté logo!")
        sys.exit(0)


def escolher_numero(prompt, maximo):
    """Pede um número de 0 a 'maximo'. Repete até a entrada ser válida."""
    while True:
        texto = ler(prompt).strip()
        if texto.isdigit() and 0 <= int(texto) <= maximo:
            return int(texto)
        print(f"Opção inválida. Digite um número de 0 a {maximo}.")


def mostrar_cabecalho():
    print("=" * 60)
    print(" CITIZEN ASSIST AI - orientação cidadã (protótipo)")
    print("=" * 60)
    print(respostas.AVISO_NAO_OFICIAL)
    print("Não digite dados pessoais (CPF, RG, endereço, e-mail...).")
    print()


def mostrar_menu(modelo):
    print("\nMENU")
    print("  1 - Fazer uma pergunta")
    print("  2 - Escolher um tema")
    print("  3 - Ver os temas disponíveis")
    print(f"  4 - Trocar o modelo de resposta (atual: {modelo} - {respostas.MODELOS[modelo]['nome']})")
    print("  0 - Sair")


def mostrar_registro(base, reg_id, modelo):
    """Mostra a resposta e permite navegar pelos assuntos relacionados (grafo)."""
    while True:
        print()
        print(respostas.formatar_resposta(base["registros"][reg_id], modelo))
        vizinhos = sorted(base["grafo"][reg_id])[:MAX_RELACIONADOS]
        if not vizinhos:
            return
        print()
        print(respostas.formatar_opcoes(base, vizinhos, "Assuntos relacionados para continuar:"))
        print("  [0] Voltar ao menu")
        escolha = escolher_numero("Escolha uma opção: ", len(vizinhos))
        if escolha == 0:
            return
        reg_id = vizinhos[escolha - 1]


def fluxo_pergunta(base, modelo):
    texto = ler("\nDigite sua dúvida (ou Enter para voltar): ")
    if texto.strip() == "":
        print(respostas.MENSAGENS["vazia"])
        return
    resultado = busca.consultar(texto, base)
    tipo = resultado["tipo"]
    if tipo in respostas.MENSAGENS:
        print("\n" + respostas.MENSAGENS[tipo])
    elif tipo == "sem_resposta":
        print("\n" + respostas.formatar_sem_resposta(base, resultado["ids"]))
    elif tipo == "ambigua":
        ids = resultado["ids"]
        print("\n" + respostas.formatar_ambigua(base, ids))
        print("  [0] Nenhum deles / voltar ao menu")
        escolha = escolher_numero("Escolha uma opção: ", len(ids))
        if escolha != 0:
            mostrar_registro(base, ids[escolha - 1], modelo)
    else:
        mostrar_registro(base, resultado["ids"][0], modelo)


def fluxo_tema(base, modelo):
    siglas = sorted(base["temas"])
    print("\nTEMAS")
    for n, sigla in enumerate(siglas, start=1):
        print(f"  [{n}] {base['temas'][sigla]}")
    print("  [0] Voltar")
    escolha = escolher_numero("Escolha um tema: ", len(siglas))
    if escolha == 0:
        return
    sigla = siglas[escolha - 1]

    subtemas = sorted(base["arvore"].get(sigla, {}))
    print(f"\n{base['temas'][sigla].upper()} - assuntos")
    for n, sub in enumerate(subtemas, start=1):
        print(f"  [{n}] {sub}")
    print("  [0] Voltar")
    escolha = escolher_numero("Escolha um assunto: ", len(subtemas))
    if escolha == 0:
        return
    ids = base["arvore"][sigla][subtemas[escolha - 1]]

    print(respostas.formatar_opcoes(base, ids, f"\n{subtemas[escolha - 1]} - perguntas disponíveis:"))
    print("  [0] Voltar")
    escolha = escolher_numero("Escolha uma pergunta: ", len(ids))
    if escolha != 0:
        mostrar_registro(base, ids[escolha - 1], modelo)


def mostrar_temas(base):
    print("\nTemas disponíveis na base:")
    for sigla in sorted(base["temas"]):
        subtemas = base["arvore"].get(sigla, {})
        total = sum(len(v) for v in subtemas.values())
        print(f"  - {base['temas'][sigla]}: {total} orientações")
        print("      assuntos: " + ", ".join(sorted(subtemas)))


def trocar_modelo(modelo):
    novo = "A" if modelo == "B" else "B"
    print(f"\nModelo de resposta alterado para {novo} - {respostas.MODELOS[novo]['nome']}.")
    return novo


def main():
    caminho = sys.argv[1] if len(sys.argv) > 1 else base_mod.CAMINHO_PADRAO
    try:
        base = base_mod.carregar_base(caminho)
    except base_mod.BaseInvalidaError as erro:
        print(f"Não foi possível iniciar o assistente: {erro}")
        print("Verifique o arquivo data/base_conhecimento.json e tente novamente.")
        sys.exit(1)

    mostrar_cabecalho()
    print(f"Base carregada: {len(base['registros'])} orientações em {len(base['temas'])} temas "
          f"(versão {base['meta']['versao_base']}).")
    for aviso in base["avisos"]:
        print("Aviso sobre a base:", aviso)

    modelo = "B"
    while True:
        mostrar_menu(modelo)
        opcao = ler("Escolha uma opção: ").strip()
        if opcao == "1":
            fluxo_pergunta(base, modelo)
        elif opcao == "2":
            fluxo_tema(base, modelo)
        elif opcao == "3":
            mostrar_temas(base)
        elif opcao == "4":
            modelo = trocar_modelo(modelo)
        elif opcao == "0":
            print("Obrigado por usar o Citizen Assist AI. Até logo!")
            break
        elif opcao == "":
            print("Você não digitou nada. Escolha uma das opções do menu.")
        else:
            print("Essa opção não existe. Escolha uma das opções do menu.")


if __name__ == "__main__":
    main()
