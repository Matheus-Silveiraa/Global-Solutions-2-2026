"""Testes automáticos e indicadores do Citizen Assist AI.

Execução (a partir da pasta do projeto):
    python src/testes.py

Gera:
    data/resultados_testes.csv   (um registro por teste)
    docs/resultados_testes.md    (indicadores e comparação dos modelos)
"""
import contextlib
import csv
import io
import os
import sys
import time
from collections import deque

import base as base_mod
import busca
import respostas
import sistema

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
REPETICOES = 200  # cada consulta é repetida para medir um tempo médio confiável

# ---------------------------------------------------------------------------
# Casos de teste. 'esperado' é o id do registro que deve aparecer, ou o tipo
# de resultado esperado ('sem_resposta', 'ambigua', 'vazia', ...).
# ---------------------------------------------------------------------------
RODADA_1 = [
    # id, categoria, entrada, esperado
    ("T01", "direta", "Como tiro a segunda via do título de eleitor?", "DP-08"),
    ("T02", "direta", "Quanto tempo tenho para pedir o seguro-desemprego?", "TB-02"),
    ("T03", "direta", "Como renovar a CNH?", "VH-02"),
    ("T04", "direta", "Meu RG antigo ainda vale?", "DP-02"),
    ("T05", "direta", "Como consulto o saldo do FGTS?", "TB-04"),
    ("T06", "direta", "Qual o prazo para transferir um carro que comprei?", "VH-04"),
    ("T07", "reformulacao", "perdi meu título eleitoral, o que eu faço", "DP-08"),
    ("T08", "reformulacao", "fui demitido sem justa causa, até quando posso pedir o benefício?", "TB-02"),
    ("T09", "reformulacao", "minha habilitação está vencendo", "VH-02"),
    ("T10", "reformulacao", "quero saber quanto tenho de fundo de garantia", "TB-04"),
    ("T11", "fora_do_tema", "Como funciona o imposto de renda?", "sem_resposta"),
    ("T12", "fora_do_tema", "Qual a previsão do tempo para amanhã?", "sem_resposta"),
    ("L01", "limite", "", "vazia"),
    ("L02", "limite", "???", "invalida"),
    ("L03", "limite", "segunda via", "ambigua"),
    ("L04", "limite", "quanto custa exatamente a 2ª via do RG em SP?", "DP-05"),
    ("L06", "limite", "meu cpf é 123.456.789-09, como regularizar?", "dado_pessoal"),
]

# Conjunto adicional, escrito depois do primeiro sistema pronto, para medir
# se as melhorias servem para perguntas novas (e não só para as de rodada 1).
RODADA_2 = [
    ("H01", "direta", "quero tirar minha primeira habilitação", "VH-01"),
    ("H02", "direta", "como vejo se meu CPF está regular", "DP-07"),
    ("H03", "direta", "como pegar a carteira de trabalho no celular", "TB-01"),
    ("H04", "direta", "o que é o cadastro único", "TB-05"),
    ("H05", "direta", "meu carro precisa de licenciamento todo ano?", "VH-03"),
    ("H06", "direta", "recebi uma multa de trânsito, posso pagar com desconto?", "VH-05"),
    ("H07", "reformulacao", "como faço para sacar meu fundo de garantia", "TB-04"),
    ("H08", "reformulacao", "por quanto tempo vale a nova identidade", "DP-04"),
    ("H09", "reformulacao", "onde me inscrevo no bolsa família", "TB-05"),
    ("H10", "reformulacao", "meu RG vai deixar de valer?", "DP-02"),
    ("H11", "fora_do_tema", "quanto custa um iphone novo", "sem_resposta"),
    ("H12", "fora_do_tema", "como abrir uma empresa", "sem_resposta"),
]


# Rodada 3: escrita ANTES das melhorias da busca, para medir de forma menos
# enviesada se as melhorias funcionam em perguntas que não foram usadas para ajustar.
RODADA_3 = [
    ("R01", "direta", "quanto custa tirar a identidade de novo", "DP-05"),
    ("R02", "reformulacao", "esqueci onde guardei meu título de eleitor", "DP-08"),
    ("R03", "direta", "como faço o agendamento no INSS?", "TB-03"),
    ("R04", "direta", "quando termina o prazo do abono do PIS", "TB-06"),
    ("R05", "reformulacao", "preciso vender meu carro, o que devo fazer", "VH-04"),
    ("R06", "direta", "como baixar a CNH digital no celular", "VH-06"),
    ("R07", "reformulacao", "tirar carteira de motorista pela primeira vez", "VH-01"),
    ("R08", "reformulacao", "o que fazer se meu CPF estiver irregular", "DP-07"),
    ("R09", "direta", "emitir a identidade nova pelo poupatempo", "DP-03"),
    ("R10", "reformulacao", "como funciona o seguro desemprego para quem foi demitido", "TB-02"),
    ("R11", "fora_do_tema", "como emitir passaporte", "sem_resposta"),
    ("R12", "fora_do_tema", "qual a melhor receita de bolo", "sem_resposta"),
]


