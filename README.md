# Citizen Assist AI - assistente de orientação cidadã

## Identificação

Projeto individual (Global Solution 2026.2 - desafio CitizenTech).

- **Aluno:** Matheus Silveira
- **RM:** 570447
- **GitHub:** [Matheus-Silveiraa](https://github.com/Matheus-Silveiraa)
- **Repositório:** [Global-Solutions-2-2026](https://github.com/Matheus-Silveiraa/Global-Solutions-2-2026)

## 👩‍🏫 Coordenação

- <a href="https://www.linkedin.com/in/andregodoichiovato/">André Godoi Chiovato</a>

## 📜 Descrição

### Problema, público e temas

Muitas pessoas encontram informações dispersas, termos difíceis ou instruções incompletas quando precisam resolver questões do dia a dia, como tirar uma segunda via de documento ou pedir um benefício. O Citizen Assist AI é um assistente de texto, feito em Python, que organiza orientações **verificadas em fontes oficiais**, responde dúvidas simples, mostra **a fonte e a data em que a informação foi conferida** e avisa quando não tem base suficiente para orientar.

- **Público beneficiado:** cidadãos que buscam orientação básica, com linguagem simples, sobre documentos, trabalho e veículos.
- **Temas (3) e assuntos (22 orientações):**
  - **Documentos pessoais (DP):** CIN/RG, CPF, título de eleitor.
  - **Trabalho e benefícios (TB):** Carteira de Trabalho Digital, seguro-desemprego, INSS, FGTS, CadÚnico, PIS/Pasep.
  - **Veículo e habilitação (VH):** primeira habilitação, renovação da CNH, licenciamento, transferência de veículo, multas, CNH digital.

O assistente **não é um canal oficial** de nenhum órgão público e não promete integração com eles.

### Organização da base de conhecimento

A base fica em `data/base_conhecimento.json`. Cada registro tem:

| Campo | Obrigatório | Para que serve |
|---|---|---|
| `id` | sim | Identificador único (ex.: `DP-08`; o prefixo é o tema) |
| `tema` | sim | Sigla do tema (`DP`, `TB` ou `VH`), definida em `temas` |
| `subtema` | sim | Assunto dentro do tema (ex.: "Título de eleitor") |
| `pergunta` | sim | Pergunta principal que o registro responde |
| `palavras_chave` | sim | Lista de termos usados na busca (inclui sinônimos) |
| `orientacao` | sim | Resposta resumida e em linguagem simples |
| `referencia` | sim | Lista de fontes (órgão, título e URL) |
| `data_verificacao` | sim | Data em que a informação foi conferida (AAAA-MM-DD) |
| `aviso` | não | Alerta mostrado quando a informação exige confirmação |
| `relacionados` | não | Ids de assuntos ligados, usados na navegação |

A origem de cada orientação são páginas oficiais (gov.br, TSE, Receita Federal, Ministério do Trabalho, Caixa, Detran-SP, Planalto etc.), conferidas pelo autor em 04/11/2026, com atualização da referência VH-04 em 17/11/2026. Detalhes em [`docs/base_de_conhecimento.md`](docs/base_de_conhecimento.md).

**Estruturas de dados usadas** (arquivo `src/base.py`):

- **Lista de dicionários** para os registros lidos do JSON.
- **Dicionário por id** (`registros`) para recuperar um registro direto pelo identificador.
- **Árvore (hierarquia)** `tema -> subtema -> lista de ids` (`arvore`), usada no menu de temas.
- **Grafo simples** (`grafo`): cada registro aponta para os relacionados, e a ligação vale nos dois sentidos. Usado na navegação entre assuntos ("Assuntos relacionados para continuar"). O teste T13 usa busca em largura (BFS) para provar que dá para chegar de um assunto a outro só pelas opções oferecidas.

**Manutenção da base:** para corrigir ou acrescentar uma orientação basta editar o JSON, sem mexer no código. O programa valida os registros ao carregar: arquivo ausente, vazio, JSON quebrado ou sem registros válidos impedem o início com uma mensagem clara; registros com campos faltando, tema inexistente, data inválida ou id repetido são ignorados com aviso na tela.

### Estratégia de busca (arquivo `src/busca.py`)

1. A pergunta é normalizada (minúsculas, sem acentos e sem pontuação) e as palavras muito comuns são removidas ("de", "para", "como"...). Pequenas equivalências são aplicadas (ex.: "2ª" vira "segunda", "habilitação" vira "cnh").
2. Cada registro recebe uma **pontuação**: 2 pontos por palavra de cada palavra-chave encontrada (uma expressão de duas palavras vale 4), 1 ponto por palavra da pergunta cadastrada e 2 pontos por palavra do subtema. Palavras da mesma família (renovar, renovação, renovo) são consideradas iguais por um comparador simples de radicais.
3. **Várias correspondências:**
   - se a melhor pontuação for menor que **4**, não há resposta confiável e o assistente avisa isso;
   - se dois ou mais registros ficarem a até **2 pontos** do melhor, a consulta é **ambígua** e o usuário escolhe entre até 3 opções;
   - caso contrário, mostra o registro de maior pontuação (em empate exato, vale a ordem do id).

### Regras de resposta e modelos de instrução (arquivo `src/respostas.py`)

Foram documentados dois modelos de resposta, comparados em [`docs/modelos_de_resposta.md`](docs/modelos_de_resposta.md):

- **Modelo A (parágrafo curto):** orientação, aviso e fonte em um único parágrafo.
- **Modelo B (resposta estruturada, padrão):** título, tópicos curtos, aviso destacado, fontes com link, data de verificação e declaração de que o assistente não é oficial.

Regras comuns: toda resposta cita a fonte; o aviso do registro sempre aparece; sem registro correspondente, o assistente informa o limite e **não inventa instruções nem alega atendimento oficial**; nenhum dado pessoal é pedido.

## ▶️ Como executar

Requer Python 3.8 ou superior (testado com Python 3.12). Não há dependências externas.

```
python src/sistema.py
```

Para rodar os testes automáticos e gerar os indicadores:

```
python src/testes.py
```

Para executar a mesma suíte com um painel visual no terminal (ideal para a demonstração em vídeo):

```
python src/auditoria.py
```

O painel reaproveita `src/testes.py`, atualiza os arquivos CSV e Markdown e apresenta o resultado por categoria, incluindo as consultas que ainda precisam de atenção.

## 💬 Exemplos de uso

**Pergunta direta (modelo B):** `Qual o prazo para transferir um carro que comprei?`

```
============================================================
COMPREI OU VENDI UM CARRO, O QUE FAZER?
============================================================
O que fazer:
  • Na transferência de propriedade, o comprador deve providenciar a emissão do novo registro
    do veículo dentro do prazo legal de 30 dias [...]
ATENÇÃO: O fluxo e a documentação dependem do tipo de documento do veículo e do caso. [...]
Fontes consultadas:
  - Planalto — Código de Trânsito Brasileiro - Lei nº 9.503/1997, art. 123 e art. 134
    https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm
Informação conferida em: 17/11/2026
```

**Consulta ambígua:** `segunda via`

```
Sua pergunta pode se encaixar em mais de um assunto. Qual deles você quer ver?
  [1] Quanto custa a 2ª via?  (RG/CIN)
  [2] Perdi meu título, como tiro a 2ª via?  (Título de eleitor)
  [3] Como emito o comprovante do CPF?  (CPF)
```

**Pergunta sem base:** `Como funciona o imposto de renda?` → "Não encontrei informação confiável na minha base para essa pergunta. Não vou inventar uma orientação..." e a lista dos temas cobertos.

**Entradas inválidas:**

| Entrada | Comportamento |
|---|---|
| Vazia | Pede que a pessoa escreva a dúvida ou volte ao menu |
| `???` | Informa que não entendeu e dá um exemplo de pergunta |
| Opção de menu inexistente | Informa o erro e pede de novo |
| Número de documento ou e-mail | Pede para reescrever sem dados pessoais e não repete o dado |
| Base ausente, vazia ou sem registros válidos | O programa não inicia e explica o motivo |

## 🧪 Plano de testes, indicadores e interpretação

Os testes automáticos (`src/testes.py`) executam **43 casos** em três rodadas: perguntas diretas, reformulações, perguntas fora dos temas, 6 situações de limite (entrada vazia, só símbolos, consulta ambígua, ausência de resposta confiável, opção de menu inexistente e dado pessoal) e um teste de navegação. O registro completo (entrada, resposta esperada, obtida, acerto e tempo) está em [`docs/resultados_testes.md`](docs/resultados_testes.md) e em `data/resultados_testes.csv`.

| Indicador | Antes das melhorias | Depois das melhorias |
|---|---|---|
| Taxa de acerto (43 casos) | 30/43 = **69,8%** | 40/43 = **93,0%** |
| Rodada 1 (19 casos) | 84,2% | 100% |
| Rodada 2 (12 casos) | 66,7% | 91,7% |
| Rodada 3 (12 casos) | 50,0% | 83,3% |
| Tempo médio de consulta | cerca de 2 ms | cerca de 2 ms |

**Interpretação.**

- No primeiro resultado, as **reformulações** foram as que mais erraram (por exemplo, "fundo de garantia" não aparecia nas palavras-chave do FGTS), porque a busca depende de palavras. Fora do tema e entradas inválidas funcionaram desde o início.
- As melhorias foram duas: mais **palavras-chave e sinônimos** nos dados (sem mexer nas regras do programa) e **maior peso para o subtema** na pontuação.
- Os 3 casos restantes são consultas sobre identidade que o assistente tratou como **ambíguas**: validade da CIN (H08), custo da nova identidade (R01) e emissão pelo Poupatempo (R09). Eles contam como erro porque o teste esperava uma resposta direta, mas o sistema pediu que a pessoa escolhesse entre opções em vez de inventar uma resposta.
- O tempo de consulta é de poucos milissegundos, porque a base é pequena. O tempo que importa para a pessoa é o do teste de usabilidade ([`docs/teste_usabilidade.md`](docs/teste_usabilidade.md)).

**Facilidade de uso:** ainda não avaliada por participantes externos. Até o momento, somente o autor utilizou o sistema. Portanto, não há resultados de usabilidade com usuários a declarar. O roteiro e a ficha de registro estão em [`docs/teste_usabilidade.md`](docs/teste_usabilidade.md).

**Duas melhorias possíveis:** (1) tolerar erros de digitação (por exemplo, comparar palavras por distância de edição); (2) pedir um esclarecimento em vez de listar opções quando a consulta for ambígua, e aprender com as escolhas das pessoas.

**Limitações da avaliação:** o conjunto de testes é pequeno (43 casos); as perguntas foram escritas pelo próprio autor, o que favorece o sistema; as melhorias foram guiadas pelos erros das três rodadas, então a taxa final é **otimista** e uma avaliação justa exigiria perguntas novas escritas por outras pessoas; o tempo medido é o do programa, não o de uma pessoa usando; nenhum participante externo realizou as tarefas de usabilidade até a data desta versão; a comparação dos modelos A e B usa critérios objetivos (fonte, aviso, data, tópicos), e a clareza percebida por usuários não foi medida; e as orientações mudam com o tempo, então a base precisa ser reverificada.

## 🔒 Cuidados: clareza, acessibilidade, privacidade e informação não oficial

- **Clareza:** frases curtas, tópicos, sem siglas sem explicação; a resposta mostra sempre de onde a informação veio.
- **Acessibilidade:** interface só de texto, sem depender de cores ou imagens (o que facilita o uso com leitores de tela); opções numeradas e mensagens de erro que dizem o que fazer.
- **Privacidade:** o assistente não pede nem guarda dados pessoais; se a pessoa digita algo parecido com CPF, RG, e-mail ou outro número de documento, a consulta é interrompida, o dado não é repetido na tela e nada é gravado (o programa não mantém histórico).
- **Informação não oficial:** o assistente se declara informativo, mostra a data de verificação e manda confirmar nas fontes oficiais. Valores, prazos e regras que mudam não são afirmados sem aviso.

## 📁 Estrutura de pastas

* **`data/`** `base_conhecimento.json` (a base verificada), `resultados_testes.csv` (resultados finais) e `resultados_testes_antes.csv` (antes das melhorias).
* **`docs/`** documentação: base de conhecimento, modelos de resposta, resultados de testes, teste de usabilidade, uso de IA e roteiro do vídeo.
* **`src/`** código-fonte: `sistema.py` (interface), `base.py` (leitura e validação), `busca.py` (busca), `respostas.py` (modelos e mensagens), `testes.py` (testes e indicadores) e `auditoria.py` (painel de demonstração dos resultados).
* **`README.md`** este arquivo.

## 📎 Links

* **Repositório:** [GitHub - Global-Solutions-2-2026](https://github.com/Matheus-Silveiraa/Global-Solutions-2-2026)
* **Vídeo de apresentação:** ainda será gravado e publicado como não listado no YouTube.

## 🧠 Decisões técnicas

- Base em JSON, separada do código, para permitir corrigir e acrescentar registros sem reescrever as regras.
- Navegação em grafo com ligações nos dois sentidos, escolha feita no código para não duplicar as ligações nos dados.
- Avisos escritos para quem lê na tela; regras do assistente (não pedir dados, não inventar valores) ficam nos modelos de resposta.
- Busca por pontuação, sem IA externa nem APIs, para ser simples de explicar e de testar.

## 🏁 Conclusões, limitações e melhorias

O protótipo cumpre o fluxo completo (pergunta ou menu, orientação, fonte, aviso e continuidade) e trata entradas inválidas e perguntas sem base. A busca por palavras acerta bem perguntas diretas e fica mais frágil com jeitos novos de perguntar. A base cobre 22 orientações e precisa ser revisada periodicamente. Como melhorias futuras: tolerância a erros de digitação, mais registros e temas, revisão periódica automática das datas de verificação e uma interface web.

## 📋 Licença

Projeto acadêmico. As orientações são informativas e vêm das fontes citadas em cada registro.
