"""Busca de orientações na base de conhecimento.

Estratégia (explicada também no README):
1. A pergunta é normalizada: minúsculas, sem acentos, sem pontuação, sem
   palavras muito comuns (como "de", "para", "como").
2. Cada registro recebe uma pontuação:
   - cada palavra-chave do registro que aparece na pergunta soma 2 pontos
     por palavra (uma expressão de 2 palavras vale 4);
   - cada palavra da pergunta cadastrada do registro que aparece na
     pergunta do usuário soma 1 ponto, e cada palavra do subtema
     (o assunto, como "FGTS" ou "Licenciamento") soma 2 pontos.
3. O resultado depende das pontuações (ver consultar()):
   - pontuação máxima abaixo do limiar -> sem resposta confiável;
   - dois ou mais registros muito próximos -> consulta ambígua (o
     usuário escolhe);
   - caso contrário -> responde com o registro de maior pontuação.
"""
import re
import unicodedata

LIMIAR = 4            # pontuação mínima para considerar que existe resposta
MARGEM = 2            # registros até 2 pontos abaixo do melhor entram como empate
MAX_OPCOES = 3        # quantas opções mostrar em caso de ambiguidade
MAX_CARACTERES = 200  # tamanho máximo aceito para uma pergunta
SUGESTAO_MINIMA = 3   # pontuação mínima para sugerir um assunto parecido

# Palavras muito comuns que não ajudam a achar o assunto (já normalizadas).
STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas", "ao", "aos", "para", "pra", "por", "com", "e", "ou",
    "que", "se", "eu", "me", "meu", "minha", "meus", "minhas", "como", "qual", "quais",
    "quando", "onde", "quanto", "quanta", "quem", "posso", "preciso", "quero", "saber",
    "fazer", "faco", "fui", "foi", "ser", "ter", "tem", "tenho", "sobre", "isso", "essa",
    "esse", "ate", "ja", "gostaria", "favor", "pode", "poderia", "tipo", "muito", "mais",
}

# Pequena tabela de equivalências para jeitos comuns de escrever.
SINONIMOS = {"2a": "segunda", "2o": "segundo", "1a": "primeira", "1o": "primeiro",
             "habilitacao": "cnh"}

# Terminações removidas para comparar palavras da mesma família
# (renovar, renovação, renovo -> "renov").
SUFIXOS = sorted(["acoes", "acao", "oes", "mente", "ando", "endo", "indo", "ados", "adas",
                  "idos", "idas", "ado", "ada", "ido", "ida", "ar", "er", "ir", "os", "as",
                  "es", "a", "e", "o", "s"], key=len, reverse=True)


def normalizar(texto):
    """Minúsculas, sem acentos, só letras e números, devolvendo a lista de palavras."""
    texto = unicodedata.normalize("NFKD", texto.lower())
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"[^a-z0-9]+", " ", texto)
    return texto.split()


def preparar(texto):
    """Normaliza, troca sinônimos e tira palavras comuns."""
    palavras = [SINONIMOS.get(p, p) for p in normalizar(texto)]
    return [p for p in palavras if p not in STOPWORDS]


def radical(palavra):
    """Remove uma terminação comum, mantendo pelo menos 3 letras."""
    for sufixo in SUFIXOS:
        if palavra.endswith(sufixo) and len(palavra) - len(sufixo) >= 3:
            return palavra[:-len(sufixo)]
    return palavra


def parecido(a, b):
    """True se as palavras são iguais, da mesma família ou começam igual (6 letras)."""
    if a == b:
        return True
    if a.isdigit() or b.isdigit():
        return False  # números só valem se forem exatamente iguais
    if radical(a) == radical(b):
        return True
    return len(a) >= 6 and len(b) >= 6 and a[:6] == b[:6]


def contem_dado_pessoal(texto):
    """Detecta sequências longas de números (CPF, RG, CNH...) ou e-mails."""
    if "@" in texto:
        return True
    for trecho in re.findall(r"\d[\d.\-/ ]*\d", texto):
        if len(re.sub(r"\D", "", trecho)) >= 7:
            return True
    return False


def construir_indice(base):
    """Prepara as palavras de cada registro uma única vez (usa lista de dicionários)."""
    indice = []
    for reg_id in sorted(base["registros"]):
        reg = base["registros"][reg_id]
        frases = []
        for frase in reg["palavras_chave"]:
            tokens = preparar(frase)
            if tokens:
                frases.append((frase, tokens))
        texto = set(preparar(reg["pergunta"]))
        subtema = set(preparar(reg["subtema"]))
        indice.append({"id": reg_id, "frases": frases, "texto": texto, "subtema": subtema})
    return indice


def pontuar(tokens_pergunta, entrada):
    """Devolve (pontuação, palavras-chave que casaram) de um registro."""
    pontos = 0
    acertos = []
    for frase, tokens in entrada["frases"]:
        if all(any(parecido(t, q) for q in tokens_pergunta) for t in tokens):
            pontos += 2 * len(tokens)
            acertos.append(frase)
    for t in entrada["texto"]:          # palavras da pergunta cadastrada: 1 ponto
        if any(parecido(t, q) for q in tokens_pergunta):
            pontos += 1
    for t in entrada["subtema"]:        # palavras do subtema (assunto): 2 pontos
        if any(parecido(t, q) for q in tokens_pergunta):
            pontos += 2
    return pontos, acertos


def consultar(texto, base):
    """Classifica uma consulta e devolve um dicionário com o resultado.

    tipo pode ser: 'vazia', 'dado_pessoal', 'longa', 'invalida', 'sem_resposta',
    'ambigua' ou 'resposta'. 'ids' traz os registros relacionados ao tipo
    e 'pontuacoes' o ranking completo (útil para os testes).
    """
    if not isinstance(texto, str) or not texto.strip():
        return {"tipo": "vazia", "ids": [], "pontuacoes": []}
    texto = texto.strip()
    if contem_dado_pessoal(texto):
        return {"tipo": "dado_pessoal", "ids": [], "pontuacoes": []}
    if len(texto) > MAX_CARACTERES:
        return {"tipo": "longa", "ids": [], "pontuacoes": []}
    tokens = preparar(texto)
    if not tokens:
        return {"tipo": "invalida", "ids": [], "pontuacoes": []}

    if "indice" not in base:
        base["indice"] = construir_indice(base)

    ranking = []
    for entrada in base["indice"]:
        pontos, acertos = pontuar(tokens, entrada)
        ranking.append((pontos, entrada["id"], acertos))
    ranking.sort(key=lambda item: (-item[0], item[1]))  # maior pontuação; empate por id
    pontuacoes = [(r[1], r[0]) for r in ranking if r[0] > 0]

    melhor = ranking[0][0]
    if melhor < LIMIAR:
        sugestoes = [r[1] for r in ranking if r[0] >= SUGESTAO_MINIMA][:2]
        return {"tipo": "sem_resposta", "ids": sugestoes, "pontuacoes": pontuacoes}

    candidatos = [r for r in ranking if r[0] >= LIMIAR and r[0] >= melhor - MARGEM]
    if len(candidatos) > 1:
        return {"tipo": "ambigua", "ids": [r[1] for r in candidatos[:MAX_OPCOES]],
                "pontuacoes": pontuacoes}
    return {"tipo": "resposta", "ids": [ranking[0][1]], "pontuacoes": pontuacoes,
            "acertos": ranking[0][2]}