def executar_consulta(base, entrada, modelo="B"):
    """Consulta + formatação, como o programa faz. Devolve (resultado, texto)."""
    resultado = busca.consultar(entrada, base)
    tipo = resultado["tipo"]
    if tipo in respostas.MENSAGENS:
        texto = respostas.MENSAGENS[tipo]
    elif tipo == "sem_resposta":
        texto = respostas.formatar_sem_resposta(base, resultado["ids"])
    elif tipo == "ambigua":
        texto = respostas.formatar_ambigua(base, resultado["ids"])
    else:
        texto = respostas.formatar_resposta(base["registros"][resultado["ids"][0]], modelo)
    return resultado, texto


def medir_tempo_ms(base, entrada):
    """Tempo médio (em milissegundos) de uma consulta completa."""
    inicio = time.perf_counter()
    for _ in range(REPETICOES):
        executar_consulta(base, entrada)
    return (time.perf_counter() - inicio) / REPETICOES * 1000


def avaliar(base, caso):
    """Roda um caso e devolve um dicionário com o resultado."""
    cid, categoria, entrada, esperado = caso
    resultado, texto = executar_consulta(base, entrada)
    tipo, ids = resultado["tipo"], resultado["ids"]
    esperado_ids = {"L03": {"DP-05", "DP-06", "DP-08"}}.get(cid)

    if esperado in base["registros"]:
        obtido = ids[0] if tipo == "resposta" else tipo
        reg = base["registros"][esperado]
        acerto = (tipo == "resposta" and ids[0] == esperado
                  and "http" in texto
                  and (not reg.get("aviso") or reg["aviso"] in texto))
    elif esperado == "ambigua":
        obtido = f"{tipo}: {', '.join(ids)}"
        acerto = tipo == "ambigua" and esperado_ids is not None and esperado_ids <= set(ids)
    elif esperado == "dado_pessoal":
        obtido = tipo
        acerto = tipo == "dado_pessoal" and "123" not in texto and "456" not in texto
    elif esperado == "sem_resposta":
        obtido = tipo
        acerto = tipo == "sem_resposta" and "Não encontrei" in texto and "oficial" in texto.lower() or \
            (tipo == "sem_resposta" and "Não vou inventar" in texto)
    else:  # vazia, invalida
        obtido = tipo
        acerto = tipo == esperado and len(texto) > 0
    return {"id": cid, "categoria": categoria, "entrada": entrada, "esperado": esperado,
            "obtido": obtido, "acerto": "sim" if acerto else "NÃO",
            "tempo_ms": round(medir_tempo_ms(base, entrada), 4)}


def teste_menu_inexistente():
    """L05: opções inexistentes no menu devem gerar mensagem e pedir de novo."""
    entradas = iter(["9", "abc", "", "2"])
    original = sistema.ler
    sistema.ler = lambda prompt: next(entradas)
    saida = io.StringIO()
    inicio = time.perf_counter()
    try:
        with contextlib.redirect_stdout(saida):
            escolhido = sistema.escolher_numero("Escolha: ", 3)
    finally:
        sistema.ler = original
    tempo = (time.perf_counter() - inicio) * 1000
    ok = escolhido == 2 and saida.getvalue().count("Opção inválida") == 3
    return {"id": "L05", "categoria": "limite", "entrada": "9 / abc / (vazio) / 2",
            "esperado": "3 mensagens de erro e depois aceitar 2",
            "obtido": f"escolhido={escolhido}, mensagens={saida.getvalue().count('Opção inválida')}",
            "acerto": "sim" if ok else "NÃO", "tempo_ms": round(tempo, 4)}


def caminho_mais_curto(grafo, origem, destino):
    """Busca em largura (BFS) no grafo de assuntos relacionados."""
    fila = deque([[origem]])
    visitados = {origem}
    while fila:
        caminho = fila.popleft()
        if caminho[-1] == destino:
            return caminho
        for vizinho in sorted(grafo[caminho[-1]]):
            if vizinho not in visitados:
                visitados.add(vizinho)
                fila.append(caminho + [vizinho])
    return None


