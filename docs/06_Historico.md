
---

## 11/11, nona volta — o clone do SAC no ar, e a BOMBA da carga dos formulários

🔵 Dele: *"a pagina SAC será refeita para cá, pois não vamos mais usar o
bitrix, o mesmo para os formularios que ainda não avançaram"* · *"subir o clone
identico, com a diferença dos formularios novos endereçados no paniel menu que
abre lateralmente"* · *"todos os recursos devem ser iguais ao do atual 100%"* ·
*"tudo que foi pedido deve ser entregue, principalmente os formularios que
ainda nao sairam"*.

### O clone do SAC: `http://212.85.17.184:8090/`

🚨 **Prévia numa porta, não publicação.** O `sac.movisat.com.br` segue no
Bitrix24.Sites até ele mandar virar o DNS; a porta 8090 foi aberta no ufw com a
nota *"fechar quando virar o DNS"*, e o host manda `noindex, nofollow`.

📘 **A fonte inteira, com de onde cada byte veio:**
`/home/claude/sac_clone_fonte/README.md` — os 2 scripts, o `sac_online.zip`
dele, o JSON extraído e a conf do nginx.

🚨 **Por que este host PROXEIA os formulários** em vez de apontar para o
`forms.movisat.com.br`: aquele host manda `X-Frame-Options: DENY`, e **está
certo** que mande — formulário com CNPJ e telefone não deve ser embutível por
ninguém. A gaveta lateral precisa embutir. Afrouxar o `forms` para `SAMEORIGIN`
resolveria aqui e **abriria o formulário para ser embutido por qualquer página
daquele domínio**, e não é lá que a decisão pertence. Então o clone serve os
mesmos três caminhos (`/f/`, `/pub/assets/`, `/api/publico/`) por proxy para
`127.0.0.1:8008`, e só no `/f/` **dele** o cabeçalho é `SAMEORIGIN`.
✅ Conferido depois de subir: o `forms` continua respondendo **DENY**.

### O 16º formulário: `Ideias e sugestões` (Bitrix 38)

Era o **único dos 8 cartões do SAC sem formulário nosso** — não estava entre os
15 levantados em 22/10, e só apareceu quando o clone foi medido.

`/f/ideias-sugestoes`, 11 campos, 2 regras condicionais, 3 etapas, formato novo,
**painel nulo** (ideia de melhoria não é OS nem cobrança) e **desligado**: a
régua da casa é que carregar a definição e publicar são dois atos, e só o
segundo é dele. Enquanto estiver desligado, o cartão 8 do clone aponta para o
Suporte — apontar para um 404 seria pior.

⚠️ **Dois erros do Bitrix ficaram para trás:** o campo *"Detalhe ao máximo a
melhoria"* vinha com **uma linha** (agora 6), e os 11 campos vinham **todos
obrigatórios, CPF e CNPJ juntos** — resolvido pelas 3 regras do próprio
formulário, que fazem os três nascerem escondidos.

### 🚨 A BOMBA: `carregar_formularios.py` ia apagar 55 validações

**Medido em 11/11, rodando a carga completa e comparando o retrato antes e
depois:** o script **sem argumento** teria

| o quê | quanto |
|---|---|
| validações apagadas | **55 das 60** |
| formulários revertidos de `novo` para `classico` | **14** |
| etapas perdidas | **as dos 15** |
| tipos revertidos a `string` | **2** (e-mail e telefone **do novo titular**) |

— tudo **em silêncio, sem erro nenhum**.

🚨 **A causa não é bug de código: são DUAS VERDADES.** O arquivo se declara a
fonte única (*"`gravar_definicao` APAGA e reescreve os campos a cada carga"*) e
não era: as validações entraram pelas **migrações 103/104** e as etapas pelo
**`etapas_dos_formularios.py`**, direto no banco. A verdade que o script tinha
era a menor — 5 validações contra 60, e `FORMATO_NOVO = {"SUPORTE"}` contra 15.

⚠️ **E nenhuma suíte pegaria isso, porque o estado no ar estava CERTO.** Só
quem rodasse a carga descobriria — depois.

**O conserto, em quatro partes:**

