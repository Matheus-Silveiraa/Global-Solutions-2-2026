# Roteiro do vídeo (5 a 7 minutos) e guia para explicar o código

> Publicar no YouTube como **Não listado** e colocar o link no README e no arquivo .txt da entrega.

## Roteiro

| Tempo | O que mostrar | O que falar |
|---|---|---|
| 0:00 | Tela do README | Seu nome, o projeto (Citizen Assist AI) e o problema: informação cidadã dispersa e difícil de confiar |
| 0:30 | Pastas do repositório | `data/` (base), `src/` (código), `docs/` (documentação). Que o projeto é individual |
| 1:00 | Abrir `data/base_conhecimento.json` | Campos de cada registro, as fontes oficiais, a data de verificação e o `aviso`. Que dá para corrigir ou acrescentar sem mexer no código |
| 2:00 | Rodar `python src/sistema.py` | Aviso de que não é canal oficial e de que não se digitam dados pessoais |
| 2:20 | Opção 1, pergunta direta | "Qual o prazo para transferir um carro que comprei?" Mostrar resposta, aviso, fonte e data |
| 2:50 | Navegação | Escolher um assunto relacionado e mostrar que dá para continuar a consulta |
| 3:10 | Opção 2, menu por tema | Tema > assunto > pergunta |
| 3:30 | Pergunta ambígua | "segunda via": o assistente pede para escolher |
| 3:50 | Sem base | "Como funciona o imposto de renda?": avisa o limite e não inventa |
| 4:10 | Entradas inválidas | Enter vazio, `???`, opção "9" no menu, um CPF inventado (não é repetido na tela) |
| 4:40 | Opção 4, trocar para o modelo A | Repetir uma pergunta para mostrar a diferença entre A e B |
| 5:00 | `docs/resultados_testes.md` | 43 casos, 40 acertos (93,0%) na versão atual, comparação com 30/43 (69,8%) antes das melhorias, tempo médio e limitações |
| 5:40 | `docs/teste_usabilidade.md` | Informar com transparência que ainda não houve teste com participante externo; não apresentar resultados inexistentes. Se conseguir alguém antes da gravação, executar as tarefas e atualizar o documento. |
| 6:10 | `docs/uso_ia.md` | Onde a IA foi usada e como você validou. Seja sincero |
| 6:40 | Conclusão | Limitações (base pequena, busca por palavras) e melhorias |

## Guia para explicar o código (em linguagem simples)

**`src/sistema.py`** é a tela de texto. Mostra o menu, lê o que a pessoa digita e chama os outros arquivos. `escolher_numero` repete a pergunta enquanto a opção for inválida; `mostrar_registro` mostra a resposta e as opções de continuidade; `fluxo_pergunta` e `fluxo_tema` são os dois caminhos do menu.

**`src/base.py`** lê o JSON e confere se está tudo certo. `carregar_base` trata arquivo ausente, vazio ou quebrado; `validar_registro` confere os campos obrigatórios de cada registro; `montar_estruturas` cria três organizações dos mesmos dados: um dicionário por id, a árvore tema > subtema e o grafo de relacionados.

**`src/busca.py`** decide qual registro responde. Passos:
1. `preparar` deixa a pergunta em minúsculas, sem acento e sem palavras comuns.
2. `parecido` diz se duas palavras são "da mesma família" (renovar e renovação) usando um radical simples.
3. `pontuar` dá pontos a cada registro (palavras-chave, pergunta, subtema).
4. `consultar` decide: pontuação baixa (menos de 4) = sem resposta; dois registros quase empatados (diferença de até 2) = ambígua; senão, responde com o melhor.
5. Antes disso, trata vazio, texto só com símbolos, texto muito longo e dado pessoal (`contem_dado_pessoal` procura sequências longas de números e e-mails).

**`src/respostas.py`** escreve o que aparece na tela: os modelos A e B, as mensagens de erro e o aviso de limitação.

**`src/testes.py`** roda as perguntas, mede o tempo, calcula a taxa de acerto e gera `docs/resultados_testes.md`. O teste de navegação usa busca em largura (BFS) para achar o caminho entre dois assuntos.

## Perguntas que podem aparecer e boas respostas

- **Por que pontuação em vez de IA?** É simples de explicar, testar e corrigir, não depende de serviço externo, e permite mostrar exatamente por que um registro foi escolhido.
- **Por que o limiar é 4?** Uma única palavra-chave vale 2 pontos; com o limiar em 4, é preciso mais de um sinal para responder. Com limiar 3, perguntas como "quanto custa um iPhone" passariam por causa da palavra "custa".
- **O que acontece em empate?** Se os registros ficam a até 2 pontos do melhor, o assistente lista as opções para a pessoa escolher; só no empate exato de ordem interna vale o id.
- **Por que a taxa de 93% pode ser otimista?** Porque as perguntas foram escritas pelo autor e as melhorias foram guiadas pelos erros observados. Além disso, três consultas sobre identidade continuam sendo classificadas como ambíguas. Os 93% representam somente esta suíte de 43 casos, não uma garantia para qualquer pergunta.
- **O que o assistente faz com dados pessoais?** Não pede, não grava e não repete; se a pessoa digitar algo parecido com um documento, a consulta é interrompida.
- **Como acrescento uma orientação nova?** Edito o JSON, sem mexer no código, e rodo os testes.