def teste_navegacao(base):
    """T13: de DP-01 chega-se a DP-05 usando só as opções de continuidade."""
    inicio = time.perf_counter()
    caminho = caminho_mais_curto(base["grafo"], "DP-01", "DP-05")
    tempo = (time.perf_counter() - inicio) * 1000
    minimo_vizinhos = min(len(v) for v in base["grafo"].values())
    ok = caminho is not None and len(caminho) <= 4 and len(base["grafo"]["DP-01"]) >= 3
    return {"id": "T13", "categoria": "navegacao", "entrada": "DP-01 -> DP-05 pelas opções de continuidade",
            "esperado": "caminho com até 3 passos; DP-01 com 3 ou mais opções",
            "obtido": (" -> ".join(caminho) if caminho else "sem caminho") +
                      f" (menor número de opções em um registro: {minimo_vizinhos})",
            "acerto": "sim" if ok else "NÃO", "tempo_ms": round(tempo, 4)}


def taxa(resultados):
    if not resultados:
        return 0.0
    return 100.0 * sum(1 for r in resultados if r["acerto"] == "sim") / len(resultados)


def comparar_modelos(base, casos):
    """Aplica A e B nas perguntas de teste que têm registro esperado."""
    linhas = []
    for modelo in ("A", "B"):
        total = completos = 0
        soma_criterios = 0
        maior_bloco = []
        for cid, _, entrada, esperado in casos:
            if esperado not in base["registros"]:
                continue
            resultado, texto = executar_consulta(base, entrada, modelo)
            if resultado["tipo"] != "resposta":
                continue
            reg = base["registros"][resultado["ids"][0]]
            criterios = [
                "http" in texto,                                              # fonte exibida
                (not reg.get("aviso")) or reg["aviso"] in texto,              # aviso quando existe
                respostas.data_br(reg["data_verificacao"]) in texto,          # data de verificação
                "NÃO é um canal oficial" in texto,                            # declara não ser oficial
                any(l.lstrip().startswith("•") for l in texto.splitlines()),  # tópicos curtos
            ]
            total += 1
            soma_criterios += sum(criterios)
            completos += all(criterios)
            blocos = [len([p for p in l.split() if "http" not in p]) for l in texto.splitlines() if l.strip()]
            maior_bloco.append(max(blocos))
        linhas.append({"modelo": modelo, "respostas": total,
                       "criterios_medios": round(soma_criterios / total, 2) if total else 0,
                       "respostas_completas": f"{completos}/{total}",
                       "maior_bloco_medio_palavras": round(sum(maior_bloco) / len(maior_bloco), 1) if maior_bloco else 0})
    return linhas


def resumo(resultados):
    """(acertos, total, taxa %, tempo médio em ms)."""
    acertos = sum(1 for r in resultados if r["acerto"] == "sim")
    tempo = sum(r["tempo_ms"] for r in resultados) / len(resultados)
    return acertos, len(resultados), taxa(resultados), tempo


def salvar_csv(caminho, todos):
    with open(caminho, "w", newline="", encoding="utf-8") as arq:
        campos = ["rodada", "id", "categoria", "entrada", "esperado", "obtido", "acerto", "tempo_ms"]
        escritor = csv.DictWriter(arq, fieldnames=campos)
        escritor.writeheader()
        for rodada, r in todos:
            escritor.writerow({"rodada": rodada, **r})


def ler_csv(caminho):
    if not os.path.exists(caminho):
        return None
    with open(caminho, encoding="utf-8") as arq:
        return list(csv.DictReader(arq))


def resumo_csv(linhas, rodada):
    itens = [l for l in linhas if l["rodada"] == rodada]
    acertos = sum(1 for l in itens if l["acerto"] == "sim")
    return acertos, len(itens), 100.0 * acertos / len(itens)


