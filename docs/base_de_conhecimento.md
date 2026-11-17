# Base de conhecimento

Arquivo: `data/base_conhecimento.json` (versão 1.3, 22 registros, 3 temas).

## Estrutura do arquivo

```
projeto, versao_base, data_revisao, observacao   -> informações gerais
temas      -> dicionário sigla -> nome (DP, TB, VH)
registros  -> lista de registros (ver campos abaixo)
```

## Campos de cada registro

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | sim | Único; começa com a sigla do tema (`DP-01`) |
| `tema` | sim | Sigla definida em `temas` |
| `subtema` | sim | Assunto (ex.: "FGTS", "Multas") |
| `pergunta` | sim | Pergunta principal respondida |
| `palavras_chave` | sim | Termos que as pessoas usam, com sinônimos |
| `orientacao` | sim | Resposta curta e em linguagem simples |
| `referencia` | sim | Lista de `{orgao, titulo, url}` |
| `data_verificacao` | sim | Quando a fonte foi conferida (AAAA-MM-DD) |
| `aviso` | não | Texto mostrado ao usuário quando é preciso confirmar algo |
| `relacionados` | não | Ids de assuntos ligados (navegação) |

## Organização

- **Hierarquia:** tema -> subtema -> registros. Por exemplo: Documentos pessoais -> Título de eleitor -> DP-08, DP-09, DP-10. É a árvore usada no menu "Escolher um tema".
- **Grafo:** os campos `relacionados` formam um grafo de assuntos. O programa trata cada ligação como de mão dupla. Exemplos: DP-01 (CIN) liga em DP-02, DP-03 e DP-04; TB-05 (CadÚnico) liga em DP-01, DP-06 e DP-08, o que conecta os temas entre si.

## Origem das orientações

Páginas oficiais conferidas pelo autor em 04/11/2026, com atualização da referência de transferência de veículo em 17/11/2026: gov.br, Tribunal Superior Eleitoral, Receita Federal, Ministério do Trabalho e Emprego, Caixa (FGTS), Meu INSS, Senatran, Detran-SP, Poupatempo e Planalto (Código de Trânsito Brasileiro). A lista completa está no campo `referencia` de cada registro.

Regra editorial: valores, taxas e prazos que mudam não entram no texto da orientação; ficam no `aviso`, mandando consultar a fonte.

## Como corrigir ou acrescentar uma orientação (sem mexer no código)

1. Abra `data/base_conhecimento.json`.
2. Para **corrigir**, altere o texto do registro e atualize `data_verificacao`.
3. Para **acrescentar**, copie um registro existente, troque o `id` (sequência do tema), preencha todos os campos obrigatórios e cadastre bastante palavras-chave (sinônimos, jeitos informais de perguntar).
4. Se quiser ligar ao restante da navegação, coloque ids existentes em `relacionados` (basta ligar em um sentido).
5. Rode `python src/sistema.py`: se algo estiver errado, a tela mostra qual registro foi ignorado e por quê. Depois rode `python src/testes.py` para ver se as respostas continuam certas.

## Validações feitas ao carregar

- Arquivo ausente, vazio ou que não seja JSON válido: o programa não inicia e explica.
- Faltando `temas` ou `registros`: o programa não inicia.
- Registro sem campo obrigatório, com tema inexistente, data fora do formato, referência sem URL ou id repetido: o registro é ignorado com aviso.
- `relacionados` apontando para id que não existe: a ligação é ignorada com aviso.

## Atualização de referência

- **VH-04 (transferência de veículo):** além do Código de Trânsito Brasileiro, agora inclui a Carta de Serviços do Poupatempo/Detran-SP [Transferir Propriedade de Veículo Registrado em São Paulo](https://www.poupatempo.sp.gov.br/carta/859FFA63-4EEB-472A-843B-F9595D5AAA32), conferida em 17/11/2026. A página oficial descreve etapas, documentação e canais de solicitação.