1. `VALIDACOES` passou a ter as **64** (as 60 medidas + as 4 do 16º);
2. `FORMATO_NOVO = None`, que significa **todos** — ⚠️ lista volta a divergir no
   dia em que o 17º nascer e ninguém lembrar de acrescentá-lo;
3. as etapas são **derivadas**, chamando o `derivar()` do próprio
   `etapas_dos_formularios.py`. 🚨 Copiar os 15 agrupamentos para dentro do
   carregador criaria a **terceira** verdade;
4. o `AJUSTES` passou a aceitar **`tipo`**, e é lá que o conserto da migração
   104 agora mora — nos dois campos que definem **o dono do contrato**.

⚠️ **E o derivador ganhou o `if __name__ == "__main__"` que faltava:** com
`main()` solto no fim, qualquer `import` rodava o relatório dos 16 e podia
chamar `sys.exit(1)` na cara de quem importou.

**Provas:** carga completa → só o 16º mudou · **segunda carga seguida não muda
nada** · as travas novas comparam **banco × script**, em vez de contar.

---

## 11/11, décima volta — a barra de etapas no card, e a trava que era da HORA

🔵 **Item dele, do bloco de 11/11:** *"a barra interna de mudar etapa nos cards
dessas etapas"*.

### 1. A barra de etapas dentro do card

📏 **O que existia, medido antes:** um `<select>` de 190 px na faixa do card
(`DialogoDeChamado.vue`). Ele **movia** — então isto não era defeito, era o
pedido: com as **10 etapas do Financeiro** a sequência ficava atrás de um
clique, e não se via onde o card está nela.

**O que entrou:** uma barra de passos numerados abaixo da faixa, uma linha que
**rola** (`flex-wrap: nowrap` + `overflow-x: auto`). A faixa continua dizendo a
etapa atual em texto — ela deixou de ser **controle** e voltou a ser **medida**.

🚨 **A etapa atual não é botão: é `<strong>`, com `aria-current="step"`.** A
distinção é **estrutural**, não de cor — cor sozinha não é portador, e a régua
é da casa. Os outros passos são `<button>`.

⚠️ **O `<select>` saiu.** Dois controles para mover o mesmo card deixariam o
estado ambíguo.

⚠️ **Card finalizado não mostra a barra** — reabrir primeiro é o gesto, mesma
régua do `<select>` de antes. Mas a faixa **continua dizendo** em que etapa ele
parou: esconder a barra não pode esconder o fato.

**Travas:** `frontend/src/barra_etapa_1111.teste.js`, **8 verificações**.
🚨 Elas olham **estrutura**, não gesto: o jsdom não faz layout, e uma barra com
`pointer-events: none` passaria verde — foi exatamente o defeito do card inerte
de 09/11, com 22 travas verdes sobre tela morta.
**Defeitos forjados, os dois ficam vermelhos:** tirar o `aria-current` e deixar
a barra aparecer em card finalizado.

**E a 9ª conferência de CSS publicado** (`conferir_css_publicado.mjs`):
`.trilha` tem de ser `nowrap` **e** `overflow-x: auto`, e
`.trilha__passo--atual` tem de existir. 🚨 É a classe de defeito que **só** ela
pega: com `flex-wrap: wrap`, a barra quebra em três fileiras e empurra o corpo
do card fora da tela — e a trava de tela fica **verde**, porque `scrollWidth` é
sempre 0 no jsdom. **Forjado:** `wrap` → a conferência reprova com a frase
inteira.

### 2. 🚨 A trava que eu disse ser da ORDEM era da HORA

🚨 **Correção de um diagnóstico meu de hoje.** Eu escrevi que esta suíte usa
**`pytest-randomly`** e que o verde dependia do sorteio da ordem.
📏 **Medido:** `pip list` no venv devolve **só `pytest`** — o plugin **não está
instalado**, e `--randomly-seed` é recusado como argumento desconhecido. **A
ordem é determinística.**

**O que estava vermelho de verdade**, e falhava **sozinho**:
`teste_agendamento::test_o_dia_traz_as_os_de_cada_compromisso`.

