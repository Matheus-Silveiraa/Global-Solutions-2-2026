# Resultados dos testes

Gerado automaticamente por `python src/testes.py`. Não edite à mão: rode o script de novo.

## Como os testes são avaliados

- **Pergunta normal:** acerto = o registro esperado vem em primeiro lugar, a fonte (link) aparece e, se o registro tem aviso, o aviso aparece.
- **Fora do tema:** acerto = o assistente informa que não há base suficiente e não inventa orientação.
- **Limites:** acerto = mensagem compreensível, sem erro do programa e sem repetir dados pessoais.
- **Tempo:** média de 200 execuções de cada consulta completa (busca + formatação), em ms.

## Indicadores por rodada

| Rodada | Testes | Acertos | Taxa de acerto | Tempo médio (ms) |
|---|---|---|---|---|
| rodada 1 | 19 | 19 | 100.0% | 1.726 |
| rodada 2 | 12 | 11 | 91.7% | 2.219 |
| rodada 3 | 12 | 10 | 83.3% | 2.475 |
| **Total** | 43 | 40 | **93.0%** | 2.072 |

## Antes e depois das melhorias

| Rodada | Taxa antes | Taxa depois |
|---|---|---|
| rodada 1 | 16/19 = 84.2% | 19/19 = 100.0% |
| rodada 2 | 8/12 = 66.7% | 11/12 = 91.7% |
| rodada 3 | 6/12 = 50.0% | 10/12 = 83.3% |

## Taxa de acerto por tipo de pergunta (resultado final)

| Tipo | Acertos | Taxa |
|---|---|---|
| direta | 15/17 | 88.2% |
| reformulacao | 12/13 | 92.3% |
| fora_do_tema | 6/6 | 100.0% |
| limite | 6/6 | 100.0% |
| navegacao | 1/1 | 100.0% |

## Registro completo dos testes

