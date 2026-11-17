# Uso de inteligência artificial

> **Antes de entregar:** os trechos marcados com **[CONFIRMAR]** só devem ficar se forem verdade. Se não forem, ajuste o texto. Este documento precisa refletir o que realmente aconteceu.

## Ferramenta usada

Claude (Anthropic), em conversa pelo aplicativo, entre 04/11/2026 e 12/11/2026.

O protótipo **não usa nenhum modelo de IA ou API externa em funcionamento**. A busca é feita por regras e pontuação em Python, e todas as respostas vêm da base verificada.

## Onde a IA foi usada

| Etapa | Uso da IA | Quem decidiu e validou |
|---|---|---|
| Planejamento | Organização das etapas, definição dos campos da base e do cronograma | O autor escolheu os temas (documentos pessoais, trabalho e benefícios, veículo e habilitação) |
| Pesquisa de fontes | Busca inicial e rascunho dos textos dos 22 registros | O autor abriu e conferiu as fontes, trocou fontes fracas por oficiais e fechou a base em 04/11/2026 |
| Plano de testes e modelos de resposta | Rascunho das perguntas de teste e dos dois modelos de resposta | O autor aprovou a estrutura **[CONFIRMAR]** |
| Código Python e documentação | O código dos arquivos em `src/`, o README e os documentos em `docs/` foram escritos pelo Claude a pedido do autor, que teve pouco tempo para o prazo | **[CONFIRMAR]** O autor leu o código, executou o programa e os testes e consegue explicar o funcionamento |
| Testes | Execução dos testes automáticos e geração dos relatórios | O relatório disponível registra 43 casos, com 40 acertos (93,0%). O teste de usabilidade com outra pessoa ainda não foi realizado. **[CONFIRMAR que o autor executou localmente `python src/testes.py`]** |

## Revisão posterior com ChatGPT

Em 17/11/2026, o ChatGPT (OpenAI) foi utilizado nesta conversa para revisar a documentação publicada no repositório, preencher a identificação do aluno com os dados fornecidos, alinhar o README e o roteiro do vídeo aos resultados registrados e documentar que o teste de usabilidade ainda não foi realizado. Essa revisão documental não substitui a conferência do código, das fontes oficiais nem a execução dos testes pelo autor.

## Validação crítica realizada

A IA cometeu ou deixou passar erros que foram encontrados na conferência e corrigidos:

1. **Data de validade do RG antigo:** o rascunho da IA trazia 23/02/2032, copiado de uma matéria. Outras fontes e a página oficial apontavam 28/02/2032, que ficou na base.
2. **CNH digital:** matérias de jornal diziam que era preciso conta gov.br nível prata ou ouro. Ao conferir a página oficial, o autor encontrou outros requisitos (CNH com QR Code e conta Gov.br) e corrigiu o registro VH-06.
3. **Referências inadequadas:** uma referência do VH-02 era uma notícia sobre outro assunto (curso teórico no Paraná) e a do VH-04 era apenas a página inicial do Detran-SP. Ambas foram retiradas.
4. **Avisos escritos como ordens ao assistente** ("o assistente não deve...") foram reescritos para linguagem que a pessoa possa ler na tela. O aviso do DP-10 estava desatualizado e foi trocado por um texto geral.
5. **Fontes em conflito sem solução automática:** idade na renovação automática da CNH, gravidade da multa por atraso na transferência e a data do PIS/Pasep. Nesses casos, a base **não afirma** o ponto duvidoso e manda confirmar na fonte.
6. **Avaliação dos testes:** a primeira versão registrada acertou 30/43 casos (69,8%); a versão atual acertou 40/43 (93,0%). Os três casos restantes são consultas sobre validade, custo e emissão da identidade que foram classificadas como ambíguas. As melhorias foram guiadas pelos erros observados, portanto o resultado é específico desta suíte e pode ser otimista (ver `docs/resultados_testes.md` e o README).

## Cuidados e limites

- Nenhuma informação da base foi aceita sem fonte identificável e sem data de verificação.
- A IA pode errar valores, prazos e regras que mudam; por isso o assistente avisa e manda confirmar nas fontes oficiais.
- Nenhum dado pessoal foi inserido na IA nem é coletado pelo programa.