**A causa, medida às 21:21 BRT (00:21 UTC):** `agendamento.do_dia` compara
`a.inicio::date`, e o Postgres resolve esse cast no **fuso da sessão**
(`current_setting('TimeZone')` → `America/Sao_Paulo`). O teste perguntava a data
em **UTC**. Das **21h à meia-noite** a data UTC já virou e a do banco não —
então o teste pedia o dia 21 e o compromisso estava no dia 20. **Três horas por
dia de vermelho, e verde nas outras vinte e uma.**

🔵 **A produção está certa, e isso importa:** quem chama `do_periodo` é a tela,
e a data vem do navegador, que está no mesmo fuso do banco; quem mexe com fuso
no código (`presenca.py`) escreve `AT TIME ZONE` explícito. O defeito era **só
do teste**.

**O conserto:** o dia vem do **próprio banco**, com o mesmo cast da consulta
(`_dia_do_banco`) — não é cálculo de fuso escrito à mão, e se o fuso da sessão
mudar o teste acompanha sozinho. Mais uma trava que guarda o defeito
(`test_o_dia_e_o_do_BANCO_e_nao_o_de_UTC`), **forjada e vermelha** quando se
volta a perguntar em UTC.

⚠️ **Duas primas da mesma forma ficam anotadas e não foram tocadas:**
`teste_ligacoes_consulta.py:180` e `teste_orcamento_consulta.py:347/351` também
perguntam a data em UTC. Elas passam porque o filtro delas é
`< (%s::date + 1)` e a data um dia à frente **alarga** a janela — passam por
tolerância, não por estarem certas.

⚠️ **E a trava do `teste_presenca` que eu disse depender da ordem:** ela
reprovou numa rodada de 16:34 e **não reproduz agora** — passa sozinha (58
verdes) e passa nas duas metades da suíte. Fica anotada como **não
reproduzida**, não como explicada.

### 3. 📏 A medição do item "aba do Financeiro espelhando o Fechamento do FPSL"

🔵 Ele pediu *"meça antes"*. Medido no cache do FPSL (`data/fpsl.db`), em
11/11:

| estado dos cards de fechamento | quantos |
|---|---|
| `cancelado` | **6** |
| qualquer outro estado | **0** |

**Só dois técnicos** tiveram card na vida (Franck 14262 e Pedro Felipe 14316),
contra **191 técnicos reais** na tabela.

**E o funil do dinheiro, com as mesmas regras do `gerar_cartoes`:**

| filtro | OS | valor |
|---|---|---|
| OS no cache com valor de técnico (`PAGAMENTO DE TECNICO` 653939 + `KM DESLOCAMENTO` 6971) | 70 | **R$ 8.442,75** |
| … e na situação **15694** | 16 | R$ 2.271,60 |
| … e com técnico não-excluído na OS | 8 | R$ 1.413,70 |
| … e esse técnico está na tabela `tecnicos` | 8 | R$ 1.413,70 |
| … e a OS tem linha de **conferência** (o portão) | **5** | **R$ 860,70** |

🚨 **A tela entrega 10% do dinheiro, e o buraco não é da tela — é do funil.**
As duas maiores perdas: a exigência de estar na **situação 15694** (70 → 16 OS)
e o técnico da OS ser um **usuário interno excluído** (16 → 8). Espelhar a tela
no MoviZap hoje espelharia **seis cards cancelados e R$ 860,70**.
🟡 Então a ordem que proponho é: **consertar o funil no FPSL primeiro**, e só
depois espelhar. 🔴 Decisão dele.

### 4. ⚠️ Uma colisao de nome de classe, achada no CSS publicado

🚨 A barra nasceu com a classe `.etapas` — e `grep` no CSS publicado mostrou
**duas** regras `.etapas`, de componentes diferentes (`DisparosOperacao.vue` e
`ChecklistDeCards.vue` ja usavam o nome, uma delas com
`flex-direction: column`). O `scoped` do Vue isola no navegador, mas a **9ª
conferencia le o CSS publicado como texto** e pegaria a primeira regra que
casasse: ela passaria ou reprovaria **por sorte da ordem do bundle**.

**Conserto:** a barra virou `.trilha` / `.trilha__passo` /
`.trilha__passo--atual`, nome que nao existia em lugar nenhum. 📏 Conferido no
bundle: **uma** regra `.trilha`. As 8 travas e as 9 conferencias seguem verdes.

