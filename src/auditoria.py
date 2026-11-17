"""Demonstração visual da suíte de testes do Citizen Assist AI.

Execute na raiz do repositório:
    python src/auditoria.py

O script reaproveita a suíte oficial de src/testes.py, atualiza os relatórios
e apresenta um resumo por categoria no terminal.
"""
import csv
import os
from collections import defaultdict

import testes


RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_RESULTADOS = os.path.join(RAIZ, "data", "resultados_testes.csv")


def carregar_resultados():
    with open(ARQUIVO_RESULTADOS, newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def barra(percentual, largura=24):
    preenchido = round(percentual / 100 * largura)
    return "[" + "#" * preenchido + "-" * (largura - preenchido) + "]"


def exibir_painel(resultados):
    total = len(resultados)
    acertos = sum(item["acerto"] == "sim" for item in resultados)
    percentual = (acertos / total * 100) if total else 0
    falhas = [item for item in resultados if item["acerto"] != "sim"]

    print("\n" + "=" * 62)
    print("                 CITIZEN ASSIST AI")
    print("               PAINEL DE AUDITORIA")
    print("=" * 62)
    print(f"Casos executados : {total}")
    print(f"Casos aprovados  : {acertos}")
    print(f"Casos com falha  : {len(falhas)}")
    print(f"Taxa de acerto   : {percentual:.1f}%")
    print(f"{barra(percentual)}")
    print("-" * 62)

    categorias = defaultdict(list)
    for item in resultados:
        categorias[item["categoria"]].append(item)

    print("RESULTADO POR CATEGORIA")
    for categoria, itens in sorted(categorias.items()):
        aprovados = sum(item["acerto"] == "sim" for item in itens)
        taxa = aprovados / len(itens) * 100
        print(f"{categoria:<16} {aprovados:>2}/{len(itens):<2} "
              f"{taxa:>6.1f}%  {barra(taxa, 16)}")

    print("-" * 62)
    if falhas:
        print("CASOS QUE PRECISAM DE ATENÇÃO")
        for item in falhas:
            print(f"- {item['id']}: esperado {item['esperado']}; "
                  f"obtido {item['obtido']}")
            print(f"  Consulta: {item['entrada']}")
    else:
        print("Todos os casos desta suíte passaram.")

    print("-" * 62)
    print("Relatórios atualizados:")
    print("  data/resultados_testes.csv")
    print("  docs/resultados_testes.md")
    print("\nObservação: o resultado vale para estes casos de teste.")
    print("Ele não garante o comportamento para toda pergunta possível.")
    print("=" * 62)


def main():
    print("=" * 62)
    print("Iniciando a suíte automatizada...")
    print("=" * 62)
    testes.main()
    resultados = carregar_resultados()
    exibir_painel(resultados)


if __name__ == "__main__":
    main()
