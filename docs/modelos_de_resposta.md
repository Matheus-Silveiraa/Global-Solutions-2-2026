# Modelos de resposta (instruções e formatação)

O assistente não usa um modelo de IA externo. Os "modelos de prompt" são **instruções de formato e de regras** que o programa aplica a cada resposta (arquivo `src/respostas.py`, dicionário `MODELOS`). Dá para trocar de modelo no menu (opção 4).

## Modelo A - parágrafo curto

- **Papel:** assistente informativo de orientação cidadã, sem vínculo com órgãos públicos.
- **Formato:** orientação, aviso (quando houver) e fonte em um único parágrafo.
- **Obrigações:** citar a fonte; não responder sem registro correspondente na base.

Exemplo (VH-04):

> Na transferência de propriedade, o comprador deve providenciar a emissão do novo registro do veículo dentro do prazo legal de 30 dias, contado da assinatura do documento de transferência aplicável. Antes de concluir o processo, verifique débitos e restrições [...] Atenção: O fluxo e a documentação dependem do tipo de documento do veículo e do caso. [...] Fonte: Planalto, Código de Trânsito Brasileiro, Lei nº 9.503/1997, art. 123 e art. 134 (https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm).

## Modelo B - resposta estruturada (padrão)

- **Papel:** o mesmo, com declaração explícita de que não é canal oficial de nenhum órgão público.
- **Formato:** título do assunto, orientação em tópicos curtos, aviso destacado, fontes com link e data de verificação.
- **Obrigações:** citar sempre a fonte e a data de verificação; avisar quando a informação exigir confirmação; informar o limite quando não houver base suficiente; não inventar instruções nem pedir dados pessoais.

Exemplo (VH-04):

```
============================================================
COMPREI OU VENDI UM CARRO, O QUE FAZER?
============================================================
O que fazer:
  • Na transferência de propriedade, o comprador deve providenciar a emissão do novo
    registro [...] dentro do prazo legal de 30 dias [...]
  • Antes de concluir o processo, verifique débitos e restrições [...]
  • O vendedor deve formalizar a comunicação de venda pelos canais do Detran.

ATENÇÃO: O fluxo e a documentação dependem do tipo de documento do veículo e do caso. [...]

Fontes consultadas:
  - Planalto — Código de Trânsito Brasileiro - Lei nº 9.503/1997, art. 123 e art. 134
    https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm
Informação conferida em: 04/11/2026
```

## Comparação nas perguntas de teste

As mesmas 28 perguntas que têm um registro esperado (rodadas 1, 2 e 3) foram respondidas pelos dois modelos. Cada resposta recebe 1 ponto por critério: fonte exibida, aviso exibido quando existe, data de verificação, declaração de que não é canal oficial e orientação em tópicos curtos.

| Modelo | Critérios atendidos (média de 5) | Respostas completas | Maior bloco de texto (palavras, média) |
|---|---|---|---|
| A | 2,0 | 0 de 28 | 92,8 |
| B | 5,0 | 28 de 28 | 30,3 |

**Qual oferece respostas mais claras e consistentes: o modelo B.**

- **Consistência:** o B tem sempre as mesmas seções, na mesma ordem (o que fazer, atenção, fontes, data), então a pessoa sabe onde procurar cada coisa. O A mistura tudo em um bloco.
- **Clareza:** o maior bloco de texto contínuo do A tem em média 93 palavras, contra 30 do B, o que torna a leitura mais fácil.
- **Transparência:** só o B mostra a data da verificação e declara que não é canal oficial, o que é exigido pelo enunciado.

**Limitação desta comparação:** os critérios refletem os requisitos do trabalho, e o B foi desenhado para cumpri-los, então a vantagem é em parte por construção. A clareza percebida por pessoas reais não foi medida; o teste de usabilidade pode incluir a pergunta "qual formato você achou mais fácil de entender?" para completar a comparação.