| Rodada | ID | Tipo | Entrada | Esperado | Obtido | Acerto | Tempo (ms) |
|---|---|---|---|---|---|---|---|
| 1 | T01 | direta | Como tiro a segunda via do título de eleitor? | DP-08 | DP-08 | sim | 3.1574 |
| 1 | T02 | direta | Quanto tempo tenho para pedir o seguro-desemprego? | TB-02 | TB-02 | sim | 2.7781 |
| 1 | T03 | direta | Como renovar a CNH? | VH-02 | VH-02 | sim | 1.3749 |
| 1 | T04 | direta | Meu RG antigo ainda vale? | DP-02 | DP-02 | sim | 2.9294 |
| 1 | T05 | direta | Como consulto o saldo do FGTS? | TB-04 | TB-04 | sim | 1.9594 |
| 1 | T06 | direta | Qual o prazo para transferir um carro que comprei? | VH-04 | VH-04 | sim | 2.5681 |
| 1 | T07 | reformulacao | perdi meu título eleitoral, o que eu faço | DP-08 | DP-08 | sim | 2.1917 |
| 1 | T08 | reformulacao | fui demitido sem justa causa, até quando posso pedir o benefício? | TB-02 | TB-02 | sim | 3.6065 |
| 1 | T09 | reformulacao | minha habilitação está vencendo | VH-02 | VH-02 | sim | 2.0816 |
| 1 | T10 | reformulacao | quero saber quanto tenho de fundo de garantia | TB-04 | TB-04 | sim | 1.4285 |
| 1 | T11 | fora_do_tema | Como funciona o imposto de renda? | sem_resposta | sem_resposta | sim | 1.7303 |
| 1 | T12 | fora_do_tema | Qual a previsão do tempo para amanhã? | sem_resposta | sem_resposta | sim | 2.1621 |
| 1 | L01 | limite | (vazia) | vazia | vazia | sim | 0.0003 |
| 1 | L02 | limite | ??? | invalida | invalida | sim | 0.0019 |
| 1 | L03 | limite | segunda via | ambigua | ambigua: DP-05, DP-08, DP-06 | sim | 1.383 |
| 1 | L04 | limite | quanto custa exatamente a 2ª via do RG em SP? | DP-05 | DP-05 | sim | 3.3896 |
| 1 | L06 | limite | meu cpf é 123.456.789-09, como regularizar? | dado_pessoal | dado_pessoal | sim | 0.0017 |
| 1 | L05 | limite | 9 / abc / (vazio) / 2 | 3 mensagens de erro e depois aceitar 2 | escolhido=2, mensagens=3 | sim | 0.0251 |
| 1 | T13 | navegacao | DP-01 -> DP-05 pelas opções de continuidade | caminho com até 3 passos; DP-01 com 3 ou mais opções | DP-01 -> DP-03 -> DP-05 (menor número de opções em um registro: 2) | sim | 0.0193 |
| 2 | H01 | direta | quero tirar minha primeira habilitação | VH-01 | VH-01 | sim | 1.9393 |
| 2 | H02 | direta | como vejo se meu CPF está regular | DP-07 | DP-07 | sim | 2.6081 |
| 2 | H03 | direta | como pegar a carteira de trabalho no celular | TB-01 | TB-01 | sim | 2.5904 |
| 2 | H04 | direta | o que é o cadastro único | TB-05 | TB-05 | sim | 1.4456 |
| 2 | H05 | direta | meu carro precisa de licenciamento todo ano? | VH-03 | VH-03 | sim | 3.4338 |
| 2 | H06 | direta | recebi uma multa de trânsito, posso pagar com desconto? | VH-05 | VH-05 | sim | 2.9009 |
| 2 | H07 | reformulacao | como faço para sacar meu fundo de garantia | TB-04 | TB-04 | sim | 1.5587 |
| 2 | H08 | reformulacao | por quanto tempo vale a nova identidade | DP-04 | ambigua | NÃO | 2.1213 |
| 2 | H09 | reformulacao | onde me inscrevo no bolsa família | TB-05 | TB-05 | sim | 2.0686 |
| 2 | H10 | reformulacao | meu RG vai deixar de valer? | DP-02 | DP-02 | sim | 2.5203 |
| 2 | H11 | fora_do_tema | quanto custa um iphone novo | sem_resposta | sem_resposta | sim | 2.0913 |
| 2 | H12 | fora_do_tema | como abrir uma empresa | sem_resposta | sem_resposta | sim | 1.347 |
| 3 | R01 | direta | quanto custa tirar a identidade de novo | DP-05 | ambigua | NÃO | 2.6459 |
| 3 | R02 | reformulacao | esqueci onde guardei meu título de eleitor | DP-08 | DP-08 | sim | 2.7654 |
| 3 | R03 | direta | como faço o agendamento no INSS? | TB-03 | TB-03 | sim | 1.4727 |
| 3 | R04 | direta | quando termina o prazo do abono do PIS | TB-06 | TB-06 | sim | 2.7688 |
| 3 | R05 | reformulacao | preciso vender meu carro, o que devo fazer | VH-04 | VH-04 | sim | 2.1379 |
| 3 | R06 | direta | como baixar a CNH digital no celular | VH-06 | VH-06 | sim | 2.2454 |
| 3 | R07 | reformulacao | tirar carteira de motorista pela primeira vez | VH-01 | VH-01 | sim | 4.0056 |
| 3 | R08 | reformulacao | o que fazer se meu CPF estiver irregular | DP-07 | DP-07 | sim | 1.9456 |
| 3 | R09 | direta | emitir a identidade nova pelo poupatempo | DP-03 | ambigua | NÃO | 3.2722 |
| 3 | R10 | reformulacao | como funciona o seguro desemprego para quem foi demitido | TB-02 | TB-02 | sim | 2.723 |
| 3 | R11 | fora_do_tema | como emitir passaporte | sem_resposta | sem_resposta | sim | 1.4392 |
| 3 | R12 | fora_do_tema | qual a melhor receita de bolo | sem_resposta | sem_resposta | sim | 2.2725 |

## Comparação dos modelos de resposta A e B

Mesmas perguntas, dois formatos. Critérios (cada um vale 1 ponto): fonte exibida, aviso exibido quando existe, data de verificação, declaração de que não é canal oficial, orientação em tópicos curtos.

| Modelo | Respostas avaliadas | Critérios atendidos (média de 5) | Respostas completas | Maior bloco de texto (palavras, média) |
|---|---|---|---|---|
| A | 28 | 2.0 | 0/28 | 92.8 |
| B | 28 | 5.0 | 28/28 | 30.3 |