def gerar_relatorio(todos, comparacao, antes):
    """Escreve docs/resultados_testes.md com tabelas de resultados e indicadores."""
    L = ["# Resultados dos testes", "",
         "Gerado automaticamente por `python src/testes.py`. Não edite à mão: rode o script de novo.", "",
         "## Como os testes são avaliados", "",
         "- **Pergunta normal:** acerto = o registro esperado vem em primeiro lugar, a fonte (link) aparece "
         "e, se o registro tem aviso, o aviso aparece.",
         "- **Fora do tema:** acerto = o assistente informa que não há base suficiente e não inventa orientação.",
         "- **Limites:** acerto = mensagem compreensível, sem erro do programa e sem repetir dados pessoais.",
         f"- **Tempo:** média de {REPETICOES} execuções de cada consulta completa (busca + formatação), em ms.",
         "", "## Indicadores por rodada", ""]
    L.append("| Rodada | Testes | Acertos | Taxa de acerto | Tempo médio (ms) |")
    L.append("|---|---|---|---|---|")
    for rodada in ("rodada 1", "rodada 2", "rodada 3"):
        itens = [r for rd, r in todos if rd == rodada]
        a, t, tx, tm = resumo(itens)
        L.append(f"| {rodada} | {t} | {a} | {tx:.1f}% | {tm:.3f} |")
    todos_res = [r for _, r in todos]
    a, t, tx, tm = resumo(todos_res)
    L.append(f"| **Total** | {t} | {a} | **{tx:.1f}%** | {tm:.3f} |")

    if antes:
        L += ["", "## Antes e depois das melhorias", "",
              "| Rodada | Taxa antes | Taxa depois |", "|---|---|---|"]
        for rodada in ("rodada 1", "rodada 2", "rodada 3"):
            ant = resumo_csv(antes, rodada)
            itens = [r for rd, r in todos if rd == rodada]
            a2, t2, tx2, _ = resumo(itens)
            L.append(f"| {rodada} | {ant[0]}/{ant[1]} = {ant[2]:.1f}% | {a2}/{t2} = {tx2:.1f}% |")

    L += ["", "## Taxa de acerto por tipo de pergunta (resultado final)", "",
          "| Tipo | Acertos | Taxa |", "|---|---|---|"]
    categorias = {}
    for r in todos_res:
        categorias.setdefault(r["categoria"], []).append(r)
    for cat, itens in categorias.items():
        L.append(f"| {cat} | {sum(1 for r in itens if r['acerto'] == 'sim')}/{len(itens)} | {taxa(itens):.1f}% |")

    L += ["", "## Registro completo dos testes", "",
          "| Rodada | ID | Tipo | Entrada | Esperado | Obtido | Acerto | Tempo (ms) |",
          "|---|---|---|---|---|---|---|---|"]
    for rodada, r in todos:
        entrada = r["entrada"] if r["entrada"] else "(vazia)"
        L.append(f"| {rodada[-1]} | {r['id']} | {r['categoria']} | {entrada} | {r['esperado']} | "
                 f"{r['obtido']} | {r['acerto']} | {r['tempo_ms']} |")

    L += ["", "## Comparação dos modelos de resposta A e B", "",
          "Mesmas perguntas, dois formatos. Critérios (cada um vale 1 ponto): fonte exibida, aviso exibido "
          "quando existe, data de verificação, declaração de que não é canal oficial, orientação em tópicos curtos.",
          "", "| Modelo | Respostas avaliadas | Critérios atendidos (média de 5) | Respostas completas | "
          "Maior bloco de texto (palavras, média) |", "|---|---|---|---|---|"]
    for c in comparacao:
        L.append(f"| {c['modelo']} | {c['respostas']} | {c['criterios_medios']} | "
                 f"{c['respostas_completas']} | {c['maior_bloco_medio_palavras']} |")
    caminho = os.path.join(RAIZ, "docs", "resultados_testes.md")
    with open(caminho, "w", encoding="utf-8") as arq:
        arq.write("\n".join(L) + "\n")


def main():
    base = base_mod.carregar_base()
    rodada1 = [avaliar(base, c) for c in RODADA_1]
    rodada1.append(teste_menu_inexistente())
    rodada1.append(teste_navegacao(base))
    rodada2 = [avaliar(base, c) for c in RODADA_2]
    rodada3 = [avaliar(base, c) for c in RODADA_3]
    todos = ([("rodada 1", r) for r in rodada1] + [("rodada 2", r) for r in rodada2]
             + [("rodada 3", r) for r in rodada3])

    pasta_dados = os.path.join(RAIZ, "data")
    if "--antes" in sys.argv:
        salvar_csv(os.path.join(pasta_dados, "resultados_testes_antes.csv"), todos)
        print("Resultados 'antes das melhorias' salvos em data/resultados_testes_antes.csv")
    else:
        salvar_csv(os.path.join(pasta_dados, "resultados_testes.csv"), todos)
        comparacao = comparar_modelos(base, RODADA_1 + RODADA_2 + RODADA_3)
        antes = ler_csv(os.path.join(pasta_dados, "resultados_testes_antes.csv"))
        gerar_relatorio(todos, comparacao, antes)
        print("Relatório gerado em docs/resultados_testes.md")

    for nome, res in (("Rodada 1", rodada1), ("Rodada 2", rodada2), ("Rodada 3", rodada3)):
        a, t, tx, tm = resumo(res)
        print(f"{nome}: {a}/{t} acertos = {tx:.1f}% | tempo médio {tm:.3f} ms")
    print()
    for rodada, r in todos:
        if r["acerto"] != "sim":
            print(f"[ERRO] {r['id']} {r['categoria']:<13} esperado={r['esperado']} obtido={r['obtido']}  <- {r['entrada']}")
    print()
    for linha in comparar_modelos(base, RODADA_1 + RODADA_2 + RODADA_3):
        print("modelo", linha)


if __name__ == "__main__":
    main()
