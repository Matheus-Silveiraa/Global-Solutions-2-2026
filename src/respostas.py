"""Montagem das respostas apresentadas ao usuário.

Dois modelos de resposta (estratégias introdutórias de instrução):

MODELO A - parágrafo curto
    papel: assistente informativo de orientação cidadã (não oficial)
    formato: orientação + aviso (se houver) + fonte, tudo em texto corrido
    obrigações: citar a fonte; nunca responder sem registro correspondente

MODELO B - resposta estruturada (padrão)
    papel: o mesmo, com declaração explícita de que não é canal oficial
    formato: título, orientação em tópicos curtos, aviso destacado,
             fontes com link, data de verificação
    obrigações: as mesmas do A + informar o limite quando faltar base
                + sempre mostrar a data em que a informação foi conferida

Os textos de papel/formato/obrigações abaixo são a documentação oficial
dos modelos e também são usados nos relatórios de teste.
"""
import re

MODELOS = {
    "A": {
        "nome": "Parágrafo curto",
        "papel": "Assistente informativo de orientação cidadã, sem vínculo com órgãos públicos.",
        "formato": "Orientação, aviso (quando houver) e fonte em um único parágrafo.",
        "obrigacoes": "Citar a fonte; não responder sem registro correspondente na base.",
    },
    "B": {
        "nome": "Resposta estruturada",
        "papel": ("Assistente informativo de orientação cidadã. Declara que não é canal oficial "
                  "de nenhum órgão público."),
        "formato": ("Título do assunto, orientação em tópicos curtos, aviso destacado, "
                    "fontes com link e data de verificação."),
        "obrigacoes": ("Citar sempre a fonte e a data de verificação; avisar quando a informação "
                       "exigir confirmação; informar o limite quando não houver base suficiente; "
                       "não inventar instruções nem pedir dados pessoais."),
    },
}

AVISO_NAO_OFICIAL = ("Este assistente é informativo e NÃO é um canal oficial de órgãos públicos. "
                     "Confirme sempre nas fontes indicadas.")

MENSAGENS = {
    "vazia": "Você não digitou nada. Escreva sua dúvida (por exemplo: \"Como renovar a CNH?\") "
             "ou volte ao menu e escolha um tema.",
    "invalida": "Não consegui entender essa entrada. Tente escrever uma frase com palavras, "
                "como \"Como tirar a segunda via do título de eleitor?\".",
    "dado_pessoal": "Parece que sua mensagem tem um número de documento ou um e-mail. "
                    "Por segurança, não digite dados pessoais aqui. Reescreva a dúvida sem "
                    "esses dados (o assistente não os guarda, mas é melhor não informar).",
    "longa": "Sua pergunta ficou muito longa. Tente resumir em uma frase curta.",
}


def data_br(data_iso):
    """Converte 2026-11-04 em 04/11/2026."""
    partes = str(data_iso).split("-")
    if len(partes) == 3:
        return f"{partes[2]}/{partes[1]}/{partes[0]}"
    return str(data_iso)


def dividir_frases(texto):
    """Divide a orientação em frases (usado para os tópicos do modelo B)."""
    return [f.strip() for f in re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", texto) if f.strip()]


def formatar_resposta(reg, modelo="B"):
    """Apresenta um registro no modelo escolhido ('A' ou 'B')."""
    refs = reg["referencia"]
    aviso = reg.get("aviso", "")
    if modelo == "A":
        partes = [reg["orientacao"]]
        if aviso:
            partes.append("Atenção: " + aviso)
        r = refs[0]
        partes.append(f"Fonte: {r['orgao']}, {r['titulo']} ({r['url']}).")
        return " ".join(partes)

    linhas = ["=" * 60, reg["pergunta"].upper(), "=" * 60,
              "O que fazer:"]
    for frase in dividir_frases(reg["orientacao"]):
        linhas.append("  • " + frase)
    if aviso:
        linhas += ["", "ATENÇÃO: " + aviso]
    linhas += ["", "Fontes consultadas:"]
    for r in refs:
        linhas.append(f"  - {r['orgao']} - {r['titulo']}")
        linhas.append(f"    {r['url']}")
    linhas.append(f"Informação conferida em: {data_br(reg['data_verificacao'])}")
    linhas += ["", AVISO_NAO_OFICIAL]
    return "\n".join(linhas)


def formatar_opcoes(base, ids, titulo):
    """Lista numerada de registros (ambiguidade, sugestões e navegação)."""
    linhas = [titulo]
    for n, reg_id in enumerate(ids, start=1):
        reg = base["registros"][reg_id]
        linhas.append(f"  [{n}] {reg['pergunta']}  ({reg['subtema']})")
    return "\n".join(linhas)


def formatar_ambigua(base, ids):
    return formatar_opcoes(base, ids,
                           "Sua pergunta pode se encaixar em mais de um assunto. Qual deles você quer ver?")


def formatar_sem_resposta(base, ids):
    """Aviso de limitação, sem inventar orientação nem alegar atendimento oficial."""
    linhas = ["Não encontrei informação confiável na minha base para essa pergunta.",
              "Não vou inventar uma orientação: o assistente cobre apenas os temas abaixo."]
    for sigla, nome in base["temas"].items():
        linhas.append(f"  - {nome}")
    linhas.append("Dica: reescreva a pergunta com outras palavras ou escolha um tema pelo menu.")
    linhas.append("Para outros assuntos, consulte diretamente o órgão responsável (por exemplo, gov.br).")
    texto = "\n".join(linhas)
    if ids:
        texto += "\n\n" + formatar_opcoes(base, ids, "Assuntos com palavras parecidas (podem não ser o que você procura):")
    return texto