### 5. 📏 CONFERENCIA A PEDIDO DELE: *"os formularios devem estar funcionando, bem como os demais recursos"*

**Os 16 formularios, medidos DE FORA** (`forms.movisat.com.br`, chamada real do
Windows, nao de dentro do servidor):

| | resultado |
|---|---|
| os **15 ativos** | pagina `200` **e** definicao `200`, com o titulo e a contagem de campos certos (18 aditivo · 11 administrativo · 5 CES · 8 contato · 32 credenciamento · 15 demonstracao · 36 ficha cadastral · 10 financeiro · 16 fornecedores · 9 NPS · 16 pagamento tecnicos · 17 rescisao · 17 substituicao · 11 suporte · 14 teste gratuito) |
| `ideias-sugestoes` | pagina `200`, definicao **404** — **correto**: ele esta **desligado**, e ligar e decisao dele. A pagina mostra *"Formulario nao encontrado"*, a **mesma frase** de "nao existe", de proposito: distinguir contaria ao mundo quais formularios a casa tem |

**As travas do caminho inteiro:** `teste_rotas_formularios` +
`teste_rotas_pipeline` + `teste_formularios` + `teste_validacao_dos_formularios`
+ `teste_destino_do_card` + `teste_formato_novo` +
`teste_etapas_dos_formularios` = **203 passaram, 1 ignorado**. Entre elas esta o
envio publico de verdade, que **cria o card**.

**Os demais recursos, de fora:** painel `200` · `/api/saude` `200`
(migracao **106**, Postgres 16.15, **41 telas ativas**) ·
`/api/paineis/operacao` **401** sem credencial, que e o certo ·
`/api/publico/desafio` `200` · clone do SAC `200` e o `/f/suporte` proxeado
`200` · FPSL, MoviServer, Prospeccao e o SAC atual todos `200`.
**Servicos:** os 9 do usuario e o nginx `active running`; `movizap` com
**NRestarts=0** desde 16:31 e **zero** linha de `warning` no log desde as 21:00.

⚠️ **`forms.movisat.com.br/` sozinho devolve 404** — nao existe indice, so
`/f/<slug>`. E o desenho de hoje; quem digitar o dominio puro ve um 404 cru.

✅ **E producao esta LIMPA de residuo de teste:** **7** cards, **zero** com OS de
teste (>= 990000), zero solicitacao de teste com card, zero agendamento
`997xxx`, zero atendente `zz_teste%`.

⚠️ **Um fato novo que a barra de etapas trouxe, e que ele deve saber:** a barra
tambem aparece no card da coluna **`Chamados`**, que hoje tem **2** etapas
(`Chamados` e `Serviço Realizado`) -- entao mover um chamado **sem OS** para
`Serviço Realizado` passou a ser **um clique**. 🔵 Nao e capacidade nova: o
`<select>` de antes oferecia o mesmo, e `pipeline.mover` so barra aba diferente
e card finalizado, porque **"nao existe caminho proibido" e decisao dele**. O
que mudou e a visibilidade.

---

## 11/11, décima primeira volta — O FORMULÁRIO PRÉ-PREENCHIDO PELO LINK (migração 107)

🔵 **Pedido dele**, do bloco de 11/11: formulários *"pré-preenchidos quando
abertos pelo botão dentro do chat"*.

📏 **Medido antes:** nenhuma peça existia — `grep` por `URLSearchParams` em
`frontend/publico/` devolvia **zero**, e não havia botão no chat.

### 🚨 A decisão de desenho, e é o ponto da frente inteira

O caminho curto seria `/f/suporte?cnpj=...&telefone=...`. **Não é o caminho.**
Dado de cliente no endereço entra no **log de acesso do nginx**, no **histórico
do navegador** de quem abriu, no `Referer` de qualquer recurso que a página
carregue, e em **qualquer repasse do link** por WhatsApp ou e-mail. Base64 não
resolve nada disso: esconde do olho, não do log.

➡️ Então o que viaja na URL é um **bilhete opaco** (`secrets.token_urlsafe(16)`)
e os valores ficam na tabela `formulario_convite`. 🔴 O caminho curto segue
sendo decisão dele, e está escrito como tal no documento do Desktop.

