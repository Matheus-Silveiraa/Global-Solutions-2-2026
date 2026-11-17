"""Leitura e validação da base de conhecimento do Citizen Assist AI.

A base fica em data/base_conhecimento.json. Este módulo só lê e valida;
as regras de busca e de resposta ficam em outros arquivos, para que seja
possível corrigir ou acrescentar registros sem mexer no código.
"""
import json
import os
import re

CAMINHO_PADRAO = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "..", "data", "base_conhecimento.json")

# Campos que todo registro precisa ter (e não podem estar vazios).
CAMPOS_OBRIGATORIOS = ["id", "tema", "subtema", "pergunta", "palavras_chave",
                       "orientacao", "referencia", "data_verificacao"]


class BaseInvalidaError(Exception):
    """Erro que impede o uso da base (arquivo ausente, vazio ou sem registros válidos)."""


def validar_registro(reg, temas):
    """Devolve a lista de problemas encontrados em um registro (vazia se estiver ok)."""
    problemas = []
    for campo in CAMPOS_OBRIGATORIOS:
        if campo not in reg or reg[campo] in (None, "", [], {}):
            problemas.append(f"campo obrigatório ausente ou vazio: {campo}")
    if problemas:
        return problemas
    if reg["tema"] not in temas:
        problemas.append(f"tema '{reg['tema']}' não existe em 'temas'")
    if not isinstance(reg["palavras_chave"], list):
        problemas.append("palavras_chave deve ser uma lista")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(reg["data_verificacao"])):
        problemas.append("data_verificacao deve ter o formato AAAA-MM-DD")
    if not isinstance(reg["referencia"], list):
        problemas.append("referencia deve ser uma lista")
    else:
        for ref in reg["referencia"]:
            if not isinstance(ref, dict) or not str(ref.get("url", "")).startswith("http"):
                problemas.append("toda referência precisa de uma url que comece com http")
                break
    return problemas


def montar_estruturas(registros):
    """Monta os índices usados pelo programa: por id, árvore de temas e grafo."""
    por_id = {r["id"]: r for r in registros}

    # Árvore: tema -> subtema -> lista de ids (organização hierárquica).
    arvore = {}
    for r in registros:
        arvore.setdefault(r["tema"], {}).setdefault(r["subtema"], []).append(r["id"])

    # Grafo: cada registro lista seus relacionados; a ligação vale nos dois sentidos.
    grafo = {r["id"]: set() for r in registros}
    for r in registros:
        for vizinho in r.get("relacionados", []):
            if vizinho in por_id and vizinho != r["id"]:
                grafo[r["id"]].add(vizinho)
                grafo[vizinho].add(r["id"])
    return por_id, arvore, grafo


def carregar_base(caminho=CAMINHO_PADRAO):
    """Lê o JSON, valida e devolve um dicionário com a base pronta para uso.

    Registros inválidos são descartados e viram avisos. Se o arquivo não
    existir, estiver vazio, não for JSON ou não sobrar nenhum registro
    válido, levanta BaseInvalidaError.
    """
    if not os.path.exists(caminho):
        raise BaseInvalidaError(f"Arquivo da base não encontrado: {caminho}")
    try:
        with open(caminho, encoding="utf-8") as arq:
            conteudo = arq.read()
    except OSError as erro:
        raise BaseInvalidaError(f"Não foi possível ler a base: {erro}")
    if not conteudo.strip():
        raise BaseInvalidaError("O arquivo da base está vazio.")
    try:
        dados = json.loads(conteudo)
    except json.JSONDecodeError as erro:
        raise BaseInvalidaError(f"O arquivo da base não é um JSON válido: {erro}")

    if (not isinstance(dados, dict) or not isinstance(dados.get("registros"), list)
            or not isinstance(dados.get("temas"), dict)):
        raise BaseInvalidaError("A base precisa ter os campos 'temas' (dicionário) e 'registros' (lista).")

    temas = dados["temas"]
    avisos = []
    validos = []
    ids_vistos = set()
    for reg in dados["registros"]:
        if not isinstance(reg, dict):
            avisos.append("um item de 'registros' não é um objeto e foi ignorado")
            continue
        problemas = validar_registro(reg, temas)
        if not problemas and reg["id"] in ids_vistos:
            problemas.append("id repetido")
        if problemas:
            avisos.append(f"registro {reg.get('id', '(sem id)')} ignorado: " + "; ".join(problemas))
            continue
        ids_vistos.add(reg["id"])
        validos.append(reg)

    if not validos:
        raise BaseInvalidaError("Nenhum registro válido foi encontrado na base.")

    por_id, arvore, grafo = montar_estruturas(validos)
    for r in validos:
        for viz in r.get("relacionados", []):
            if viz not in por_id:
                avisos.append(f"registro {r['id']}: relacionado '{viz}' não existe e foi ignorado")

    meta = {k: dados.get(k) for k in ("projeto", "versao_base", "data_revisao", "observacao")}
    return {"meta": meta, "temas": temas, "registros": por_id,
            "arvore": arvore, "grafo": grafo, "avisos": avisos}