### 🚨 O segundo achado, que mudou o código: a sugestão é por RÓTULO, não por TIPO

📏 Medido nas 16 definições:

| armadilha | onde |
|---|---|
| **dois** campos `phone` e **dois** `email`, e os segundos são *"... do novo titular"* | `rescisao` |
| **dois** `phone` (da empresa e pessoal) | `ficha-cadastral` |
| `double` é **CNPJ, CPF, RG e "Quantidade de veículos"** | em quatro formulários |

⚠️ Sugerir o telefone de quem está rescindindo no campo do **novo titular** não
é defeito de tela: é **a pessoa errada escrita num termo**. Por isso
`SUGESTAO_POR_ROTULO` é lista fechada, casa **exato** (sem acento, sem caixa), e
só o **primeiro** campo de cada rótulo recebe.

**Dois efeitos medidos:** a `rescisao` recebe só os campos do cliente, nunca os
do novo titular; e a `ficha-cadastral` **não** sugere nome, porque ela pede
*"Nome completo do responsável em assinar o contrato"*, que não bate exato com
*"Nome completo"* — e quem fala no WhatsApp não é necessariamente quem assina.

### Dois fatos do banco que o código teve de obedecer

1. 🚨 **`conversa` não tem `cliente_id`** — só `contato_id`; o cliente vem por
   `contato.cliente_id`.
2. 🚨 **`cliente.tipo_pessoa` é INTEIRO**: `{0: '—', 1: 'Jurídica',
   2: 'Física', 3: 'Estrangeiro'}`. ⚠️ **É ele quem decide se o documento vai
   no CNPJ ou no CPF, nunca o comprimento do texto** — cadastro com documento
   pela metade existe, e adivinhar pelo tamanho poria CNPJ no campo de CPF.
   `0` e `3` não sugerem documento nenhum.

### As quatro regras da tabela

**vence** em 7 dias · **abrir não gasta** (recarregar a página não pode quebrar
o link) · **enviar não apaga** (o rastro explica depois de onde saiu a
solicitação) · **valor é sugestão, nunca verdade** (o envio revalida tudo).

⚠️ E o pré-preenchimento **falha em silêncio**, de propósito: bilhete vencido,
formulário desligado depois do convite, rota fora do ar → a página abre
**vazia**, que é o que ela já fazia antes. ⚠️ Quando pré-enche, a tela **diz**:
*"Já preenchemos o que sabemos. Confira antes de enviar e corrija o que estiver
diferente."*

### Um conflito de nome que a leitura pegou

🚨 `/api/conversas/{id}/convidar` **já existe** e significa outra coisa (chamar
um colega para a conversa). As rotas novas viraram
`/api/conversas/{id}/link-de-formulario` e `.../links-de-formulario` para não
colidir na leitura. A rota pública é `/api/publico/convite/{bilhete}`.

### O que falta, e é pouco

🔴 **O botão na tela da conversa.** A rota existe e exige login (`401` sem
credencial, conferido no ar). 🚨 **E ela não manda mensagem nenhuma, de
propósito:** devolve o link, e quem manda é a pessoa, escrevendo — mensagem ao
cliente é irreversível.

### Provas

**Travas:** `tests/teste_convite_de_formulario.py`, **34**. A que mais importa
procura o CNPJ, o telefone, o nome, o sobrenome e o e-mail **dentro da URL** e
exige que nenhum esteja lá.

**E o caminho inteiro, de fora:** convite real criado para o Suporte →
`GET /api/publico/convite/<bilhete>` em `forms.movisat.com.br` devolveu **200**
com os **cinco** campos sugeridos, e a página abriu **200**. O convite de teste
foi apagado em seguida (`formulario_convite` voltou a **zero** linhas).

⚠️ **Dois erros meus nesta volta, e os dois foram achados pelo vermelho, não
pela leitura:** eu supus que `MAPA["70"]` era o Suporte (é a **pesquisa CES**,
sem telefone, e-mail nem CNPJ), e esqueci que o `TestClient` com `with` **fecha
o pool** na saída — então a limpeza de depois do teste estourava e deixaria
resíduo em produção.
