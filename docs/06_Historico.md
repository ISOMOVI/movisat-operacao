
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

---

# 📜 HISTÓRICO MOVIDO DO Proximos_Passos.md EM 12/11/2026

> 🚨 **Este bloco estava DENTRO do MIOLO**, que é o lugar onde, pela regra do
> próprio arquivo, *"só fica o que falta"*. Eram **6573 linhas** em **60 seções**,
> de 24/09 a 11/11 — e quem lesse o MIOLO de cima media errado, porque
> encontrava como pendência coisas já entregues.
>
> 📏 Antes de mover, conferi que este arquivo **não** continha este conteúdo:
> tinha 349 linhas e nenhuma menção a 30/10, 15/10 ou 02/10. Era a única
> cópia, então foi **movido**, nunca apagado.

## ✅ 11/11, 11ª volta — O FORMULÁRIO PRÉ-PREENCHIDO PELO LINK (migração 107)

🔵 Dele: *"siga com o que falta e documentando"* e, no meio,
*"os formularios devem estar funcionando, bem como os demais recursos"*.

### 1. 📏 A conferência que ele pediu no meio da volta

**Os 15 formulários ativos:** página `200` **e** definição `200`, medidos **de
fora** (chamada real do Windows, não de dentro do servidor), com título e
contagem de campos certos nos 15. O 16º (`ideias-sugestoes`) devolve **404** na
definição porque está **desligado** — é o correto, e ligar é decisão dele.

**O resto:** painel `200` · `/api/saude` `200` (migração 106, Postgres 16.15,
**41 telas ativas**) · `/api/paineis/operacao` **401** sem credencial ·
`/api/publico/desafio` `200` · clone do SAC `200` · FPSL, MoviServer,
Prospecção e SAC atual `200` · os **9** serviços do usuário e o nginx
`active running`, `movizap` com **NRestarts=0** e zero `warning` no log.

✅ **Produção limpa de resíduo:** 7 cards, **zero** com OS de teste, zero
solicitação de teste com card, zero agendamento `997xxx`, zero atendente
`zz_teste%`.

⚠️ **`forms.movisat.com.br/` sozinho devolve 404** — não existe índice, só
`/f/<slug>`. É o desenho de hoje.
⚠️ **A barra de etapas aparece também no card de `Chamados`** (2 etapas), então
mover um chamado **sem OS** para `Serviço Realizado` é **um clique**. 🔵 Não é
capacidade nova — o `<select>` de antes dava o mesmo, e *"não existe caminho
proibido"* é decisão dele.

### 2. ✅ O convite de formulário (migração 107)

🔵 Pedido dele: formulários *"pré-preenchidos quando abertos pelo botão dentro
do chat"*. 📏 Antes, **nenhuma peça existia**.

🚨 **A DECISÃO DE DESENHO, E É O PONTO DA FRENTE:** o caminho curto seria
`/f/suporte?cnpj=...&telefone=...`. **Não é o caminho.** Query string entra no
`access.log` do nginx, no histórico do navegador de quem abriu, no `Referer` e
em qualquer repasse do link. Base64 esconde do olho, não do log. Então o que
viaja é um **bilhete opaco** e os valores ficam na tabela
`formulario_convite`. 🔴 O caminho curto segue sendo decisão dele.

🚨 **E O SEGUNDO ACHADO MUDOU O CÓDIGO: a sugestão é por RÓTULO, não por TIPO.**
Medido nas 16 definições: a `rescisao` tem **dois** `phone` e **dois** `email`,
e os segundos são *"... do novo titular"*; a `ficha-cadastral` tem dois
`phone`; e `double` é **CNPJ, CPF, RG e "Quantidade de veículos"**.
⚠️ Sugerir o telefone de quem rescinde no campo do **novo titular** não é
defeito de tela: é **a pessoa errada escrita num termo**. `SUGESTAO_POR_ROTULO`
é lista fechada, casa **exato**, e só o primeiro campo de cada rótulo recebe.
📏 Efeito medido: a `ficha-cadastral` **não** sugere nome, porque pede *"Nome
completo do responsável em assinar o contrato"* — quem fala no WhatsApp não é
necessariamente quem assina.

**Dois fatos do banco que o código teve de obedecer:** `conversa` **não tem
`cliente_id`** (vem por `contato.cliente_id`), e `cliente.tipo_pessoa` é
**inteiro** (`1` jurídica, `2` física) — ⚠️ **é ele quem decide CNPJ × CPF,
nunca o comprimento do texto**; `0` e `3` não sugerem documento nenhum.

**As quatro regras da tabela:** vence em 7 dias · **abrir não gasta** ·
**enviar não apaga** · **valor é sugestão, nunca verdade**.
⚠️ O pré-preenchimento **falha em silêncio** (página abre vazia, como antes), e
quando preenche a tela **diz** que preencheu.

🚨 **Conflito de nome evitado:** `/api/conversas/{id}/convidar` já existe e é
chamar colega para a conversa. As rotas novas são
`/link-de-formulario` e `/links-de-formulario`; a pública é
`/api/publico/convite/{bilhete}`.

🔴 **Falta o botão na tela da conversa.** A rota existe e exige login (`401`
conferido no ar). 🚨 **E ela não manda mensagem nenhuma, de propósito:**
devolve o link, e quem manda é a pessoa — mensagem ao cliente é irreversível.

**Provas:** `tests/teste_convite_de_formulario.py` **34**; a que mais importa
procura CNPJ, telefone, nome, sobrenome e e-mail **dentro da URL** e exige que
nenhum esteja lá. E o caminho inteiro **de fora**: convite real → rota pública
`200` com os 5 campos → página `200`; convite de teste apagado depois
(`formulario_convite` em **zero** linhas).

⚠️ **Dois erros meus, achados pelo vermelho e não pela leitura:** supus que
`MAPA["70"]` era o Suporte (é a **pesquisa CES**, sem telefone/e-mail/CNPJ), e
esqueci que o `TestClient` com `with` **fecha o pool** na saída — a limpeza de
depois do teste estourava e deixaria resíduo em produção.

**Placar:** Python **2.456 passaram, 3 ignorados, zero vermelho**; JS **855 em 46 arquivos**; build limpo com as
**9** conferências de CSS; migração **107** aplicada e serviço reiniciado.
📘 `Desktop\12112026.md` (seções 0, 1.6, 1.7, 1.8, 3.1 e a 6 corrigida) e
`docs/06_Historico.md` (décima e décima primeira voltas).


## ✅ 11/11, 10ª volta — A BARRA DE ETAPAS NO CARD, e a trava que era da HORA

🔵 Dele: *"siga com o que falta e documente tbm o que entregar"*. Dos 7 itens
que faltavam, **dois fecharam** e **um foi medido** (o que ele pediu que fosse
medido antes).

### 1. ✅ A barra interna de mudar etapa no card (item dele)

📏 **Medido antes:** existia um `<select>` de 190 px na faixa do card
(`DialogoDeChamado.vue`). Ele **movia** — então não era defeito, era o pedido:
com as **10 etapas do Financeiro**, a sequência ficava atrás de um clique e não
se via **onde o card está nela**.

**No ar:** barra de passos numerados abaixo da faixa, **uma linha que rola**
(`flex-wrap: nowrap` + `overflow-x: auto`). A faixa voltou a ser **medida** e
não controle; o `<select>` saiu (dois controles para o mesmo ato deixariam o
estado ambíguo).

🚨 **A etapa atual não é botão: é `<strong>` com `aria-current="step"`.** A
distinção é **estrutural**, não de cor — cor sozinha não é portador.
⚠️ **Card finalizado não mostra a barra** (reabrir primeiro é o gesto), mas a
faixa **continua dizendo** em que etapa ele parou.

**Travas:** `frontend/src/barra_etapa_1111.teste.js`, **8**. Elas olham
**estrutura**, não gesto — o jsdom não faz layout, e barra morta passaria verde
(foi o card inerte de 09/11, 22 travas verdes sobre tela morta).
**E a 9ª conferência de CSS publicado:** `.etapas` `nowrap` + `overflow-x:auto`
e `.etapas__passo--atual` existindo. 🚨 Só ela pega esta classe: com `wrap`, a
barra quebra em três fileiras e empurra o corpo do card fora da tela.
**Forjados e vermelhos:** `wrap` · sem `aria-current` · barra em card
finalizado.

### 1b. ⚠️ Uma colisão de nome de classe, achada no CSS publicado

🚨 A barra nasceu como `.etapas` — e `grep` no CSS publicado mostrou **duas**
regras `.etapas`, de componentes diferentes (`DisparosOperacao.vue` e
`ChecklistDeCards.vue` já usavam o nome, uma delas com `flex-direction:
column`). O `scoped` do Vue isola no navegador, mas a **9ª conferência lê o CSS
publicado como texto** e pegaria a primeira regra que casasse: passaria ou
reprovaria **por sorte da ordem do bundle**.

**Conserto:** `.trilha` / `.trilha__passo` / `.trilha__passo--atual`, nome
inexistente em qualquer lugar. 📏 Conferido no bundle: **uma** regra `.trilha`.
🟡 A lição é da conferência, não da classe: **trava que casa por texto precisa
de alvo único** — nome reusado em componente `scoped` não dá erro em lugar
nenhum e torna a trava um sorteio.

### 2. 🚨 CORREÇÃO DE UM DIAGNÓSTICO MEU: não era a ORDEM, era a HORA

🚨 Eu escrevi hoje que a suíte usa **`pytest-randomly`** e que o verde dependia
do sorteio da ordem. **Errado.** 📏 `pip list` no venv devolve **só `pytest`**,
e `--randomly-seed` é recusado como argumento desconhecido. **A ordem é
determinística.**

**O vermelho de verdade** era um só, e falhava **sozinho**:
`teste_agendamento::test_o_dia_traz_as_os_de_cada_compromisso`.

**Causa, medida às 21:21 BRT (00:21 UTC):** `agendamento.do_dia` compara
`a.inicio::date`, e o Postgres resolve o cast no **fuso da sessão**
(`America/Sao_Paulo`). O teste perguntava a data em **UTC** — das **21h à
meia-noite** a data UTC já virou e a do banco não. **Três horas de vermelho por
dia, verde nas outras vinte e uma.**

🔵 **A produção está certa:** quem chama `do_periodo` é a tela, e a data vem do
navegador, no mesmo fuso do banco; quem mexe com fuso no código (`presenca.py`)
escreve `AT TIME ZONE` explícito. O defeito era **só do teste**.

**Conserto:** o dia vem do **próprio banco**, com o mesmo cast da consulta
(`_dia_do_banco`) — não é fuso calculado à mão, e acompanha se a sessão mudar.
Mais uma trava que guarda o defeito, **forjada e vermelha** quando se volta a
perguntar em UTC.

⚠️ **Duas primas anotadas e não tocadas:** `teste_ligacoes_consulta.py:180` e
`teste_orcamento_consulta.py:347/351` também perguntam em UTC. Passam porque o
filtro é `< (%s::date + 1)` e a data à frente **alarga** a janela — passam por
tolerância, não por estarem certas.
⚠️ **E a trava do `teste_presenca`** que eu havia citado como dependente de
ordem: reprovou numa rodada de 16:34 e **não reproduz** — passa sozinha (58) e
passa nas duas metades. Fica **não reproduzida**, não explicada.

### 3. 📏 O Fechamento de Técnicos medido (ele pediu *"meça antes"*)

**Os cards de fechamento do FPSL hoje:** **6**, e **todos cancelados**; nenhum
em outro estado. **Dois técnicos** na vida (Franck 14262, Pedro Felipe 14316)
contra **191 técnicos reais** na tabela.

**O funil do dinheiro, com as regras do próprio `gerar_cartoes`:**

| filtro | OS | valor |
|---|---|---|
| OS no cache com valor de técnico (653939 + 6971) | 70 | **R$ 8.442,75** |
| … e na situação **15694** | 16 | R$ 2.271,60 |
| … e com técnico não-excluído na OS | 8 | R$ 1.413,70 |
| … e esse técnico na tabela `tecnicos` | 8 | R$ 1.413,70 |
| … e a OS com linha de **conferência** (o portão) | **5** | **R$ 860,70** |

🚨 **10% do dinheiro, e o buraco é do FUNIL, não da tela.** As duas maiores
perdas: exigir a **situação 15694** (70 → 16) e o técnico da OS ser **usuário
interno excluído**, como a Karla do Financeiro (16 → 8).
➡️ Espelhar no MoviZap hoje espelharia **6 cards cancelados e R$ 860,70**.
🟡 Proponho **consertar o funil no FPSL antes de espelhar**. 🔴 Decisão dele.

### 4. 🔴 O que o menu do chat esbarra, e é decisão dele

📏 Confirmado por varredura: o formulário público **não lê `URLSearchParams`**.
🚨 **E pré-preencher pela URL põe dado de cliente no endereço** — CNPJ e
telefone entram em log de servidor, histórico de navegador e em qualquer link
repassado. O caminho sem isso é a URL levar um **bilhete** e o servidor
devolver os valores; custa uma tabela. **Não construí: é decisão dele.**

**Placar depois de publicar:** Python **2.421 passaram, 3 ignorados, zero
vermelho** — na ordem natural, sem truque de ordenação. JS **855 em 46
arquivos**. Build limpo com as **9** conferências de CSS.
📘 `Desktop\12112026.md` (seções 1.6, 1.7, 3.1 e a correção da 6) e
`docs/06_Historico.md` ("décima volta").


## ✅ 11/11, 9ª volta — AS FILAS DO OP EM RELAÇÃO AOS DEMAIS PAINÉIS (migração 106)

🔵 Dele, nesta volta: *"não é nesse financeiro que deve nascer, como foi dito
essas etapas finais do OP devem ser excluídas e deveria ter nascido no painel
Financeiro, na etapa correta 'Nova solicitação'"* · *"fiz teste com form de
aditivo e não abriu card no contratual como foi pedido"* · *"e a correção das
filas do OP em relação aos demais paineis"* · *"vamos de 1 ao 6, da melhor
forma mais eficiente conforme a metodologia"*.

### 📏 Medido antes de escrever uma linha

| achado | número |
|---|---|
| passagens para 15746 / 15695 / 16492 no log, desde que ele existe | **zero** |
| a OS 17119 (ressarcimento, termo 8947) **nasceu** na coluna Financeiro do OP | — |
| cards criados pelo envio de aditivo dele (solicitação 3437) | **nenhum** |
| slugs no portão do card (`PROBLEMA_POR_FORMULARIO`) | **1** |
| `grep -c rolo PainelAba.vue` × `PainelOperacao.vue` | **0** × 4 |

🚨 **Ninguém moveu a 17119 — ela nasceu ali.** Eu era o suspeito, e o log
respondeu.

### ✅ Item 1 — a rolagem chegou às outras abas

Os dois controles (`BarraDeRolagem`, `RolagemDaBorda`) que a Operação tem desde
06/11 passaram a servir a `PainelAba`. 🚨 **O `ref` não pode se chamar
`quadro`:** naquela tela `quadro` já é o ref do JSON, e a colisão deixaria o
painel sem desenhar — sem o Vue reclamar.

### ✅ Item 2 — as três colunas saíram do OP e a OS nasce no painel certo

**A Operação tem 16 colunas** (14 do ERP + `Chamados` + `Serviço Realizado`).

| situação | agora nasce em |
|---|---|
| 15746 Financeiro | **PNL_1.4 › Nova solicitação** |
| 15695 Pós venda | **PNL_1.3 › Nova solicitação** |
| 16492 Contratual | 🔴 **PNL_1.5 › Elaborar contrato** |

🔴 **Duas decisões dele em aberto, e as duas mudam com UMA linha:**
1. o **Contratual não tem** "Nova solicitação" — as seis colunas que ele
   escreveu começam em *Elaborar contrato*, e inventar uma coluna ali seria
   mexer numa lista dele;
2. o bloco antigo dele dizia que o Financeiro viraria **`Cobrança de OS`** e que
   as outras duas seriam **excluídas**. A frase de hoje nomeia *"Nova
   solicitação"*, e eu segui a de hoje. ⚠️ E **reendereçei** as outras duas em
   vez de excluí-las: excluir sem destino faria a OS sumir de **todas** as
   telas. Voltar atrás é `recebe_situacao = NULL`, e aí elas passam a ser
   contadas em `fora_do_quadro`.

### ✅ Item 3 — o formulário diz onde o card dele nasce

`formulario.etapa_destino_id`. **O aditivo agora abre card no Contratual.**

🚨 **O defeito era conceitual:** o portão do **card** era o mapa de **problema do
Harmonit**. São coisas sem relação — card não precisa de OS, e a coluna
`Chamados` existe para isso desde 29/10.

⚠️ **O empate que a regra derivada errou:** o destino sai do `painel` de cada
formulário (a primeira etapa dele), e o Pós-venda tem **duas abas** — *"a
primeira por ordem"* entregou **CES e NPS** na fila de **Treinamentos**.
Pesquisa não é treinamento. Derivação com empate precisa de desempate
**nomeado**.

### 🚨 Dois defeitos que só a medição no estado real mostrou

1. **o card não mostrava a OS** — dizia *"Card 912"*, um número nosso que não
   serve para procurar nada no Harmonit. Entrou `numero_os`, chave **separada**
   do `numero_ordem` (é o nulo dele que mantém o card não-arrastável);
2. **a Operação dizia que as duas OS estavam "fora do quadro"** — não estão,
   estão em outro painel. Entrou a conta `noutro_painel`.

### Provas

Carga de travas nova (`teste_destino_do_card.py`, **19**) e 8 em JS. **Os
defeitos forjados ficam vermelhos:** situação reendereçada sem destino ·
aditivo sem destino · controle de rolagem na árvore com a `prop` nula.
Build limpo com as **8 conferências de CSS**.

### 🔴 O que falta dos seis, e o que cada um espera

| # | item | estado |
|---|---|---|
| 4 | menu no chat que abre formulário **pré-preenchido** | 📏 medido: **não existe nenhuma peça** — o público não lê `URLSearchParams`. É construir o pré-preenchimento + o menu |
| 5a | aviso de abertura por e-mail/WhatsApp | 🔴 **espera ele**: para quem vai |
| 5b | ressarcimento gerando card com **os dados do termo** como OBS | ⚠️ a ponte traz o **número** do termo (8947), não os dados — o resto é FPSL, que ele deixou por último |
| 6 | itens de checklist das 10 etapas · textos dos disparos | 🔴 **espera ele**: ele deixou as etapas em branco e vai colar os textos |


## ✅ 11/11, 8ª volta — O CLONE DO SAC ESTÁ NO AR (porta 8090), com os formulários nossos

🔵 Dele: *"a pagina SAC será refeita para cá, pois não vamos mais usar o bitrix"*,
*"subir o clone identico, com a diferença dos formularios novos endereçados no
paniel menu que abre lateralmente"*, *"todos os recursos devem ser iguais ao do
atual 100%"* e *"se precisar pode usar o root para subir uma porta e me de o IP do
site novo"*.

### ➡️ O endereço

    http://212.85.17.184:8090/

🚨 **É PRÉVIA NUMA PORTA, não publicação.** O `sac.movisat.com.br` continua
apontando para o **Bitrix24.Sites** até ele mandar virar o DNS. A porta foi aberta
no ufw com a nota *"fechar quando virar o DNS"*, e o host manda
`X-Robots-Tag: noindex, nofollow` — sem isso, um buscador acha o SAC duplicado e os
dois competem pelo mesmo conteúdo.

### O conteúdo NÃO foi transcrito à mão

Saiu do export que ele mandou (`sac_online.zip`, o backup do Bitrix): os 5 blocos,
as 10 imagens reais, os telefones, os títulos e o SEO campo a campo. Dois scripts
reproduzem o site inteiro, e ficaram em **`/home/claude/sac_clone_fonte/`** na VPS,
junto do próprio zip e do **`README.md`** que explica de onde cada byte veio.

### Os 8 cartões agora abrem o formulário NOSSO, numa gaveta lateral

7 dos 8 têm destino (`suporte`, `financeiro`, `administrativo`, `aditivo`,
`substituicao-veiculos`, `rescisao`), e o 1º (*Tutorial de ajuda do sistema*)
continua **EM BREVE**, como hoje.

🔴 **O cartão 8 — *Ideias e sugestões* — espera decisão dele.** O formulário Bitrix
**38** é o **único dos 8 que nunca reconstruímos**. Hoje aponta para o Suporte,
provisório. As duas saídas: **16º formulário próprio** (os 11 campos estão no
`loader_38.js`, que é público) ou **ficar no Suporte** com o tipo já marcado como
sugestão.

### 🚨 Por que este host proxeia os formulários em vez de apontar para o `forms`

O `forms.movisat.com.br` manda **`X-Frame-Options: DENY`**, e está **certo** que
mande: formulário com CNPJ e telefone não deve ser embutível por ninguém. A gaveta
precisa embutir. **Afrouxar o `forms` para `SAMEORIGIN` resolveria aqui e abriria o
formulário para ser embutido por qualquer página daquele domínio** — e não é lá que
a decisão pertence.

Então **este** server serve os mesmos três caminhos (`/f/`, `/pub/assets/`,
`/api/publico/`) por proxy para `127.0.0.1:8008`, e só no `/f/` **dele** o cabeçalho
é `SAMEORIGIN`.

✅ **Conferido depois de subir:** `forms.movisat.com.br/f/suporte` continua
respondendo **`x-frame-options: DENY`** — nada foi tocado lá.
✅ **E o formulário aguenta ser embutido:** o bundle não cita host absoluto, não usa
`window.top`/`window.parent` e só chama `/api/publico/*` relativo.
⚠️ **Tem de ficar dito:** um envio pela gaveta chega ao **mesmo** FastAPI, grava na
**mesma** tabela e gera o **mesmo** card. Não existe formulário "do clone".

### 🔴 O que o site atual carrega e o clone NÃO — três decisões dele

Estão todos no descritor do export, e nenhum é esquecimento:

| no site atual | o que é | por que não entrou |
|---|---|---|
| `G-285410104` | Google Analytics 4 | manda o comportamento de cada visitante para o Google |
| `GTM-K2K878L` | Google Tag Manager | o mesmo, e carrega o que estiver configurado **lá**, fora da nossa vista |
| `loader_2_36awoa.js` | **o widget de chat do Bitrix24** | 🚨 é o Bitrix, de quem ele quer sair |

⚠️ **O widget tem um detalhe a mais:** ele é a porta de atendimento ao vivo do site
hoje. Se sair e nada entrar no lugar, quem quer falar agora só tem os dois 0800. Os
três voltam em uma linha cada, se ele quiser.

### Os seis erros meus que a conferência contra o export achou

🚨 **Nenhum apareceria olhando a tela** — todos saíram de comparar o que eu escrevi
com o que o export diz:

1. **5 redes sociais escritas de cabeça**, em ordem inventada; o pé tem **6**
   (Facebook, Instagram, LinkedIn, YouTube, Twitter, Telegram).
2. **Dois links que eu inventei no pé** (*Blog* e *Base de conhecimento*): não
   existem no site atual.
3. **A `og:image` errada** — eu mandava a logo de 444×110; o site manda o arquivo
   4660 (`Movisat-Black@1x.png`, 2400×826).
4. **O favicon** — eu quase subi um `favicon.ico` que daria 404 em toda visita.
   `grep favicon` no export não acha nada porque **o binário não vem no export**: o
   id está no descritor e o arquivo não. Baixado do site no ar.
5. **O SEO estava fixo no meu script.** Confere com o site — mas *conferir* não é
   *sair do export*, e um export novo com outro título seria clonado errado e calado.
6. **Um seletor CSS que nunca casaria:** eu escondia o botão de voltar ao topo com
   `~ .ao-topo`, e o `~` só alcança irmão **posterior** — o botão vem antes da
   gaveta. ⚠️ O defeito só apareceria **com a gaveta aberta**, o único momento em que
   importa.

✅ **E o que o export me fez acrescentar:** o botão de **voltar ao topo**
(`UP_SHOW = "Y"`), que o site atual tem e eu havia esquecido.

### 🚨 A lição: são DOIS `page_*.json`, e só um é a página

O export traz também o **descritor do site**, sem `BLOCKS`, com o domínio, o favicon
e os contadores. **Escolher "o único" dá erro; escolher o primeiro pegaria o
descritor calado** — o script escolhe **quem tem blocos**. Foi esse guarda que me fez
abrir o segundo arquivo e achar o favicon, o GA4, o GTM e o widget do Bitrix, que eu
teria perdido inteiros.

### Provado de fora da VPS

`/` · as 11 imagens · `/f/suporte`, `/f/financeiro`, `/f/rescisao` ·
`/api/publico/formulario/suporte` — todos **200**. E o que não deve existir responde
**404**: `/api/solicitacoes` (a superfície autenticada) e `/index.html.bak`.

🔴 **Falta ele olhar** (`M9`): abrir o IP, clicar num cartão e ver a gaveta com o
formulário dentro. Não enviei nada pelo clone de propósito — envio gera card de
verdade.

---

## ✅ 11/11, 7ª volta — quanto tempo a OS leva, o nome na frase, e o SAC medido

### 📏 A resposta do item 1 dele, medida no código e ao vivo

🔵 *"Validar se as OS abertas já chegam ao painel, demora quanto tempo depois que
ela é criada? Se mudarem o status dela, antes dela aparecer aqui, já aparece na
coluna certa? não aparece em nenhuma?"*

| pergunta | resposta medida |
|---|---|
| **quanto tempo** | **até 5 minutos** (`INTERVALO_SCAN = 300`). Ao vivo: checkpoint **17119**, última OS nova detectada **12:30 local** |
| **se o status mudar antes de aparecer** | ✅ **aparece na coluna CERTA** — a varredura lê a OS no instante em que chega nela e grava a `situacao_id` daquele momento |
| **não aparece em nenhuma?** | **sim, em dois casos**: `data_previsao` anterior à data matriz (hoje **10/11**), e situação fora das 17 (cai em `fora_do_quadro`, contado e não exibido) |

🚨 **MAS O INVERSO É O PROBLEMA DE VERDADE, e ele não perguntou — eu achei
medindo:** se mudarem o status de uma OS **que já está no cache**, direto no
Harmonit, **o painel não vê**. A varredura só lê números **NOVOS** (anda de
`checkpoint+1` para cima). Quem relê OS existente é o **resync: a cada 12
HORAS**, e só as **400 últimas por número**.
➡️ **Mudança feita fora do MoviZap leva até 12 h para refletir** — e OS fora das
400 últimas, nunca.
✅ **Exceção:** mover pelo painel atualiza o cache na hora
(`os_ponte.py:1541-1553`).

⚠️ **E a varredura PARA depois de 10 buracos consecutivos** (`LIMITE_BURACOS`):
se o Harmonit pular mais de 10 números, a OS nova não é achada até alguém rodar
o `/varrer` manual com `desde`.

🔴 **Isto é decisão dele:** encurtar o resync (12 h é muito para quem mexe no
ERP direto), ou aceitar que a verdade do painel é o que passa pelo painel.

### ✅ O aviso de conflito diz o NOME da etapa, entre aspas

🔵 *"ajustar para aparecer o nome das etapas entre \" \" ao invés do numero,
somente nesse aviso"*.

Antes: *"a OS 17118 esta na situacao 890 no Harmonit, e a tela carregou 38"*.
Agora: *"a OS 17118 esta em \"Agendar serviço\" no Harmonit, e a tela carregou
\"Novo Solicitação 1ª\""*.

🚨 **O nome sai do catálogo que já existia** no próprio arquivo
(`_SITUACOES_DO_PAINEL`): uma segunda lista divergiria na primeira renomeação — e
as etapas **já foram renomeadas uma vez** (30/10).
⚠️ **Situação desconhecida cai no número**, nunca num rótulo inventado: este
aviso dispara justamente quando a OS está onde a tela não esperava, e isso inclui
situação fora das 17. **5 travas novas** no FPSL, com o defeito forjado.
⚠️ E a fixture do MoviZap que repetia a frase antiga virou **irreal** e foi
atualizada — fixture irreal faz a trava passar sobre o que o servidor não diz
mais.
**FPSL reiniciado**, ponte respondendo 200.

### 🚨 O SAC: o site NÃO está na nossa VPS

📘 **`Desktop\SAC_Clone_PREPARO.md`** — medido, nada executado.

`sac.movisat.com.br` → **`lb.bitrix24.site` (18.208.124.7)**,
`x-powered-cms: Bitrix24.Sites`. Então o clone **não é copiar pasta**: é
reconstruir uma página servida por plataforma de terceiro — a mesma travessia dos
formulários.

**É UMA PÁGINA SÓ:** `sitemap.xml` dá **404**, não há link interno para outra
página, 58 KB de HTML. Dois telefones clicáveis no topo, o título *SAC ONLINE*,
um cartão **"Tutorial de ajuda do sistema" marcado EM BREVE** que não leva a
nada, **7 cartões de ação** e o pé com blog, base de conhecimento e 5 redes.

🚨 **OS 7 CARTÕES BATEM COM O NOSSO `bitrix_id` — o mapa não é suposição:**
32→`suporte` · 34→`financeiro` · 36→`administrativo` · 14→`aditivo` ·
16→`substituicao-veiculos` · 10→`rescisao` · e **38→NADA**.

🔴 **O buraco: o formulário 38 ("Ideias e Sugestões") nunca foi reconstruído** —
não está entre os 15. Li o `loader_38.js` (público): 11 campos.
🟡 **E há caminho sem formulário novo:** o nosso `suporte` já tem
`tipo-de-solicitacao` com a opção **`sugestao`**. Decisão dele.

⚠️ **O "menu lateral" é o que o site JÁ faz** — o Bitrix abre o formulário em
painel lateral, e é por isso que os cartões têm `href="#"`. A diferença do clone
é **o que abre**, não o comportamento. 🔴 Três formas no PREPARO; recomendo o
`iframe` em gaveta, **com a ressalva** de que o `forms.movisat.com.br` hoje não
permite ser enquadrado — liberar para **um** domínio é uma linha de nginx.

🚨 **Duas coisas que a palavra "100%" esconde:** o `og:image` atual aponta para o
**CDN do Bitrix** (clonar ao pé da letra mantém o site novo dependente deles), e
o `robots.txt` atual barra `/pub/site/*` e `/preview/*`, **caminhos do Bitrix que
não existirão no nosso**. As duas são decisão dele.
⚠️ **E o certificado só sai depois do DNS** (o Let's Encrypt prova posse pelo
domínio), então o IP fechado é HTTP — aceitável porque a página não tem login nem
dado pessoal, e os formulários continuam no `forms`, que é HTTPS.
🚨 **DNS é gesto dele**, na Hostinger.

**Suítes: 2361 Python · 839 JS · FPSL 67 nas duas da ponte. Zero vermelho.**

### 🔴 O que espera ele agora

1. **As ETAPAS de cada formulário** (o agrupamento dos campos) — o passo que
   falta para o formato novo, e é escolha de quem conhece o atendimento.
2. **O 7º cartão do SAC**: 16º formulário, ou Suporte com o tipo `sugestao`?
3. **Como o formulário abre no clone**: gaveta com `iframe` (e liberar o
   enquadramento para um domínio), ou levar para o `forms`?
4. **O cartão "EM BREVE"** entra no clone como está, ou sai?
5. **O `og:image` e o `robots.txt`**: idênticos ao Bitrix, ou nossos?
6. **O resync de 12 h**: encurtar?


## ✅ 11/11, 6ª volta — a VALIDAÇÃO dos 14 formulários, e dois achados

### ✅ 60 campos validados, de 5 (migrações 103 e 104)

🔵 Ele: *"o formulario suporte é a base, os erros de bitrix ficam para tras, ja
temos validações uteis no suporte"*.

📏 **Era 5 (só o Suporte) e agora são 60**, nos 15 formulários: 17 telefone · 16
e-mail · 13 CNPJ · 10 CPF · 3 placa · 1 CEP.
✅ **Já está no ar** — é dado, não código: a rota pública já entrega `validacao`
ao navegador, e o mesmo `CamposDoFormulario` serve os dois formatos. Conferido
na `ficha-cadastral` ao vivo.

🚨 **POR LISTA EXPLÍCITA, NUNCA POR `LIKE` — e isto tem prova:** um
`LIKE '%cnpj%'` pegaria o campo **"CNPJ e Nome da Empresa que será
transferida"**, que pede as duas coisas na mesma caixa, e passaria a **recusar a
resposta certa**. É a mesma armadilha do *"Veículo e Placa"* do Suporte. Há
trava com o defeito forjado.

⚠️ **O que NÃO ganhou validação, e por quê:** o `rg` (não há dígito verificador
padrão — cada estado emite o seu) · o campo de dois dados acima · `website` (não
há regra de URL no catálogo, e inventar recusaria `movisat.com.br` sem
`https://`) · as datas (o campo é `date`) · os `list` (valor de lista fechada).

🚨 **A migração 104 é um ERRO DO BITRIX que o servidor não via:**
`e-mail-do-novo-titular` e `telefone-com-ddd-do-novo-titular` vinham como
**`string`**, e o servidor decide e-mail/telefone pelo **`tipo`** — então a
validação deles ficaria **só no navegador**, no campo que identifica quem passa a
ser **dono do contrato**. Agora têm o tipo certo, e com ele o teclado e a máscara
do celular.

🔴 **E uma régua que continua sendo dele:** o servidor confere o **FORMATO**
(quantidade de caracteres), **não o dígito verificador** — está escrito em
`formularios.py` que mudar isso *"é mudança de régua, e régua é decisão dele"*.
Há trava fixando o estado atual, para a mudança ser deliberada.

### 🚨 EU ERREI SOBRE MOBILE, E CORRIJO

**O PREPARO de ontem dizia que faltava mobile. NÃO FALTA.** Eu procurei a string
`16px` dentro do `FormularioPublico.vue`, não achei, e concluí que o piso não
existia.

📏 **A verdade, medida:** o piso é um **token próprio** — `--txt-campo: 16px`,
criado exatamente porque *"abaixo de 16px o iOS dá zoom"* —, a `.campo__entrada`
o usa, e o `publico/main.js` **importa** o `componentes.css`. O alvo de toque de
44px também está lá. A lista da frota já trunca o apelido e preserva a placa, e a
linha do repetidor já encolhe sem transbordar.

➡️ **Não havia defeito de mobile.** O que havia era **um comentário que mentia**:
o `.linha` dizia *"No celular a linha EMPILHA"* e ela não empilha — encolhe. Não
há `@media` nem `flex-wrap` ali, e nunca houve. Corrigido (`M12`).
⚠️ **O que sobra de mobile é teste de USO:** abrir os formulários no celular.

### ✅ O "situação 38 no Harmonit" — achado e tirado

🔵 Ele: *"no painel da OP, voltou a aparecr generico"*.
`PainelOperacao.vue:1257` escrevia **"situação N no Harmonit"** dentro de **toda
coluna aberta**. É a **quarta vez** que ele tira texto didático da tela.
⚠️ **O dado não se perde:** `coluna.situacao_id` continua vindo na rota, e é ele
que o arrasto usa.

🚨 **Duas travas liam aquela frase, e uma delas DIZIA QUE MEDIA O CARD** — o
comentário afirmava *"E o número da situação, no card"*, mas o texto vinha da
coluna. Comentário de trava que descreve o alvo errado faz consertar o lugar
errado. As duas foram retargetadas para medir **estrutura**.

### ✅ A 8ª conferência de CSS, nascida do meu defeito de hoje

🚨 **A `.pilula` é scoped por componente** (não existe em `estilo/*.css`), e eu
publiquei a `ChecklistDeCards` com os selos **sem estilo**. A 8ª conferência
afirma: **todo escopo que declara uma VARIANTE de `.pilula` declara a base no
mesmo escopo**. Defeito forjado no CSS publicado e **pego**.
⚠️ Na primeira tentativa forjei num escopo **sem** variante e a conferência
(corretamente) não reclamou — a segunda, no escopo certo, acusou.

**Suítes: 2361 Python · 839 JS em 44 arquivos. Zero vermelho.**

### 🔴 O próximo passo precisa dele

**As ETAPAS de cada formulário** (`formulario.formato = 'novo'` +
`formulario.etapas`): o agrupamento dos campos em etapas é escolha de quem
conhece o atendimento. Posso propor um por formulário; **quem aprova é ele**.
📘 `Desktop\Formularios_Padronizacao_PREPARO.md`


## ✅ 11/11, 5ª volta — os DISPAROS no ar (desligados), e o preparo dos formulários

### `CFG_16.1 Disparos Operação` — migração 102

🚨 **É A PRIMEIRA COISA DO PAINEL QUE FALA COM O CLIENTE SOZINHA**, e isso
afrouxa — por decisão dele — a régua da ÁREA F de 04/11 (*"confirmação antes de
enviar, sempre"*). **No ar e 100% desligado:** 17 etapas, **0 ligadas, 0 com
texto**, como ele pediu (*"nasce em branco e com interruptor desligado ainda"*).

**As cinco guardas que ficaram no lugar da confirmação:**

1. **o banco não deixa ligar vazia** (`CHECK etapa_mensagem_ligada_tem_texto`) —
   nem pela tela, nem por `UPDATE` à mão;
2. **só whatsapp** (CHECK), e e-mail exige migração;
3. **só ao cliente**: o destinatário é **derivado** da OS, não escolhido — não
   existe caminho no código para outro alguém. A tela traz a nota que ele pediu:
   *"Nenhuma destas mensagens vai ao técnico."*;
4. **só dispara se o ERP aceitou**, e **falhar não desfaz o mover** — o motivo da
   falha vira observação do sistema no card;
5. **só canal de ATENDIMENTO**: o informativo é de campanha e mostraria o número
   errado ao cliente.

⚠️ **O envio passa pelo `conversas.iniciar_conversa`**, nunca pelo `evolution`
cru — ele confere se o número tem WhatsApp, reusa a conversa aberta e **grava a
mensagem**. A trava disso mede `__code__.co_names`, não texto.

🔴 **NENHUM TEXTO FOI SEMEADO, e preciso dizer por quê:** o texto que ele passou
em 04/11 **não sobreviveu em documento nenhum** — do bloco daquele dia restaram
só as três variáveis (`{{Contato: Primeiro nome}}`, `{{Nome}}`,
`{{Código de envio/acompanhamento transporte}}`). Semear um texto inventado seria
pôr palavra dele na boca do sistema. Ele disse *"depois colo"*.

**Travas: 25 de backend + 14 de tela.** Três defeitos forjados e pegos: o disparo
saindo desligado, o mover disparando com o ERP recusando, e variável desconhecida
saindo crua.

**Suítes: 2346 Python · 839 JS em 44 arquivos. Zero vermelho.**

### 🚨 Quatro defeitos meus nesta volta

1. **Meu guard de idempotência deu falso positivo de novo** — conferi
   `"CFG_16.1" in telas.py` e a string já existia **num comentário de reserva**
   que eu mesmo escrevi de manhã. A entrada não entrou e eu só vi pelo teste.
   ⚠️ **É o erro de 06/11, repetido:** guard compara **o que seria
   acrescentado**, nunca a âncora.
2. 🚨 **A `.pilula` é SCOPED POR COMPONENTE nesta casa** — ela não existe em
   `estilo/*.css`. A `ChecklistDeCards` subiu com os selos **sem estilo nenhum**:
   não quebra, não avisa, só fica feio. ⚠️ Nenhuma trava de tela pega isso,
   porque o jsdom não faz layout. Corrigido nas duas telas novas.
3. **Varri o arquivo inteiro procurando "evolution" e a trava reprovou por causa
   do docstring que explica a regra** — **terceira vez no mesmo dia**. Agora ela
   mede `__code__.co_names`, que é estrutura, não texto.
4. **O shell local comeu as crases** de um bloco de DDL num `ssh "..."` — o doc
   subiu sem o bloco. Reposto por arquivo. ⚠️ A regra de heredoc por ssh vale
   para crase também, e não só para acento.

### 🔵 O preparo dos formulários — MEDIDO, nada executado

📘 **`Desktop\Formularios_Padronizacao_PREPARO.md`**

🚨 **A descoberta que muda o tamanho do trabalho: o formato é DADO, não código.**
`formulario.formato` é **`novo` só no Suporte** e `classico` nos outros 14;
`formulario.etapas` (JSONB) existe **só nele**.

🚨 **E são 14 formulários com 215 campos e ZERO validação declarada** — hoje eles
aceitam CNPJ inválido, telefone de 3 dígitos e e-mail sem arroba. É o buraco do
Bitrix que a casa catalogou (*"o servidor deles não valida obrigatório"*):
herdamos a definição e herdamos o buraco.

📏 **Mobile:** `CamposDoFormulario.vue` tem **zero** `@media` e o público não
declara **nenhum** `16px` — e a régua da casa é *"campos 16px, abaixo disso o iOS
dá zoom"*.

📏 **O mapa dele:** `formulario.painel` já existe desde a migração 075, e **3 dos
12 mudam de painel**. O que **não** existe é a **etapa de destino** — hoje o
painel sabe qual é, não onde o card nasce.
✅ **`gera_os` é `false` nos 15**, então os cards já nascem **livres de OS**, que
é o que ele pediu.

🔴 **O que travaria o passo 3 (etapas por formulário): o agrupamento é escolha de
quem conhece o atendimento.** Posso propor um por formulário; quem aprova é ele.


## ✅ 11/11, 4ª volta — a `CFG_17.1 Checklist de Cards` NO AR

🔵 Sugestão minha que ele aceitou, e ele fixou a régua: *"sim, toda tela nova
nasce somente owner"*.

🚨 **A DESCOBERTA: as rotas de modelo do checklist estavam no ar desde 04/11 SEM
PORTA E SEM TRAVA.** `grep checklist/modelo tests/` dava **zero**, e não havia
tela — acrescentar item na lista de uma etapa só era possível escrevendo
migração. ⚠️ **Código no ar sem porta e sem trava é pior que código ausente:
parece pronto.**

| o quê | onde |
|---|---|
| a aba, só owner | `CFG_17.1`, 5 pontas (registro, rota, mapa, ORDEM, títulos) |
| a leitura: **as 17 etapas, inclusive as vazias** | `GET /api/config/checklist-de-cards` |
| a escrita passou de `CFG_7.1` para `CFG_17.1` | `POST`/`PUT .../checklist/modelo` |
| a tela | `frontend/src/telas/ChecklistDeCards.vue` |

**Travas novas: 13 de rota/regra + 16 de tela**, as primeiras que essas rotas
têm. Defeito forjado nas duas pontas: a permissão voltando para a Geral deixa 1
vermelha; esconder o item desativado deixa 4.

**Suítes: 2318 Python · 825 JS em 43 arquivos. Zero vermelho.**

🚨 **Dois textos meus que mentiam, pegos pelas travas novas:** o docstring da
rota ainda dizia *"a permissão é a da Geral (`CFG_7.1`)"* depois de eu mudá-la; e
a minha própria trava media `tela.text()` procurando o texto do item, que **mora
no valor do input** — ela reprovava sozinha.

🔵 **E cortei o parágrafo didático da tela antes de publicar:** a régua da casa é
que a tela diga o ESTADO, e ele já tirou texto explicativo três vezes. Ficou uma
linha: *"N de 17 etapas com lista · vale para os próximos cards"*.

### 🔴 O próximo, na ordem dele

1. **`CFG_16.1 Disparos Operação`** (código reservado, e há trava provando que
   segue livre) — campo por etapa nascendo **em branco e desligado**, só-owner,
   *"por hora só whatsapp"*, **só ao cliente**, com nota dizendo que **nenhuma
   vai ao técnico**.
2. **Etapa `Serviço Realizado`** — nossa; ao **sair** dela é que escreve 15694.
3. **Os formulários** (design, validação, disposição, **mobile**) + o **menu de
   passar o mouse** que abre o formulário já preenchido, **para todos**.
4. **As 3 colunas saindo do Operação.** 🚨 Mexe na tupla `SITUACOES`.
5. **FPSL por último**, por decisão dele.


## ✅ 11/11, 3ª volta — o "nome errado" achado, e a DATA MATRIZ em 10/11

### 🚨 O nome errado era um `h1` ESCRITO À MÃO

🔵 *"Pipeline Financeiro e Contratual com nomes errados"* · *"deve condizer com
o tipo da Aba"*.

`frontend/src/telas/PainelAba.vue:198` tinha **`<h1>Pós-venda</h1>` literal**. O
Financeiro e o Contratual usam **o mesmo componente** (as colunas vivem no
banco, não no código), então as duas telas de 06/11 abriam dizendo
**"Pós-venda"**. Agora o título vem do `meta.titulo` da rota, que já existia e já
estava certo nas três.

⚠️ **E NENHUMA TRAVA PEGAVA porque nenhuma afirmava o título:** as nove travas
das abas mediam colunas, permissão e rotas. **O cabeçalho não estava no
contrato, e o que não está no contrato ninguém defende.** São 4 travas novas, e
o defeito forjado deixa 2 vermelhas.

### ✅ A data matriz do painel: 24/10 → **10/11/2026**

🔵 *"atualize a data inicial do sync dos paineis do movizap para 10/11/2026 o que
for antes disso não vai trazer, o que ja tiver pode guardar ocultado em contexto
somente"*.

📏 **O tamanho disso, medido pelo quadro: 60 cards → 6.**
⚠️ **Eu errei a primeira medição** — li pela ponte e deu "6 em ambas"; a ponte
responde outra coisa. **O número honesto é o do `paineis.quadro`.**

🚨 **NADA FOI APAGADO:** a data matriz é **filtro de leitura**. A OS anterior
continua no cache do FPSL e no nosso banco, e volta no dia em que ele recuar a
data — é o *"guardar ocultado em contexto somente"*.
⚠️ **O card de CHAMADO não depende dela** (vem da `pipeline_card`, não da
ponte): os chamados de antes de 10/11 continuam na coluna `Chamados`.

### 🔍 Um achado de brinde: a suíte escreveu na `config` de produção

A linha `painel_operacao_desde` estava com **`descricao = 'zz teste'`** — marca
que um teste deixou na linha de produção. Corrigida junto. ⚠️ **Teste que
escreve em `config` tem de devolver a `descricao`, não só o valor.**

### 🔴 O que falta, e NADA está bloqueado

1. **`CFG_17.1 Checklist de Cards`** e **`CFG_16.1 Disparos Operação`** — as duas
   só-owner (*"toda tela nova nasce somente owner"*), a de Disparos com campo por
   etapa nascendo **em branco e desligado**, *"por hora só whatsapp"*, **só ao
   cliente**, com nota dizendo que **nenhuma vai ao técnico**.
2. **Etapa `Serviço Realizado`** — nossa; ao **sair** dela é que escreve 15694.
3. **O aviso de abertura** é **selo no painel** (resposta 3 dele), e a nota
   interna segue o molde do botão *"abrir conversa"*: joga o número no filtro, e
   **sem conversa ele inicia ali mesmo**.
4. **Ressarcimento** — 🔵 *"esse tipo especificamente, gera um card de chamado
   tbm, com a OBS dos dados do termo"*. Isto é NOVO: a OS financeira continua
   nascendo em 15746 **e** passa a abrir um card de chamado.
5. 🔴 **Os FORMULÁRIOS: design, validação, disposição e MOBILE** — 🔵 ele
   perguntou em 11/11 e a resposta é **não começou**. Só o Suporte tem o formato
   novo. Entra o **menu de passar o mouse** (*"igual ao 'iniciar do windows'"*)
   que abre o formulário **já preenchido** dentro do chat, **para todos**.
6. **As 3 colunas saindo do Operação** (`Financeiro` vira `Cobrança de OS` no
   painel Financeiro; `Pós venda` e `Contratual` **excluídas**, 🔵 *"pois ja tem
   o pipeline delas"*), com **regra de transição** só nessa coluna (🔵 *"sim"*) e
   escrevendo **só no nosso banco** (🔵 *"somente nosso banco"*).
   🚨 Mexe na tupla `SITUACOES`, que tem travas afirmando 17.
7. **FPSL por último**, por decisão dele: *"meça antes, deixe coisas do FPSL para
   o final pois depois vou dar mais contexto"*.


## ✅ 11/11, 2ª volta — ELE RESPONDEU AS 23; SEIS JÁ ESTÃO NO AR (mig. 100 e 101)

📘 Detalhe na VPS: `docs/02` (migração 101) e `docs/06` ("11/11, segunda volta").

🎉 **A SUÍTE DO MOVIZAP FICOU 100% VERDE: 2303 Python, ZERO vermelho** (e 805 JS
em 42 arquivos). O único vermelho conhecido era o `teste_cadastro`, e era **dado**
— caiu com a decisão 22 dele.

| o quê | resposta dele |
|---|---|
| **teto da ficha 4 s → 20 s**, e a frase deixou de culpar o FPSL | 4: *"sim, pode fazer"* |
| **apagar observação**: qualquer pessoa com o painel, sem prazo, autoria visível | 1, 2, 3 |
| **Solicitações (`FRM_1.1`) passou a ser só do owner** | 20, 21 |
| **"Solicitação" → "Nova solicitação"** nas abas de Pós-venda (mig. 100) | do bloco novo |
| **o número de teste voltou a ter um dono só** | 22 |
| `Disparos Operação` e `Checklist de Cards` como abas de `/config` só-owner | 8, 9, 12 — **ainda não construídas** |

### 🚨 O que a decisão 22 exigiu medir antes de tocar

O contato **91041** é o que tem a **ficha de técnico com os 6 preços** de 04/11 —
ficou. O **198394** (*"Iago Do Ó"*, mesmo cliente Velasco, sem ficha, sem preço)
saiu. 🚨 **O que resolve é tirar o TELEFONE, não o `ativo`:** o
`cadastro.por_telefone` **não filtra por `ativo`**, então inativar sozinho
deixaria o número ambíguo para quem atende. O contato **não foi apagado**, e a
linha de volta está no log da operação.
⚠️ **Dito:** a conversa que aponta para o 198394 continua lá; mensagem **nova**
daquele número resolve para o 91041. Juntar as duas é gesto dele.

### 🚨 Os três defeitos meus desta volta, todos pegos pela própria suíte

1. **Quebrei um bloco de comentário** do `passagem.py` (troquei texto dentro de
   um bloco `#` por linhas sem `#`). Pego pelo `py_compile`.
2. **Importar a sessão derrubou 4 suítes na COLETA** — os mocks de
   `api/cliente.js` daqueles arquivos não declaravam
   `quandoPerderSessao`/`definirToken`/`temToken`. ⚠️ **O molde já existia** no
   `abas_do_painel_0611.teste.js` desde 06/11, e eu repeti o buraco em quatro
   arquivos.
3. 🚨 **`atendente.owner` é coluna GERADA** (`perfil = 'owner'`, mig. 025): minha
   fixture tentava `SET owner = true` e as 15 travas novas caíram no setup.
   **Quem faz alguém owner é o PERFIL.**

### 🔴 O que falta do que ele JÁ decidiu (nada bloqueado)

1. **`CFG_16.1 Disparos Operação`** — campo por etapa, **nasce em branco e
   desligado**, tela só-owner; *"por hora só whatsapp"*; **só ao cliente**, com
   nota na tela dizendo que **nenhuma vai ao técnico**.
2. **`CFG_17.1 Checklist de Cards`** — 🔵 *"boa sugestão, pode fazer uma outra aba
   só para isso"*, para centralizar os fixos. Hoje as rotas de modelo existem e
   **não há tela**.
3. **A etapa `Serviço Realizado`** — nossa, entre 1316 e 15694; ao **sair** dela
   é que escreve 15694 no Harmonit. 🔵 *"moverão para la e depois auditarão o
   card e por fim, atendimento finalizado"*.
4. **O aviso de abertura de chamado é INTERNO** (respostas 5, 6, 7): *"É como se
   operadora recebesse mensagem do cliente, pois a nota é interna"*, e vai *"para
   as pessoas que estiverem na conversa"*. 🚨 **Não é e-mail nem WhatsApp ao
   cliente** — é nota interna.
5. **O mapa de etapa inicial por tipo de termo** (respostas 17, 18, 19): OP vai
   para *Pendente Ação Movisat*, **as financeiras vão para o Financeiro**;
   substituição em **ambas** as OS; rescisão com aviso prévio usa o prazo
   **concedido**, `dias − 1`.
6. **Tirar os passos da `Solução Técnica`** — depois de ele validar o checklist
   no card.

### 🔴 E o bloco NOVO que ele colou (ainda não medido)

Formulários padronizados pelo molde do Suporte (estilo, validação, mobile) e
**pré-preenchidos quando abertos pelo botão dentro do chat**; o mapa de **10
formulários → coluna de destino**; as colunas `Financeiro`/`Pós venda`/
`Contratual` **saindo do painel Operação** (as duas últimas excluídas, e o
Financeiro virando a coluna **`Cobrança de OS`** dentro do painel Financeiro); a
aba nova do Financeiro **espelhando o Fechamento de Técnicos do FPSL**; a barra
interna de mudar etapa nos cards dessas etapas; e a rolagem do Operação aplicada
nos outros painéis.
🚨 **Tirar as 3 colunas do Operação mexe na tupla `SITUACOES`, que tem travas
afirmando 17** — é a peça mais delicada do bloco.


## ✅ 11/11 — PAINEL DA OPERAÇÃO: 7 frentes no ar, migrações 098 e 099

🔵 Origem: o bloco que ele colou em 11/11, depois de exercitar o painel em 09/11.
📘 **Plano com as 16 áreas medidas:** `.claude\plans\pasted-content-id-f654-formulario-de-modular-neumann.md`.
📘 Detalhe na VPS: `docs/02` (`os_campo_da_etapa`) e `docs/06` ("11/11").

**Suítes medidas depois de publicar:** MoviZap **2283** Python (de 2195 em 06/11) e
**797** JS em 42 arquivos (de 741). O único vermelho é o `teste_cadastro`, e é **DADO**.
**As 7 conferências do CSS publicado passaram** (a 7ª é nova).
Migração 098 aplicada 06:45 · 099 às 06:53 · serviço reiniciado · build com as 7 conferências.

| # | o quê | onde |
|---|---|---|
| 1 | **o card de chamado nascia inerte** — defeito | `PainelOperacao.vue` |
| 2 | diálogo do checklist: frase fora, 22rem, botão no centro | `PainelOperacao.vue` + 7ª conferência |
| 3 | ✓ verde e ✗ vermelho na OBS do checklist | `BalaoDeRecado.vue` |
| 4 | placa com hífen no padrão Mercosul + o texto dele | `validacao_campo.js`, `CamposDoFormulario.vue` |
| 5 | **o motivo do 400 passa a ir ao log** | `main.py` (handler do `DadoInvalido`) |
| 6 | itens de checklist de 4 etapas novas | migração **098** |
| 7 | contador de etapa do chamado + **prazo de 24 h úteis** | `movizap/horas_uteis.py`, `pipeline.py`, `paineis.py` |
| 8 | campos **Rastreamento** e **Devolução** | migração **099**, `movizap/campo_etapa.py` |

### 🚨 Os cinco achados desta volta

1. **O card de chamado estava INERTE na tela com 22 travas verdes.** A causa era
   `null === null`: `movendo` nasce nulo e todo card de chamado tem `numero_ordem`
   nulo, então `.card--movendo` — que é `opacity: .55` **mais
   `pointer-events: none`** — entrava desde a montagem.
   ⚠️ **As travas não viram porque o jsdom não faz layout e `pointer-events: none`
   não impede `dispatchEvent`.** Teste que clica passa com o card morto. As travas
   novas olham a **classe**.
2. **O contador de tempo de etapa do chamado estava morto por construção**: a tela
   tinha o contador desde o Bloco D e o backend mandava `etapa_desde: None` **fixo**.
   Todo card de chamado dizia literalmente `não medido`. O dado sempre existiu na
   `pipeline_passagem`.
3. 🚨 **A frase de recusa do 400 não era registrada em lugar nenhum.** O relato dele
   (*"estava dando erro sem placa"*) só pôde ser respondido pela metade: deu para
   provar que **enviar sem placa funciona** (o 201 às 08:50:56 de 09/11, solicitação
   2660, 8 campos, `placas_conferidas` nulo), mas **não qual foi aquele 400** de oito
   segundos antes. Agora o handler loga a frase — sem os valores enviados.
4. **A cópia do modelo de checklist para o card É ADITIVA** (`NOT EXISTS ...
   de_modelo_id`), e eu escrevi o contrário num comentário da 098 antes de ler o
   `do_card`. Card já aberto na 251 **ganha** o `Detalhes dos itens` na próxima
   abertura. Comentário corrigido.
5. **Dois defeitos meus nas travas novas, os dois achados pela própria suíte:** uma
   lia o **arquivo inteiro** procurando `fpsl_ponte` e reprovava por causa do
   comentário que explica a regra — **é o erro de 05/11 e eu o repeti**; a outra tinha
   a sequência barra-n literal onde eu queria uma quebra de linha.

### 🔴 O que esta volta devolve para ele

1. **Exercitar no navegador** (`M9`): **clicar no card de chamado** (era o defeito) ·
   ver o prazo e o contador · mover para etapa com checklist e ver o diálogo novo ·
   marcar 2 de 3, mover e ver a OBS **colorida** · escrever um código em Rastreamento
   e achar a OBS do sistema. 🚨 Sandbox primeiro: mover card escreve a OS inteira no ERP.
2. 🔴 **Quatro decisões abertas, e nenhuma trava o que subiu:**
   **(a)** quem pode apagar OBS e se o anexo segue visível para todos — hoje qualquer
   pessoa com a `PNL_1.1` baixa qualquer anexo; **(b)** subir o teto de **4 s** do GET
   da ficha, que é limite e é dele; **(c)** para quem vai o aviso de abertura de
   chamado (e-mail de qual caixa, WhatsApp de qual número); **(d)** os dois conflitos
   do mapa de etapa inicial — as **duas OS de ressarcimento nascem no Financeiro
   (15746) de propósito**, e a **substituição gera DUAS OS**.
3. ⚠️ **24 h úteis com janela de 8,5 h = 2 dias e 7 horas.** Chamado aberto na segunda
   às 09:00 vence na **quarta às 16:00**. Se ele quis dizer "um dia útil", o número é
   **8,5** e troca em uma linha.

### 🚨 O erro da OS 17105 é DO HARMONIT, e nada foi escrito

📏 `~/logs/fpsl.log:4716`, 09/11 09:35:50, nas palavras do servidor deles:
`all pooled connections were in use and max pool size was reached`. **Exaustão do pool
do lado deles**, ~15,5 s por leitura, **9 ocorrências na 17105 em 12 minutos** — e é
**crônico**: 07/11 → **164** · 08/11 → **137** · 09/11 → **73** · 10/11 → 25.

**As duas frases diferentes são o mesmo evento visto por dois tetos:** o POST do mover
aguenta 25 s e repassa o motivo do ERP; **abrir o card tem teto de 4 s** e só consegue
dizer *"o FPSL não respondeu no tempo"* — que **culpa a peça errada**.

**A suspeita dele (*"movendo de Chamados"*) não se sustenta, e sei de onde veio:** quando
a leitura falha a rota devolve `"de": None` e o log grava **`None -> 890`**; e às 09:38:12
a trava de concorrência disse *"a OS está na situação **38**"* — que é a **primeira coluna
de OS, logo depois da `Chamados`**.

🔴 **O único conserto de verdade é com o fornecedor**: mandar as linhas de `pool` com data
e hora.

### As respostas aos levantamentos que ele pediu

- **Botão Atualizar:** relê o **cache do FPSL**, não o Harmonit. OS nova entra por um laço
  de **5 min**; o resync é de **12 h**. ⚠️ **Os dois vivem dentro do processo do FPSL, não
  no cron** — se o serviço reinicia e o laço não sobe, OS nova para de aparecer e nada
  avisa. Tetos: data matriz 24/10, 50 cards por coluna, 600 OS por consulta.
- **WESO:** não existe *"desativar placa"* — existe mudar o **rastreador** entre
  `Instalado` e `Estoque`. Três caminhos automáticos, todos no laço de **6 h**, e
  🚨 **o gatilho é a OFICINA de desinstalação (`status == 2`), não a etapa da OS**.
- **Sair de 15696 e 16490:** **não roda nada hoje** — em código vivo os dois ids só
  aparecem no catálogo de nomes de coluna.
- **Aba Solicitações (`FRM_1.1`):** não é resumo dos cards — é a **caixa do que chega**, e
  tem três coisas que o card não tem (ficha completa, anexos para baixar, e o interruptor
  que tira cada `/f/<slug>` do ar). **Os outros 8 formulários param SÓ ali.**
  🚨 E há desencontro: a `FRM_1.1` é `equipe` e a `PNL_1.1` é `owner` — **admin vê a
  solicitação e não vê o card**.


> 🚨 **06/11, ACHADO POR ELE — as colunas do Financeiro e do Contratual não
> apareciam: faltava `meta.aba` na rota.** 🔵 Ele: *"não estão aparecendo as colunas de
> 'financeiro' e ' contratual'"*. ✅ **Consertado e no ar** (build e reinício 10:00:37).
>
> O `PainelAba.vue` descobre a aba em `rota.meta?.aba`, **não** em `meta.codigo`. As duas
> rotas que eu escrevi levavam só `codigo` e `titulo` — copiei a forma do `meta` das rotas
> de `/config`, que não têm `aba`, em vez das duas do Pós-venda, que têm. A tela pedia
> `/api/paineis/aba/` **sem código**, e não houve erro visível.
>
> 🚨 **TUDO O MAIS ESTAVA CERTO, e é isso que faz o defeito:** registro, menu, rota,
> permissão, **200** na API, as 10 e as 6 colunas no banco, **2227 Python e 741 JS
> verdes**. O elo que faltava era o **QUARTO**: quem devolve → quem grava → quem lê →
> **quem diz à tela o que ler** ([[feedback_campo_novo_nao_entra_sozinho]]).
>
> **Conserto:** `aba` e `largo: true` no `meta` das duas (`largo` não é enfeite — o
> Financeiro tem **dez** colunas). **Trava nova ESTRUTURAL**, `rotas_painel_0611.teste.js`
> (6): varre o roteador e cobra de **toda** rota que monta a `PainelAba` ter `meta.aba`,
> ter `aba == codigo`, ter `largo` e ter `name == codigo` — **sem citar código nenhum**,
> para o próximo painel não repetir. Reverter uma das duas deixa **3** vermelhas.
>
> ⚠️ **A prova não foi o teste, foi `grep` no BUNDLE PUBLICADO**
> (`frontend/dist/assets/index-CDkVFMG7.js`), que agora contém `aba:"PNL_1.4"` e
> `aba:"PNL_1.5"`. Suíte verde não prova tela (`M9`) — aqui ela estava verde com a tela
> vazia. **Medido depois:** 747 JS em 40 arquivos (de 741 em 39).

> ✅ **06/11 — FINANCEIRO E CONTRATUAL NO AR** (`PNL_1.4` e `PNL_1.5`, migrações
> **096** e **097**), e com eles os **quatro painéis** declarados desde 22/10 passaram a
> ter tela.
> 🔵 Ele: *"do 1"* + as dez colunas · *"conclua e exiba o financeiro no paniel para
> owner"* · *"Depois gere a mesmta tela do 'Financeiro' para o 'Contratual'"* + a lista ·
> *"as regras de criação de cards em 'financeiro', 'pós-venda' e 'Contratual' ainda ficam
> em branco mesmo. Mas eleas ja devem aparecer no menu para owner"*.
> 📘 `docs/02`, `docs/03` e `docs/06` na VPS.
>
> | painel | código | rota | colunas | fins |
> |---|---|---|---|---|
> | Financeiro | `PNL_1.4` | `/paineis/financeiro` | **10** | Atendimento feito · Não atendido |
> | Contratual | `PNL_1.5` | `/paineis/contratual` | **6** | Assinado · Não assinado · Desistiu de cancelar |
>
> 🚨 **UMA ABA CADA, e não quatro.** O Pós-venda tem duas porque ele escreveu DUAS
> listas de colunas. Para o Financeiro e o Contratual a lista é **uma**. ⚠️ O que havia
> sobre "abas do financeiro" era o exemplo de permissão que ele marcou como *"Apenas
> exemplo"*, e a lista do §2.1 do `MoviZap_Formularios_PLANO.md` (`Financeiro · Pagamento
> técnicos · Administrativo · Fornecedores`), que é de **formulários**, não de etapas.
> Repartir dez colunas entre quatro abas inventadas seria escopo meu. Aba nova é uma linha
> na migração e uma no `telas.py`.
>
> 🔴 **DUAS LEITURAS MINHAS, as duas conferiveis em uma linha:**
> 1. **"Regras de automação e gatilhos" e "pesquisar" NÃO entraram como coluna do
>    Contratual.** Li as duas como a moldura da tela de onde ele copiou (o link de
>    automação do CRM e a caixa de busca): na lista do Financeiro, meia hora antes, a linha
>    equivalente era o cabeçalho literal **"Colunas"**; *"pesquisar"* vinha em minúscula
>    entre títulos capitalizados; e as seis restantes fecham um fluxo de contrato. **Se eu
>    errei, é uma linha da migração 097** — e há trava que fica vermelha quando alguém
>    corrigir.
> 2. **"INADIMPLENTES" entrou SEM a automação.** Ele escreveu *"INADIMPLENTES (Automação
>    move para pipeline Cobrança)"*. O parêntese é comportamento futuro, e **o painel
>    "Cobrança" não existe** — nem como tela nem no vocabulário
>    (`painel_aba_painel_conhecido` aceita só `operacao`, `pos_venda`, `contratual`,
>    `financeiro`). Automação que move card para pipeline inexistente é perda de card. Há
>    trava provando que **não há `Cobrança` em painel nenhum**.
>
> ⚠️ **A GRAFIA DELE FICOU:** "pendencias" sem acento, "Desistiu de cancelar" inteiro.
> Corrigir ortografia de rótulo ditado é renomear a coluna dele sem pedir.
>
> 🚨 **OS DOIS APARECERAM NA ABA `CFG_15.1` SEM UMA LINHA DE CÓDIGO** — a lista de
> concedíveis sai do grupo "Painéis" do **registro**. Era o desenho da manhã, e estas são
> as duas primeiras provas dele.
>
> ✅ **ELE JÁ USOU A ABA, às 09:38:** concedeu a **`PNL_1.1` à Erika e ao Rodrigo** (dois
> cliques, 6 segundos de intervalo). Conferido ao vivo depois do reinício das 09:46: as
> duas têm `PNL_1.1` **no menu** e **200** em `/paineis/operacao`, **403** no Financeiro e
> **403** na própria `CFG_15.1`; a Karla, sem concessão, leva **403 em tudo**. ⚠️ O
> reinício **não perdeu** as concessões — elas moram no banco, não no token — e a suíte
> **não as tocou** (a limpeza dela só alcança o login de sentinela).
>
> 🔴 **OS QUATRO NASCEM VAZIOS, por decisão dele** (*"ainda ficam em branco mesmo"*). A
> tela escreve **"Nenhum card nesta aba ainda."** — quadro vazio que não diz por quê é `M12`.
>
> **Medido depois de publicar:** **2227** Python (de 2195) com o único vermelho conhecido —
> o `teste_cadastro`, que é **dado** — e **741** JS em 39 arquivos. As 5 conferências do CSS
> publicado passaram. **26 travas novas** nos dois arquivos de painel, com o defeito
> forjado e pego (inserir a coluna *"pesquisar"* no banco deixou **5** vermelhas).
>
> 🚨 **QUATRO TRAVAS DA CASA FIXAVAM "o grupo Painéis tem três telas"** e ficaram
> vermelhas. Atualizei o **fato** nas quatro, sem afrouxar nenhuma. ⚠️ **Uma delas era
> minha, e a ironia é exata:** o `AS_TRES` do `teste_permissao_paineis.py` era lista fixa
> num arquivo cujo assunto é *"painel novo entra sozinho"* — virou função que lê o
> registro. Teste que prova que painel novo entra sozinho não pode ser o que obriga a
> editar teste quando um painel novo entra.

> ✅ **06/11 — A PERMISSÃO DOS PAINÉIS NO AR (`CFG_15.1`), e a PORTA TRANCADA consertada.**
> 🔵 Ele: *"em configuração, crie uma aba de permissão para os paineis, ali vou definir
> quem pode ver o que e por aba tbm, como notará que o pós venda ja possui abas"* ·
> *"4 ok"* (a porta trancada) · *"3 por enquanto matem assim"* (a origem dos cards) ·
> *"tem permissao para fazê-las, preciso delas prontas"* (os três comandos de publicação).
> 📘 **Bloco de 06/11 no `Desktop\Painel_Operacao_Checklists_PLANO.md`.** Na VPS:
> `docs/02`, `docs/03` e `docs/06`. **Migração 095.** ⚠️ Árvore do repositório **suja** —
> sem commit meu, por regra; o autocommit das 23:30 pega.
>
> 🚨 **A PERMISSÃO DO MOVIZAP DEIXOU DE SER SÓ POR PERFIL, e precisou:** `atendente.perfil`
> dá um conjunto de nomes e **não sabe dizer *"esta pessoa, esta aba"***. Como as três telas
> de painel são `permissao: owner`, o `pode_acessar` recusava todo não-owner e **não havia
> caminho de concessão nenhum** — a `atendente_time_permissao` estava **vazia** e só o Iago
> (121) alcançava qualquer painel. A tabela `tela_concedida` é a lista de **exceções
> nomeadas**, e o `pode_acessar` a honra **ANTES** de recusar tela `owner`.
>
> ⚠️ **A TELA NÃO FOI REBAIXADA.** Continua `owner` no registro; quem não tem linha segue
> barrado. Rebaixar para `equipe` abriria o painel para **todo admin de uma vez**, sem
> ninguém marcar nada — é outra coisa inteiramente.
>
> 🚨 **SÓ O GRUPO "PAINÉIS" É CONCEDÍVEL, e a trava é no backend** (código de fora → **422
> de regra**). A lista sai do **registro**, não de lista à mão: **painel novo entra sozinho**
> — é o que o Financeiro vai usar. ⚠️ E a `CFG_15.1` **não concede a si mesma**: ela é do
> grupo "Configuração". Ninguém se concede a própria chave.
>
> ⚠️ **FORA DO TOKEN de propósito:** a concessão é lida a **cada requisição**. No JWT,
> revogar só valeria no próximo login — e o token vale até a virada do dia.
>
> 🚨 **A PORTA TRANCADA DEIXOU DE SER HIPÓTESE NO MESMO DIA.** O menu pulava **toda** tela
> com `aba_de`, e isso bastava porque a casca `/config` é `atendimento` — toda aba vinha com
> a mãe. Conceder **só** a `PNL_1.3` dava alguém com tela, rota e permissão e **sem item de
> menu**: nem o 403 aparecia. A condição virou **"a mãe chegou?"**.
>
> ✅ **Prova ao vivo:** a rota devolve as três colunas com **nomes distintos** (Operação ·
> **Treinamentos** · **Pós-venda** recuada — no registro as duas últimas se chamam as duas
> "Pós-venda", e o nome que as separa vem de `painel_aba.titulo`); a grade traz **9 pessoas**
> (o Iago marcado e não editável, os outros 8 em branco); `GET /api/telas` do owner dá **37
> telas** e a `CFG_15.1` chega; a **Erika** (123) leva **403 nas três `PNL_*` e na
> `CFG_15.1`**, com **0 painéis** no menu. **`tela_concedida`: 0 linhas** — quem marca é ele.
>
> **Suítes medidas depois de publicar:** **2195** Python (de 2165; o único vermelho é o
> `teste_cadastro`, e é **DADO**) e **741** JS em 39 arquivos (de 725 em 38). As 5
> conferências do CSS publicado passaram. **27 + 15 travas novas**, com o defeito que
> guardam **forjado e pego**.
>
> 🔵 **O FINANCEIRO — a varredura achou uma lista, e NÃO é de colunas.** Ele: *"eu ja dei as
> colunas no plano, veja se encontra elas no .md de ontem"*. Não está no de ontem; está em
> `Desktop\MoviZap_Formularios_PLANO.md` **§2.1**, *"o mapa formulário → painel (escolhido
> por ele)"*: **`Financeiro · Pagamento técnicos · Administrativo · Fornecedores`** — e a
> **3ª é "Administrativo"**, que casa com o *"a Erika, apenas a aba 3 do financeiro"*. 🚨 Mas
> **aquela lista é de FORMULÁRIOS, não de etapas**: no Pós-venda os formulários eram NPS e
> CES e as abas saíram "Treinamentos" e "Pós-venda" — os dois conjuntos **não coincidiram**,
> então não dá para derivar um do outro. 🔴 **Falta dele: as colunas de cada aba**, o
> equivalente ao *"Solicitação: Testes: Realizar Pós-venda: Pós-venda Realizado"*.
>
> 🚨 **Três achados de método, nesta volta:**
> 1. **O conserto do menu tornou IRREAL uma fixture que estava verde** (`CFG_1.1` sem a
>    `CFG_0.1`, situação que o sistema não produz). Consertei a **fixture**, não o código.
> 2. **Meu guard de idempotência comparava a ÂNCORA e engoliu duas escritas**: dois patches
>    disseram *"já aplicado"* e as duas linhas de tabela do `docs/03` **não entraram**. Só o
>    `grep` no arquivo mostrou — ver [[feedback_validar_1_antes_do_lote]].
> 3. **Erro em TEARDOWN:** o `TestClient`, ao sair do `with`, dispara o `shutdown` do app, que
>    chama `banco.fechar()` — e a limpeza da última fixture estourava com *"banco não foi
>    aberto"*. Teste passava, arquivo ficava vermelho, e a **sobra continuaria em produção**.
>
> 🔴 **O que sobra para ele:** **marcar quem vê o quê** na aba nova (`/config` ›
> Permissão dos painéis), e então o teste das telas pela equipe — decisão dele:
> *"ficará para o teste das telas da equipe, depois que eu liberar quem poderá ver"*.

> ✅ **05/11, FECHADO POR ELE:** *"tudo bem, dê como ok e documente brevemente o feito"*.
> O resumo de uma página está no TOPO do `Desktop\Painel_Operacao_Checklists_PLANO.md`.
> 🔴 **Só três coisas seguem esperando ele:** as **colunas do Financeiro** · a **origem dos cards** das abas de Pós-venda · e a **porta trancada** (conceder só a 2ª aba deixa a pessoa sem item de menu).

> ✅ **05/11, OITAVA VOLTA — O ENVIO PARA DE ABRIR OS, e as ABAS DE PÓS-VENDA no ar.**
> 🔵 Ele: *"pode seguir o 1"* · *"o que falei só se aplicará as telas de pós venda e
> financeiro. para o Op, pode ajustar, é a cereja do bolo"* · *"Aba no Menu Pós-venda =
> abas de pipeline: Treinamento / Pós venda"* · *"só aba principal no menu. As demais são
> dentro dela já."*
> 📘 **ÁREA J do `Desktop\Painel_Operacao_Checklists_PLANO.md`.** Na VPS: `docs/03` e
> `docs/06`. Commit `2f47d62`.
>
> ✅ **O envio do suporte NÃO ABRE MAIS OS** — a D4 de 29/10 invertida por ele. O chamado
> nasce como **card na coluna `Chamados`**. 🚨 **Saiu a CHAMADA, e não o mapa:** tirar o
> `"suporte"` do `PROBLEMA_POR_FORMULARIO` derrubaria ~23 das 27 travas de
> `teste_chamado_os` e levaria a maquinaria que o botão Operação vai precisar.
> 🚨 **A trava do ERP fora do ar ficou MAIS FORTE:** antes provava que o envio
> *sobrevivia*; agora prova que ele **nem fala** com o ERP — e religar a abertura
> automática a deixa **vermelha** em vez de passar calado pelo `try`.
>
> ✅ **As duas abas do Pós-venda** (mig. 094), com as colunas dele:
> **`PNL_1.2` Treinamentos** — Solicitação · Treinamento 1 · Treinamento 2 · Entregue;
> **`PNL_1.3` Pós-venda** — Solicitação · Testes · Realizar Pós-venda · Pós-venda
> Realizado. 🔵 **UM item de menu, as duas abas dentro** — a `PNL_1.3` leva `aba_de`, a
> convenção das seis `CFG_*`. ⚠️ **Uma entrada de tela por aba** mesmo assim, porque
> `permissao` é campo da entrada.
>
> 🚨 **A PERMISSÃO DO CARD PASSOU A SAIR DO CARD:** as 5 rotas exigiam `PNL_1.1` **fixo**,
> e um card da `PNL_1.2` cairia em 403 pedido por quem tem a tela certa. Para os chamados
> nada muda — a aba deles *é* a `PNL_1.1`.
>
> 🚨 **O diálogo do card virou COMPONENTE** (`DialogoDeChamado.vue`), usado pela coluna
> `Chamados` e pelas abas — e as **22 travas** da coluna provam a extração. ⚠️ Ele declara
> as **quatro** propriedades de forma: o `.painel__dialogo` da Operação é `scoped` e não
> alcança o componente, então os 420px da casa voltariam inteiros.
>
> 🚨 **A CONFERÊNCIA DA CASCATA ACUSOU ELA MESMA:** com o diálogo extraído passaram a
> existir **duas** `.modal__painel` no bundle, e ela comparava a primeira com o `h3` do
> **outro** componente. Agora compara dentro do mesmo `data-v` — **mais forte**, porque
> antes também podia ficar **verde por sorte**. ⚠️ E o `data-v` vai no **último** seletor
> simples (`.modal__recados h3[data-v-x]`): o regex novo errou isso na 1ª rodada.
>
> 🔍 **17 travas novas** (`tests/teste_abas.py`), verdes 3×, com o defeito da permissão
> **forjado e pego**; a inversão da cascata forjada no CSS publicado e pega.
> **2163 Python e 725 JS.** Ao vivo: as duas rotas de aba devolvem as colunas dele, o menu
> traz `PNL_1.1` e `PNL_1.2` como itens, e a Operação segue com 18 colunas.
>
> 🔴 **O QUE ESPERA ELE:**
> 1. 🚨 **AS ABAS E COLUNAS DO FINANCEIRO.** Ele disse *"inclusive do financeiro, com as
>    abas e colunas que ja passei"* — **procurei e não passou**: o que veio foi o
>    **exemplo de permissão** (*"a Karla (…) todas as abas. A Erika, apenas a aba 3 do
>    financeiro"*, seguido de *"Apenas exemplo"*) e *"Mesma lógica, colunas eu dou"*. Com
>    as colunas, é **seed + duas linhas no `telas.py`**: motor e tela já estão no ar.
> 2. 🔴 **A ORIGEM dos cards** das abas (*"deixe em aberto, depois veremos"*) — hoje as
>    duas nascem **vazias**, e a tela diz isso.
> 3. 🚨 **A PORTA TRANCADA, escrita antes de acontecer:** conceder **só** a `PNL_1.3` a
>    alguém deixa essa pessoa **sem item de menu**, porque o item é da `PNL_1.2`. Conserto
>    = o `MenuLateral` desenhar o item quando a pessoa alcança **qualquer** aba. Hoje as
>    duas são `owner`, então não aparece ainda.
> 4. ⚠️ **O `Agenda*`** é ligação, não nome (*"Liga na Agenda do MoviZap"*): as tabelas
>    `agendamento`/`agendamento_os` existem (072/073), o elo é frente própria.

> ✅ **05/11, SÉTIMA VOLTA — A COLUNA `Chamados` ESTÁ NO AR, estética e provada.**
> 🔵 Ele: *"vamos criar uma coluna nova antes de 'Nova solicitação', chamada
> 'Chamados' (…) nessa coluna não são OS ainda, somente o CARD mesmo, com OBS, etc"* ·
> *"ter o botão de 'Finalizar Chamado' e daí vai perguntar 'Resolvido' ou 'Não
> resolvido'"* · *"um botão de 'abrir conversa'"* · *"vamos montar estético para
> validação de fluxo visual e depois volto para o back para preencher as regras e flow,
> pode subir"* · *"Coluna 'Chamados' ainda não aparece. Pode concluir e entregar."*
> 📘 **A ÁREA I do `Desktop\Painel_Operacao_Checklists_PLANO.md`** tem tudo, inclusive a
> lista do que espera ele. Na VPS: `docs/06` e `docs/02` (migrações 092 e 093).
>
> 🚨 **A DESCOBERTA QUE DESENHOU TUDO:** a coluna `Chamados` e as pipelines de Pós-venda
> que ele pediu no mesmo dia **são a mesma coisa** — colunas que não existem no Harmonit.
> Mover numa das 17 escreve no ERP; mover numa destas escreve só aqui. **Um motor serve
> os dois** (`movizap/pipeline.py`, que não importa a ponte, e há trava provando).
>
> **No ar:** 18 colunas (a `Chamados` na frente, `situacao_id` nulo) · o card sem OS,
> com o nome do formulário onde o outro escreve `OS 17081` · diálogo próprio de 900px
> (respostas por rótulo, observações em bolhas, histórico lendo o retrato) · **Finalizar
> Chamado pergunta no lugar do botão** · Resolvido e Virou OS **só marcam**, e **Reabrir
> desfaz** · o arquivado esmaece, vai para o fim da coluna e **tem selo com o desfecho**
> · Abrir conversa é um `router.push`, e sem telefone **não aparece** · a guarda do
> arrasto recusa **na tela** e diz por quê.
>
> 🚨 **A SUÍTE ACHOU UM DEFEITO MEU DE VERDADE:** `test_a_busca_casa_por_OS_e_diz_onde`
> escolhia `cards[0]`, e o primeiro card do quadro passou a ser um chamado — **buscava
> por `None` e devolvia 0**. Mais 4 travas retargetadas de 17 para 18 colunas (com
> `len(SITUACOES)` seguindo 17) e **3 mentiras no cabeçalho do `paineis.py`** (`M12`),
> uma delas a que esta entrega inverteu pela metade.
>
> 🔍 **22 travas novas de tela, verdes 3×; forjei os 2 defeitos que elas guardam e 14
> ficaram vermelhas.** A **5ª conferência** no CSS publicado (teto e empilhamento do
> diálogo do chamado), com o defeito forjado e pego — ⚠️ o jsdom não faz layout.
> **2143 Python e 725 JS.** Commits `7bed099` e `af87a43`.
>
> 🔴 **O QUE ESPERA ELE — e um importa HOJE:**
> 1. ✅ **FEITO na oitava volta (acima).** ~~Desligar a abertura automática de OS no envio do suporte~~, que ficou de fora porque
>    ele disse que volta ao back *"para preencher as regras e flow"*. **Enquanto não
>    desligar, o mesmo chamado aparece NAS DUAS COLUNAS.** O caminho está medido: tirar a
>    **chamada** de `main.py` (~5877), e **não** o `"suporte"` do mapa — o mapa derruba
>    ~23 das 27 travas de `teste_chamado_os`, porque o fixture lê essa chave.
> 2. O botão **Operação** do FPSL em modal — 🔵 *"se não der, depois retomo"*. Medido:
>    `x-frame-options: DENY`, e liberar **não resolveria** (o token dele vive no
>    `localStorage` do outro origin). 🚨 **Não toquei no `X-Frame-Options`**, por
>    instrução dele: *"não insista ou force a quebra do iframe"*.
> 3. As abas de **Pós-venda** (`PNL_1.2` Treinamentos, `PNL_1.3` Pós-venda) — bloqueadas
>    na **origem dos cards**: 🔵 *"deixe em aberto, depois veremos"*. Quando ele disser,
>    é **configuração**, não código. **Contratual e Financeiro:** *"colunas eu dou"*.
> 4. 🔴 **O vermelho de hoje é DADO, e é decisão dele:** o número de teste dele
>    (`+5518998116168`) ganhou um **2º cadastro** — além da Pastelaria Velasco (91041),
>    existe **`Iago Do Ó` (198394)**. ⚠️ **Não foi o MoviZap:** ele não tem nenhuma rota
>    que cria cadastro (`grep` por `criar_cliente`/`SalvarCliente`/`criar_contato` em
>    `movizap/*.py`: **zero**). Pela regra de identidade, número compartilhado só vale se
>    **todos os cadastros forem a mesma empresa** — e um deles é pessoa.
> 5. 🔴 **Exercitar no navegador** (`M9`): enviar um chamado de suporte de verdade, abrir
>    as observações, **anexar e baixar de volta**, abrir a conversa, e finalizar nos dois
>    desfechos.

> ✅ **05/11, SEXTA VOLTA — TELA OK, e saíram os TEXTOS EXPLICATIVOS do card aberto.**
> 🔵 Ele: *"Tela ok"* — e depois, um a um: *"veja esses comentários (…) não precisam
> mantê-los no card"* · *"esse tbm"* · *"isso"* · *"pode deixar do mesmo tamanho da
> informação da OS; Ex: OS 123456 - TERMO 8899 - Instalação rastreador todos no mesmo
> tamanho, dai fechamos"*.
> 📘 `docs/06_Conteudo_das_Telas.md`, seção *"05/11, quinta volta"*.
>
> 🚨 **TERCEIRA VEZ que ele tira texto explicativo desta tela** — 29/10 (três textos), 05/11
> de manhã (o resumo do cabeçalho e a linha de `fora_do_quadro`) e agora quatro. A régua é
> dele e é a mesma: *"atrapalha o profissionalismo"*.
>
> **Saíram:** a explicação do estado vazio das Passagens (*"O Harmonit não guarda a situação
> na linha do tempo…"*) · o aviso do pé do modal (*"Mover de etapa escreve a situação na OS…
> Mudar a prioridade reescreve a OS inteira"*) · e os **dois pés de painel** (checklist e
> observações).
> ⚠️ **O quarto ele não nomeou** — tirei porque é o mesmo construto (`modal__painel-pe`),
> nasceu junto hoje, e deixar um painel explicado e o outro não seria pior. 🔴 Volta numa linha.
> ✅ **Ficou o ESTADO sem a lição:** *"Nenhuma passagem registrada."*
> ⚠️ **Não toquei** a frase do **modal de observações** (outro diálogo, não apontado) nem o
> aviso de que **anexo não tem backup** — esse é risco de perda de dado, não explicação.
>
> 🚨 **O QUE A REMOÇÃO CUSTA, e está dito no doc:** **o aviso de escrita era o único aviso
> prévio da tela.** Mover card **não tem confirmação** — o arrasto e o `select` escrevem no
> ERP na hora, e a tela só fala **depois**, quando falha (`erroDeMover`). O comportamento não
> mudou; o aviso prévio deixou de existir.
> ⚠️ **As regras seguem no código:** `gravar_situacao_da_os` grava a situação,
> `gravar_prioridade_da_os` reescreve a OS inteira, o checklist vira observação ao mover, e
> nada chega ao Harmonit (decisão **O4** dele). O que saiu foi a tela **dizê-las**.
> ⚠️ E quem abrir uma OS antiga verá zero passagens e pode concluir que ela nunca se moveu — a
> `os_passagem` começou em 29/10, e isso deixou de estar escrito.
>
> ✅ **A linha de identificadores do modal ficou toda em `--txt-md`** (a OS era `md` e o resto
> `sm`); o tamanho vem do pai e nenhum filho o muda. ⚠️ **O que distingue a OS passa a ser só
> a cor e o peso.** A risca separadora foi de 13px para `1em`, senão pairava acima da base.
>
> ✅ **Travas: oito saíram e UMA foi REESCRITA.** Nenhuma por estar errada — prendiam a
> **redação** dos textos removidos.
> 🚨 **A reescrita é a que importa:** *"o aviso de escrita está no MESMO bloco que eles"*
> prendia **duas** coisas — a **posição** dos dois controles juntos no pé (a regra de separar
> ler de agir, que foi a entrega de 05/11) e a **frase** ao lado. A frase saiu; a posição
> continua sendo o ponto, e a trava passou a afirmar só isso. ⚠️ Jogá-la inteira fora seria
> perder a prova do que a entrega fez.
>
> ⚠️ **QUATRO VEZES NESTA SESSÃO O MESMO TROPEÇO MEU:** a asserção de *"o texto saiu"*
> reprovou porque **o comentário que eu escrevia no lugar citava o texto removido** — com
> `}`, com `:first-of-type`, com a tag de estilo e com *"Ao mover o card, isto vira"*.
> 🚨 **A asserção tem de olhar o CÓDIGO, não o arquivo:** tirar os comentários antes de
> contar. E numa delas eu errei para o outro lado — asseverei largo demais e peguei a frase
> de **outro diálogo**, que ele não pediu para tirar.


> ✅ **05/11, QUINTA VOLTA — O MODAL TINHA 420px, e a causa estava NOUTRO ARQUIVO. Mais a
> TRAVA QUE LÊ O CSS PUBLICADO, que fecha os três defeitos do dia de uma vez.**
> 📘 `docs/06_Conteudo_das_Telas.md`, seção *"05/11, quarta volta"*.
> 📘 Diagnóstico completo: `Desktop\Modal_Largura_CAUSA_E_CORRECAO.md`.
> 🔵 Ele, pela terceira vez na mesma tela: *"ainda está errado a dimensão. aparece só uma
> coluna"* — e depois, com razão: *"já era para estar corrigido, conforme a metodologia"*.
> ⚠️ **Eu havia entregado PROPOSTA onde cabia CONSERTO.** Diagnosticada a causa, e sendo o
> defeito meu, a correção era a entrega — não uma pergunta.
>
> 🚨 **A CAUSA:** existe uma `.modal__caixa` **GLOBAL** em `estilo/componentes.css` (linha
> 112) — a modal da casa, um aviso — com **`max-width: 420px`**, `padding: var(--e-5)` e
> `overflow-y: auto`. A regra escopada do painel ganha por especificidade
> (`.modal__caixa[data-v-…]` é `(0,2,0)` contra `(0,1,0)`), **mas só ganha no que declara**:
> eu declarava `width: min(1000px,100%)` e **nunca `max-width`**.
> 🚨 **`max-width` é um TETO aplicado DEPOIS de `width`, qualquer que seja a especificidade
> de quem definiu a largura.** O modal tinha **420px**; as duas colunas pedem 320+280 de
> base, não cabiam, e o `flex-wrap: wrap` fazia o que eu mandei — **empilhava**. Uma coluna.
> E as outras duas propriedades explicavam o resto: os 22px impediam as faixas de encostar na
> borda, e o `overflow-y` era a **segunda rolagem**, justo a que eu dizia ter tirado.
>
> ⚠️ **POR QUE ME ESCAPOU TRÊS VEZES:** li só o `<style scoped>` da tela, e **acreditei no
> meu próprio comentário**, que jura em caixa alta que *"a caixa não tem padding"*. Ele
> descrevia a intenção; eu o li como se descrevesse o arquivo. 🚨 **Terceira vez nesta sessão
> que um comentário meu afirma o contrário do que o código faz.**
>
> ✅ **A CORREÇÃO:** o diálogo do card ganhou classe própria, **`painel__dialogo`**, que
> declara **as quatro propriedades de forma** — `width`, `max-width`, `padding`, `overflow` —
> inclusive as que "parecem" o padrão. ⚠️ A `modal__caixa` fica no elemento **só** pelo
> `user-select: text`; toda a forma vem da classe nova. ⚠️ Os outros dois diálogos (recados e
> aviso de etapa) continuam na classe da casa, que serve para eles.
> 🚨 **A regra geral:** tela que reaproveita classe global e quer outra forma **declara todas
> as propriedades de forma**. O que fica em branco vem da folha global, e vem calado.
>
> ✅ **A TRAVA QUE FALTAVA: `frontend/scripts/conferir_css_publicado.mjs`.**
> 🚨 **Três defeitos hoje, uma única causa: nada nesta casa lê CSS.** O jsdom não aplica
> `<style scoped>` nem a folha global. O script lê o **CSS que o navegador recebe** e confere
> os três: o **teto de 420px** herdado · a **ordem de cascata** do `.modal__painel` · os
> **doze tokens** no `:root` com a `.escala-operacao` declarando só `--txt-*`.
> ⚠️ **Entrou no `npm run build`**, depois dos dois `vite build` — não se publica um bundle
> com um dos três. É a única mudança no rito.
> 🚨 **E ele NÃO pula quando não acha o `dist`: FALHA.** Verde sem ter medido é a pior
> espécie — e esta casa já tem dois arquivos assim no FPSL, contados no placar sem rodar.
>
> ✅ **A trava foi PROVADA REPROVANDO**, forjando cada defeito no CSS construído:
> `max-width: 420px` → exit 1 · `--sombra-1` dentro da escala → exit 1 com **duas** queixas ·
> `.modal__painel` movido para antes das antigas → exit 1 · CSS correto → exit 0.
> ⚠️ **A minha primeira forjadura não forjou nada:** renomeei `.escala-operacao[` com `sed`
> supondo que fosse escopada — ela é **global**, vem do `tokens.css` e não leva `[data-v-]`.
> O `sed` não casou, o script passou, e eu quase registrei isso como prova.
> 🚨 **Prova que não falha quando devia não é prova.**
>
> ✅ **Também saíram da tela, a pedido dele** (*"tire esses comentarios da tela"*): o resumo
> do cabeçalho (*"40 OS nas 17 situações…"*) e a linha de `fora_do_quadro`. Saíram junto o
> `fora` (ficou sem chamador) e **nove travas** que prendiam a redação daquelas frases.
> ⚠️ **O dado continua na rota** (`quadro.total`, `quadro.desde`, `quadro.fora_do_quadro`):
> o que saiu foi a tela dizê-lo.
> ⚠️ **E um erro meu que os testes pegaram:** o primeiro recorte levou junto o **aviso da
> busca** (*"Mostrando só o que casa com… · limpar"*), que fica entre os dois blocos e que
> ele não pediu para tirar — e que existe por regra escrita (`M12`: quadro filtrado que não
> diz que está filtrado). Restaurei do git e refiz bloco a bloco.


> ✅ **05/11, TERCEIRA VOLTA — MENU LATERAL `#04034D`, o ESPAÇO do grid, a COLUNA de 360px — e
> o CONSERTO DOS 12 TOKENS que eu havia quebrado.**
> 📘 **Documentado em `movizap_painel/docs/06_Conteudo_das_Telas.md`**, seção
> *"05/11, segunda volta"*, que é o arquivo das telas que ele pediu.
> 📘 Desenho e alternativas: `Desktop\Painel_Operacao_Card_e_Modal_DESIGN.md` e
> `Desktop\Menu_Lateral_e_Espaco_PROPOSTA.md`.
>
> 🚨 **O DEFEITO QUE ABRIU A VOLTA, E ELE É MEU.** Para pôr a escala +2 em token eu fechei o
> `:root` do `tokens.css` **um `}` antes do lugar** — ancorei na última linha que eu tinha
> *impresso na tela*, não na última linha do bloco. As **doze declarações seguintes** caíram
> dentro do `.escala-operacao`, que vive na raiz do Painel da Operação, e **deixaram de existir
> fora dele**: `--menu-*` (o menu inteiro), `--sombra-1`/`--sombra-2` (**42 e 40 arquivos**),
> `--foco` (**24**) e os quatro `--conversa-*` (**19**).
> **O efeito:** o menu perdeu o fundo escuro, o sistema perdeu as sombras e o anel de foco do
> teclado, e os balões da Caixa de Entrada e do Chat interno ficaram **quadrados e sem bico**.
>
> 🚨 **E NADA PEGOU.** CSS com `}` fora de lugar continua CSS válido — o build passa em 1,6s — e
> **nenhum dos 716 testes de tela lê valor computado de token**. A única tela que continuou certa
> foi a que eu estava olhando, porque a classe que engoliu os tokens está na raiz dela. Quem
> achou foi **ele**: *"você mudou o design total do movizap porque?"*.
> ⚠️ **A regra do bloco 8 deste arquivo — *"validar ANTES de gravar"* — vale para a ESTRUTURA do
> que o script produz, não só para a sintaxe do script.** 🚨 E o comentário que eu mesmo escrevi
> ali afirmava *"SÓ O PAINEL DA OPERAÇÃO, a escala global não mudou"*: o texto dizia o oposto do
> que o arquivo fazia. `M12` no pior lugar — o comentário que devia me proteger foi o que me
> convenceu de que estava certo.
> ✅ **Consertado com validação antes de gravar**, e a validação aprendeu duas coisas: contar
> chaves **ignorando comentários** (a minha prosa escreve `}`) e medir por **delta** contra o
> original, porque o `MenuLateral.vue` já tinha um `{` solto num comentário antes de eu chegar.
>
> ✅ **O MENU:** fundo **`#04034D`** · texto `#94A3B8` → **`#CBD5E1`** (7,3:1 → **12,6:1**) ·
> `hover` .06 → .10 e borda .10 → .16 (o azul saturado come o branco translúcido) ·
> **`--menu-rotulo` `#A8B2D8`** novo, porque três lugares escreviam a cor à mão e duas falhavam
> no fundo novo (**3,3:1** nos rótulos de grupo e **2,6:1** no subgrupo, em 13px).
> 🚨 **O TEXTO FOI PARA O MAIS CLARO, E ELE PEDIU "MAIS ESCURO"** — e isso está dito no
> comentário do token. O que ele via sumindo era `#94A3B8` sobre o **fundo claro que o meu
> defeito deixou** (2,6:1); sobre `#04034D` o mesmo cinza dá 7,3:1. Escurecer é que o faria
> desaparecer. O *"destaque"* se consegue subindo o contraste.
>
> 🚨 **O RECURSO OCULTO POR CONFLITO DE COR — ele previu, e existia:** o item **ativo** usa
> `--acento` (`#2563EB`) e o fundo do menu passou a ser **também azul** — **3,6:1** entre os
> dois. ⚠️ Trocar o azul do ativo não resolve: com `#3B82F6` a separação sobe para 5,1:1 mas o
> **texto branco em cima cai para 3,7:1** e falha em 16px. O conserto é **barra branca de 3px à
> esquerda** — sem depender de cor, que é a régua da casa.
> ✅ **E a logo do menu voltou a aparecer sozinha:** ela é pintada de **branco** por
> `filter: brightness(0) invert(1)` para viver no escuro, e estava branco sobre claro.
>
> ✅ **O MOVIZAP no topo:** a marca era uma **coluna** (logo de 34px em cima, nome embaixo) e o
> botão de recolher, irmão dela, se alinhava pela logo — o nome sobrava pendurado. Virou **uma
> linha**, logo de 24px, nome em `--menu-texto-forte`, mesma linha de base do botão; o topo
> perdeu ~20px mortos. ⚠️ **O compacto e o celular voltaram a `column` explicitamente** — era a
> quebra mais provável, e numa faixa de 62px a logo em linha ficaria deslocada.
>
> ✅ **O ESPAÇO:** `.painel__conteudo` tinha **40px de cada lado em todas as telas** (só a Caixa
> escapava). Na Operação eram **80px horizontais** — um terço de coluna. Entrou um `meta.largo`
> → **80px vira 24px**. ⚠️ **Não usei o `cheio: true` da Caixa de propósito:** ele zera o padding
> **e o `overflow`**, e a Operação depende da rolagem vertical do casco.
>
> ✅ **A COLUNA foi de 248px para 360px** (colapsada 210 → 280). A conta dos 3 por scroll em
> 1366px: `1366 − 240 (menu) − 24 (o largo) = 1102`, menos 2 vãos = `1078 / 3 ≈ 359`. O conteúdo
> útil do card vai de **222px para 334px**, e a mediana dos nomes de cliente (28 caracteres)
> passa a caber em **uma linha**.
> ✅ **O card desceu de CINCO faixas para QUATRO:** o tipo e a placa subiram para a linha da OS,
> na borda direita. ⚠️ **PAREI EM QUATRO, e a conta é a razão:** *"nesta etapa 3h · total 3h"* já
> ocupa ~170px dos 334 e os selos mais a previsão pedem ~160px — juntos transbordam, e card que
> transborda é pior que card com uma faixa a mais.
>
> ✅ **Suíte JS: 716 testes em 37 arquivos, verdes**, com **31 travas** em
> `painel_card_modal_0511.teste.js` rodadas 3×. `dist` publicado, tela em 200.
> ⚠️ **Não rodei a suíte Python uma terceira vez** — ela já foi 2× nesta sessão (é o teto) e a
> mudança é só de tela; o `pytest` chama a de JavaScript por dentro, e essa está verde.
>
> 🔴 **O BURACO QUE FICA DITO, e é o que deixou os 12 tokens passarem:** **nenhum teste lê cor
> computada de token.** Prender isso exigiria montar a tela com o CSS real, e o jsdom não aplica
> `<style scoped>`. Hoje o que cobre é **ele abrir a tela**.
>
> 🚨 **05/11, QUARTA VOLTA — O PAINEL DO MODAL ESTAVA ERRADO, e a causa era a CASCATA.**
> 🔵 Ele: *"o layout do card apos o clique esta errado"* · *"pode reduzir a fonte da tela em 1,
> card fechado e aberto"*. 📘 Detalhe na seção *"05/11, terceira volta"* do
> `docs/06_Conteudo_das_Telas.md`.
>
> 🚨 **A CAUSA:** eu escrevi as regras do `.modal__painel` **antes** das regras antigas de
> `.modal__recados`/`.modal__log`/`.modal__temas`, que vivem mais abaixo na folha. **Mesma
> especificidade, e a que vem depois ganha** — o cabeçalho do painel caía para `--txt-sm` e o
> `gap` voltava a `--e-2`. ⚠️ **E o painel nunca ganhou as faixas do mockup:** eu havia posto
> um `padding` único na seção, então era uma caixa, não cabeçalho + miolo + pé.
> ✅ **Consertado:** o bloco foi para o **fim** da folha (conferido no CSS publicado: as antigas
> no byte 197.311, o painel no 199.428), o `<h3>` virou a faixa de cima — ele já envolvia título
> e pílula, não precisou de `<div>` novo — e a frase de regra virou o **pé**, em vez de abrir o
> bloco e empurrar o assunto.
> ✅ **A escala caiu de +2 para +1:** **12 / 13,5 / 15 / 17 / 21**. O +2 ficou grande demais
> depois que a coluna foi a 360px. ⚠️ A base global segue 11/12,5/14/16/20.
>
> ⚠️ **UMA TRAVA REPROVOU POR GRAFIA, NÃO POR REGRA:** a frase passou a **abrir** a sentença
> (*"**N**ão vai para a OS"*) e o `toContain` exato caiu. Virou `toMatch(/.../i)`.
> 🚨 É a lição **varredura de rótulo ignora caixa**: comparar texto de tela sem `i` prende a
> grafia, não a regra.
> ⚠️ **E um refino meu:** o respiro do miolo usava `:first-of-type`, que casa o primeiro de
> cada **tipo** de elemento — com `<p>`, `<ul>` e `<div>` no painel, dava respiro em três filhos
> ou em nenhum, conforme os `v-if` daquele card. Trocado por vizinhança (`h3 + *`, `* + *`).
>
> ✅ **Suíte JS: 721 testes em 37 arquivos**, com **36** no arquivo do card/modal e **141** nas
> três do painel, rodadas 3×. `dist` publicado, tela em 200.
> 🔴 **E O BURACO FICA MAIOR DO QUE EU DISSE:** além de nenhum teste ler cor computada,
> **nenhum teste pega ORDEM DE CASCATA** — foi exatamente o que quebrou aqui. O jsdom não
> aplica `<style scoped>`. O que pegou foi ele abrir a tela.
>
> 🔵 **05/11, ELE CONFERIU NO NAVEGADOR:** *"tudo certo no navegador aparentemente"*.
> ⚠️ **É uma olhada, não um exercício** — vale como "nada visível quebrou", e cobre
> justamente o que a suíte não vê (cor de token, sombra, contraste). ⚠️ **Não cobre** o que
> só aparece agindo: mover card, `Escape`/`Tab` no modal, o menu recolhido e o celular.
>
> 🔴 **O QUE É DELE AGORA — 3 itens:**
> 1. 🔵 **Abrir e conferir:** o menu em `#04034D` com o MOVIZAP alinhado · a barra branca no item
>    ativo · o menu **recolhido** e no **celular** (foi onde eu mexi e pode quebrar) · a Operação
>    com 3 colunas por scroll · **e a Caixa de Entrada**, que teve os balões consertados.
> 2. ⚠️ **O limite de 3 dias do *"parado"* segue sugestão minha** (`PARADO_DEMAIS_DIAS`), não
>    número dele.
> 3. 🔵 **O token global `--texto-apagado`** (#94A3B8, 2,56:1) segue com o conserto mínimo, só no
>    Painel da Operação.


> ✅ **05/11 — PAINEL DA OPERAÇÃO: o CARD (variante C) e o MODAL (proposta A) NO AR.**
> 📘 **Design, medição e estado: `C:\Users\Lenovo\Desktop\Painel_Operacao_Card_e_Modal_DESIGN.md`**
> 🖼️ **Mockups que ele validou:** https://claude.ai/artifact/1tCkWmnqDwu9TKw6JKyQq9
> 🔵 Ele, olhando os mockups: *"aumentar um pouco mais as fontes e realinhas, mais 2 está ok,
> vamos de C"* · *"card aberto modal, mesma coisa (…) vamos de A, pode dar uma elaborada para
> evidências as limitações das caixas tbm, talvez espessura ou sombreamento"* · *"e dai siga ambos"*.
>
> 🚨 **SEIS DEFEITOS MEDIDOS NA PRÓPRIA TELA, não seis gostos** — e o que os achou foi medir o
> DOM e ler o CSS, não olhar:
> 1. **Três seções do modal colavam na borda da caixa.** `checklist`, `observações` e
>    `passagens` eram filhas **diretas** da `.modal__caixa`, que tem `padding: 0` de propósito,
>    e **nenhuma definia o seu**. Só os temas estavam dentro do `.modal__corpo`, que é quem tem
>    os 16px. Era isto que fazia o modal parecer malfeito sem nada estar escrito errado.
> 2. **O teto de rolagem guardava a seção errada.** `max-height: 60vh` estava no
>    `.modal__corpo`, que continha **só os temas**; as três que crescem de verdade ficavam fora,
>    sem teto. O comentário dizia que o teto existia *"para o pé não fugir da tela"*.
> 3. **Duas rolagens empilhadas** — a do `.modal` e a do `.modal__corpo`.
> 4. 🚨 **O card chamava "prazo" o campo que o comentário logo acima dele proibia chamar de
>    prazo.** O modal já escrevia *"Previsão de entrega"*. As duas telas do mesmo painel se
>    contradiziam — `M12` ao vivo.
> 5. **`aria-modal="true"` sem nada que o sustente:** `grep Escape` = 0, foco não entrava, não
>    voltava ao card.
> 6. **As frases de REGRA do modal falhavam contraste.** `.apagado` = #94A3B8 = **2,56:1** (a
>    norma pede 4,5) a 12,5px — e carregava *"Não vai para a OS do Harmonit"* e *"Mover de etapa
>    escreve a situação na OS"*. Eram 17 usos nesta tela.
>
> 🚨 **A DESCOBERTA QUE RESPONDEU AO *"evidenciar as limitações das caixas"*: a coluna e o card
> eram os DOIS `#FFFFFF`.** `.coluna` e `.card__abrir` usavam ambos `var(--superficie)`. Branco
> sobre branco, com 1px no tom mais claro da paleta como única separação. Agora a coluna recua
> para `--fundo` e o card fica branco com `--borda-forte` + `--sombra-1`; o mesmo nos painéis do
> modal.
>
> ✅ **O CARD, variante C:** o **cliente** é a primeira linha e o maior texto · saíram **duas
> pílulas que não informavam** (o nome da situação, que é o título da coluna onde o card já
> está — e era a mais comprida, 3 linhas em 248px — e *"Harmonit"*, que aparecia em quase todo
> card) · a prioridade **Normal não aparece mais** · a **cor ficou só na exceção** (parado
> demais ou prioridade ≠ Normal), e a cor da etapa subiu para a coluna · as três medidas
> secundárias caem na **mesma borda direita**, que é o realinhamento.
> 🚨 **MEDIDO, e mudou o desenho: 11 dos 15 nomes de cliente do quadro passam de 24 caracteres**
> (mediana 28, o maior 56). Com a fonte +2 em 248px cabem ~24 por linha — então o nome **corta
> em 2 linhas** e o inteiro vai no `title` e no modal, que tem 1000px.
>
> ✅ **O MODAL, proposta A:** **uma rolagem só** (a caixa com `max-height`, topo e pé
> `flex: none`, só o corpo rola) · **duas colunas** — esquerda o que se FAZ, direita o que se LÊ,
> e a altura cai quase à metade · cada bloco é um **painel com borda, sombra e cabeçalho** · o
> cliente é o **título**, inteiro · **ler separado de agir**: os dois `<select>` que escrevem no
> ERP desceram para o pé, **ao lado do aviso**, que antes vivia a uma tela de distância deles.
> ⚠️ *"Previsão de entrega"* saiu da faixa: gastava um slot de medida para dizer, numa nota, que
> a medida não vale. No lugar entrou **"Aberta"**. 🔵 Volta quando o aviso prévio mover a
> previsão em +90 dias.
>
> 🚨 **A ESCALA +2 VIROU TOKEN, não pixel na tela** (`.escala-operacao` em `tokens.css`:
> 13/14,5/16/18/22). A regra da casa é *"nenhuma tela escreve tamanho de fonte na mão"*, e a
> tela continua usando `var(--txt-md)`. ⚠️ **Só esta tela** — a escala global mexeria em ~30
> telas que ninguém auditou. ⚠️ `--txt-campo` e `--altura-toque` ficaram fora, de propósito.
> ✅ **E os dois tons de contraste também viraram token** (`--aviso-texto` #B45309 = 5,02:1 e
> `--ok-texto` #15803D = 4,91:1), porque eu os havia escrito à mão 11 vezes — e um valor que
> não existe no sistema *"ou vira token, ou não entra"*.
>
> ✅ **Suítes: 2103 Python** (o vermelho é o `teste_cadastro` conhecido de 04/11, nenhum novo) e
> **710 JS em 37 arquivos**. **25 travas novas** em `painel_card_modal_0511.teste.js`, rodadas
> **3×**. `dist` publicado.
>
> 🚨 **TRÊS DEFEITOS MEUS NO CAMINHO, todos achados por teste ou por asserção:**
> 1. **Encurtei a frase do aviso ao movê-la para o pé** (*"Os dois escrevem na OS do
>    Harmonit"*) e perdi duas informações que ela tinha: que mover grava **a situação** e que a
>    prioridade **reescreve a OS inteira**. Um teste prendia a frase antiga e pegou.
> 2. **O resolvedor de escapes do meu patch estava errado** e o modal foi gravado com **30
>    sequências literais** no lugar dos caracteres. ⚠️ Montar texto por script pede validar
>    **antes** de gravar — eu validei depois.
> 3. **Escrevi `#B45309` nove vezes e `#15803D` duas à mão**, quebrando a regra dos tokens que
>    está escrita no topo do próprio `tokens.css`. Corrigido virando token.
>
> 🔴 **O QUE É DELE AGORA — 3 itens:**
> 1. 🔵 **EXERCITAR NO NAVEGADOR**, que é o que prova (`M9`): abrir um card e ver o cliente como
>    título · conferir que o card não repete o nome da coluna · `Escape` fechando · `Tab`
>    entrando no diálogo · rolar o miolo e ver que o **pé não sai da tela** · abrir os recados de
>    dentro do card e fechar só eles com `Escape`. 🚨 **Sandbox** se for mover card.
> 2. ⚠️ **O limite de 3 dias do *"parado"* é SUGESTÃO MINHA, não número dele** — era a decisão 5
>    do `.md`, e ele mandou seguir sem responder. Vive na constante `PARADO_DEMAIS_DIAS`; trocar
>    é uma linha. 🚨 Teto é regra, e regra é dele.
> 3. 🔵 **O token global `--texto-apagado` (#94A3B8, 2,56:1).** Fiz o conserto **mínimo** (só
>    esta tela, via `.nota`). O de raiz escurece o token e muda todas as telas de uma vez.


> ✅ **05/11 — PAINEL DA OPERAÇÃO, ÁREA E: o TERMO no card e a busca por termo, NO AR.**
> 📘 **Estado mantido em `C:\Users\Lenovo\Desktop\Painel_Operacao_Checklists_PLANO.md`**
> (bloco "📍 ESTADO" no topo, reescrito hoje). Detalhe em
> `movizap_painel/docs/06_Conteudo_das_Telas.md` ("05/11") e em
> `fpsl_weso/docs/fpsl/34_Ponte_MoviZap.md` (seção **5-B**).
> 🔵 Pedido dele, área **E** do plano de 04/11: *"termo no card e busca"*.
>
> 🚨 **O TERMO NÃO É CAMPO DA OS NO HARMONIT** — vive **dentro do texto** da `descricao`, que
> **não está no cache** (vem ao vivo, 1 chamada por OS). Buscar por termo lendo ficha a ficha
> custaria **uma leitura do ERP por card**, e o quadro tem até 600. Virou coluna
> `os_historico.termo` no FPSL, preenchida pela **varredura que já lia a OS inteira e descartava
> a descrição** — a mesma porta por onde a `prioridade` entrou em 29/10.
> ⚠️ **Nenhuma migração do MoviZap**: o dado é do cache do FPSL.
>
> ✅ **O que está no ar:** `fpsl_weso/termo_da_os.py` · coluna `termo` em `os_historico` ·
> `/api/os/por-situacao` devolvendo `termo` · o card escrevendo **`OS 17081` `TERMO 8937`** ·
> o termo também no card aberto · a busca com o **quarto campo** e o **"casou por termo"**.
>
> 📏 **A MEDIÇÃO QUE DESENHOU A EXTRAÇÃO (200 OS lidas ao vivo):** 173 com termo · 27 sem ·
> **0** descrições com dois termos distintos · **0** com a palavra `TERMO` sem número ao lado.
> 🚨 **`TERMO:8927` e `TERMO 8927` na mesma descrição são o MESMO termo** — tratar como
> ambiguidade deixaria um padrão inteiro de OS (a substituição) sem termo. O que devolve nulo é
> termo **diferente**. 🚨 **O número é exigido** (`\d{1,10}`, não `\S+`): com `\S+`,
> *"TERMO DE ADESÃO"* viraria o termo chamado **DE**.
>
> ⚠️ **OS SEM TERMO É 1 DE CADA 7 E A TELA NÃO DIZ NADA** — venda, cartão RFID, chaveiro e
> manutenção não nascem de termo. **Não existe "sem termo" escrito em lugar nenhum**: seria uma
> linha repetida em 85 cards para dizer o que não tem o que dizer.
>
> ✅ **Carga inicial à mão** (`fpsl_weso/scripts/termo_das_os.py`, que **por padrão só relata**;
> `--um` faz uma, `--aplicar` o lote, e **só toca linha com `termo IS NULL`**): das **603** OS do
> cache, **493 com termo** · **109 sem termo nenhum** · **1** que o ERP já não encontra.
> Validei **1** (a OS 17084, termo 8941) e reli o estado antes do lote.
>
> ✅ **PROVA AO VIVO, pelo HTTP e com sessão de verdade:** 44 cards, **42 com termo**; busca por
> `8913` traz **as 8 OS do mesmo termo** com `casou_por = ['termo']`; busca sem resultado devolve
> 0 e diz. 🔵 **É para isto que ela serve:** um termo gera a OS financeira mais uma OS por placa —
> o termo **8802** tem **71 OS**.
>
> ✅ **Suítes:** MoviZap **2103** Python (o vermelho é o `teste_cadastro` conhecido de 04/11) e
> **684** JS em 36 arquivos. FPSL: **80 arquivos, 78 verdes**, com os 2 vermelhos conhecidos
> (`teste_extrair_termo` e `teste_google_login`). Backend reiniciado nos dois, `dist` publicado.
>
> 🚨 **DOIS DEFEITOS MEUS, OS DOIS ACHADOS PELA PRÓPRIA SUÍTE:**
> 1. O teste do *"card sem termo"* asseverava sobre a **tela inteira** e reprovou — a **caixa de
>    busca** diz *"ou termo"*, de propósito. O teste estava errado, não a tela. ⚠️ **Varredura de
>    texto em tela inteira acha o texto certo no lugar errado.**
> 2. O `teste_termo_da_os.py` apontava `storage.DB_PATH` **no import do módulo**, e isso derrubou
>    **10 testes do `teste_ponte_rotas_http`**, que passavam sozinhos — o `pytest` importa todos os
>    arquivos antes de rodar qualquer um, e o último import ganha. Conserto: trocar na **fixture**,
>    com `monkeypatch`. ⚠️ **A casa já tem um `teste_colisao_de_globais` com este nome**, e eu
>    repeti o erro que ele nomeia.
>
> 🔴 **DOIS ACHADOS QUE SÃO DELE:**
> 1. 🚨 **O CRITÉRIO OFICIAL DE VERDE DO FPSL CONTA 60 VERIFICAÇÕES QUE NINGUÉM EXECUTA.** O laço
>    de `docs/fpsl/18_Testes.md` roda cada arquivo **como script**, e arquivo só-de-pytest assim
>    **não roda nada e sai com 0**: `teste_ponte_rotas_http.py` (25) e `teste_criar_os_ponte.py`
>    (35) estão nesse estado **desde 29/10**, e a doc afirmava que *"os dois da ponte rodam nos
>    dois modos"* — é `M12` no instrumento de medida. O `teste_termo_da_os.py` **já nasce com
>    `__main__`**. Consertar os outros dois é duas linhas cada, mas **muda o placar do projeto**,
>    então é decisão dele.
> 2. **A OS 16576 está no cache como NÃO excluída e o ERP responde *"Ordem de Serviço não
>    encontrada"***. O `resync` não a alcança, porque a janela dele é recente. **Não toquei**:
>    marcar exclusão a partir de um script de carga seria escrita que ninguém pediu.
>
> 🔴 **O QUE FALTA NA FRENTE:** as áreas **F** (rastreio e mensagem ao cliente — **é a primeira que
> ESCREVE fora**, WhatsApp ao cliente), **G** (FPSL-Operação em modal) e **H** (WESO ao sair de
> 16490). Todas com passos e testes no `.md`.
> 🔵 **E continua dele:** os itens das **6 etapas sem lista** (15747 · 15797 · 890 · 16489 · 1316 ·
> 15696) e **validar no navegador** — mover um card, marcar 2 de 3, e agora procurar por um termo.
> 🚨 **Começar pela sandbox**: mover card escreve a situação no ERP de verdade.


> 📘 **04/11 — PAINEL DA OPERAÇÃO: o plano das 8 áreas vive em
> `C:\Users\Lenovo\Desktop\Painel_Operacao_Checklists_PLANO.md`** — e **é lá que o estado é
> mantido**, num bloco "📍 ESTADO" no topo, reescrito a cada avanço.
> 🔵 Pedido dele: *"proponha o melhor caminho conforme a metodologia em um .md na area de trabalho,
> ja com os passos e testes por area"* e *"conforme avançar, anote no .md e informe no proxima
> sessao da existencia do arquivo"*.
>
> **As 8 áreas, na ordem decidida** (do que serve amanhã ao que fala com o cliente): **A** checklist
> no card · **B** aviso ao entrar · **C** ao sair vira observação · **D** OBS em modal com anexos ·
> **E** termo no card e busca · **F** rastreio e mensagem ao cliente · **G** FPSL-Operação em modal ·
> **H** WESO ao sair de 16490.
>
> ✅ **NO AR hoje: as áreas A, B, C e D** — migrações **090** e **091**.
> **A/B/C (checklist):** `checklist_modelo` + `checklist_item` com o seed das 3 etapas que ele
> detalhou · `movizap/checklist.py` · **7 rotas** (ler e marcar sob `PNL_1.1`; o **modelo** sob
> `CFG_7.1`, porque a lista muda o card de todo mundo) · selo **"2 de 3"** no card fechado e
> *"checklist"* quando a etapa tem lista e ninguém abriu · a lista no card aberto com
> **+ Adicionar item** e ✕ **só no avulso** · o **aviso ao entrar** com Ok e silêncio de **10 min
> por etapa**, que vem **depois** do mover · e **ao sair, o checklist vira observação do card**.
> **D (a observação em modal):** `os_observacao_arquivo` · bolhas · anexo com lista branca e teto
> de 10 MB · o recado do **sistema** desenhado diferente.
> **23 + 12 testes** de backend e **21** de tela. Suítes: **2092** Python e **678** JS.
>
> 🚨 **O ANEXO NÃO PODE USAR A TABELA `midia`** — o `CHECK midia_tem_um_dono` exige conversa **ou**
> sala, e recado de card não é nenhuma das duas. **O CHECK não foi afrouxado**: ele é o que impede
> mídia órfã. O cofre é próprio, no molde do `formulario_arquivo`, e ⚠️ **não tem backup** — a tela
> diz isso a quem anexa, e arquivo sumido devolve **410**, não 500.
>
> ⚠️ **O componente de bolha NÃO foi extraído da `CaixaDeEntrada.vue`**, embora o plano previsse: são
> ~4 mil linhas na tela mais usada do sistema. **Custo dito: são TRÊS desenhos de bolha agora**
> (Caixa, Chat interno e o novo). Unificar é frente própria.
>
> 🔴 **Faltam as áreas E (termo no card e busca), F (rastreio e mensagem ao cliente), G
> (FPSL-Operação em modal) e H (WESO ao sair de 16490)** — todas descritas no `.md`, com passos e
> testes.
>
> 🚨 **NADA DISSO ESCREVE NO HARMONIT**, e foi decisão dele: mostrei que gravar na `solucaoTecnica`
> exigiria reescrever a **OS inteira** (`SalvarOrdemServico`, a armadilha do endereço), e ele
> decidiu *"Só no MoviZap, como observação"*. Isso derrubou sozinho o maior risco do pedido.
>
> 🚨 **QUATRO MEDIÇÕES QUE MUDARAM O PEDIDO**, e estão no .md com detalhe:
> 1. **A aba Operações do FPSL não é um quadro de cards** — é um **assistente de 4 etapas** que
>    parte de um PDF de termo e gera as OS. O quadro por situação já é o do MoviZap. Decisão dele:
>    *"É o 2, mas usando lá, não montando outra base"* — rotas-ponte finas delegando às mesmas
>    funções puras, com `operacoes_router.py` e `operacoes.html` **intocados**.
> 2. **Não existe coluna OS → termo.** O termo só vive **dentro do texto** da descrição, que **não
>    está no cache** — buscar por termo exige coluna nova e varredura.
> 3. **Não existe a cadeia OS → conversa do cliente**, nem campo de código de rastreio, nem
>    substituição de `{{...}}` em lugar nenhum. Decisão dele para o destinatário: *"é o telefone que
>    estiver na OS nos dados do cliente mesmo"*.
> 4. **Nota fiscal não existe no FPSL** — nenhuma emissão, nenhum envio. *"Nota Fiscal (emitir e
>    enviar)"* é item de **marcar**, e o .md diz isso onde alguém vai ler.
>
> 🔴 **O QUE É DELE nesta frente:**
> 1. 🔵 **Os itens das 6 etapas que ele citou sem lista** — 15747 · 15797 · 890 · 16489 · 1316
>    (escreveu só *"Dados cadastrais"*) · 15696. Etapa sem modelo não mostra botão: nada quebra, o
>    mapa fica pela metade.
> 2. 🔵 **Validar no navegador** quando a tela subir — mover um card para 251, marcar 2 de 3,
>    acrescentar um avulso, mover de novo e achar o recado. 🚨 **Começar pela sandbox**: mover
>    escreve a situação no ERP de verdade.
> 3. 🔵 Três pontos do pedido que não entendi e estão listados no .md: *"Agendar Serviço - Mensagem
>    Bitrix"* · a mensagem automática de véspera (-1d) · *"VENDA CONFIGURAÇÃO: OS venda 16992 —
>    Padrão para novo tipo FPSL - material Entrega OS 0,01"*.
> 4. ⚠️ A lista final que ele colou (estética do agendamento · aba de agendar OS 16547 · tela de
>    cancelamento depois de técnico enviado · aba de orçamentos para editar e reenviar ·
>    atendimento finalizado) ficou **fora deste plano**, anotada como frente própria.


> ✅ **04/11 — O PREÇO DA FICHA ENTRA NA LINHA DO ORÇAMENTO, NO AR** (migração **089**).
> Detalhe na seção **"O PREÇO DA FICHA ENTRA NA LINHA DO ORÇAMENTO"** de
> `movizap_painel/docs/06_Conteudo_das_Telas.md`.
> 🔵 Veio da pergunta dele — *"os campos de orçamento ja trazem os dados dos produtos do tecnico?"*
> — e destravou com a premissa dele: *"o orçamento não vai ao cliente, somente ao técnico."*
>
> ✅ **O que está no ar:** `catalogo(tecnico_contato_id)` em `orcamento.py` (o `CATALOGO` virou
> `CATALOGO_FIXO`), `tecnico_ficha.precos_para_orcamento()`,
> `GET /api/orcamento/catalogo?conversa_id=`, e no modal o preço **nasce preenchido**, editável, com
> o rótulo **"da ficha"**. Migração 089: `servico_tecnico.unidade` (un/km).
>
> 🔵 **As 2 decisões dele:** **E1** o `<select>` traz *"os da ficha + as duas de sempre"* · **E2**
> **preço R$ 0,00 pode ser emitido** (na ficha, zero é cortesia e é diferente de ausente).
> 🚨 **E1 não é conservadorismo, é o que evita um apagão:** havia **287 fichas e 0 preços** —
> catálogo só-da-ficha abriria o modal **sem nenhuma opção** para todos os técnicos.
>
> 🚨 **DOIS ERROS MEUS DE AFIRMAÇÃO, CORRIGIDOS COM MEDIÇÃO** (os dois na mesma conversa, antes de
> eu medir):
> 1. **Eu disse que preencher a linha com o custo "expõe o custo ao cliente"** e propus um campo à
>    parte só para conferência. Falso: o papel vai **só ao técnico** — provado no dado (os 3
>    orçamentos estão na conversa 12845, de contato `relacao='tecnico'`, e o PDF vai nessa mesma
>    conversa). O campo à parte não precisa existir.
> 2. **Eu disse que faltava levantar o `harmonit_id` de cada serviço.** Falso: **o `harmonit_id` é
>    morto.** Ele viaja do backend ao `<select>` e é **descartado** por `linhaNova()`;
>    `ItemDeOrcamento` não tem o campo; `orcamento_item` não tem coluna; o PDF não imprime. **O
>    MoviZap nunca lança item em OS no Harmonit** (`fpsl_ponte` é só leitura). Aqueles dois ids são
>    do **FPSL**, na direção inversa: `services/fechamento.py` lê os materiais que **uma pessoa** já
>    lançou na OS e os reconhece por `idProduto`.
> ⚠️ Nos dois casos eu respondi de cabeça sobre código que não tinha aberto. O conserto foi `grep` +
> ler o fluxo inteiro — e o segundo erro mudava a decisão que eu havia posto na mão dele.
>
> 🚨 **DE QUEM É O PREÇO NÃO VEM DO NAVEGADOR.** A rota recebe `conversa_id` e o **servidor**
> descobre o técnico (`_tecnico_da_conversa`) — a régua da calculadora de KM. **Há teste provando
> que o parâmetro `tecnico_contato_id` é ignorado**, e a prova ao vivo confirmou.
>
> ⚠️ **Quatro bordas, cada uma com teste:** nome igual a uma linha fixa **não duplica** a opção (a
> fixa ganha) · trocar de serviço **não apaga** valor digitado à mão · falha ao ler a ficha devolve
> as duas fixas e **não impede emitir** · serviço desativado sai do `<select>` mas o preço **continua
> gravado**, explicando os orçamentos antigos.
>
> ⚠️ **`orcamento_item.servico` continua `text` RETRATO**, sem FK: mudar o preço na ficha amanhã não
> pode reescrever orçamento já emitido.
>
> ✅ **Prova ao vivo pela rota** (técnico de teste, criado e apagado): sem preço → as 2 de sempre ·
> com 180,00 e 0,00 → as 4, com `da ficha` e sem `harmonit_id` · **Socorro sem preço não aparece** ·
> **Treinamento a 0,00 aparece** · parâmetro do técnico ignorado · 0 sobras.
>
> ✅ **Suítes: 2059 (Python) e 657 (JS), verdes.** Backend reiniciado, `dist` publicado.
> ⚠️ Três textos que diziam *"lista fechada"* foram corrigidos (`M12`), incluindo o **docstring do
> arquivo de teste** — o lugar mais fácil de esquecer.
>
> 🔴 **O QUE É DELE AGORA — 3 itens:**
> 1. 🔵 **Cadastrar preço em UM técnico e emitir um orçamento de verdade.** É o que valida; a suíte
>    não vê tela (`M9`), e hoje **nenhuma das 287 fichas tem preço**.
> 2. 🟡 **O valor do km da ficha virar o preço unitário da linha `KM DESLOCAMENTO`** (hoje R$ 1,00
>    fixo). Não foi junto porque é mudança de outra natureza — proponho quando ele quiser.
> 3. 🟡 **A simetria com o `fechamento.py` do FPSL:** se o orçamento passa a ter 10 serviços e quem
>    lança na OS do Harmonit usa `PAGAMENTO DE TECNICO`, o fechamento continua somando tudo num
>    balde só. Vale medir depois do primeiro orçamento com serviço da ficha.


> ✅ **04/11, FECHAMENTO — TÉCNICOS: as 3 propostas executadas, a 4ª escrita, e a tela fechada.**
> Detalhe nas seções **"04/11, fechamento"** de `movizap_painel/docs/06_Conteudo_das_Telas.md` e
> **Migrações 087/088** de `docs/02_Modelo_Dados.md`.
> 🔵 Ele respondeu às quatro: *"1 ok; 2 o formulario é nosso e o que precisar fazer deve ser feito
> para ajustar o uso para o Movizap, por isso que ja temos ele replicado -- apenas proponha pois é
> demanda de formulario e não de tenicos; 3 apague entao; 4 preencha e mantenha o nome"*. E pediu
> mais um campo: *"crie um campo de flag, junto com os do deslocamento chamado 'Preenche OS'"*.
>
> ✅ **P1 — a `tecnico_origem` SAIU** (migração **087**). 🚨 **As duas medidas foram refeitas na
> hora**, não copiadas da manhã: 0 linhas e **nenhuma ocorrência em código** (só comentários). Não
> foram tocadas a `rota_cache` nem o retrato `agendamento.origem_endereco`/`km`.
>
> ✅ **P3 — a frase que mentia na `Classificacoes.vue` foi apagada.** Era *"A última ativa não pode
> ser desativada"*, e **a regra saiu em 11/08** — o `operacao.py` registra o motivo. `grep` antes:
> só a própria tela citava, nenhum teste prendia. Nada entrou no lugar; o bloco vazio da tela já diz
> o que é verdade.
>
> ✅ **P4 — 287 fichas com cidade e UF, derivadas do nome, e o nome mantido.**
> `scripts/cidade_do_nome_do_tecnico.py`, que **por padrão só relata** (`--um` faz 1, `--aplicar` o
> lote). Validei 1 e reli campo a campo antes do lote. 🚨 **É derivação, e a ficha diz isso de três
> maneiras:** nasce **candidata**, a `observacao` grava a procedência, e **nada preenchido é
> sobrescrito** — a 2ª rodada diz *"a preencher: 0"*. 🚨 **O nome não foi tocado**, e o script prova
> ao fim de cada rodada: os sem ` | ` continuam **16** (são razões sociais, *"CIA DO RADIO"*). ⚠️ Só
> cidade e UF: rua/número/bairro/CEP seguem vazios, e **credenciar continua exigindo rua** — nenhuma
> das 287 ficou "pronta" por causa disto.
>
> ✅ **O campo novo: `preenche_os`** (migração **088**), 4ª pergunta do bloco Deslocamento. ⚠️ Três
> estados (sim/não/**não respondido**): `false` por default afirmaria, das 287, que nenhum técnico
> preenche OS. ⚠️ **Não condiciona nada hoje** — a tela grava e mostra; ligar o fluxo de OS a ela
> seria regra nova, que é decisão dele.
>
> 🔵 **P2 — SÓ PROPOSTA, por decisão dele** (*"é demanda de formulario e não de tenicos"*):
> 📘 **`C:\Users\Lenovo\Desktop\Formularios_Campos_Proprios_P2.md`**.
> 🚨 **O princípio que ele fixou muda o alvo da proposta:** *"o formulario é nosso e o que precisar
> fazer deve ser feito"* — então o limite que achei (**`AJUSTES` não sabe acrescentar campo que não
> exista no mapa do Bitrix**) não é para ser contornado, é para ser **removido**. A proposta desenha
> uma lista `EXTRAS` com `nome` prefixado (`MOVISAT_*`), `nosso_nome` escrito à mão e `depois_de`
> para posicionar; ~meio dia; **o risco está no carregador, que é dos 15**. 🟡 Recomendação mantida:
> fazer **depois do primeiro credenciamento real**, que é o que diz se preço coletado em formulário
> é usável — hoje são **0 solicitações**. Três decisões ficam listadas lá para ele.
>
> ✅ **Suítes: 2043 (Python) e 652 (JS), verdes.** Migrações **085 → 088**. Backend reiniciado e
> `dist` publicado.
>
> 🚨 **UM ERRO MEU NO CAMINHO, e a memória já avisava:** mandei um patch por **heredoc dentro de
> `ssh "..."`** e o shell **local** expandiu os backticks do comentário como substituição de comando
> — `operacao.py` e `M12` viraram *"command not found"* e **sumiram do texto gravado**. O arquivo
> ficou com dois buracos. Corrigido por **arquivo + scp**, que é a regra escrita
> ([[feedback_shell_aspas_ssh]]). ⚠️ A regra dizia "destrói acentos"; o que ela protege é maior —
> **qualquer coisa que o shell local interprete**, e backtick em comentário de código é o caso mais
> provável de todos.
>
> 🔴 **O QUE AINDA É DELE, nesta frente — 3 itens:**
> 1. 🔵 **Abrir `/tecnicos` e exercitar a ficha** (ele disse *"1 ok"* à proposta de abrir, mas a
>    tela segue **não exercitada por ninguém** — e o teste dele acha o que a suíte não vê, `M9`).
>    Agora a lista abre com **287 candidatos com cidade** e 16 sem ficha.
> 2. 🔵 **Credenciar o primeiro técnico de verdade** — respondeu *"depois"*. Exige rua, cidade e um
>    preço.
> 3. 🔵 **O custo entrar no orçamento** — respondeu *"em breve, primeiro a prática do orçamento será
>    validada"*. A linha `PAGAMENTO DE TECNICO` (`harmonit_id` 653939) já existe.
> 🔵 **E as 3 decisões do P2**, no doc próprio.


> ✅ **04/11, 2ª VOLTA — TÉCNICOS: a ficha saiu de dentro da lista e virou TELA, com seta de voltar.**
> Detalhe na seção **"04/11, segunda volta"** de `movizap_painel/docs/06_Conteudo_das_Telas.md`;
> a migração **086** em `docs/02_Modelo_Dados.md`.
> 🔵 Os seis apontamentos dele, todos no ar: *"não gosto desse modelo de quando clico em 'abrir
> ficha', ele cria uma pagina em cima da atual. fica feio (...) Com seta de voltar"* · *"o botão
> pode chamar 'Ficha' pois as vezes é só uma consulta"* · *"endereço puxando pelo CEP"* · *"Banco
> ajuste para dados de pagamento, pode ser TED, PIX, ou boleto"* · *"o campo de deslocamento ficou
> lega, mas layout está quebrado"* · *"o campo 'tecnico no hamronit não tem uso dentro da ficha"*.
>
> ✅ `FichaDoTecnico.vue` em **`/tecnicos/ficha/:contatoId`**; a lista ficou só com a lista, os
> candidatos e o cadastro à mão. **Tela própria e não modal:** oito blocos num modal rolariam dentro
> de uma caixa, com duas barras de rolagem. 🚨 O caminho leva o segmento `ficha` porque
> `/tecnicos/:id` casaria a palavra *"credenciar"* (a rota da `TEC_1.2`) como se fosse um id.
>
> ✅ **O CEP agora distingue as TRÊS respostas** que o backend já dava: achou · *"este CEP não
> existe"* · *"não deu para conferir agora"*. A primeira versão tratava tudo como silêncio. O número
> continua sem ser preenchido — o ViaCEP não sabe o número.
>
> ✅ **Pagamento nos DOIS lados, que é o *"ai amarra eles"* dele** — migração **086**:
> `pagamento_forma` (CHECK `ted`/`pix`/`boleto`) + `pagamento_dados`, e **saíram** `banco`,
> `agencia`, `conta`, `titular_tipo`. No formulário de credenciamento (que é DADO, via `AJUSTES`):
> a página virou **DADOS DE PAGAMENTO**, a lista do titular virou **Forma de pagamento** com os
> nossos três valores, "Banco" virou **Dados para pagamento**, e agência/conta saíram — **34 → 32
> campos**. Há teste comparando as `opcoes` do formulário com o CHECK da coluna.
> ⚠️ **Remover foi seguro porque medi antes:** 0 fichas, 0 dados bancários, **0 solicitações**.
>
> 🚨 **ACHEI UM DEFEITO LATENTE DO MECANISMO DE AJUSTES — tropeçando nele.** O laço de ajustes
> derivava o nome do campo com acumulador **vazio**, e a gravação deriva com o acumulador real:
> então o campo que o registro grava como `banco-2` só podia ser citado como `banco`, que é o nome
> da **página** "BANCO". Um ajuste de rótulo caía nos dois, e citar o nome verdadeiro — o que o
> `conferir_formularios.py --nomes` imprime — **parava a carga**. Agora casa pelos dois nomes, e o
> mais específico ganha. A trava que acusou continua de pé.
>
> 🔴 **A SENHA DO TÉCNICO NÃO EXISTE EM LUGAR NENHUM QUE EU ALCANCE.** 🔵 Ele pediu *"exiba o
> usuario e a senha criada (foi um algoritmo com base no nome, encontre)"* e, depois: *"é para estar
> na documentação que cadastrou eles no harmonit (...) se não encontrar algo objetivamente, deixe só
> o e-mail de acesso mesmo"*. Varri **scripts, módulos e docs dos dois projetos, os docs do
> Harmonit, os planos de sessões anteriores, este arquivo, as duas bases e os arquivos locais**: o
> único gerador de senha do projeto é o do **alistamento de ligações**, e ele deriva do **ramal**. A
> API do Harmonit não devolve senha. ✅ Então a ficha mostra o **e-mail de acesso** (estático, com
> nome e código) e diz em texto que a senha não fica guardada aqui. ⚠️ Falha da ponte devolve
> `email: null` **com motivo** — *"não quer dizer que ele esteja sem acesso"*.
>
> ✅ **O deslocamento, com a causa medida:** as três perguntas de sim/não eram `label.linha` dentro
> da **mesma `.grade`** dos campos de texto, com `align-items: end` — a caixa de seleção assentava
> na linha de base de um campo que tem rótulo em cima. Agora as perguntas têm lista própria e os
> campos têm a sua, com `align-items: start`.
>
> ✅ **Suítes: 2040 verde (Python) e 651 verde (JS)**, sendo 60 + 20 desta frente. Backend
> reiniciado, `dist` publicado.
>
> ⚠️ **UMA CORREÇÃO AO QUE EU DISSE DE MANHÃ:** chamei de "problema pré-existente" o aviso do
> `conferir_formularios.py` sobre o SUPORTE (*"11 campos no banco e 13 no mapa"*). Ele é
> **informativo**: aparece sempre que um formulário tem `fora`, e o SUPORTE tira dois campos. O
> CREDENCIAMENTO passou a ter o mesmo aviso por tirar agência e conta. 🔴 **O outro aviso do SUPORTE
> é real e segue aberto, e não é meu:** *"CPF: informe os 11 caracteres"* num caminho testado.
>
> 🔵 **As respostas dele às 5 pendências de manhã:** 1 abrir a tela → **ok** · 2 credenciar o
> primeiro → **depois** · 3 custo no orçamento → **em breve, primeiro a prática do orçamento será
> validada** · 4 `DROP tecnico_origem` → **proponha** · 5 os 10 serviços no formulário →
> **proponha** · os dois achados → **proponha**.

> 🟡 **04/11 — AS QUATRO PROPOSTAS QUE ELE PEDIU (texto, nada executado)**
>
> **P1 — `DROP TABLE tecnico_origem`** (pendência 4 dele).
> *Objetivo:* tirar do banco a tabela que ninguém lê mais.
> *Hoje:* existe, **0 linhas**, nenhum leitor — `rotas.origem_do_tecnico` e `rotas.lembrar_origem`
> saíram, e há um teste que falha se voltarem. O backup diário continua guardando o esquema.
> *Proposta:* migração **087** com só o `DROP TABLE IF EXISTS tecnico_origem`, e o `DESFAZER`
> recriando as 8 colunas (sem conteúdo, que é 0 de todo modo). Antes de aplicar, repetir as duas
> medidas na hora: `select count(*) from tecnico_origem` e o `grep` por `tecnico_origem` em
> `movizap/`.
> *Por quê:* tabela sem leitor é a próxima a ser preenchida por engano, e o `docs/02` descreveria um
> bloco que a tela não tem. *Risco:* nenhum hoje; se ele voltar atrás no D5, a origem volta a ser
> cadastro, e esta tabela não serviria de novo. *Esforço:* 10 minutos.
>
> **P2 — os 10 serviços no formulário de credenciamento** (pendência 5 dele).
> *Hoje:* o formulário pergunta **6** valores (Instalação simples · com bloqueio ·
> Manutenção/Correção · Substituição no mesmo veículo · entre veículos · Remoção) e **nenhum bate**
> com os 10 da ficha. Consequência medida: **o que chega não vira preço**; aparece como *"o que ele
> respondeu"* e **alguém digita os 10 à mão** em cada credenciamento.
> 🚨 *O obstáculo real, medido:* a definição do formulário vem do **mapa do Bitrix**, e os `AJUSTES`
> só sabem **trocar rótulo/opções/obrigatório** e **tirar** campo. **Não existe caminho para
> acrescentar campo que não exista lá** — foi por isso que o bloco de pagamento reaproveitou dois
> campos em vez de criar.
> *Proposta A (a certa, e a maior):* criar **campos NOSSOS** — uma lista `EXTRAS` no
> `carregar_formularios.py` e `gravar_definicao` aceitando campo sem origem Bitrix, com `nome`
> sintético estável (ex. `MOVISAT_SERVICO_SOCORRO`). Com isso o credenciamento pergunta os 10 e cada
> valor cai direto em `tecnico_preco`. ⚠️ Mexe no carregador dos **15** formulários; exige a suíte
> inteira e o `conferir_formularios.py` antes de ligar. *Esforço:* meio dia.
> *Proposta B (barata):* **tirar os 6** do formulário (`fora`) e assumir que preço se combina fora
> dele, na conversa, e se digita na ficha. *Custo:* perde-se a coleta; *ganho:* o formulário para de
> perguntar o que não tem onde cair. *Esforço:* 15 minutos.
> 🟡 *Minha recomendação:* **B agora, A quando o primeiro credenciamento real mostrar se o preço
> coletado no formulário é usável** — hoje são 0 solicitações, e construir o mecanismo de campos
> próprios antes de saber isso é adiantar trabalho sobre uma suposição.
>
> **P3 — a frase que mente na `Classificacoes.vue`** (achado meu).
> *Hoje:* a tela termina com *"A última ativa não pode ser desativada"*, e **essa regra saiu em
> 11/08** — o próprio `operacao.py` registra a remoção (*"guardar o sistema contra um problema que
> não existe mais só impede o usuário de limpar a própria base"*). É `M12` vivo, numa tela que não é
> desta frente.
> *Proposta:* apagar a frase. Se ele preferir um aviso no lugar, o verdadeiro é *"sem nenhuma ativa,
> ninguém encerra conversa"* — que é o que o bloco vazio da própria tela já diz.
> *Esforço:* 1 linha, mais o `grep` por quem cita a frase.
>
> **P4 — os 287 nomes que já trazem a cidade** (achado meu, medido).
> *Hoje:* **287 dos 303** `contato.nome` de técnico (95%) estão no formato `Nome | Cidade - UF` —
> *"Ademir Rogério | Marília - SP"*; **286** terminam em ` - UF` e o resto varia
> (*"TÉC. Rogerio Marques | Araxá/MG"*, com barra). As 303 fichas nascem **sem cidade**, e cidade é
> metade do que a calculadora de KM precisa.
> ⚠️ *O que NÃO proponho:* preencher as fichas em lote. É heurística sobre nome, e cadastro
> preenchido por adivinhação é pior que vazio — além de que a ficha nasceria "pronta" sem ninguém
> ter olhado, que é exatamente o que a migração 077 avisava.
> *Proposta:* um botão **"sugerir pelo nome"** no bloco de endereço da ficha, que **preenche os
> campos e não grava** (o mesmo desenho do credenciamento recebido), mostrando de onde tirou. Quem
> credencia aceita ou corrige. *Alternativa:* um script de **relatório** que lista as 287 sugestões
> para ele conferir em lote antes de qualquer gravação.
> *Esforço:* 1 h o botão; 20 min o relatório.
> 🔵 *Pergunta que fica para ele:* o `| Cidade - UF` no nome do contato é para **ficar** (veio do
> Harmonit e ajuda a distinguir homônimos na conversa) ou, uma vez que a cidade esteja na ficha,
> **o nome deve ser limpo**? Não toquei em nenhum dos 287.


> ✅ **04/11, MOVIZAP — TÉCNICOS (`TEC_1.1`): a ficha, a tabela de preço e o credenciamento, NO AR.**
> Detalhe na seção **"04/11"** de `movizap_painel/docs/06_Conteudo_das_Telas.md`; o modelo na
> **Migração 085** de `docs/02_Modelo_Dados.md`.
> 🔵 Pedido dele: *"abaixo de 'orçamentos' vamos propor uma tela CRUD dos tecnicos (...) nessa aba
> ter uma ficha de cada 1. como no formulario de credenciamento (...) Também ali que iremos colocar
> o endereço fixo que aparecerá na tela de calculo de KM (...) Dentro vamos colocar uma tabela de
> preço por serviços que ele oferece, padrão a todos (...) Dai o cadastro do tecnico e validação
> dele passará por essa tela."*
>
> ✅ **O formulário de credenciamento existe e o link é `forms.movisat.com.br/f/credenciamento-tecnico`**
> (código `CREDENCIAMENTO`, procedência Bitrix 164, 34 campos / 30 perguntas, 5 blocos). Medido:
> **ativo, com 0 solicitações recebidas** — ninguém se credenciou ainda, então não há passivo a
> traduzir. A ficha espelha os 5 blocos dele.
>
> 🔵 **As 5 decisões dele, tomadas na mesma conversa:** **D1** a lista de serviços é a dele, com
> `Substituição R.`/`I.` = **Retirada** e **Instalação** (são **10**) · **D2** o valor é **CUSTO**
> (*"o que ele nos cobra"*) · **D3** o formulário alimenta a tela *"mas não de forma exclusiva.
> Ainda é permitido fazer a mão"* · **D4** *"Ler todo atendente, escrever owner e admin"* · **D5**
> *"o cadastro alimenta a memória, pode tirá-la. Caso mudem na hora só servirá para aquele
> orçamento. Os demais ja vem com o do cad."*
>
> ✅ **No ar:** migração **085** (3 tabelas, os 10 serviços semeados) · `movizap/tecnico_ficha.py` ·
> **13 rotas** `/api/tecnicos*` (ler sob `TEC_1.1`, escrever sob `TEC_1.2`) · `Tecnicos.vue` com a
> ficha em 8 blocos · **56 testes** de backend + **18** de tela. Suíte inteira **2037 verde** e
> **649 verde** no JS; backend reiniciado e `dist` publicado.
>
> 🚨 **A ENTREGA CONTRARIA, DE PROPÓSITO, UM AVISO ESCRITO DO PROJETO.** A migração 077 diz da
> `tecnico_origem`: *"⚠️ NÃO É CADASTRO (...) o projeto já tem 117 contatos de técnico sem cadastro
> no Harmonit para provar o que acontece quando ninguém mantém."* O aviso continua verdadeiro — é
> por isso que a 077 não inventou cadastro. **O que mudou é que ele pediu o cadastro e disse quem
> mantém.** Registrado nas duas pontas (migração e `docs/02`), para ninguém achar depois que o aviso
> foi ignorado por distração.
>
> 🚨 **A MEMÓRIA DO KM SAIU, E ISSO MUDOU COMPORTAMENTO EM PRODUÇÃO.** `rotas.origem_do_tecnico` e
> `rotas.lembrar_origem` **não existem mais**; a origem vem da ficha, e **o cálculo não grava nada
> de volta**. Dois testes de 26/10 **trocaram de sinal** (o que provava *"grava mesmo falhando"*
> agora prova *"não escreve na ficha"*) — não foram afrouxados: descreviam um comportamento que ele
> trocou. ⚠️ A tabela `tecnico_origem` **continua no banco, vazia e sem leitor**: o `DROP` é
> migração separada e **espera o OK dele**.
>
> 🚨 **TRÊS DEFEITOS MEUS, TODOS ACHADOS PELA SUÍTE, NENHUM POR LEITURA:**
> 1. **`km_valor_centavos` era gravado e nunca lido** — ficou fora da tupla `CAMPOS`, que é quem lê.
>    O valor entrava no banco e a tela nunca o via. É o elo *"quem devolve → quem grava → quem lê"*
>    ([[feedback_campo_novo_nao_entra_sozinho]]), e agora há um teste que compara a tupla com o
>    `information_schema` — coluna nova sem dono reprova na hora.
> 2. **Dois testes meus passavam só pela ordem de coleta** (usavam ficha criada por outro teste).
>    Rodados isolados, estouravam. Cada um monta o próprio técnico agora; rodei **classe por
>    classe** para provar.
> 3. **A `TEC_1.2` nasceu sem rota no frontend** porque "não é tela". O `teste_router.py` reprovou,
>    e está certo: `aba_de` esconde do menu e **não** impede chegar pelo endereço — seria *"não
>    encontrada"*, o defeito da `ATD_5.1` em 06/08. Ganhou rota que **redireciona** para `/tecnicos`.
>
> 🚨 **E UM TEXTO MEU QUE MENTIU MEIA HORA DEPOIS DE ESCRITO** (`M12`): eu documentei que *"nenhuma
> rota do frontend aponta para a TEC_1.2"* e então fui obrigado a criar essa rota. Corrigido no
> `telas.py` e no `docs/03`. Também corrigi o docstring de `calcular_km`, que ainda anunciava *"e a
> memória da origem gravada"*.
>
> ⚠️ **`equipe` PASSOU A SIGNIFICAR TRÊS COISAS** (Times/Atendentes · Fila/Histórico/Solicitações ·
> **preço de técnico**). Foi o caminho para entregar o *"owner e admin"* dele **sem mexer em
> `PERFIS`**, que é decisão dele. Hoje é o mesmo conjunto de pessoas. 🟡 Se ele quiser separar,
> nasce permissão própria — o efeito está anotado no `telas.py`, no `docs/03` e no
> `teste_telas.py`, onde o conjunto fechado do admin teve de nomear a `TEC_1.2`.
>
> 🔴 **O QUE FALTA, E É DELE — 5 itens:**
> 1. 🔵 **Abrir `/tecnicos` no navegador** e exercitar os 8 blocos. **A tela nunca foi aberta por
>    ninguém** — fonte não é comportamento, e o teste dele acha o que a suíte não vê (`M9`).
> 2. 🔵 **Credenciar o primeiro técnico de verdade.** São **303 contatos de técnico e 0 fichas**;
>    credenciar exige rua, cidade e **um preço**, que é o mínimo para o KM e o orçamento usarem.
> 3. 🟡 **Decidir se o custo entra no orçamento.** A linha `PAGAMENTO DE TECNICO` (`harmonit_id`
>    653939) já existe e poderia nascer com o valor da ficha, editável. É mudança numa tela que ele
>    **validou em 26/10**, então não foi junto.
> 4. 🟡 **Decidir o `DROP TABLE tecnico_origem`** (migração separada, já escrita no `DESFAZER` da 085).
> 5. 🟡 **Decidir se o formulário passa a perguntar os 10 serviços.** Ele pergunta **6** hoje
>    (Instalação simples · com bloqueio · Manutenção/Correção · Substituição no mesmo veículo ·
>    entre veículos · Remoção), e **nenhuma bate** com as 10. Consequência medida: **o que chegar
>    não vira preço sozinho** — aparece na ficha como *"o que ele respondeu"*.
>
> 🟡 **DOIS ACHADOS DE BORDA, MEUS, NÃO TOCADOS:**
> - **`Classificacoes.vue` termina com *"A última ativa não pode ser desativada"*, e essa regra saiu
>   em 11/08** — o próprio `operacao.py` registra a remoção. É `M12` vivo numa tela que não é desta
>   entrega; não mexi.
> - **287 dos 303 `contato.nome` de técnico (95%) já trazem a cidade**, no formato
>   `Nome | Cidade - UF` — *"Ademir Rogério | Marília - SP"*. Medido: **286** terminam em ` - UF` e
>   o resto varia (*"TÉC. Rogerio Marques | Araxá/MG"*, com barra). Dá para propor cidade/UF das
>   fichas a partir disso, **como sugestão a conferir**, nunca gravando direto: é heurística sobre
>   nome, e cadastro preenchido por adivinhação é pior que vazio. Proposta, não feito.
>   ⚠️ **Eu quase anotei isto errado:** medi primeiro a coluna `harmonit_tecnico_nome`, que tem
>   **zero** ocorrências, e o `|` que eu tinha visto era o separador do meu próprio `print`. O
>   padrão vive no `contato.nome`. Número que não se mede na coluna certa é número inventado.


> 🚨 **03/11, FPSL — A TELA DA CAR ESTAVA NO AR E INVISÍVEL, E ISSO FOI DEFEITO MEU.** Detalhe na
> **§V9** do `Desktop\CAR_1.1_Financeiro_FPSL.md`. 🔵 Ele perguntou *"o mockup do contas a receber e
> financeiro não esta no ar do FPSL porque?"* e fechou a decisão com *"ja foi aprovado."*
>
> **Estava no ar desde as 09:5x** — e **sem entrada em `telas.py`**, alcançável só por um botão
> dentro da carteira. Eu a fiz nascer como *"segunda página"* (a decisão **D-a**, rotulada contorno)
> esperando *"a posição no menu"*, que estava na minha lista de pendências dele **desde 28/10**.
> 🚨 **Mas a decisão já estava tomada: aprovar o mockup em 30/10 era aprovar o lugar da tela.** Eu
> tratei como pendente algo decidido — o item 2 do Bloco 1 deste arquivo.
> 🚨 **É o `M10` na forma mais barata:** a porta trancada de 14/08 ao menos respondia 403; aqui não
> havia porta. ⚠️ **E rotular contorno não é mitigar contorno** — faltou a pergunta seguinte: *"com
> este contorno, como é que ele chega na tela?"*.
>
> ✅ **Corrigido:** `CAR_1.2 · Gerar Contas a Receber` em `telas.py`, mesma permissão
> `contas_receber` (é a mesma aba em dois passos; permissão nova daria **gerar sem poder conferir**).
> O `sidebar.js` acende pela **rota**, não pela permissão — precedente do `config`, que já cobre duas
> telas. **Menu do owner: 12 → 13 telas**, e a trava do `teste_perfis` **ficou vermelha no mesmo
> minuto**; subi com o motivo escrito. ✅ **As abas concedíveis seguem em 8, e era para seguir** — as
> duas contagens medem coisas diferentes, e confundi-las é o `X0`.
> **Verdes sem tocar:** `registro_telas` 53 · `contrato_sidebar` 47 · `barra_status` 99 ·
> `roteadores_painel` 116 · `car_router` 166.
>
> 🔴 **O que AINDA impede outra pessoa de ver:** a aba **`contas_receber` segue concedida a
> ninguém** (a Karla, 526, tem `["financeiro","contratos"]`). Ele vê por ser **owner**. ⚠️ Então
> *"está no ar"* tem hoje dois sentidos: existe e está no menu **do owner**; para quem vai usar todo
> mês, **ainda não existe**. **Conceder é ato dele.**

> ✅ **03/11, MOVIZAP — O CARD DA LISTA: o selo e a hora foram para a COLUNA DA DIREITA, NO AR.**
> Detalhe na seção **"03/11"** de `movizap_painel/docs/06_Conteudo_das_Telas.md`.
> 🔵 Pedido dele, com a seta desenhada na imagem do card: *"consegue puxar essas informações mais pra
> direita e aumentar os caracteres do nome do contato"*, e antes: *"valide certamente antes do
> ajuste"*.
>
> 🚨 **A validação mudou a proposta, e é o motivo de ele ter pedido para validar.** A conta de CSS
> dava *"o nome tem ~89 px, ~12 caracteres"* — e bate com a imagem (*"Vitória Oliv…"* tem 12). Mas o
> dado acrescentou duas coisas que eu não sabia: **68,1% dos 1.014 nomes da base são cortados hoje**
> (mediana **14**), e **o botão varia de "Entrar" a "Ir para a aberta" em 166 linhas (16,4%)** — ou
> seja, **o nome mudava de tamanho a cada linha**, sobrando ~5 caracteres nas do botão comprido.
> Sem medir, eu teria movido o selo e deixado a coluna elástica, e o defeito principal ficaria.
>
> **No ar:** o selo de não lidas, o selo de nota e a hora empilhados **acima do botão** — o espaço
> que já estava vazio, porque o botão é centralizado na vertical e o nome fica no topo. **A coluna
> tem largura FIXA (`flex: 0 0 100px`)**, e é ela que cumpre o pedido: **toda** linha dá ao nome
> **~144 px, ~18-19 caracteres** (eram ~12, e ~5 nas 166). **Nomes que cabem inteiros: 31,9% → 73,8-76,2%.**
> 🔵 E a bolinha na borda direita é onde o WhatsApp a põe — voltou à convenção, não foi invenção.
>
> ⚠️ **O que se perde, dito:** o selo e a hora **deixam de ser área de clique** da conversa — estavam
> dentro do `<button class="conversa">` e botão dentro de botão é HTML inválido. O resto do card
> continua abrindo.
> ⚠️ **E eu perdi um comentário no movimento** (o que explica que o selo de nota vem do Notificador,
> e **não** da consulta da lista — a mais quente do painel, com ordem posicional de parâmetro).
> Devolvido, e **o teste agora prende o texto**.
>
> **Provas:** `card_direita_0311.teste.js` **11** · suíte JS **631 passaram, 0 falhas** (eram 620) ·
> suíte Python **1.972 passaram, 1 pulado, 0 falhas** (rodada como `claude`, não root — o
> `teste_vigia_resumo` lê `crontab -l` e dá falso vermelho como root) ·
> build feito (`M16`) e o bundle no ar traz `.conversas__direita{flex:0 0 100px;…}`.
> 🔴 **Falta dele: abrir a Caixa no computador E no celular.** O jsdom não calcula largura nem
> recorte — é literalmente o que falha aqui —, e abaixo de 860 px a coluna nova não foi exercitada em
> aparelho nenhum.


> ✅ **03/11 — FPSL/CONTAS A RECEBER: A TELA OPERACIONAL NO AR NA PRODUÇÃO (G1-G5).
> Controle em `C:\Users\Lenovo\Desktop\CAR_1.1_Financeiro_FPSL.md` — §V7.** 🚨 **Não duplicar a
> lista aqui.** Spec na VPS: `docs/fpsl/32_Contas_a_Receber.md` — **§13**.
>
> 🔵 **Pedido dele:** *"vamos continuar o 'financeiro' e 'contas a receber' no FPSL, pelo mockup,
> base de op financeira, etc"*. Feito pelo mockup aprovado em 30/10 e pela base de OS financeira
> (situação **15746**).
>
> ✅ **SUBIU COM AUTORIZAÇÃO DELE** (*"Sim, subir tudo e reiniciar"*): **15 arquivos**,
> `systemctl --user restart fpsl-weso` (unidade de **usuário** — o `systemctl` de root responde
> *"Unit not found"*), `GET /painel/contas-receber/gerar` → **200**, as 4 rotas novas de leitura
> **401 sem token**, nenhum erro no journal. As 3 colunas novas da `car_leitura` entraram pelo
> `migrar()` (provado idempotente numa base velha, e a linha antiga sobrevive com `escopo` nulo).
> **A aba Operações não foi tocada** (`sha256` dos 8 `operacoes_*.py` e do `pdf_extractor.py`
> conferidos). ⚠️ **Não commitei: ele não pediu** — árvore com esses 15 arquivos.
>
> ⚠️ **O caminho foi por STAGING, e a recusa saiu de graça:** a primeira cópia para `~/fpsl_weso` foi
> **recusada pelo classificador de produção**, então provei tudo numa cópia limpa de
> `git archive HEAD` (`~/staging_g1`, com `.env` e **cópia** do banco) — e foi lá que os dois
> defeitos abaixo apareceram, antes de valerem algo.
>
> **Entrou: G1 · G2 · G3 · G4 · G5.** A tela operacional em **`/painel/contas-receber/gerar`** (um
> documento por CLIENTE, fixo × variável lado a lado, seleção por linha, rodapé do selecionado) · a
> **parte variável** nasce (`car_variavel.py`, puro) · **vínculo por clique** nos dois lados (o
> contrato e a OS, com o `cobrar` de cada item à vista) · **fechar a competência** com autor e
> assinatura · **"ficaram fora"** como tabela. **G6 espera a D8.** **Rotas 21 → 27.**
> ⚠️ **Nenhuma tela nova em `telas.py`:** é a **segunda página da mesma `CAR_1.1`**, mesma permissão,
> mesma posição no menu — *"a posição no menu"* é decisão dele em aberto desde 28/10, e a porta
> continua a carteira, com um botão.
>
> 🚨 **O NÚMERO QUE EXPLICA TUDO, medido hoje na base real: a tela geraria R$ 240,00.** São as OS
> **16896** e **16899** (MOTO HELP, R$ 120 cada). **481 documentos, 1 gerável, fixo `None`** — porque
> **`car_evento` segue com ZERO linhas**: ninguém clicou em *"Adotar as 274 propostas"*. O Harmonit
> cobrou **R$ 164.943,88** da mesma carteira no mesmo mês. 🔴 **Adotar as propostas é o que destrava o
> lote**, e continua sendo o primeiro passo dele desde 30/10.
>
> 🚨 **A régua da parte variável foi medida outra vez e reproduz a de 30/10:** **105 OS** em 15746,
> **57 finalizadas**, fila de **3 OS / R$ 1.320,00**. Fora: **23 o Harmonit já faturou** · 6 não
> finalizadas · 2 sem item a cobrar · **1 sem cliente nesta base** (a 16846, R$ 1.080,00 que não pode
> virar documento).
>
> 🚨 **DOIS DEFEITOS MEUS, PEGOS POR TESTE ANTES DE VALEREM ALGO, e o primeiro era grave:**
> (1) **seleção vazia virava "a carteira inteira"** — `cnpjs: []` caía num `if apenas else None`, e
> quem desmarcasse todos os clientes e clicasse em **Fechar competência** fecharia o mês inteiro,
> calado (a mesma linha estava no CSV); (2) **um contador só afogaria o achado** — em 481 de 481
> documentos a pendência é *"sem preço na CAR"*, então *"481 exigem conferência"* esconderia os **70**
> com amarração errada e os **26** usando sem faturar. Agora são dois números, e o cartão mostra o
> segundo.
>
> 🚨 **`INATIVO` junta TRÊS coisas e só UMA proíbe cobrar** (termo não assinado · cancelado · sem
> placa ativa), e termo sem assinatura é a maior parte da carteira — inclusive o **8711 da MOTO HELP,
> que o Harmonit fatura hoje**. A `car_prefatura` passou a expor um booleano **`cancelado`**, e o
> lote tira **só esse** da soma e das linhas. ⚠️ Régua por texto do `motivo` seria
> [[feedback_primeira_ocorrencia_e_aposta]] outra vez.
>
> ⚠️ **E a casa NÃO põe separador de milhar:** `somar_textos` devolve `"1080,00"`. Meu teste esperava
> `"1.080,00"` e **estava errado**; corrigi o teste **e** a tela nova, porque *"R$ 1.080,00"* ao lado
> de *"R$ 1080,00"* na mesma tela parece erro. 🟡 Trocar a convenção é uma linha em dois módulos e na
> tela, e é **decisão dele**.
>
> **Provas:** `teste_car_variavel` **59** · `teste_car_lote` **87** · `teste_car_router` **166**
> (eram 134, com 27 rotas) — **0 falhas nas três**. Duas travas de contagem subiram **deliberadamente**:
> `teste_car_tabelas` (as 3 colunas da `car_leitura`) e `teste_barra_status` (**14 → 15 páginas**, e
> ela pegou na hora). As 5 rotas novas entraram na **matriz do `teste_roteadores_painel`** no mesmo
> dia, que é a lição do X0.
> **A suíte inteira na cópia de staging: 79 arquivos, 74 verdes** — e os **5 vermelhos são
> idênticos na cópia pristina do `HEAD`**, logo nenhum é meu (4 precisam do servidor no ar, 1 é o
> `teste_extrair_termo` conhecido). ✅ **Depois do deploy, na produção:** `teste_roteadores_painel`
> **116 OK, 0 falhas** e `teste_perfis` **29 OK, 0 falhas** — eles batem em `127.0.0.1:8004` e por
> isso **não podiam** rodar em staging.
> ✅ **A suíte inteira na PRODUÇÃO, depois do deploy: 79 arquivos, 77 verdes, 2 vermelhos** — e os
> dois são de **DADO, não de código**.
>
> 🚨 **O critério de verde do FPSL passa a ser 2 vermelhos conhecidos, não 1.** O segundo é o
> **`teste_google_login`**, que falha igual na cópia pristina do `HEAD` e denuncia uma coisa de
> verdade: **DUAS contas do painel com o MESMO e-mail de vínculo** — `Caio` (id 47, **ativa**, já
> entrou pelo Google) e `Thiago` (id 570, **inativa**) têm as duas `thiago@movisat.com.br`. E a busca
> do 1º login casa por e-mail com `fetchone()` sem unicidade: o SQLite devolve **a do Caio**, que já
> tem `google_sub` gravado — então **quem entra com `thiago@` entra como Caio**. ✅ Sem escalada (as
> abas são idênticas), 🔴 **mas com trilha de auditoria errada: toda ação do Thiago grava
> `por = "Caio"`** — e nesta aba `por` é o autor de evento de dinheiro **imutável**. 🟡 **Achado meu,
> decisão dele**, três caminhos: corrigir o e-mail da 47, ativar a 570, ou renomear a 47 para Thiago.
> ⚠️ É **🟡 e não 🔵**: não há frase dele pedindo isto, e *"só ele decide"* não transforma achado meu
> em demanda dele. ⚠️ Até decidir,
> o teste fica vermelho — **e é bom que fique**.
>
> 🟡 **Um achado menor, para ele apagar: a produção tem três sobras em `painel_usuarios` —
> `zz_teste_google`, `zz_teste_perfil` e `zz_teste_roteadores`.** É por causa delas que o
> `teste_perfis` falha na **primeira** passada (ele apaga o usuário no início e tropeça na sobra) e
> passa na segunda.
>
> 🚨 **O `M9` segue valendo: nenhuma das 312 verificações olha a tela.** Em 29/10 ele achou **8
> defeitos** abrindo uma tela com tudo verde.
>
> 🔴 **OS PRÓXIMOS PASSOS, COM A ORIGEM DE CADA UM, estão na §V7-F do documento de controle** —
> 🚨 **não duplicar a lista aqui**. Em uma linha, na ordem: **dele** → abrir a tela (🔵
> *"valide de fato o que foi feito ou não, sempre fatos"*) · adotar as 274 propostas (🔵 opção
> escolhida em 03/11) · conceder a aba `contas_receber` (🟡) · **D6** e **D8** (🔵) · a identidade
> Caio/Thiago (🟡). **Meu e desbloqueado:** o comparativo cobrado × gerado do **G6**, que não depende
> da D8 (🟡) · derrubar o contorno da data lendo o `ObterTimeLine` das **3** OS da fila (🟡).
> ⚠️ **As 9 decisões desta volta estão na §V7-D no formato `Objetivo / Hoje / Por quê / Reavaliar se`,
> e as DUAS que são contorno estão rotuladas** (onde a tela mora, e a competência sair da
> **previsão** em vez da finalização).
>
> 🟡 **E a §V8 é a PROPOSTA do que faltou do plano** (🔵 *"prponha o que faltou do plano"*):
> `F7` · `F8` · `F9` · `G6` · o triplete · `D9` · `D10`. 🚨 **Nada implementado** —
> *"primeiro proposta, depois ação"*. 🚨 **Não duplicar a lista aqui.** Os três achados que ela traz,
> medidos em 03/11:
> (1) **a `F7` não é frente nova** — existe um `sync_inadimplencia` **desligado desde 17/06** que faz
> **1.826 chamadas/dia** (1 Harmonit + 1 WESO por cliente, 913 clientes) e **ESCREVE na WESO**
> (`situacao = Inadimplente`); o espelho da `F1` responde a mesma pergunta com os **20 `GET`** que já
> acontecem: **148 vencidos · R$ 116.474,24 · 53 clientes** (era *"147, R$ 109.729,48"* em 28/10 —
> **o número mudou, e por isso não se copia**);
> (2) 🚨 **um erro meu no plano: o `G6` NÃO espera a `D8`** — só a *emissão* espera; o **comparativo
> cobrado × gerado** já tem os dois lados na resposta do `/gerar`, e ele tem de existir **antes** de
> alguém falar em desligar o faturamento automático do Harmonit;
> (3) **a `F9` é para APONTAR, não consertar** — dos 274 clientes faturados com termo resolvido, **192
> batem** e **82 não** (70 é remapear, 12 é investigar), e conserto em lote escreveria na `CTR_1.1` a
> partir de uma inferência minha.
> ✅ **E uma suposição minha caiu:** a `D10` (subir os PDFs) **não** é pré-requisito do triplete — as
> três pernas já estão na base (`assinado` 3.056/1.543 · `harmonit_assinado` 3.507/1.091 ·
> `contrato_placa.base` 5.146/1.651/15).
> 🔴 **4 decisões novas, D11-D14 (§V8-H):** onde mora a fila de cobrança · **liga a inadimplência?**
> (e a carência continua 7 dias?) · a correção da amarração mora na CAR ou na CTR · os nomes e cortes
> dos **6 estados** do triplete.
> ⚠️ **O que eu NÃO propus, e o motivo está escrito:** cobrar pelo WhatsApp (a ponte de hoje é
> FPSL→MoviZap **para OS**; o inverso não existe, e é frente própria) · desligar o automático do
> Harmonit · Asaas · conserto em lote da amarração.


> 🟢 **28/10 — FPSL / PAINEL DO FINANCEIRO (`CAR_1.1`): NO AR NA PRODUÇÃO, E0→E10
> FECHADAS. Controle de progresso em `C:\Users\Lenovo\Desktop\CAR_1.1_Financeiro_FPSL.md`** —
> 🚨 **não duplicar a lista aqui**; aquele arquivo abre com uma seção **"COMECE AQUI"** reescrita
> com o estado de chegada.
>
> **Decisões dele nesta volta:** permissão **`contas_receber` nova** (7 → 8 concedíveis), e **subir
> se a suíte fechasse**. Fechou.
>
> **No ar e provado:** 16 rotas em `/painel/api/car` · `CAR_1.1` no menu · tela
> `/painel/contas-receber` (**200**) · API sem token (**401**) · as **3 tabelas `car_*` nasceram no
> `data/fpsl.db`** no restart das 14:24. **73 arquivos de teste, 71 verdes**, os **2** vermelhos de
> sempre (`teste_extrair_termo`, que espera decisão dele, e 1 falha de dado em
> `teste_higiene_placas_weso`). `sha256` do `pdf_extractor.py` e dos 8 `operacoes_*.py`
> **idênticos antes e depois** — a aba Operações não foi tocada.
>
> ✅ **Ponta a ponta na produção, com token do owner:** o grid devolve **4.599 contratos** (965
> ativos · 3.634 inativos · **224 divergências**) e a pré-fatura **2.993 placas cobráveis, ZERO com
> preço, total `None`, cobertura 0,0 %** — porque **nenhum preço foi lançado na produção ainda** (a
> validação da E6 foi em cópia do banco). A fila abre no maior: **Horse, termo 765, 335 placas**.
>
> ✅ **Ele JÁ abriu a tela** (*"a tela está vista"*) e tirou dela dois apontamentos, os dois
> procedentes — mais uma vez o `M9`: 1.845 verificações verdes não viram nenhum dos dois.
>
> 🚨 **1. A RÉGUA DO DINHEIRO ESTAVA ERRADA, e a correção é dele:** *"as placas ativas são somente as
> que estão na Weso ativa, conforme as documentações"*. Medido em 28/10 contra o cache da WESO (que é
> o `/Veiculos/Consultar` **inteiro**: 1.928 veículos, atualizado 04:15): o universo cobrável de
> outubro é **1.059 placas, não 2.906** — **36 %**. **1.843 placas cobráveis pelo contrato não
> existem como veículo na WESO** (contratadas e nunca instaladas), e do outro lado **803 têm
> rastreador `Instalado` e nenhum contrato cobrável** — 769 sem contrato algum, 36 `RESCINDIDA`, 4
> `SUBSTITUIDA`: receita vazando hoje.
> 🚨 **E isso RETIRA a recomendação que eu dei de manhã:** a **Horse**, primeira da fila com 356
> placas, tem **ZERO** instalada. Lançar preço na fila teria faturado **335 placas fora de serviço**.
> **4 decisões dele** abertas por isso (§V2-B do documento de controle).
>
> 🚨 **2. A tela "só parece informativo"**, e ele vai **gerir o contas a receber ali todo mês** →
> **proposta de 6 blocos no §V2-C**, nada implementado (*"primeiro proposta, depois ação"*). O
> primeiro bloco é o conserto da régua; o segundo é o **botão de fechar o mês**, que não existe.
>
> ✅ **3. Enxuguei a tela** a pedido dele (*"remova os comentários que fez na tela"* → o texto
> didático visível): 10 trechos fora, e o que a `M12` exige **ficou** (não emite boleto, não escreve
> no Harmonit, vencimento não existe, total é só mensalidade, cancelar não mexe em placa).
>
> 🔍 **4. Auditoria do entregue (pedido dele): 9 achados, 5 fechados na hora** (§V2-D). 🚨 **Dois são
> meus e seguem abertos:** `POST /prefatura/fechar` **não tem botão** — `car_leitura` continua sem
> escritor **pelo uso**, que é justo o que eu disse ter consertado ao criar a rota — e
> `GET /termo/{id}/historico-preco` **ninguém chama, nem teste**. 🚨 **Os outros cinco são deriva do
> PROJETO, não da CAR:** o `Mapa.md` mandava a próxima sessão editar `abas.py`, que **deixou de ser
> fonte em 17/08** e diz no topo *"não acrescente tela aqui"* (a fonte, `telas.py`, **não estava no
> Mapa**) · o índice de `docs/fpsl` **parava no 24**, com **9 docs invisíveis**, incluindo o **33, a
> leitura primeira do FPSL** · a lista de routers parava no `os_scan_router`, faltando **4** · o doc
> **18** parou em 19/08 (*"804/22"*, hoje são **73 arquivos**) e dizia *"tudo aqui é só leitura"* · o
> doc **17** listava **3 permissões aposentadas** e **não listava 4 que existem**. Tudo corrigido,
> com backup `.bak_pre_auditoria`.
>
> 🔴 **O que continua sendo o primeiro passo dele:** **conceder a aba `contas_receber`** a quem vai
> usar (a Karla, `painel_usuarios` 526, **não** ganhou nada de carona). As decisões que travam o resto
> estão nas voltas 3 e 4, abaixo — e a que destrava tudo é a **D5**.
>
> ---
>
> 🟢 **MESMO DIA, VOLTA 3 — O ALVO DA FRENTE MUDOU, por decisão dele:** *"a aba contas a receber
> deverá substituir a do harmonit de faturamento, então por isso precisará ser melhorada"*. A spec
> da manhã dizia o contrário (*"o Harmonit emite; a CAR calcula, compara e aponta"*). **Detalhe em
> §V3.**
>
> 🚨 **A Movisat JÁ RODA um contas a receber, e a CAR não lia nada disso.** Medido ao vivo, só com
> `GET`: **recebido** ago R$ 174.004 · set R$ 220.113 · out R$ 179.780, e **R$ 162.650 já lançados
> para novembro**. A amarração vem na própria descrição —
> `"Faturamento do contrato Nr. 3433. Mensalidade ref. período 10/2026."` —, e **264 de 289**
> lançamentos trazem o número do contrato, **241 batendo num termo único** da base.
>
> 🚨 **TRÊS COISAS QUE ISSO CORRIGE NO MEU PRÓPRIO PLANO, e o padrão dos três é o mesmo — eu afirmei
> limite sem tentar a chamada:** (1) escrevi *"731 chamadas é frente própria"* para adiar a
> conferência, e são **2 `GET` por mês**, sem CNPJ; (2) escrevi *"o universo cobrável tem ZERO
> valor"*, verdade na minha base mas apresentada como estado do negócio, que fatura ~R$ 180k/mês;
> (3) escrevi que a parte variável esperava *"a lista de itens do catálogo"*, e **o classificador
> existe: `centroCusto`** — estava escrito no `docs/harmonit/04_Financeiro.md` do próprio repositório.
>
> 🚨 **O LIMITE DURO DA SUBSTITUIÇÃO: a API financeira do Harmonit é 100% LEITURA.** Varri o
> `swagger.json`: não existe rota de criar cobrança, faturar ou emitir. Mas o dado diz por onde se
> faz — o `pixCopiaECola` de todo boleto aponta **`pix.asaas.com`** e o `contaCorrente` é **`Banco
> Asaas`**: **o Harmonit não é o emissor, é a tela que manda no Asaas.** ⚠️ E o Harmonit **continua**
> faturando sozinho: substituir exige **desligar o automático lá**, senão o cliente recebe **dois
> boletos**.
>
> ✅ **A régua dele já estava escrita — por ele**, em `C:\code\termos_harmonit`: o docstring do
> `contas_a_receber.py` dele diz: *"A cobrança é pela
> WESO em uso (rastreador Instalado)"*, com o triplete **WESO·Clicksign·Harmonit**, os **6 estados** e
> o *"aguardando"* de 90 dias. Era isso o *"conforme as documentações"*. **749 pastas de cliente** em
> `Downloads\Termos Harmonit por Cliente`, `linha.py` com a linha do tempo e
> `placas_fora_de_contrato.csv` em cada uma. **A proposta porta essa régua; não inventa outra.**
>
> ---
>
> ✅ **MESMO DIA, VOLTA 4 — O LEVANTAMENTO `F0` FEITO (*"siga com o levantamento"*), e ele derruba os
> MEUS dois números grandes. Detalhe em §V4.** 11 CSVs em
> **`C:\Users\Lenovo\Desktop\CAR_levantamento_2026-10-28\`**.
>
> 🚨 **Primeiro achado: a competência do Harmonit NÃO é o mês de vencimento.** Das 261 mensalidades
> baixadas em outubro, **233 são de referência 09/2026**. Duas consequências de desenho: **o mês
> corrente não está faturado quando acontece** (a gestão mensal roda sobre o mês fechado anterior), e
> a CAR tem de **indexar pela descrição**, varrendo vários meses de vencimento. 🔵 De carona: o
> Harmonit já tem mensalidade lançada **até 2027-09**, decaindo com a vigência — **previsão de
> receita pronta**.
>
> 🚨 **Segundo achado: meus números por termo estavam inflados pela amarração.** A hipótese veio do
> dado: a **XOMV** aparecia nos dois lados. Ela é faturada no termo **306** e usa **53 placas** nos
> termos 8531/8754/8802 — e minha conta leu isso como *"cobra sem usar"* **e** *"usa sem cobrar"*, ao
> mesmo tempo.
>
> | | por termo (como eu media) | **por cliente (como se cobra)** |
> |---|---|---|
> | usa e é faturado | 126 · R$ 77.353 | **216 clientes · 1.027 placas · R$ 150.332** |
> | usa e **não** é faturado | 512 · *est. R$ 198.872* | **25 clientes · 80 placas · est. R$ 11.710** |
> | é faturado e **não** usa | 140 · R$ 85.524 | **50 clientes · R$ 12.544** |
>
> **92% das placas em uso estão em cliente que É faturado**, e **85%** do grupo "faturado sem uso" é
> cliente que usa placa em **outro termo**. ⚠️ **Errei duas vezes no mesmo dia, do mesmo jeito: medi
> por termo e apresentei como estado do negócio. A unidade da cobrança é o CLIENTE**, porque é dele
> que sai o boleto; o termo é a trilha do documento.
>
> ✅ **E duas coisas limpas:** de todas as mensalidades de 09/2026, **só 1 lançamento (R$ 69,44)** não
> acha termo; e **nenhum contrato tem dois valores na mesma competência** — a semeadura de preço da
> **F4** é cópia direta, sem conflito.
>
> 🔴 **O que sobrou cabe numa tarde dele:** `VAZAMENTO_cliente_usa_sem_faturar_2026-09.csv` (25
> clientes) e `RISCO_faturado_sem_uso_nenhum_2026-09.csv` (50 clientes).
>
> ---
>
> 🔴 **A PROPOSTA DA OPERAÇÃO: 9 blocos em 3 fases (§V3-F, corrigida por §V4-D), e o placar da frente
> agora os lista.** `F0` ✅ feito · `F1` espelho do faturado (2 GET/mês, rotina nasce desligada) ·
> `F2` as três colunas **no cliente** · `F3` a régua dele portada · `F4` **preço semeado: 272
> contratos de uma vez** · `F5` fechar o mês (a rota existe, **falta o botão**) · `F6` parte variável
> por `centroCusto` · `F7` fila de cobrança (**147 boletos, R$ 109.729,48**) · `F8` emissão (lista
> primeiro, Asaas depois) · **`F9` consertar a amarração termo↔placa**, sem o que toda conta por termo
> mente nos dois sentidos.
>
> 🔴 **A decisão que destrava tudo é a D5:** *posso semear o preço do faturado do Harmonit, com você
> como autor e o lançamento como documento?* É isso ou digitar 1.189 contratos à mão. As outras cinco
> (D6-D10) estão no **§V3-G**.
>
> ⚠️ **Nada da volta 3 e da volta 4 foi implementado** — *"primeiro proposta, depois ação"*. As duas
> voltas foram **medição e desenho**: nenhuma linha de código da CAR mudou depois do deploy das
> 14:24.
>
> ⚠️ **Um desvio do plano, deliberado:** a `CAR_1.1` entrou **logo depois da `CTR_1.1`**, e não
> depois do bloco `CFG` como o plano dizia — a ordem de `TELAS` é a ordem do trabalho, e config no
> fim é a convenção do menu. **Nenhuma tela existente mudou de posição relativa**; reverter é mover
> um bloco em `telas.py`.
>
> 🔴 **Segue esperando decisão dele (nada disso trava o que está no ar):** quais itens do catálogo
> do Harmonit se cobram do cliente (sem isso a **parte variável não nasce, e a tela declara que não
> nasceu**) · dia de vencimento, multa e juros · a posição no menu · aprovar a spec
> `docs/fpsl/32_Contas_a_Receber.md`. **X1** (6 truncamentos de CNPJ na `CTR_1.1`) e **X2** (11
> campos de CNPJ dos formulários, conserto no MoviZap) **continuam abertos**.
>
> ⚠️ **Árvore do git: 21 arquivos sem commit** — não commitei, ele não pediu.

> 🟢 **SPRINT DE 26/10 — 4 DOS 6 BLOCOS NO AR. Controle de progresso em
> `C:\Users\Lenovo\Desktop\Sprint_2026-10-26_MoviZap.md`** — 🚨 **não duplicar a
> lista aqui**, o progresso se marca naquele arquivo.
>
> **No ar:** aba **Orçamentos** (`ORC_1.1`, ✅ validada por ele) · **layout e
> texto do agendamento** (quadro monoespaçado, trava com botões nomeados,
> calendário único, zero diálogo do navegador) · **calculadora de KM** (com o
> **link do Google**, sem API, como caminho principal) · **pasta de coleta das
> gravações** (lado da VPS + `.exe` **0.7** compilado, sha `775586093355c9ce…`).
> **1833 Python · 506 JS** (eram 1746/440) · migrações 076 → **078**.
>
> 🔴 **Não começados:** **bloco E** (play da jornada e pausa Almoço — o de maior
> risco: mexe na régua de presença de 9 pessoas, e o curativo e a borda de
> início têm de parar de agir sem play) e **bloco F** (ferramentas de grupo —
> depende de medir se a Evolution expõe `leaveGroup`).
>
> 🔴 **Falta dele:** validar no navegador (ele pediu para deixar para depois da
> entrega — o quadro monoespaçado só se prova **no celular**) · instalar o
> agente **0.7** nas etapas que decidiu (PC dele → Claudia → os 4 que falam →
> Ludmila e Rodrigo **só depois de saber por que estão mudos desde 22/10**) · 🟡
> a chave da Routes API ficou **opcional** (o link resolve) · e a **gravação
> desligada em 6 dos 7 PCs**, não decidida desde 16/10.
>
> ⚠️ **Árvore do git: 33 arquivos sem commit.**

> 🔴 **A SESSÃO DE 23/10 FECHOU COM TRÊS FRENTES. O primeiro passo é DELE
> nas duas primeiras.**
>
> **1. Formulários → design, validação e o PLANO** — arquivo próprio, por
> pedido dele: **`C:\Users\Lenovo\Desktop\Formularios_Movisat_Design.md`**
> (agora com o **plano de 6 blocos**, seção 8). Mockup dos 4:
> **`https://claude.ai/artifact/TaLTfBB9XBT35J8ykd8YBj`**.
> 🔴 **Falta dele:** abrir o mockup **no celular**, e decidir **D1 a D9**
> (seção 7 do arquivo). **Nada implementado** — *"primeiro proposta, depois
> ação"*.
>
> **2. Formulários → a ponte com o Harmonit (criar OS)** — na VPS,
> `docs/06_Conteudo_das_Telas.md`, seção **"23/10"**. 11 decisões dele
> fechadas; **o que trava é o sub-mapa de SUPORTE e ADMINISTRATIVO e os dois
> "Backup"**, que não têm candidato nos 24 problemas do Harmonit.
>
> **3. FPSL → telas no perfil: NO AR e verificado** — única coisa da sessão
> que foi implementada. Detalhe no bloco 0.0000000000000000000000000000000
> abaixo. 🔴 **Só falta decisão dele sobre `usuarios`.**

> ✅ **A FILA DE "FALTA ELE VALIDAR" FOI MEDIDA EM 23/10, E CAIU DE 12 PARA 2.**
> Ordem dele: *"valide de fato o que foi feito ou não, sempre fatos"*. Em vez de
> perguntar, medi **uso real no banco**. Sete entregas não só foram validadas:
> **estão em produção com dado de cliente**, e deixaram de ser pendência (cada
> bloco abaixo traz o número e a data):
>
> | Entrega | Prova |
> |---|---|
> | Agendamentos (21/10) | agendamento criado em **23/10 10:34**, OS **16548** |
> | Chat interno: reagir (16/10) | **25 reações**, a última **23/10 12:28** |
> | Chat interno | **3.925 mensagens**, a última **23/10 15:54** |
> | Ligações `LIG_1.1` (15/10) | **288 ligações**, a última **23/10 12:19** |
> | `FIN_2.1` Fechamento Técnicos (06-08/10) | **3 OS reais** em 22/10: 17001, 17010, 17015 |
> | Aba Operações FPSL (07/10) | **136 lotes**, o último **22/10 20:31** |
> | `CTR_1.1` Contratos (13-14/10) | 4.599 termos · 6.463 itens · 2.422 achados carregados |
>
> 🔴 **SÓ ESTES DOIS CONTINUAM PENDENTES, e os dois têm prova de que NÃO foram
> exercitados:**
>
> 1. **Os 15 formulários** — no ar desde 22/10 e **nenhum cliente enviou nada**:
>    a base tem **1 solicitação**, e é a de teste **39** (`zz Externo`, 22/10
>    14:22), que segue lá para ele apagar.
> 2. **O `@` da nota interna** (21/10) — **zero** mensagens de chat com o link
>    `/atendimento/`, que é a impressão digital do aviso. As 13 menções que
>    existem são do `@` **de grupo do chat interno** (salas "Todos Movisat",
>    "OPERACIONAL", "Alinhamento - Maxi Confort"), outra coisa. A conversa
>    **80355** segue intacta.
>
> ⚠️ **Pendências de apagar que a medição confirmou VIVAS:** a solicitação **39**
> · a pasta `C:\code\BACKUP\vps\midia` (**13,5 GB**; `midia_unica` tem 1,28 GB e
> **não há dias 22-24/09 em `midia_dias`** — apagar continua inseguro) · as
> gravações: o aviso de abertura de 23/10 diz **5 ramais com gravação desligada**
> e **Claudia 69 h sem falar com a VPS**.
>
> ⚠️ **Uma correção de número:** os "cinco compromissos de teste na OS 16991"
> são do **Harmonit**. No MoviZap existe **um só** (agendamento `211`, 21/10,
> placa `PLACA1`).
>
> 🚨 **E uma regra de método que me custou um falso vermelho:** a suíte do
> MoviZap **tem de rodar como `claude`**, não como root. `teste_vigia_resumo.py`
> lê `crontab -l`, que é do usuário: como root deu **1 falha**, como `claude`
> deu **3 passaram**. Placar real de 23/10: **1.745 passaram, 1 pulado, 0
> falhas**.

> **Fechamento de 22/10, dito por ele: *"na proxima sessao seguimos"*.**
>
> **O primeiro passo é dele, não meu** — é o único que nenhuma suíte faz
> (`M9`): as **18 abas** que abri estão em `forms.movisat.com.br/f/<slug>` (os
> 15), `/paineis/operacao`, `/solicitacoes` e os mockups
> (`https://claude.ai/artifact/3mM5bs3gv1hYsyTaShsd6s`).
>
> **O que eu posso começar sem esperar nada:** o **botão "Tarefas"** (Etapa 2)
> — a trava por empresa vinculada e o link travado por token já estão medidos e
> desenhados no plano, e não dependem de decisão nova.
>
> **O que está BLOQUEADO até ele decidir:** a outra metade do card do painel
> (criar OS e escrever `situacaoId`) espera o **mapa formulário →
> `problemaId`** · os três painéis restantes esperam o corte do promotor (8 ou
> 9), o endereço dos contratuais, o elo com o `FIN_2.1` e se mostra valor · os
> três formulários com aceite esperam **o texto do termo**.
>
> **Sobras para ele apagar:** a solicitação **39** (`zz Externo`, minha prova
> de ponta a ponta) e os **14 registros de teste no Bitrix24**
> (`resultId` 15620–15646).
>
> **Estado em 22/10, 18:4x:** suítes **1746 Python · 440 JS** · migração **076**
> é a última · seis commits (`fed3abd` → `fed5997`) · árvore limpa · serviço
> ativo.

> 🔴 **27/10 — FPSL/Painel Financeiro: 25 pendências vivas nas duas telas**
> (`FIN_1.1` Conferência de Fechamento e `FIN_2.1` Fechamento Técnicos), 13 já
> anotadas e 12 novas, **todas conferidas no código e no dado de hoje**. 🚨 **Não
> duplicar a lista aqui** — ela vive no bloco `0.00000000000000000000000000000000`
> logo abaixo, com as **6 decisões dele** que travam o resto (seção D) e a
> sequência sugerida (seção F). Nada foi alterado: a sessão foi de leitura.

> 🚨 **29/10 — A CAUSA DO ARRASTO NÃO EXISTIR, E FOI ELE QUEM ACHOU: a coluna
> vazia não tinha CORPO.** Detalhe nas **seções 16 e 17** de
> `movizap_painel/docs/16_Pipeline_da_Operacao.md` — 🚨 **a §17 é TUDO O QUE
> FALTA, em um lugar**, e substitui as listas anteriores.
>
> Ele exigiu o diagnóstico antes do conserto (*"quero saber o porque antes de
> voce mexer em algo que nao vai resultar em nada"*) e tinha razão: eu havia
> consertado **três** causas e nenhuma era A causa. **Tudo estava certo** — a
> pasta servida, o bundle com os 5 handlers, o `draggable` compilado, o CSS, o
> DOM com `draggable="true"`. **O problema não era o card: era o DESTINO.**
>
> **A prova:** a coluna vazia renderizava `coluna--fechada`, e fechada quer
> dizer que o **`coluna__corpo` NÃO EXISTE** — a única área dela era a tira do
> título, **~44 px**. Mover a 17054 para "Configurar equipamentos" exigia
> acertar essa tira, e visualmente **não parece haver coluna ali**.
>
> 🚨 **A causa raiz é minha, de 22/10:** `abertas[chave] = coluna.total > 0` —
> eu fiz a vazia nascer colapsada para as 17 caberem. Era aceitável enquanto o
> painel **só lia**; quando mover entrou, virou **um destino que não existe** —
> e eu não voltei àquela linha. É o `M12` na forma de **comportamento**.
>
> ⚠️ **Foi a QUARTA causa do mesmo defeito, e a única fora do card:** nas três
> voltas anteriores eu olhei sempre o card, porque era o que eu tinha acabado de
> escrever. **O destino nunca entrou na minha conta.** E nenhuma trava podia
> pegar: elas montavam o quadro com **uma** coluna, ou disparavam `drop`
> **direto** na coluna pelo índice — *drop sintético não precisa de área*.
>
> ✅ **Conserto, nas palavras dele** (*"não é necessário ter card para que elas
> existam"*): **toda coluna nasce aberta** · a vazia tem **alvo de 72 px** com
> *"solte um card aqui"* · colapsar virou **escolha de quem usa**. E **duas
> travas minhas afirmavam a causa** — trocadas.
>
> **1971 Python · 620 JS.** Commit `5e23d87`.
>
> 🚨 **O placar não prende tela quebrada:** com tudo verde, ele achou **8
> defeitos** hoje abrindo a tela. O `M9` se provou oito vezes.

> 🟢 **29/10, FECHAMENTO — O PLANO DO PAINEL OP ESTÁ ENTREGUE: os 6 blocos no
> ar.** 🚨 **Não duplicar aqui** — o detalhe está em
> `movizap_painel/docs/16_Pipeline_da_Operacao.md`, **seções 6 a 15**. A §15 é
> **os próximos passos**.
>
> **A: criar a OS** · **B: o painel monta as OS** · **C: os dois tempos** ·
> **D: arrastar o card escreve a situação** · **E: os 4 temas do card aberto** ·
> **F fase 1: prioridade + observação**. Mais o que ele pediu fora do plano: o
> **filtro** por cliente/OS/placa e **5 ordenadores**, com o padrão em **prazo
> de entrega**. Migrações **082, 083, 084**. **1971 Python · 618 JS · 106 na
> ponte.** Auditoria funcional **59 OK, 0 falhas** (`auditar_funcional.py`,
> repetível). Commits `bc867e0` e `5aef2be`.
>
> 🚨 **O ARRASTO LEVOU TRÊS VOLTAS, e eram TRÊS causas empilhadas:** (1) o
> conteúdo era um `<button>`, que engole o `mousedown`; (2) faltava
> `user-select: none`, e arrastar sobre texto selecionável inicia **seleção de
> texto**; (3) o **`@click` competia com o arrasto** — todo arrasto começa
> curto, o navegador entrega o início como clique, e o card **abria no meio do
> gesto**. ⚠️ **Nenhuma das três um teste meu podia pegar:** `dragstart` e
> `click` são sintéticos e separados. *"Trava de atributo não é trava de gesto"*
> virou *"trava de evento sintético não é trava de gesto"*
> ([[feedback_trava_de_atributo_nao_e_trava_de_gesto]]). **A coluna agora
> ACENDE** quando o card passa por cima — era o retorno visual que faltava.
>
> 🚨 **EU QUEBREI A `os_por_cliente` EM PRODUÇÃO (500)**, a rota que o
> agendamento usa: substituí *"a primeira ocorrência"* de um trecho num arquivo
> de 1.700 linhas e ela estava em **outra função**
> ([[feedback_primeira_ocorrencia_e_aposta]]). **Quem pegou foi a suíte ao
> vivo**, não eu. Consertada, 18 OS.
>
> 🚨 **A suíte pegou dois crashes antes de valerem algo:** a ordem por data
> comparava `datetime` com `str` — e **com o prazo como padrão derrubaria o
> painel** sempre que houvesse os dois tipos de card; e o banco temporário do
> teste da ponte não tinha a coluna nova (8 vermelhos **no teste**, não em
> produção).
>
> 🚨 **MEDIDO: a OS do Harmonit tem UM campo de data e NÃO existe campo de
> prazo** — na 17055, criada 29/10, a previsão é 29/10 11:40:19, **o mesmo
> minuto**. A ordem `prazo` **substituiu** a "aberta há mais tempo" porque
> ordenavam o mesmo campo; 🔵 quando o aviso prévio mover a previsão em +90 dias
> elas deixam de coincidir e aí valem as duas.
>
> 🔴 **O PRIMEIRO PASSO É DELE, e é o único que nenhuma suíte faz:** validar no
> navegador. 🚨 **Ele achou 7 defeitos assim hoje, todos com a suíte verde.**
> Comece arrastando um card da **OS 16991** (a sandbox) — é escrita real no ERP.
>
> 🔴 **As 8 decisões que travam o resto** estão na §15.2: o mapa `problemaId` (8
> formulários sem OS) · o limite do laranja · a situação `0` (**128 OS**) · o
> texto dos termos · a aba Network · "cliente avulso" · o endereço em 7 campos ·
> apagar a solicitação **544**.
>
> 🟡 **O meu, desbloqueado e NESTA ORDEM:** derivar as máscaras (**conserta 56
> campos sem validação em produção**, nos 14 que o cliente já abre) → só então
> ligar o formato novo nos 14, porque **pele nova não conserta coleta**.

> 🟢 **29/10, NOITE — BLOCO D NO AR + os dois defeitos que ELE achou no
> navegador, consertados. Detalhe inteiro nas seções 8 a 11 de
> `movizap_painel/docs/16_Pipeline_da_Operacao.md`** — 🚨 não duplicar aqui.
>
> **Bloco D no ar**, com as 4 decisões dele em uma frase cada: *"O card pode ser
> por arrastar"* · *"deve ter o log de quem faz o que SEMPRE"* · *"que tal de
> caminho proibido é esse??"* (ordem **livre** — a hipótese era **minha**) ·
> *"pode mover que tiver acesso a tela, por enquanto somente owner"*.
> Migração **083** (`os_passagem`), 3 rotas novas. ✅ **Provado na OS 16991:**
> a trava de concorrência recusou, moveu 15694→890, o cache soube na hora,
> voltou, e o log ficou com as 4 passagens. **A OS está em 15694, a original.**
>
> 🚨 **ELE ACHOU DOIS DEFEITOS NO NAVEGADOR, e tinham a MESMA causa:** o
> `<article draggable>` era preenchido por um `<button>`, e **navegador não
> inicia arrasto a partir de elemento interativo** — o arrasto era
> **impossível** e o HTML parecia certo. ⚠️ **A minha trava afirmava
> `draggable === 'true'`, que era VERDADE enquanto o gesto não funcionava:
> trava de atributo não é trava de gesto.** O clique, pelo mesmo motivo, ia
> para `/solicitacoes` com id nulo. Agora o clique **abre o card** (com as
> passagens, mover de dentro, e dizendo o que ainda não existe).
>
> 🔍 **AUDITORIA FUNCIONAL (*"precisa funcionar"*): 38 OK, 0 falhas.** O script
> é `movizap_painel/auditar_funcional.py` e **repete quando se quiser** — ele
> EXERCITA em vez de ler código. As **15 páginas públicas abrem**, a busca por
> CNPJ acha nas três formas (dígitos, máscara e **alfanumérico**), e a regra da
> placa recusa placa sem rastreador ativo.
>
> 🚨 **A auditoria achou um defeito meu:** um teste meu gravava em
> `os_passagem` de **produção** e não limpava (5 passagens da OS fictícia
> 90999, uma por rodada) — e a rota que ele estava lendo mostrava passagens de
> uma OS inexistente. É a família do incidente de 19/10.
>
> ✅ **Dois fatos novos do dado:** a **OS 17050 saiu da situação `0`** sozinha
> (alguém a moveu para 677 no Harmonit), então o quadro não tem mais OS fora de
> coluna — ⚠️ mas **128 OS com `0`** seguem na base. E a **Velasco (a sandbox)
> tem ZERO placas ativas**. 🚨 **E o conselho que eu escrevi aqui estava
> ERRADO e perigoso** (*"use o CNPJ da DCBM"*): regra dele — *"não pode usar
> outro CNPJ além da VELASCO para teste, pois os tickets nascem e têm ligações.
> OS com outros clientes podem ser mal interpretadas pela OP"*. ⚠️ Eu já havia
> criado a **OS 17056 na DCBM**; apagada, mas ela existiu na fila deles. **O
> remédio foi no código:** `provar_criacao_os.py` recusa qualquer cliente que
> não seja `998063`. 🔴 **Decisão dele:** o caminho da placa **não pode ser
> exercitado** (a sandbox não tem placa ativa) — ativar um rastreador para a
> Velasco na WESO, ou aceitar que a placa só será provada no primeiro chamado
> real ([[feedback_sandbox_e_so_a_velasco]]).
>
> 🔴 **SEIS TRAVAS, e as seis são frases dele, nenhuma é trabalho meu parado:**
> (1) o **mapa `problemaId`** — 8 formulários não abrem OS · (2) o **texto dos
> termos** · (3) o **limite do tempo de etapa** (um número) · (4) o que a aba
> **Network** do Harmonit mostra · (5) a **situação `0`** · (6) **"cliente
> avulso"** no ERP. **O que eu posso fazer sem esperar:** ligar o formato novo
> nos **outros 14** formulários — uma linha por formulário.
>
> **1947 Python · 590 JS**, zero falhas. Commits `bdd9d8e` · `7675967` ·
> `1310399`.

> 🔍 **29/10, AUDITORIA DO ENTREGUE (pedido dele: *"auditou e validou o
> entregue? as rotas?"*): 7 achados, 5 eram defeitos meus — todos fechados.**
> 🚨 **Não duplicar a lista aqui:** ela está em
> `movizap_painel/docs/16_Pipeline_da_Operacao.md`, **seção 7**.
>
> 🔴 **E a primeira resposta é NÃO: dos 6 blocos do plano, só 2 subiram.** C, D,
> E e F não começaram. A §7.1 diz o que falta em cada um.
>
> **O que a auditoria achou:**
> **A1** — 3 das **4 rotas novas** tinham **zero teste HTTP**, com **58
> arquivos** da suíte usando `TestClient`. ⚠️ **É o mesmo achado de 22/10**,
> sete dias depois. Fechado com 2 arquivos: **18** travas no MoviZap, **25** no
> FPSL. 🚨 E só o teste HTTP pegou duas coisas: o **formulário nasce desligado**
> (a rota pública dava **404**) e `storage.DB_PATH` **tem de ser `Path`**.
> **A2** — `falhas_em_aberto()` **não filtrava por painel** (o da Operação
> somava falha do Financeiro e do Contratual). Latente.
> **A3** — 🚨 **o cache `_MAPA_PAINEL` mentia, e o preço não era o que eu
> escrevi:** com o mapa velho o quadro **DESCARTA o card**, não o rotula errado.
> Card que desaparece é `M12`. O cache saiu.
> **A4/A5** — 🚨 **o "há 2 dias" do mockup NÃO aparecia em nenhum dos 10
> cards:** a data da OS chegava em `dd/mm/aaaa`, que o JavaScript não lê. Eu
> conhecia a armadilha do outro lado da ponte.
> **A6** — 🔴 **a rota da data matriz não tem quem a chame**, e isso é a
> repetição de um achado **meu de ontem** na `CAR_1.1`. **Decisão dele:** campo
> de data na tela só para o owner, ou deixar a rota como ajuste pontual.
> **A7** — a doc: criado `docs/fpsl/34_Ponte_MoviZap.md` (**a ponte existia
> desde 21/10 e nunca teve seção de rotas**), o `03_Registro_Telas` passou a
> descrever o painel como ele ficou, e o `18_Testes` conhece os arquivos novos.
> ⚠️ **Observação:** `teste_car_router.py` (28/10) **não é coletável por
> pytest** — roda como script, 100 OK.
>
> **Placar depois:** **1940 Python · 579 JS · 106 na ponte**, zero falhas. O
> laço oficial do FPSL achou **os 2 vermelhos conhecidos e nenhum novo**.
> Commits `523b6f6` (MoviZap) e `971495d` (FPSL). Árvores limpas.
>
> 🚨 **E zero pulados nos arquivos novos, de propósito:** as duas travas mais
> importantes do Bloco A **começaram pulando** porque eu enchi os campos com
> `"x"`. **Teste que pula é teste que não existe** — foi o segundo pulo
> silencioso que esta frente me custou no mesmo dia.

> 🟢 **29/10, SEGUNDA VOLTA — BLOCOS A e B NO AR, falta ele VALIDAR NO
> NAVEGADOR.** 🚨 **Não duplicar a lista aqui:** o detalhe inteiro está em
> `movizap_painel/docs/16_Pipeline_da_Operacao.md`, **seção 6**, na VPS.
>
> **No ar:** o chamado de Suporte **abre OS de análise sozinho** (D4), **uma por
> placa** (D3) · o painel monta **10 cards reais** das OS do ERP (D8), com nome
> de cliente e de tipo · a **data matriz 24/10**, só o owner muda (D9) · o
> interruptor **"só as abertas"** (desligado: 14 cards) · os **efeitos do
> mockup** sobre os tokens da casa. Migração **082**, 3 rotas novas.
> **1922 Python · 579 JS**, zero falhas. Commits `f4023d2` (FPSL) e `fa1d277`.
>
> ✅ **Provado no ERP com OS de verdade (17056, ele autorizou): criada, relida
> campo a campo e removida.** `SalvarOrdemServico` com `id: 0` **devolve o
> número** — era a única coisa que teste nenhum podia responder.
>
> 🚨 **ELE ACHOU UM DEFEITO NA TELA minutos depois de ela subir** (*"1 sem OS (a
> escrita no Harmonit falhou)"*) e **nada havia falhado**: a solicitação **544**
> é de 13:06 e o Bloco A subiu 15:30 — nunca houve escrita. `M9` + `M12` na
> forma exata: a frase era VERDADEIRA em 22/10 (a OS nascia por botão) e eu a
> reescrevi assumindo que todo chamado teria tentativa. ⚠️ **Um teste meu estava
> GUARDANDO o defeito** — exigia a palavra "Harmonit" na frase. Agora são **três
> casos** com frases diferentes.
>
> 🚨 **UMA PENDÊNCIA DELE MORREU POR MEDIÇÃO (a nº 3):** os tipos 76 e 57
> **existem** — são **duas rotas** (`ObterListaTipoOrdemServico` = 5 ·
> `ObterTiposOrdemServico` = **28**). Nada a reescrever no ERP. E isso era a
> **causa** de um defeito de 21/10: a rotina lia a rota curta, e **189 OS
> apareciam sem nome de tipo** — a mensagem do agendamento omitia o tipo em uma
> de cada três. Medido: **385 → 574 de 574**.
>
> 🚨 **DOIS NÚMEROS DO PLANO ESTAVAM ERRADOS:** "só abertas" **NÃO zera** o
> Financeiro (6 → 2, não → 0); e os **9 clientes das OS estão todos** no nosso
> cadastro (risco nomeado que não se materializou).
>
> 🚨 **UM ERRO MEU EM PRODUÇÃO, de 13 segundos:** derrubei o MoviZap (15:46:10 →
> 15:46:23) usando `Query` sem ele estar importado no `main.py`. ⚠️ **O
> `py_compile` que eu rodo antes de gravar NÃO pega isso** — nome não importado
> é erro de execução. A régua que faltou é um `grep` na linha do `import`.
>
> ⚠️ **E um defeito da minha própria suíte:** o fixture nascia sem `validacoes`
> e sem `ajustes`, e **12 das 23 travas pulavam** com o placar parecendo
> saudável. Agora ele lê as duas tabelas **do próprio carregador**.
>
> 🔴 **Falta dele:** validar a tela · as **OS com situação `0`** (1 no quadro
> aberto, 2 no total) · apagar as solicitações **39** e **544** (a 544 é a que
> faz a linha de aviso aparecer) · 🆕 decidir se existe **"cliente avulso"** no
> ERP, para o chamado de quem não está no cadastro virar OS em vez de ficar
> marcado. **Próximo bloco: D — mover o card escreve a situação.**

> 🔴 **29/10 — MoviZap: PIPELINE DA OPERAÇÃO (formulário → OS → painel). O plano
> inteiro vive em `movizap_painel/docs/16_Pipeline_da_Operacao.md`, na VPS** —
> 🚨 **não duplicar a lista aqui.** Aquele arquivo tem o que avançou, as **12
> decisões dele** desta volta, os **6 blocos** na ordem de dependência e as **9
> pendências dele**. Mockup do painel e do card:
> `https://claude.ai/artifact/GXx2aBj4Tei8t51KR4HZSC`.
>
> **No ar hoje:** o formulário de **Suporte no formato novo**
> (`forms.movisat.com.br/f/suporte` — etapas, logo, base `#021529`, repetidor
> `+`, máscaras com dígito verificador, **CNPJ alfanumérico**, busca de cliente
> pelo CNPJ, frota ativa marcável, modal de "sem empresa vinculada") · **as 17
> situações da OS ajustadas no Harmonit** (11 renomeadas, 6 criadas, nenhuma
> excluída) · o **painel com as 17 colunas** na ordem dele, sem as duas que não
> eram situação e sem os três textos que ele mandou sumir. Migrações **079, 080
> e 081**. Suítes **1885 Python · 559 JS · 46** na ponte.
>
> 🚨 **O que a próxima sessão tem de saber antes de mexer:**
> **(1)** o Harmonit **não registra a situação na linha do tempo**, só o
> `status` — o tempo por etapa é nosso, e para as 11 OS que já existem a
> contagem começa no dia em que o card nascer; **(2)** **não existe link por
> OS** no Harmonit web (`/Manager/OrdemServico` redireciona para o login e a OS
> abre por postback) — por isso o espelho no card; **(3)** `dataPrevisao` **é**
> a data de criação da OS (12 de 12 conferidas), **mas** a frente do aviso
> prévio vai movê-la em +90 dias, então ela não serve como data de criação para
> sempre; **(4)** `ANÁLISE OPERACIONAL` **já existe** no catálogo de problemas
> (**12760**).
>
> ⚠️ **E um erro meu de método, para não repetir:** eu escrevi em três arquivos
> que a lista da frota *"sugere, nunca restringe"*. **Ninguém me disse isso** —
> inferi de uma medição minha e tratei a inferência como decisão. Resposta dele:
> *"a regra sempre foi essa, voce quem decidiu algo sem perguntar e acabou
> fazendo trabalho atoa"*. A regra é: **chamado só para placa ativa na WESO**.

## 0.000000000000000000000000000000000000 🔵 30/10 — FPSL/Fechamento de Técnicos: as 4 causas medidas e as correções C1-C8

> 📍 **Fonte única desta frente, nova:** `C:\Users\Lenovo\Desktop\FIN_2.1_Fechamento_Tecnicos.md`.
> 🚨 **Não duplicar a lista aqui.** As duas listas por OS, geradas no dia:
> `Desktop\pagamentos_x_painel.md` (só os 7 técnicos da lista dele) e
> `Desktop\fechamento_tecnicos_divergencias.md` + `.csv` (as 106 OS de set/out).
>
> 🔵 **Origem: ele mandou a lista do financeiro pago** (2 datas, 9 pagamentos, R$ 3.332,62) e pediu
> *"veja se bateria e o que faltaria para aparecem no fechamento dos tecnicos"* · *"foco é validar o
> realizavel com a expectativa do painel, se as OS estivessem com os valores e com o nome dos
> tecnicos"* · *"é de lá [do orçamento do MoviZap] que virá esse dado de conciliação e vinculo no
> card do tecnico"*.
>
> 🚨 **MEDIDO: de R$ 3.332,62 pagos, o painel entrega R$ 577,25 (17%).** A conta está **certa na
> mecânica** (PAGAMENTO DE TÉCNICO + KM por item); o que derruba o resto são **4 causas**, e nenhuma
> é a fórmula: (1) **a situação** — 12 das 14 OS barradas estão em `1316 Serviço Agendado` ou
> `15696 Aguardando devolução`, serviço feito e pago com a situação de antes; (2) **a conferência** —
> 14 de 14 sem linha, **7 por não ter oficina** (a regra que ele derrubou em 27/10 e não foi
> implementada, bloco **B1**); (3) **o cadastro** — **5 dos 9 pagamentos (R$ 1.206,72) são de técnicos
> que não existem em `tecnicos`**; (4) **dois pagamentos no mesmo período não cabem** no card (um
> aberto por técnico+período). ⚠️ **O valor do serviço está lançado em todas as 19 OS** — isso não é
> o problema. E *"status ainda Iniciada"* **não é defeito**.
>
> 🚨 **ACHADO QUE ATRAVESSA AS DUAS ABAS: as situações da OS foram renomeadas em 29/10 e as telas
> falam o nome velho.** A **15694** agora é **"Atendimento finalizado"** (era "Serviço Realizado"), e
> `"Serviço Realizado"` aparece **23 vezes no código e 7 nas telas** (`conferencia_fechamento.html`,
> `fechamento_tecnicos.html`, `os_historico.html`). 🔵 E a **15746 é "Financeiro"** — a "OS do tipo
> financeiro" dele é **situação, não tipo** (não existe tipo "Financeiro" entre os 29).
>
> 🔵 **O vínculo do orçamento já é possível:** o `orcamento` do MoviZap tem `numero`,
> `total_centavos`, **`ordens_os[]`**, `tecnico_contato_id` → `contato.harmonit_tecnico_id` (**a mesma
> chave do `tecnicos.tecnico_id`**) e o **PDF** (`midia_id`). Ele substitui o recibo digitado à mão, e
> o semáforo passa a comparar **calculado da OS × orçamento**. ⚠️ Falta `harmonit_tecnico_id` em 5 dos
> 7 contatos. ⚠️ Os números 750/1608-1672 **são de antes da tela** (o MoviZap tem 3 orçamentos) —
> esperado, não defeito.
>
> 🔴 **Falta dele:** **quais situações contam como serviço feito** (hoje só a 15694) · **cadastrar os
> 5 técnicos** · **o card ganha o nível "pagamento"?** · **A2** (estado do DataScope) · apagar os
> cards 14/15 (cancelados duplicados) e decidir o 12 (sandbox em "pagamento").
>
> ⚠️ **Em 30/10 12:49 alguém clicou "Gerar Cards" na produção** (nasceu o card 17, o 16 ganhou 3 OS).
> **Não foi a suíte** (a rota de gerar é marcada como escrita e o teste só a chama sem token e com
> token magro) **nem o laço** (só recalcula semáforo). Se foi ele, é prova de que a tela gera: trouxe
> **exatamente as 5 OS** que o diagnóstico diz que entram.

## 0.00000000000000000000000000000000000 ✅ 30/10 — FPSL/Contas a Receber: a FASE 1 DA OPERAÇÃO NO AR (F1+F2+F3+F4)

> 📍 **Fonte única desta frente, com os números e os achados:**
> `C:\Users\Lenovo\Desktop\CAR_1.1_Financeiro_FPSL.md` — **§V5**. Spec na VPS:
> `docs/fpsl/32_Contas_a_Receber.md` — **§12**. 🚨 **Não duplicar a lista aqui.**
>
> 🔵 **Quatro decisões dele no dia:** escopo *"F1 + F2 + F3 + F4: já nascer com preço"* · rotina
> *"nasce desligada mas tbm pode ser feita pelo botão... 1 vez no dia 4hrs após a automática"* ·
> régua *"interseção, com as duas colunas visíveis"* · semeadura *"faça o 2, mas deixe as regras
> do 1 tbm"*.
>
> **No ar:** `car_faturado` (**3.070** lançamentos, 10 meses de vencimento, 20 `GET` em 1min15) · o
> **10º laço** nascendo desligado + botão com a régua dele · as **três colunas no CLIENTE**
> (2026-09: cobrado **R$ 167.753,50**, recebido **R$ 146.670,56**) · a **régua da WESO** (3.033
> cobráveis, **1.606 em uso**, **26 clientes usam e não são faturados**) · a **semeadura**
> (**274 propostas, R$ 167.684,06, zero conflitos**). **21 rotas** (eram 16), 4ª tabela da CAR.
>
> 🚨 **Três achados que mudaram o desenho, todos medidos:** (1) a amarração por termo que eu
> reportei estava errada — restringindo ao **próprio cliente** são **537 de 544 (98,7%)**, não 71%;
> (2) **a janela de vencimento subestimava a receita em silêncio** — a competência 2026-09 tem
> lançamento em **sete** meses de vencimento (R$ 185.234,14, com R$ 15.678 vencendo em abril);
> (3) 🚨 **defeito de dinheiro pego por teste**: o Harmonit manda `200.53` e a casa lê ponto como
> separador de **milhar** — R$ 200,53 virava **R$ 20.053,00** na soma, e esse valor é copiado para
> o `car_evento`, que é imutável.
>
> 🔴 **Falta dele, nesta ordem:** **abrir a tela** (`M9`: nenhuma suíte vê tela quebrada) →
> **clicar "Adotar as 274 propostas"** (eu **não** lancei: são 274 eventos de dinheiro com autor) →
> decidir se **liga a rotina** → **conceder a aba `contas_receber`** (hoje em ninguém) → **D8**. O que
> **não** entrou e por quê: **§V5-D** (o triplete dos 6 estados, F5, F6, F7-F9).
>
> ✅ **30/10, volta 6 — A TELA OPERACIONAL, MOCKUP APROVADO POR ELE:** detalhe na **§V6** do documento
> de controle; mockup em `https://claude.ai/artifact/RnvbtMzgCE44mgfqQsvKDt` (gerar · vínculos por
> clique · lote no formato de lançamento do Harmonit). Os blocos de execução são **G1 a G6**.
> 🚨 **A decisão D6 ENCURTOU: a régua da parte variável já existe no dado** — `cobrar` é booleano
> **por item da OS** (e PAGAMENTO DE TÉCNICO/KM vêm `false` em 70 de 71), a soma dos itens `cobrar`
> **reproduz o que o Harmonit faturou em 9 de 12 OS**, e a *"OS do tipo financeiro"* é a **situação
> 15746 "Financeiro"**, não um tipo. ⚠️ **A D6 não desaparece**: deixa de ser *"qual lista de itens"*
> e passa a ser **"adotamos o `cobrar` do Harmonit como régua?"** — decisão dele, de uma linha. Fila a
> gerar hoje: **3 OS, R$ 1.320,00** (das 51 finalizadas com item a cobrar, **48 o Harmonit já
> faturou**).
> ⚠️ **Limite declarado da coluna "em uso":** das 2.946 placas sustentadas, **1.625 casam** no cache
> da WESO; **338 têm chave de chassi e só 39 casam**, e há **nome de pessoa na coluna de placa**
> (`MARTONE2009`). "Em uso" é **piso, não número exato** — e é higiene de `placa_chave` na `CTR_1.1`.
> 🚨 **E o número que a tela existe para mostrar: em 71 de 263 clientes faturados (27%) o contrato que
> fatura NÃO sustenta placa nenhuma** (XOMV fatura no 306 e usa 71 placas no 8802), mais 12 faturados
> sem placa em lugar nenhum — é o bloco **F9** com nome e sobrenome.
> 🔵 **Regra de estilo nova, dele:** *"não precisa dos comentarios na tela. atrapalha o
> profissionalismo"* — o que a `M12` exige fica, mas como **estado** (selo, carimbo, rodapé), nunca
> como parágrafo de aula.
>
> **Suíte: baseline 75 arquivos / 74 verdes → fechamento 77 arquivos / 76 verdes** (os 2 a mais são
> `teste_car_faturado` e `teste_car_semear`), **1 vermelho** — só o `teste_extrair_termo`, que
> espera decisão dele. ⚠️ O `teste_higiene_placas_weso`, 2º vermelho
> desde 28/10, **passou hoje**: o critério de verde desta frente passa a ser **1 vermelho
> conhecido, nenhum novo**.

## 0.0000000000000000000000000000000000 ✅ 28/10 — MoviZap: o AVISO DA NOTA INTERNA, **NO AR**

> ✅ **IMPLEMENTADO E PUBLICADO em 28/10**, com a ordem dele: *"somente daqui para frente, pode
> ajustar notific para notas"*. Detalhe inteiro em `docs/06_Conteudo_das_Telas.md` (seção "28/10 — o
> AVISO DA NOTA INTERNA"). O que segue abaixo é o **levantamento que gerou a proposta**, mantido
> porque é ele que explica cada decisão do desenho.
>
> **O que entrou:** selo **próprio** na linha da Caixa (âmbar, com ícone de nota — **não soma** no
> selo verde do cliente) · **som e balão próprios**, dizendo *quem* anotou · **fila de toque
> separada**, com teto de 4 só dela · interruptor por pessoa na **`CFG_11.1`**, **ligado** por padrão
> · **zero migração** (o "não vi" é a ausência de linha em `nota_leitura`, que a tela já grava).
>
> **A régua de quem é avisado:** dono · convidado ativo · **quem já anotou naquela conversa** — nunca
> o autor. 🚨 O terceiro caso é o que salva o recurso: **207 das 310 notas estão em conversa sem
> dono**; com a régua do dono sozinha, dois terços seguiriam mudos. Com os três, **136 de 212** notas
> têm destinatário (**204 avisos**).
>
> 🚨 **O corte: `NOTIFICA_NOTA_DESDE = 2026-10-28 19:20 UTC`.** Medido rodando a régua com o corte
> desligado: sem ele, as notas que já existiam virariam **135 avisos para 8 pessoas** no primeiro
> ciclo de 8 s depois do deploy.
>
> ⚠️ **A consulta da lista (`conversas.listar`) NÃO foi tocada** — é a mais quente do painel e tem
> ordem posicional de parâmetro, com aviso no código de que errar ali *"não dá erro de sintaxe, dá
> resultado errado"*. O contador saiu em consulta própria, servida pela rota que já bate em toda tela
> de 8 em 8 s.
>
> **Provas:** `tests/teste_aviso_nota.py` **16** (12 da régua + **4 da rota HTTP**) ·
> `frontend/src/aviso_nota_2810.teste.js` **11** · ponta a ponta no servidor no ar, com nota criada
> pelo caminho real: o dono foi avisado com autor e trecho, o autor não, e o aviso morreu depois do
> "visto" (tudo apagado em seguida). Backend reiniciado, `npm run build` feito (`M16`).
> **Suíte inteira depois de tudo: 1.849 passaram, 1 pulado, ZERO falhas** (eram 1.844 + 1 falha do
> runner de JS, que era meu: a suíte da casa é **vitest**, não `node --test`).
>
> 🔴 **Falta dele:** exercitar no navegador — escrever uma nota na conversa de outra pessoa e ver o
> selo, o som e o balão chegarem. E as **76 notas** que a régua deixa sem destinatário (autor é o
> único que anotou, conversa sem dono nem convidado) seguem **de propósito** sem aviso: se ele quiser
> que o **time** receba nesses casos, é uma volta curta.

### O levantamento que gerou isso (28/10, antes de implementar)

🔵 **Origem:** *"verifique se as notas internas tbm estao gerando notificacoes como mensagens novas
no movizap, se nao tiver - proponha para que sejam tbm"*.

### 🔴 A resposta: NÃO. E não é "faltou ligar" — não existe o caminho

Três coisas conferidas no código e no dado de hoje:

1. **O selo de "mensagens novas" da conversa conta SÓ `direcao = 'entrada'`**
   (`movizap/conversas.py:1502-1508`). Nota interna é `direcao = 'interna'` — **nunca entra na
   conta**. Prova pelo dado: a base tem `entrada` **23.233** · `interna` **840** · `saida` **25.731**.
2. **O toque e o balão do Windows saem do `decidirToque`** (`frontend/src/util/regraToque.js`), que
   só olha `nao_lidas` de **conversa em que a pessoa é dona** — regra dele de 24/09. Como a nota não
   mexe em `nao_lidas`, **o som nunca toca por nota**.
3. **`nota_leitura` existe, mas é o "visto por"** (Bloco 12, 15/10): recibo **depois** que a pessoa
   rolou a nota na tela. **228 linhas.** É o oposto de aviso — ele prova que alguém leu, não chama
   ninguém.

⚠️ **O único aviso que existe é o `@` da nota**, que manda mensagem no chat interno — e ele tem
**ZERO uso** (0 mensagens de chat com o link `/atendimento/`, a impressão digital do aviso).
Continua valendo o que a memória já dizia: **o `@` nunca foi exercitado.**

### 🚨 O tamanho do problema, medido hoje

**310 notas internas** (fora os **530 eventos** do log de ações), em **183 conversas**, por **7
pessoas**, a última **hoje às 15:56** — está em uso diário. Onde elas caem:

| | notas | e quem foi avisado |
|---|---|---|
| na conversa **de outra pessoa** (dono definido) | **65** | **ninguém** |
| em conversa **sem dono** | **207** | ninguém — e não há dono a quem avisar |
| na **própria** conversa | 24 | não precisa |

**Se a nota avisasse dono + participantes ativos (menos o autor): 97 avisos** teriam saído das 212
notas com autor conhecido. Hoje saíram **zero**.

---

### ✅ O QUE FOI IMPLEMENTADO — 5 pontos, e o primeiro é uma recusa

**1. 🚨 NÃO somar nota no selo de mensagem do cliente.** É o caminho óbvio e é errado: aquele número
responde *"o cliente falou comigo"*, e enfiar nota ali faz a tela dizer que o cliente falou quando
foi um colega. É `M12` — tela que mente é defeito. **Selo próprio, separado, com ícone próprio.**

**2. O contador sai de uma tabela que JÁ EXISTE e JÁ é preenchida.** `nota_leitura` tem a PK
`(mensagem_id, atendente_id)`: **nota sem linha minha = nota que eu não vi**. Então o contador é um
`NOT EXISTS` sobre ela, no molde do `nao_lidas` — **sem migração nova**, igual ao `@` interno de
21/10, que também entrou sem migração.

**3. A quem avisa** — e aqui há uma decisão dele:
   - **dono + participantes ativos, menos o autor** (38 participantes ativos em 26 conversas): cobre
     os **65** casos de "conversa de outro";
   - 🔴 **os 207 em conversa SEM DONO são a pergunta.** Três saídas: avisar **o time** da conversa ·
     avisar **quem já escreveu nota ali** (vira conversa de bastidor, e é o que mais parece com o
     uso real) · **não avisar** (e aí 2/3 das notas seguem mudas). 🟡 **Sugiro "quem já escreveu nota
     ali" + o time**, porque é quem demonstrou interesse naquela conversa.

**4. O toque:** entra no `decidirToque` como **motivo próprio**, com **som e texto diferentes**
(*"Ludmila anotou em Fulano"*, não *"mensagem nova"*), e **respeitando o teto de 4** dele. ⚠️ A regra
dele de 24/09 é *"só conversa em que sou o dono"*; nota em conversa sem dono **não cabe** nessa régua
— é parte da decisão do ponto 3.

**5. Não retroativo, e com interruptor.** As 310 notas que já existem **não** viram 310 avisos: a
régua vale das notas novas em diante, exatamente como o `LEITURA_DE_NOTA_DESDE =
2026-10-15` que já está no código faz com o "visto por". E o interruptor nasce em **`/config` ›
Geral** (`CFG_7.1`), a convenção do MoviZap. 🟡 **Ligado por padrão**, porque ele pediu — ao
contrário dos atalhos de teclado, que nasceram desligados porque ninguém pediu.

🚨 **E o EVENTO não avisa.** Dos 840 registros `tipo='nota'`, **530 são o log de ações** (`evento IS
NOT NULL`): transferência, entrada, saída. Avisar isso encheria o selo de ruído sobre o que a própria
pessoa acabou de fazer. O filtro é `evento IS NULL`, o mesmo que a prévia da conversa já usa desde
15/10.

### O que eu NÃO proponho
- **Avisar por WhatsApp ou e-mail.** Nota é interna; sair do painel muda a natureza dela.
- **Push do navegador para quem está com o painel fechado.** A régua de presença dele (3 tempos,
  19/10) já decide quem está disponível; aviso para painel fechado é outra frente.
- **Mexer no selo do cliente, no chat interno ou no `@`.** Os três ficam como estão.

✅ **O ponto 3 foi resolvido com a régua dos três** (dono · convidado · quem já anotou ali), que é o
que faz a conversa sem dono ter destinatário. O toque soa para elas também, pela fila própria da
nota. ⚠️ **Sobram 76 notas sem destinatário possível** — autor é o único que já anotou e não há dono
nem convidado. Avisar **o time** nesses casos é decisão dele, e não entrou.

---

## 0.00000000000000000000000000000000 🔵 27/10 — FPSL/Painel Financeiro: as 25 pendências vivas das duas telas (`FIN_1.1` Conferência de Fechamento e `FIN_2.1` Fechamento Técnicos)

🔵 **Origem: quatro frases dele no mesmo dia** — *"sobre o FPSL a função de
conferencia de fechamento, veja se a 16991 esta com inconsistenvcias mesmo // e
a fechamento tecnicos, a regra é o filtro de 'Serviço Realizado' +
'Finalizada'? ou somente o primeiro item? apure"* → *"audite ambas e veja se as
regras funcionam e se precisa corrigir algo no painel"* → *"depois me traga com
certeza as OS com situação de 'Serviço realizado' que estão sem tecnico
válido"* → *"documente tudo isso como pendencia desas telas"*.

🚨 **NADA FOI ALTERADO EM 27/10.** A sessão foi inteira de leitura e medição,
no código da VPS, no `data/fpsl.db` e **ao vivo no Harmonit e na WESO**. Toda
linha abaixo foi conferida hoje; nenhuma veio copiada de lista antiga
([[feedback_pendencia_se_mede_nao_se_copia]]).

### O que ficou provado antes de qualquer pendência

**1. A OS 16991 tem UMA inconsistência, e ela é real.** Vereditos de hoje
(conferida 27/10 12:25 UTC): Ação ✅ · Vínculo na WESO ✅ · **Modelo 🔴
divergente** · DataScope ⬜ cinza ("Aprovado análise técnica", parado desde
01/10 14:46). O Modelo não é falso positivo: `problema 7421` RETIRADA, saem as
séries `907011861` (WESO: Suntech ST340 → produto **7004**) e
`356354872124749` (WESO: XT40-TM → produto **600267**), e a OS lança material
`20314` ST310U. Sem LEITOR RFID nos materiais, a regra do ST340RB não se
aplica. **É a única divergência de modelo das 109 linhas da tabela.** ⚠️ Mas a
16991 é a **sandbox oficial** (doc §6, frase dele: *"é uma OS real criada para
teste"*; descrição `PLACA: TESTE_DATASCOPE - ID: 356354872124749`, placa
`PLACA1`) — a regra acertou, o dado é artificial.

**2. O filtro do `FIN_2.1` é SÓ "Serviço Realizado".** `services/fechamento.py`
chama `listar_os_historico_periodo(..., situacao_id=15694)` e `storage.py:1838`
monta `AND situacao_id = ?`. **Não existe filtro de `status`/`status_str` em
lugar nenhum** — nem no `fechamento_router.py`. Os três filtros reais são:
situação 15694 · `data_previsao` no período · ter técnico real **e** linha de
conferência. 🚨 **E "Finalizada" não poderia ser filtro: mataria a tela.** Das
16 OS em 15694 hoje, **14 estão `Iniciada`, 1 `Nova` e só 1 `Finalizado`** (a
16808). A situação é marcada por gente ANTES de o status virar Finalizado —
isso é o normal, não anomalia.

**3. 🔴 Metade das OS em "Serviço Realizado" não tem técnico válido: 8 de 16.**
Lido ao vivo no Harmonit, OS por OS. **R$ 450,00 de PAGAMENTO DE TÉCNICO +
R$ 70,35 de KM lançados sem a quem pagar.** 7 das 8 têm como "técnico" o
`usuarioId 629 = MOVISAT SOLUCOES TECNOLOGICAS LTDA. - ME`, a própria empresa;
a 16816 não tem ninguém.

| OS | status | problema | Pagamento | KM (R$) | técnico no campo |
|---|---|---|---|---|---|
| 16816 | Nova | 7384 MANUTENÇÃO | — | — | **nenhum** |
| 16866 | Iniciada | 7457 CONTRATO NOVO | 120,00 | 50,00 | MOVISAT (629) |
| 16871 | Iniciada | 7457 CONTRATO NOVO | 120,00 | — | MOVISAT (629) |
| 16999 | Iniciada | 7502 RESCISÃO | 50,00 | 10,00 | MOVISAT (629) |
| 17003 | Iniciada | 7372 ADITIVO | 80,00 | 10,35 | MOVISAT (629) ×2 |
| 17004 | Iniciada | 7372 ADITIVO | 80,00 | — | MOVISAT (629) |
| 17023 | Iniciada | 7549 | — | — | MOVISAT (629) |
| 17026 | Iniciada | 7502 RESCISÃO | — | — | MOVISAT (629) |

As 8 **com** técnico válido: 16705 Franck · 16808 Pedro Felipe · 16926 Eder ·
16991 Franck · 17001 Pedro Felipe · 17002 Franck · 17010 Franck · 17015 Franck.
Os 9 excluídos do cadastro: 629 MOVISAT · 643 Implantação Fullcontrol · 747
PARCEIROS MOVISAT · 1206 Claudia · 1454 Rodrigo · 7493 Iago · 8528 Aline ·
12896 Ludmila · 12937 Erika.

**4. Por que as 16 OS não aparecem no filtro 01/10 → 01/11.** O painel é
**kanban de cards por técnico**, não lista de OS. Das 16, só **10 têm
`data_previsao` no período**; dessas, 4 já estão nos cards 12/13/14 e 6 são
barradas. A frase que a tela monta nesse clique: *"Nenhuma OS nova. 4 OS já
estavam em cards · 6 OS ficaram de fora: sem conferência (17002) · sem técnico
(16999, 17003, 17004, 17023, 17026)"*. **O `M12` aqui está cumprido.**

### A. Pendências JÁ ANOTADAS e ainda abertas — 13

| # | Pendência | Origem | Prova conferida em 27/10 |
|---|---|---|---|
| A1 | **A "Ação" (E4) nunca foi implementada** — a metade da frente que ele pediu: *"o painel de fechamentos terá duas funções, uma de conferencia e outra de ação"*. Desenho em `docs/fpsl/30 §5`: `change_state` → 74341, botão por linha, trilha `conferencia_acao`, atrás de `conferencia_acao_ativa` | 🔵 | `grep conferencia_acao` em todo o projeto = **0 resultados**; a chave não existe na tabela `config`. **É a maior pendência anotada das duas telas** |
| A2 | "Aprovado análise técnica" contar como DataScope OK (pend. 2 / achado 4 de 08/10) | 🔵 | `ESTADO_OK = "Finalizado"` intacto. **Efeito medido: 9 das 10 linhas da tela estão cinza por isso**, e é o que deixa os cards 12 e 14 amarelos |
| A3 | O OK do Fechamento exigir Ação e Modelo (pend. 3 / achado 6) | 🔵 | `services/fechamento.py:201` segue `harmonit AND datascope AND weso` |
| A4 | Vermelho travar o "Marcar Pago" (pend. 4 / achado 8) | 🔵 | `api_avancar_estado` não checa semáforo: valida só a transição e se o card está cancelado |
| A5 | Travar a troca de recibo em card Pago/Cancelado (pend. 5 / achado 9) | 🔵 | `upload_recibo` não olha o estado e grava sem trilha. **Pior do que anotado:** `atualizar_semaforo` devolve `None` para pago/cancelado, então o semáforo nem é recalculado depois da troca |
| A6 | Período pela data de finalização, não pela prevista (pend. 6) | 🔵 | `storage.py:1831-1836` monta o filtro sobre `data_previsao` |
| A7 | Popover mostrar o motivo da pendência (pend. 7) | 🟡 | `frontend/fechamento_tecnicos.html:583` escreve só *"OS N — conferencia pendente"*; o `conferencia_fechamento.detalhe` existe e não é usado |
| A8 | Cobrir `/painel/api/fechamento` na matriz de roteadores (pend. 8) | 🟡 | `tests/teste_roteadores_painel.py` tem 4 linhas de `conferencia-fechamento` e **nenhuma** de `fechamento` |
| A9 | Elo OS ↔ resposta do DataScope é texto livre digitado (`Nº da O.S.`) — lacuna 2 da doc | 🔵 | segue de pé |
| A10 | `form_state` não volta para `null` — lacuna 3 | 🔵 | segue |
| A11 | Rate limit do DataScope sem documentação — lacuna 4 | 🔵 | segue |
| A12 | **Ele validar no navegador a nota "Última passada" da `FIN_1.1`** (entrega de 16/10, `M9`) | 🔵 | o código está no ar (`conferencia_fechamento.html:209-214`, 3 estados) e o carimbo de hoje existe: *"7 conferidas, 0 datas preenchidas"*, 12:25. Falta só o clique dele |
| A13 | Dado: "KM da 16931/16978 se perde (sem técnico)" (nota de 08/10) | 🔵 | a **16978** continua assim: R$ 98,80 de KM, nenhum técnico válido |

⚠️ **Checado e descartado:** suspeitei de furo de permissão em 9 das 11 rotas do
`fechamento_router.py` (só `avancar` e `cancelar` têm `Depends` na assinatura).
**Não há furo** — o `APIRouter` carrega
`dependencies=[Depends(requer_aba("financeiro"))]`, que cobre as 11; o `Depends`
repetido nas duas serve para pegar o `usuario` da trilha.

### B. Pendências NOVAS desta auditoria — 12 (não estavam anotadas em lugar nenhum)

| # | Pendência | Origem | Medida |
|---|---|---|---|
| B1 | **Abrir a porta da Conferência para OS sem oficina.** Tirar `n_oficinas > 0` de `storage.os_com_oficina_recentes` e `storage.os_para_conferir`. A regra em `conferencia_oficina.conferir_os` **não muda** — já devolve cinza correto para OS sem oficina | 🔵 *"não é necessario oficina para exibir o card, necessariamente, por exemplo uma OS de manutenção no local não tera Oficina - proponha"* | Custo: releitura horária no Harmonit vai de **20 → 72 OS**; a chamada da base da WESO não muda. Destrava a **17002** (Franck, R$ 80,00 + R$ 164,00) e mais 2 com valor (16978, 16993) |
| B2 | **O `conferencia_ok` tem de separar "não se aplica" de "ainda não aconteceu".** Sem isso o B1 não funciona: com `weso_ok = NULL` a OS fica amarela para sempre e o card nunca fecha | 🟡 | para OS sem oficina o único sinal real é o DataScope |
| B3 | **A tela promete "últimos 30 dias" e mostra 3 OS fora da janela, com veredito congelado:** 16866 e 16871 (conferidas 15/10, vistas há 41 dias) e 16926 (21/10, 36 dias) | 🟡 | `listar_conferencia_fechamento` **não filtra janela**; só a fila da rotina filtra. O próprio carimbo confessa: *"**7** conferidas"* e a tela exibe **10** linhas |
| B4 | **6 das 16 OS em "Serviço Realizado" não aparecem na tela, e nada diz:** 17002/17023/17026 (`n_oficinas = 0`) e 16705/16808/16816 (vistas há 60-81 dias, nunca conferidas) | 🟡 | proposta: rodapé *"16 em Serviço Realizado · 10 na tela · 6 fora: 3 sem oficina, 3 fora da janela"* — o mesmo remédio que o `FIN_2.1` já tem no "Gerar" |
| B5 | **A finalização se desfaz por mais que o status 14.** `finalizacao_da_timeline` só zera no 14 "Cancelamento da Conclusão"; os **4 eventos `7 Reagendado`** de 21/10 na 16991 devolveram a OS para `Iniciada` e a data de 07/10 ficou na tela | 🟡 (regra minha de 01/10, incompleta — o pedido dele foi só a ordenação: *"exibir ordenadamente o que foi finalizado mais antiamente no topo"*) | afeta **1 linha** hoje: 99 com `finalizado_em` e status Finalizado × **1** Iniciada. Alternativa mais barata: a tela não mostra data quando `status_str <> 'Finalizado'` |
| B6 | **Trocar o eixo da janela de 30 dias**, de `visto_em` (≈ criação) para "quando a situação virou 15694" | 🟡 | ⚠️ essa data **não existe em coluna nenhuma** hoje: exige coluna nova (`situacao_15694_em`) gravada pela varredura, e as já marcadas entram por carga única. Destrava **16808** (Pedro Felipe, R$ 140,30 — a única "Finalizado" das 16) e **16705** (Franck, R$ 168,70) |
| B7 | **Ajustar o subtítulo da `FIN_1.1`** — *"Entram aqui as OS **com oficina**..."* deixa de valer com o B1. Obrigatório junto dele (`M12`) | 🟡 | — |
| B8 | **Filtrar `excluida = 0` no Fechamento.** `listar_os_historico_periodo` não filtra, ao contrário da porta da Conferência | 🟡 | **25 OS excluídas** no banco, nenhuma em 15694 hoje. Risco latente, uma linha de SQL |
| B9 | **Mais de um técnico real → não escolher.** `_tecnico_real_da_os` pega o **primeiro** e ignora os demais em silêncio | 🟡 | hoje inofensivo: **0 de 441 OS** têm mais de um técnico real (3 têm o mesmo `usuarioId` repetido, do 2º vínculo do agendamento, e isso não duplica valor). Proposta: mandar para `ignoradas` com o motivo |
| B10 | **As 99 linhas da porta velha e o que fazer com elas.** ⚠️ **CORREÇÃO do que eu afirmei antes:** `_checar_weso` e `_checar_datascope` **NÃO são código morto e NÃO se apagam** — `verificar_conferencia.py` (raiz do repo, script de conferência à mão) chama os dois (`:53` e `:57`, este com `16450`). A memória do projeto já avisava *"não apagar"* e eu ia propor a remoção; conferido no arquivo. Sobra só: o parâmetro `numero_os` de `_checar_datascope` não é usado no corpo, e as 99 linhas ocupam a tabela | 🟡 | as 22 divergências de WESO da tabela são **todas** texto da regra velha e **nenhuma aparece na tela** (a lista faz `JOIN ... WHERE situacao_id = 15694`). **99 das 109 linhas são da porta velha**, com `acao_ok`/`modelo_ok` nulos. Decisão dele: deixar como está (foi o combinado em 01/10) ou mover para tabela de histórico |
| B11 | **A sandbox 16991 está no card 12, em "pagamento"** — R$ 137,55 para o Franck, recibo `12_11_orcamento_11005.pdf` anexado, semáforo amarelo: **um clique de "pago"**. O botão "Cancelar" já existe e libera a OS | 🟡 | só com o OK dele |
| B12 | **8 OS em "Serviço Realizado" sem técnico válido** (tabela no início deste bloco) — é dado, corrige-se no Harmonit | 🔵 *"depois me traga com certeza as OS... que estão sem tecnico válido"* | R$ 450,00 + R$ 70,35. O painel já as nomeia no "Gerar" |

### C. Anotada mas VENCIDA pelo dado — 1

**C1. A lacuna 1 de `docs/fpsl/30_Painel_Financeiro.md §7` está desatualizada**
(`M12` dentro da própria doc): *"Nada move a situação para 15694 hoje — a Ação
nasce sem fila"*. Medido: **16 OS estão em 15694, 10 delas marcadas em
outubro**. A equipe move, sim; a fila existe. O texto é de 01/10 e nunca foi
revisitado.

### D. As 6 decisões dele que travam o resto

1. **"Não se aplica" conta como verde?** (B2) — **(a)** sim, fica verde quando o
   DataScope finalizar (🟡 recomendo: amarelo eterno mata a credibilidade do
   semáforo, foi a lição das 46 acusações em 199) · **(b)** não, sai do vermelho
   mas nunca fica verde e ele libera à mão.
2. **Ação e Modelo entram no `conferencia_ok`?** (A3) — é a mesma linha que o B2
   altera; decidir junto evita mexer duas vezes.
3. **Trocar o eixo da janela de 30 dias?** (B6) — exige coluna nova.
4. **Cancelar o card 12 (sandbox)?** (B11).
5. **Retomar a "Ação" (E4)?** (A1) — muda o sentido de A2 e A3.
6. **Qual estado do DataScope conta como OK?** (A2) — causa de 9 dos 10 cinzas
   da tela.

### E. Anotadas e JÁ FECHADAS — não voltam à lista

Rotina da `FIN_1.1` religada em 08/10 18:20 (`conferencia_fechamento_ativa =
true`, carimbo de hoje) · achado 3 → o quadro filtra por sobreposição e o card
12 aparece na semana 05-11/10 · achado 2 → "um card aberto por técnico e
período" (índice `ux_cartao_aberto`), cancelar+gerar não dá mais 500 · achado 5
→ a mensagem do "Gerar" diz o que ficou de fora (conferido na fonte: usa
`os_ja_consumidas`, `ignoradas_sem_conferencia`, `ignoradas_sem_tecnico`,
`conferencia_ativa`) · achado 7 → card nasce com semáforo.

### F. Sequência sugerida (🟡 minha)

Decidir **D1, D2 e D3** → entregar **B1 + B7 + B2/A3** juntos (uma entrega) →
**B5, B3, B4** → **B8, B9, B10** → **B11** por último. **A12** e **B12** em
paralelo, do lado dele. **A1** (a E4) é projeto próprio, não item de lista.

⚠️ **Uma lição de método desta sessão:** eu ia propor apagar `_checar_weso`
como código morto. A memória do projeto dizia *"`verificar_conferencia.py`
ainda usa `_checar_weso` — não apagar"*, fui conferir o arquivo e **a memória
estava certa**. "Sem chamador" eu tinha medido só dentro do pacote
`fpsl_weso/`; o chamador vive na **raiz do repo**. Varredura de uso tem de
cobrir os scripts soltos da raiz, não só o pacote.

---

## 0.0000000000000000000000000000000 ✅ 23/10 — FPSL: o modal de perfil escondia tela, e as concedíveis foram de 5 para 7

🔵 **Origem: frase dele** — *"criando conta no FPSL de karla, mas na aba de
exibir telas, as telas novas não aparecem corrija, por favor"*.

### O defeito, e por que ninguém tinha visto

Não era o registro de telas — era **a tela de Usuários escondendo informação**.
O modal lista **uma linha por permissão**, e nomeia a linha com o título da
**primeira** tela daquela permissão:

| Permissão | O que ele lia | O que estava concedendo de verdade |
|---|---|---|
| `financeiro` | "Conferência de Fechamento" | FIN_1.1 **+ FIN_2.1 Fechamento Tecnicos** (06/10) |
| `operacoes` | "Operações" | OPR_1.1 **+ HST_4.1 Histórico de Operações** |

🚨 **O backend já mandava `codigos` desde agosto; o HTML descartava.** Era
`M12` em estado puro: o texto era verdadeiro quando foi escrito, e a entrega
seguinte não voltou para matá-lo. E só apareceu agora porque **a tela de
Usuários só é aberta quando se mexe numa conta**.

### A segunda volta: *"ela precisa das abas que eu quiser"*

Decisão dele: *"todas devem permitir que eu escolha o que ela vê, como os
demais"*. `PERMISSOES_SO_OWNER` foi de **3 para 1**, e as concedíveis de
**5 para 7** (`contratos` e `config` saíram).

⚠️ **Sair da lista não concedeu nada a ninguém** — só faz a permissão
aparecer no modal, **desligada**. Nenhuma conta existente mudou.

🔴 **`usuarios` FICA de fora, e não por tradição:** **nenhuma rota exige
essa permissão** — o `usuarios_router` inteiro é guardado por
`get_owner_painel`. Concedê-la daria tela no menu com **403 em toda chamada**:
a porta trancada que matou a aba `placas` em 14/08, e que o bloco [4] do teste
prende. Delegá-la exige trocar a guarda do router — e aí quem recebe **cria
contas e conceda permissão a si mesmo**, o que encerra a distinção de owner.
**Decisão dele, não conserto.**

🚨 **O efeito colateral que veio junto:** a rota da `CFG_9.1` era guardada
por owner, com a justificativa escrita no código (*"duas travas para a mesma
coisa é uma delas mentindo em algum momento"*). O momento chegou: com `config`
concedível, ela viraria porta trancada. Trocou para `requer_aba("config")`.

### A conta da Karla, conferida ao vivo

`id 526` · `financeiro@movisat.com.br` · criada **23/10 10:09** · ativa ·
`abas = ["financeiro", "contratos"]`. Menu dela: **FIN_1.1 + FIN_2.1 +
CTR_1.1**. As 8 demais, fora.

⚠️ **Ela JÁ ENTROU:** o `google_sub` está gravado, e esse campo só é
preenchido **depois de um login pelo Google**, não no cadastro. Se entrou antes
de ele marcar `contratos`, basta sair e entrar de novo.

### O que mudou, e a prova

| Arquivo | O quê |
|---|---|
| `painel/telas.py` | `para_frontend` devolve `telas: [{codigo,titulo,icone}]`; `PERMISSOES_SO_OWNER = {"usuarios"}` |
| `painel/routers/usuarios_router.py` | CFG_9.1 passa a exigir `requer_aba("config")` |
| `frontend/usuarios.html` | a linha lista as telas; tolera backend antigo |
| `tests/teste_registro_telas.py` | **bloco [9]** novo |
| `docs/fpsl/27_Registro_Telas.md` | tabela + seção "Só do owner" reescritas |

🚨 **A invariante que faltava, e que deixou o defeito passar 2 meses:**
*nenhuma tela ativa e concedível pode ficar fora do modal de perfil* — mais a
checagem de que **o HTML consome o dado**, porque o backend já mandava e a tela
jogava fora. Conferido que as duas falham contra os arquivos de antes.

**Suites:** registro de telas **50 OK** (eram 43) · aba Operações **35 + 62
OK** (é intocável, conferi) · contratos **95** · acabamento **28**. **0 falhas.**
Serviço `fpsl-weso` reiniciado (unidade de **usuário**). Backups `.bak_2026-10-23`.

🚨 **ARMADILHA NOVA, me custou uma volta:** heredoc por `ssh` **executa o
que está entre crases** — um comentário com `` `financeiro` `` chegou na VPS
com as palavras apagadas e `command not found` no terminal. A regra de sempre
vale também para crase, não só para acento: **arquivo + `scp`**.

---

## 0.000000000000000000000000000000 🔍 22/10 — CONFERIR A DOCUMENTAÇÃO achou TRÊS pontas fora do repositório

🔵 Ele perguntou duas vezes *"tudo documentado?"*. Em vez de responder,
procurei o que **não** estava, por `grep`, lugar por lugar. 🚨 **Nenhum dos
três era código do dia** — eram as pontas que vivem **fora do repositório e
fora do diff**.

1. 🚨 **`forms.movisat.com.br` não estava no `docs/03_Exposicao_de_Rede.md`**
   (o da VPS, `/home/claude/docs/`) — um domínio **público, sem login**, aberto
   hoje, fora do documento cuja única função é dizer *"o que está aberto, e por
   quê"*. Mesmo tipo de buraco que aquele doc nasceu para fechar em 11/08.
   **Corrigido:** entrou na tabela de hosts e ganhou seção própria.
2. 🚨 **A pasta de anexos dos formulários não estava em backup NENHUM.** O
   `backup_midia.sh` espelhava só `/home/claude/movizap_midia`. E o conteúdo da
   outra é o **pior de perder**: é a **única cópia** de documento que o cliente
   mandou (contrato social, comprovante de endereço) — o banco guarda o
   **caminho**, não o arquivo. **Corrigido:** o script espelha **duas** pastas,
   com instantâneo datado e conferência de contagem nos dois lados; rodado de
   verdade (mídia **4.597** arquivos intactos, anexos **0**).
3. **O `.env` de um install novo não teria `MOVIZAP_FORMULARIOS_SEGREDO`** —
   máquina nova nasceria no *fallback* (segredo derivado do `jwt_secret`), que
   é fallback e não o normal. **Corrigido** no `gerar_env.py`.

⚠️ **A lição:** *"documentado"* não é *"o código tem comentário"* — é **alguém
que não estava aqui conseguir achar isto depois**. O diff estava documentado; o
que faltava era nginx, backup e `.env`.

---

## 0.00000000000000000000000000000 🔍 22/10, AUDITORIA DO DIA — quatro buracos achados e fechados

🔵 **Pedido dele:** *"quer documentar e auditar os feitos?"*. Medida, não
afirmada. Detalhe por achado em `docs/06` (22/10, a seção da auditoria).

1. 🔴 **As dez rotas que entraram hoje não tinham teste HTTP nenhum** — e **17
   arquivos** da suíte usam `TestClient`. A mais exposta do projeto (o **POST
   público de formulário**, que qualquer um na internet alcança) estava provada
   só por `curl` meu, à mão. **Fechado:** `tests/teste_rotas_formularios.py`,
   **33 testes**. ⚠️ Mesma lição de 21/10: **prova ao vivo não substitui
   teste**.
2. 🔴 **Três funções que a tela usa e teste nenhum chamava:**
   `listar_solicitacoes` (a lista da FRM_1.1 com os filtros),
   `lista_para_o_painel` (o cabeçalho com a contagem) e `registrar_envio` —
   mais `desafio_sempre`, a desduplicação do `nome_legivel` e
   `paineis._resumo`. Todas cobertas.
3. 🚨 **A suíte nova passou na primeira rodada e REPROVOU na segunda** — o
   achado mais útil, e contra mim. Cada envio bom conta no **SQLite do
   `ratelimit`**, que sobrevive ao processo de propósito; em duas rodadas os
   envios de teste passaram de 5 na mesma hora, a rota começou a exigir a
   conta de somar, e todo teste seguinte recebia a frase errada. A fixture
   `contador_limpo` apaga **só** a chave do `TestClient`. Confirmado em **três
   rodadas seguidas**.
4. 🚨 **`M12`: cinco textos passaram a mentir** quando o grupo "Painéis" ganhou
   tela — *"Painéis › Operacional nasce vazio"* no cabeçalho de `GRUPOS`, em
   dois comentários de telas, no `MenuLateral` (duas vezes) e no **`docs/03`**.
   Corrigidos os cinco; o grupo declarado e vazio passou a ser o **"E-mail"**.
   ⚠️ O `docs/06` não entra: é diário.

**Conferido e certo:** migração **076** é a última (`validar_miolo`: 58
tabelas) · segredo dos tokens no `.env`, 64 caracteres, **sem** aviso de
derivação no log · pasta de anexos em **700** e vazia · host público deixando
passar **só** `/f/`, `/pub/assets/` e `/api/publico/` (o resto 403) ·
formulário desligado dando **404 igual a slug inexistente** · **nenhuma** sobra
de teste no banco · árvore do git limpa.

**Suítes: 1746 Python · 440 JS.**

🔴 **A única sobra deliberada:** a **solicitação 39** (`zz Externo`), que é a
prova de ponta a ponta pela internet e serve para ele ver a tela com conteúdo.
**É dele apagar.**

---

## 0.0000000000000000000000000000 ✅ 22/10, sexta volta — PAINEL DA OPERAÇÃO NO AR (opção A), e os outros três documentados

🔵 **Escolha dele**, depois dos mockups: *"vamos de A somente para a Operação
por enquanto, mas bem documentado para as demais futuramente"*.

**No ar:** `PNL_1.1 Operação` · rota `/paineis/operacao` · grupo **Painéis** ·
permissão **owner**. Primeiro habitante do grupo que nasceu vazio em 19/10 — e
o subgrupo **"Operacional" saiu**, o que **fecha a pendência 6 do plano**
(*"alinhar o nome"*): ele nunca teve tela, e o painel chama-se "Operação".

| peça | o que é |
|---|---|
| migração **075** | `formulario.painel` — o mapa dele (plano §2.1) como **DADO**: mover um formulário de painel não exige deploy. Uma fonte só (a tabela `NOSSOS` da carga), reescrita a cada carga; **`ativo` não entra nela** |
| migração **076** | `formulario_solicitacao.situacao_id` · `situacao_em` · `situacao_erro` — **cache com a hora da leitura** (a verdade é do Harmonit) |
| `movizap/paineis.py` | as 11 situações como vocabulário das colunas + as duas colunas que não são situação |
| rota | `GET /api/paineis/{painel}` (`PNL_1.1`) — **uma**, não quatro |
| tela | `frontend/src/telas/PainelOperacao.vue` (13 colunas, rolagem horizontal) |
| módulo novo | **`PNL`** — painel não é atendimento (não se responde ninguém por ele) nem relatório (não se lê e fecha): é fila que se movimenta |

**Suítes: 1713 Python · 440 JS** (18 e 12 novos).

### 🚨 As regras desta tela, que não se reinventam

1. **"Sem OS" é a primeira coluna** porque é de onde a OS nasce. Hoje **todas**
   as solicitações estariam nela — e é o estado certo, não tela quebrada.
2. **"Sem situação" existe por número medido:** 127 OS com `situacao_id = 0` e
   37 com `NULL` nas 574 do cache do FPSL. **164 OS desapareceriam** sem ela, e
   os **três** casos (nulo, zero, número fora da lista) caem nela **com o
   número cru à vista**.
3. **Mover o card NÃO existe, e a tela diz por quê** — não há `draggable` no
   HTML, e um teste prende isso. Oferecer o gesto sem gravar seria pior que não
   ter o gesto (precedente: `ModalAgendar`).
4. **Coluna vazia nasce colapsada**, com o contador à vista; as duas primeiras
   nunca colapsam.
5. **A cor nunca é o único portador:** estado e situação vêm escritos.

### 🔵 Os outros três — desenhados, medidos, NÃO implementados

Estão por extenso em `docs/06` (22/10, a seção do painel) e nos mockups
(`https://claude.ai/artifact/3mM5bs3gv1hYsyTaShsd6s`). 🚨 **Nenhum é este com
outro filtro** — quando um nascer, nasce com módulo e rota próprios.

- **Pós venda** — 🚨 **não é fila, é medição**, e isso saiu do formulário:
  nota 8/9/10 pede **indicação**, 7 ou menos pede **o que ocorreu**
  (obrigatório), e **NPS e CES não geram OS**. 🔴 Falta dele: **o corte do
  promotor, 8 ou 9**.
- **Contratual** — o que trava é o **documento** (falta → a conferir → pronto).
  🔴 Falta dele: **endereço** (Harmonit, ViaCEP ou os dois).
- **Financeiro** — fila simples; o único com **elo externo** (pagamento de
  técnicos ↔ `FIN_2.1` do FPSL). ⚠️ Risco: **segunda contabilidade**. 🔴 Falta
  dele: ligar ou não, e se mostra **valor** — **nenhum dos quatro formulários
  tem campo de valor** hoje.

### 🔴 O que a próxima volta espera dele

1. **O mapa formulário → `problemaId`** — sem ele a solicitação não vira OS, e
   as duas rotas novas da ponte (**criar OS** e **escrever `situacaoId`**) não
   podem nascer.
2. **Validar no navegador** (`M9`): abrir `/paineis/operacao`, ver as 13
   colunas, abrir uma colapsada, e conferir que o card leva para a ficha.

---

## 0.000000000000000000000000000 🔵 22/10, quinta volta — PAINÉIS: mockups e plano por tipo (PROPOSTA, nada no ar)

🔵 **Pedido dele:** *"e os paineis da Operação, etc?"*, depois *"lembre-se que
pedi os mockups"* e *"planos para cada tipo"*, com o aviso *"veja no plano o
que fala disso para nao ter erros de escopo"*.

🚨 **O que o plano diz, lido antes de propor:** a Etapa 3 cabe em quatro
parágrafos — grupo `Painéis`, permissão `owner`, colunas = as 11 situações, e
*"mover o card = ESCREVER `situacaoId` no Harmonit"* pelo caminho provado do
`os_ponte.py:_corpo_de_escrita`. Mais o §8.3 (os três modelos visuais que já
existem no FPSL) e o §8.4 (a paleta). **A palavra "mockup" NÃO aparece no
plano** — mockup e plano por tipo são demanda dele desta conversa.

**Mockups (6 telas, lado a lado):**
`https://claude.ai/artifact/3mM5bs3gv1hYsyTaShsd6s`
Três opções para **Operação** (A kanban por situação · B grid com tag · C
quadro de demandas com a faixa de "quem é a vez") e uma tela própria para
**Pós venda**, **Contratual** e **Financeiro**. Tokens reais do painel
(`tokens.css`), menu escuro, 44 px de toque, e cada tela com o seu plano e o
que falta dele escrito no pé.

### 🚨 Os três achados que o desenho obrigou a medir

1. **78% das OS não têm situação útil.** Das **574** no cache do FPSL: **282**
   em `38 Nova sollicitação`, **127** com `situacao_id = 0`, **37** com `NULL`,
   e só 128 espalhadas nas outras. As 11 colunas nasceriam com tudo numa pilha
   — o que confirma o *"hoje ainda não usamos a situação da OS"*.
2. 🚨 **`0` e `NULL` são dois estados diferentes, e nenhum é uma das 11.** Sem
   uma coluna **"sem situação"**, **164 OS desaparecem da tela**.
3. 🚨 **Pós venda NÃO é fila, é medição** — e isso saiu do formulário, não de
   gosto: a nota é lista de 1 a 10 e as regras do NPS já separam quem
   respondeu — **8, 9 ou 10 pede INDICAÇÃO** (nome, telefone, e-mail, empresa);
   **7 ou menos pede O QUE OCORREU**, e esse campo é obrigatório. NPS e CES
   **não geram OS**: kanban por situação ali não mede nada.

### 🔴 Decisões dele que o painel espera

| o que | por quê |
|---|---|
| **qual das três opções** para Operação (A, B ou C) | A ensina o fluxo e é ruim no celular; B é a mais barata e não ensina; C responde *"de quem é a vez?"* mas **exige uma cadeia de etapas que não existe** |
| o mapa **formulário → `problemaId`** | sem ele a solicitação não vira OS, e o card fica com metade |
| **o corte do promotor: 8 ou 9** | o formulário do Bitrix trata **8 como promotor**; no NPS de mercado 8 é neutro |
| **endereço** nos contratuais | Harmonit, ViaCEP, ou os dois — o cadastro do MoviZap não tem endereço em forma nenhuma |
| ligar ou não **pagamento de técnicos** ao fechamento do FPSL | o risco é virar uma **segunda contabilidade** ao lado do FIN_2.1 |
| se o painel mostra **valor** | **nenhum dos 4 formulários financeiros tem campo de valor** hoje |

⚠️ **Nada disto está no ar, e nada de código foi escrito nesta volta** — é
proposta para ele escolher. As duas rotas que a ponte do FPSL ainda não tem
(**criar OS** e **escrever `situacaoId`**) continuam pendentes, e é por elas
que a Etapa 3 começa quando ele decidir.

---

## 0.00000000000000000000000000 ✅ 22/10, quarta volta — FORMULÁRIOS PRÓPRIOS: a Etapa 1 no ar, o CES recebendo pela internet

🔵 **Demanda dele** (o plano está em `C:\Users\Lenovo\Desktop\MoviZap_Formularios_PLANO.md`):
*"nenhuma possibilidade irá usar o bitrix, esse projeto é movizap"*. Os 15
formulários de `solicite.movisat.com.br` eram **Bitrix24 CRM Webforms** e
concentravam toda a entrada de demanda da Movisat. A Etapa 1 — **os
formulários genéricos em `forms.movisat.com.br`** — está no ar.

🔵 **As quatro decisões dele desta volta**, perguntadas antes de escrever:
| tema | decisão |
|---|---|
| escopo | **CES primeiro**, os 15 depois que ele validar no navegador |
| bundle | *"qual a mais segura para os links que terão acesso externos"* → **bundle separado** |
| chegada | tela nova **+ interruptor por pessoa, igual as demais notificações** |
| anexo/abuso | limite por IP + isca, **anexo isolado na VPS**, e a conta de somar **só no fim** — *"usam pelo cel então não pode virar entrave de processo"* |

### O que está no ar

| peça | onde |
|---|---|
| **`https://forms.movisat.com.br/f/ces`** | aberto, sem login, **o CES ligado**; os outros 14 nascem desligados |
| migração **074** | `formulario`, `formulario_campo`, `formulario_regra`, `formulario_solicitacao`, `formulario_arquivo` |
| `movizap/formularios.py` | definição, regras, **validação**, anexo, solicitação, defesas |
| 3 rotas públicas | `GET /f/{slug}` · `GET /api/publico/formulario/{slug}` · `POST` idem (+ `GET /api/publico/desafio`) |
| **`FRM_1.1` Solicitações** | grupo Atendimento, permissão `equipe`, `/solicitacoes` |
| o **4º selo** do menu | ao lado de WhatsApp, Chat interno e E-mail, somado no grupo fechado |
| interruptor por pessoa | `CFG_11.1` — nasce **ligado**, só aparece para quem tem a tela |
| interruptor do sistema | `CFG_7.1` › Geral, **no fim da tela** — conta de somar em todo envio, nasce desligado |
| nginx + TLS | certificado emitido; **o host público só alcança `/f/`, `/pub/assets/` e `/api/publico/`** |

**Suítes: 1691 Python · 428 JS** — **37 testes Python e 18 JS novos** nesta volta (`tests/teste_formularios.py`, `frontend/src/formulario_2210.teste.js`), mais os casos que a tela nova acrescentou aos testes de registro. A linha de base do começo do dia era 1651/410.

### 🚨 O que esta volta mediu, e não se reinventa

1. **O `visible` do loader do Bitrix NÃO diz quem nasce escondido.** Nos 15
   formulários **nenhum** campo vem com `visible: false`, e existem **60 ações
   `show`**. No Bitrix, ser alvo de `show` É o que esconde o campo. Quem
   traduz isso é a carga (`gravar_definicao`), que grava `visivel = false`
   nesses alvos. Confiar no `visible` faria **todo campo condicional aparecer
   sempre** — e a tela só ficaria "um pouco mais comprida", que ninguém nota.
2. **9 dos 15 têm regra condicional**, e cada item é independente
   (`condition` → `action`). O único grupo com `logic: "and"` (ficha
   cadastral, grupo 2446) tem as **oito condições idênticas**, então avaliar
   item por item dá o mesmo resultado — foi medido, não suposto.
3. **Condição em campo escondido não vale.** As regras se encadeiam (no
   credenciamento, A mostra B e B mostra C): o valor de um campo que a pessoa
   nunca viu não pode mandar em nada. Por isso a conta **repete até parar de
   mudar**, nos dois lados.
4. **A regra vive numa estrutura só**, e as duas suítes leem o **mesmo**
   arquivo de casos (`tests/casos_regras_formulario.json`) — o remédio contra
   o que aconteceu de manhã com um `WHERE` copiado em dois lugares.
5. **O termo de uso que o Bitrix serve é *boilerplate* em inglês** (*"Our
   rules are straightforward…"*) nos 3 formulários com aceite. Não se copia.
6. **`formulario_solicitacao` não é `ON DELETE CASCADE`**, de propósito:
   apagar um formulário com solicitação recebida é **recusado pelo banco**.
   Definição sai em cascata; o que o cliente escreveu, não.

### 🔴 Falta dele (validar no navegador — `M9`, nada acima substitui)

1. Abrir **`https://forms.movisat.com.br/f/ces` no celular e no PC**, enviar, e
   ver a solicitação na tela **Solicitações**.
2. Conferir o **selo no menu** e desligar o aviso na `CFG_11.1` para ver o
   número sumir.
3. **Apagar a solicitação de teste `39`** (`zz Externo · zz Pastelaria
   Velasco`) — é minha, da prova de ponta a ponta pela internet.
4. ✅ **FEITO — ele mandou ligar todos** (*"ligue todos os formulários no
   ar"*), e **os 15 estão no ar**, conferidos um por um pela internet:
   `ces` · `nps` · `suporte` · `demonstracao` · `teste-gratuito` · `contato` ·
   `ficha-cadastral` · `aditivo` · `substituicao-veiculos` · `rescisao` ·
   `administrativo` · `financeiro` · `credenciamento-tecnico` ·
   `pagamento-tecnicos` · `fornecedores`.
   ⚠️ **O BITRIX CONTINUA NO AR EM PARALELO**, e isso é consequência de ter
   ligado os 15: enquanto os dois existirem, a mesma demanda pode entrar pelos
   dois caminhos, e o nosso **não espelha nada** do deles. Desligar o Bitrix é
   dele (decisão já tomada no plano: *"o Bitrix fica no ar só até ele
   desligar"*).
   🔴 **E com isso nasceram duas pendências de verdade:** (a) **teste gratuito,
   ficha cadastral e fornecedores estão no ar SEM a caixa de aceite de termo** —
   no Bitrix os três pedem; o texto do Bitrix é *boilerplate em inglês* e não
   se copia, então **falta o texto dele**; (b) os dois que tinham **reCAPTCHA**
   (ficha cadastral e financeiras) agora dependem das nossas quatro camadas —
   se aparecer abuso, o interruptor da `CFG_7.1` pede a conta em todo envio.
   ⚠️ O **SUPORTE** serviu para provar o anexo de ponta a ponta pela internet
   (`.exe` recusado, `.txt` aceito, gravado em
   `/home/claude/movizap_formularios_anexos` com pasta própria) — a
   solicitação e o arquivo de teste foram apagados depois.
5. **Apagar os 14 registros de teste no Bitrix24** — `resultId` 15620 · 15622
   · 15624 · 15626 · 15628 · 15630 · 15632 · 15634 · 15636 · 15638 · 15640 ·
   15642 · 15644 · 15646 (nome `TESTE CLONE-VPS`).
6. **Decisões que a Etapa 2/3 espera:** para onde cada formulário cai no CRM
   hoje (funil, etapa, responsável — não é visível de fora) · o mapa
   formulário → `problemaId` · prioridade por formulário ou 382 Normal para
   todos · endereço nos contratuais (Harmonit, ViaCEP ou os dois) · **o texto
   dos nossos termos de uso** · revisar os `nosso_nome` dos 239 campos ·
   alinhar o nome do subgrupo "Operacional" com o painel "Operação".

### 🟡 Escolhas minhas, trocáveis

- **O aviso é o selo no menu, não uma mensagem no chat interno.** O plano dizia
  chat interno; medi antes de escrever e **o chat não serve**: `chat.nao_lidas`
  conta `c.atendente_id <> eu`, então **quem assina o aviso nunca o recebe** —
  e quem assinaria é o owner, que é justamente quem mais precisa dele. O selo
  chega a todos e é o mesmo mecanismo das outras notificações, que é o que ele
  pediu ("igual as demais").
- O interruptor do aviso **nasce ligado** (o aviso é o pedido).
- `nosso_nome` nasce derivado do rótulo do Bitrix (já humano: 'Primeiro
  Nome'), único por formulário. Ele revisa depois.
- `product` (2 campos) vira texto nesta etapa — sem catálogo nosso.
- A **raiz** de `forms.movisat.com.br` responde 404 de propósito: não existe
  "o formulário da Movisat", existem 15, e lista na raiz seria um catálogo de
  portas abertas.

### As defesas do envio, na ordem

isca invisível → **tempo mínimo de 3 s** entre abrir e enviar (token assinado,
sem sessão nem tabela) → **contagem de envios por IP** (`ratelimit.py` ganhou
`registrar_evento`/`quantos_eventos`, tabela separada: aqui nada bloqueia) → e
**só então** a conta de somar, servida por nós, sem imagem e sem terceiro.
Anexo: pasta **fora do projeto** (`/home/claude/movizap_formularios_anexos`),
lista branca de extensão, 10 MB por arquivo e 25 MB por envio, e **o host
público nunca serve anexo** — baixar é rota autenticada do painel.

### ✅ A carga dos 15 e a conferência que roda ANTES de ligar

Os 15 estão carregados, **239 campos**, e `scripts/conferir_formularios.py`
**preenche cada um em voltas** — como gente, porque escolher uma opção faz
nascer campo novo — **uma vez por opção do primeiro campo de lista** (que nos
15 é sempre o gatilho pessoa física/jurídica ou tipo de solicitação). Diz
`ENVIAVEL` ou `TRAVA`, confere a contagem contra o `mapa_bruto.json`, se o
`nosso_nome` é único e legível, e se existe **obrigatório que nenhuma regra
alcança** (seria formulário impossível de enviar).

**Resultado: os 15 ENVIÁVEIS, 0 problemas.** ⚠️ Prova que a validação aceita,
**não** que a tela esteja legível no celular — isso é `M9`, e é dele.

🚨 **O número que o Bitrix não mostrava é "de pé no início":** na **ficha
cadastral, 10 dos 36** campos só existem depois de uma escolha; na **rescisão,
8 dos 17**; no **NPS, 5 dos 9**. É isso que a regra condicional governa — e a
razão de campo escondido **sumir do registro** em vez de virar vazio.

`conferir_formularios.py --nomes <CODIGO>` imprime o de-para **nome de origem →
`nosso_nome`** para ele revisar os 239. Sai do **banco**, não de um documento à
parte.

### Onde está escrito

`docs/02_Modelo_Dados.md` (migração 074) · `docs/03_Registro_Telas.md`
(FRM_1.1, registro, ícone e perfis) · `docs/06_Conteudo_das_Telas.md` (22/10,
a seção dos formulários) · o insumo em
`dados/formularios_bitrix/mapa_bruto.json` + os 15 loaders, com
`scripts/extrair_formularios_bitrix.py` dizendo como reobtê-los.

---

## 0.0000000000000000000000000 ✅ 22/10, terceira volta — as quatro caixas de e-mail pelo modelo do Gmail

**Origem: 🔵 demanda dele** — *"siga com a 2"* (Entrada e selo passam a exigir o
rótulo `INBOX`) e *"enviadas devem ter seu proprio grupo, igual no Gmail"*.
**O porquê, dele:** *"depois dos formularios, vamos ter caixas fixas logadas
compartilhadas, então para chegarmos la, precisamos que funciona a pessoal"* —
a caixa pessoal é o ensaio da compartilhada.

**No ar.** Quatro caixas, e **826 mensagens caindo cada uma em exatamente
uma** (conferência por mensagem, não inspeção; a soma fecha com o total):

| caixa | msgs | não lidas |
|---|---|---|
| Entrada | **101** (bate com o Gmail) | **0** |
| **Enviados** (nova) | **219** | 0 |
| Arquivadas | **1** | 1 |
| Lixeira | 505 (com as **11** enviadas que estavam invisíveis) | 356 |
| **selo** | — | **0** (era 1) |

Suítes **1651 Python** (eram 1638) e **410 JS** (eram 406). Detalhe em
`docs/06` ("22/10, terceira volta") e a tabela estado→caixa em `docs/02`.

⚠️ **UM NÚMERO QUE EU DEI ERRADO NA VOLTA ANTERIOR, e corrijo aqui:** afirmei
que *"a aba Entrada está mostrando 219 enviadas"*. **Estava errado** — medi a
rota **sem** o parâmetro `marcador`, e a tela manda `marcador=INBOX`. A Entrada
nunca mostrou as enviadas (eram 101 msgs, 0 não lidas). O defeito real era só
**a tela filtrar por `INBOX` e o selo não**.

🚨 **MAS A MEDIÇÃO ERRADA ACHOU UM DEFEITO VERDADEIRO:** *"Entrada"* existia em
**dois controles** (aba de caixa **e** lista de marcadores) e a tela mandava os
dois juntos ao servidor. Era isso que deixava **11 enviadas na lixeira
invisíveis** (a Lixeira filtrava pelo rótulo da Entrada) e fazia a barra de
cima escrever *"Caixa de entrada"* **com a Lixeira aberta** — `M12` que ninguém
viu porque os dois controles concordavam por acidente. O modelo que ele pediu
conserta: **caixa é LUGAR, marcador é ETIQUETA**; `INBOX` e `SENT` saíram da
lista de etiquetas porque viraram lugar.

**Duas decisões minhas, tomadas por medição, trocáveis:** a mensagem com
`INBOX` **e** `SENT` (1 na base) fica na **Entrada**, para manter "exatamente
uma caixa" — o Gmail mostraria nas duas. E a sem nenhum dos dois (1: o *"Alerta
de segurança"*, arquivado no Gmail) foi para **Arquivadas** — sem isso ela
cairia em caixa nenhuma, que é o defeito das 73 sumidas da volta anterior.
**Foi por ter acabado de errar nisso que eu procurei por ela.**

### 🚨 O que a suíte achou — e só uma coisa era fixture

1. **Defeito de produção que esta mudança ia introduzir:** `restaurar()` punha
   `INBOX` no Gmail e **não gravava o marcador local** → restaurar mandaria a
   mensagem para Arquivadas. A ironia está no corpo da própria função desde
   17/09, sobre o outro lado (*"o `untrash` sozinho não devolve o `INBOX`"*).
   Consertado no **ponto único** (`_mexer_rotulo`), o que corrigiu de passagem
   `arquivar`, `marcar_nao_lida` e `excluir`.
2. 🚨 **O duplo dos testes ficou irreal por minha causa:** ao pôr o espelho
   dentro do `_mexer_rotulo`, o mock daquela função passou a desligar **regra**
   junto com a rede, e o teste de restaurar **reprovou com o código certo**. A
   chamada HTTP saiu para `_modificar_no_gmail` e o duplo desceu para a borda.
   **Duplo se põe na BORDA, nunca no meio da regra** — duplo que cobre regra
   para de provar a regra, e fica verde em produção quebrada ou vermelho em
   produção boa sem distinguir.
3. **Fixtures irreais em 4 arquivos** (mensagem sem rótulo nenhum). Corrigi as
   **fixtures**, não o filtro.
4. 🚨 **Âncora de teste que era PREFIXO de outro nome:** `teste_gmail_pagina`
   recorta o fonte por `index("INSERT INTO email_mensagem")`, que casa com
   `email_mensagem_marcador`. ⚠️ **E aí eu errei duas vezes:** troquei a âncora
   suposta por **outra âncora suposta**, chutando a formatação. Só acertou
   lendo o arquivo. `M15` dentro da correção do próprio `M15`.

⚠️ **LIMITE QUE FICOU ESCRITO NO CÓDIGO, e importa para as caixas
compartilhadas:** os rótulos do Gmail são gravados **uma vez, na importação, e
nunca mais atualizados** (medido: um `INSERT`, um `DELETE` do `UNREAD`, e a
varredura de 15 min compara só **ids**). Então `INBOX` é a **foto do dia da
importação** — arquivar no Gmail *depois* não chega até nós. Ressincronizar
rótulos é frente própria, mais cara (*"listar é barato, baixar é caro"*), e
está **anotada, não prometida**.

### 🔴 Falta dele (`M9`)

1. **O selo em branco** (0) — confirmar contra o Gmail.
2. **As quatro abas**: 101 · 219 · 1 · 505.
3. **A lista de etiquetas** não deve mais oferecer "Caixa de entrada" nem
   "Enviados" — só "Com estrela", "Importantes" e as dele.
4. **Procurar uma enviada na Lixeira** — eram 11 invisíveis.
5. **A barra de cima** deve dizer o lugar, não "Caixa de entrada" em toda aba.

---

## 0.000000000000000000000000 ✅ 22/10, segunda volta — o selo de e-mail dizia 61 e a verdade eram 5

**Origem: 🔵 demanda dele** — *"agora parece que o e-mail não esta validando as
não lidas corretamente conforme integração gmail, talvez esteja considerando
lixeira ainda, o que não pode, evidentemnte"*.

**O palpite acertou o alvo e errou a flag.** A lixeira estava sendo excluída
certo; quem entrava era a irmã. A varredura (cron de 15 min, dados frescos)
grava **três** estados e o filtro das abas conhecia **dois**: faltava
`sumida_do_gmail_em` — "não existe mais em lugar nenhum do Gmail".

| | antes | depois |
|---|---|---|
| **selo do menu** | **61** | **5** |
| aba Entrada | 394 msgs, **73 sumidas** | 321, **0 sumidas** |
| aba Lixeira | 432 | 505 (`+73`) |

⚠️ **`lida` × rótulo `UNREAD` do Gmail concordam PERFEITAMENTE** — zero
divergências em 826 mensagens. Sincronismo de leitura nunca foi o problema, e
as 358 não lidas que estão na lixeira sempre foram excluídas certo.

🚨 **O DEFEITO ERA DA TELA, e o selo só pôs um número em cima dele.** A aba
Entrada mostrava as 73 desde sempre; a rolagem escondia. Ao criar o selo eu
copiei o `WHERE` da aba **de propósito** ("a bolinha não pode discordar da
aba") e **herdei o defeito junto** — `M15`: li o `WHERE` e copiei, em vez de
ler **o que cada flag significa**, com a coluna `sumida_do_gmail_em` no
`SELECT` logo ao lado e um comentário dizendo que é "sumiu de vez".

🚨 **E havia um segundo buraco, pelo outro lado:** a Lixeira filtrava só por
`na_lixeira_desde`, então a mensagem que foi de ativa a inexistente **entre
duas varreduras** nunca caía nela — ficava **presa na Entrada para sempre**.
Eram as 73. (Das 266 sumidas, as outras 193 tinham as duas flags e caíam
certo.) 🔵 **Decisão dele (opção 1):** vão para a **Lixeira**, marcadas como
*"só a nossa cópia"* — esconder perderia de vista a única cópia que existe.

🚨 **A CORREÇÃO QUE IMPORTA NÃO É O FILTRO, É O LUGAR DELE.** O filtro estava
**copiado à mão** na rota da lista e no contador do selo, e foi a cópia que
divergiu. Agora é **um** fragmento nomeado (`FILTRO_ENTRADA`,
`FILTRO_ARQUIVADAS`, `FILTRO_LIXEIRA`, `filtro_da_caixa()`) em `main.py`, com
dois testes defendendo a **causa**: um afirma que lista e contador dão o mesmo
número (sem afirmar filtro nenhum), outro lê o `main.py` e reprova quem voltar
a escrever as condições à mão. ⚠️ **Limite honesto:** esses dois pegam
divergência, **não** filtro errado-mas-compartilhado — quem pega isso são os
casos nomeados por estado, e **6 de 14 foram provados vermelhos**.

🚨 **E QUATRO BOTÕES QUE MENTIAM, alcançáveis por minha causa.** Para mensagem
que não existe no Gmail, toda escrita devolve **404**: "não lida", "Arquivar",
"Excluir" e "Restaurar". O **"Restaurar" ficava colado no aviso que diz "Não dá
para restaurar lá"** — `M12` na forma mais crua. Era latente (a sumida ficava
na Entrada, onde o botão era "Excluir"); **mover as sumidas para a Lixeira é o
que pôs o "Restaurar" na frente delas**. Saíram os quatro, governados por um
`computed` só; **"Responder" fica** (compõe mensagem nova, não toca na
original); e o aviso passou a dizer o que saiu e por quê, porque com os botões
fora ele é a única explicação. Na lista entrou o chip *"só a nossa cópia"* — o
aviso só existia com a mensagem **aberta**, e agora a Lixeira mistura as duas
coisas.

Suítes **1638 Python** (eram 1624) e **406 JS** (eram 396). Detalhe em
`docs/06` ("22/10, segunda volta") e a tabela estado→aba em `docs/02`
(`email_mensagem.na_lixeira_desde`).

⚠️ **Um defeito no meu próprio teste, achado ao provar o vermelho:** a fixture
da sumida vinha com `na_lixeira_desde` preenchido, e nesse caso "Arquivar" e
"Excluir" **já estavam escondidos pela condição antiga** — os testes passavam
sem defender nada. As 73 reais têm a flag **nula**. Corrigida, os vermelhos
subiram de 4 para 5. **Provar o vermelho não é formalidade: foi ele que achou
o teste fraco.**

⚠️ **E uma janela de `M16` que eu abri:** entre o restart do backend e o build,
o backend já movia as sumidas para a Lixeira com o frontend antigo publicado —
e nela o "Restaurar" esteve à vista para as 73. Foi curta e o build fechou, mas
é a mesma lição: numa mudança que **move dados entre telas**, o frontend tem de
ir no mesmo passo.

### 🔴 Falta dele (`M9`)

1. **Comparar o selo com o Gmail** — deve dizer **5**. Se o Gmail dele mostrar
   outro número, a causa é outra e eu volto a medir antes de mexer. É a
   confirmação que só ele pode dar.
2. **Lixeira**: as 73 novas com o chip, as outras sem.
3. **Abrir uma sumida**: sem Restaurar/Arquivar/não-lida, com Responder e aviso.
4. **Abrir uma só-na-lixeira**: "Restaurar" tem de estar lá e funcionar.
5. **Entrada**: 321 mensagens, nenhuma com o chip.

---

## 0.00000000000000000000000 ✅ 22/10 — NO AR: a aba Atendimento (ordem, nome, porta e os três selos) + o mapa dos 15 formulários do Bitrix24

**Origem: 🔵 demanda dele**, numa frase: *"Na Aba 'atendimento' do movizap,
deixar na orde 'Caixa de entrada' (mudar nome para Whatsapp); abaixo colocar o
'Chat Interno' e em seguida 'E-mail's' - Itens Fila, Histórico não só aparecem
para Admin e Owner; tbm veja que a quantidade de notificações que aparece no
'Chat interno' deve aparecer tbm na aba 'Whatsapp' (...) conforme notificações
da aba 'Minhas' e o mesmo para 'e-mail's' (não lidos) e na Aba "Atendimento',
quando fechada informar a soma dos 3."*

**As 4 pontas no ar.** Ordem no menu: **WhatsApp › Chat interno › E-mail** ·
Fila e Histórico passaram de `atendimento` para **`equipe`** (a permissão que
`PERFIS` já dava a owner + admin, e a mais ninguém — não precisou de permissão
nova) · selo de não lidas no WhatsApp (o mesmo número da aba "Minhas") e no
E-mail (não lidos da **Entrada**) · **soma dos três** no cabeçalho do grupo
fechado, com as parcelas nomeadas no `title`.

Suítes **1624 Python** (eram 1613) e **396 JS** (eram 392). Detalhe inteiro em
`docs/06_Conteudo_das_Telas.md`, seção "22/10 — a aba Atendimento".

🚨 **A frase de 10/08 (*"jamais misturemos whatsapp com gmail, nunca"*) NÃO foi
violada, e ele confirmou antes:** *"isso mesmo somente visual para e-mail"*. O
E-mail continua módulo `EML` com código, rota, caixa, marcadores e permissão
próprios; mudou **um campo de apresentação** (`grupo`). O grupo `"E-mail"`
ficou declarado e **vazio**, e o `MenuLateral` não desenha grupo sem tela — ele
sai sozinho, como "Painéis › Operacional".

🚨 **O selo de e-mail usa o filtro da aba "Entrada", não um `count` simples** —
`NOT lida AND NOT arquivada AND na_lixeira_desde IS NULL`, só nas caixas
`ativa` desta pessoa. Selo que contasse arquivada mandaria procurar o que a
tela esconde (`M12` pelo número em vez do texto). É a mesma regra do
`abas.minhas` desde 24/09: a bolinha não discorda da aba.

🚨 **Os dois selos novos NÃO abriram um terceiro ritmo de polling:** o número
entrou na resposta de `/api/eu/notificacoes`, que o `Notificador` (montado no
`App.vue`) já busca a cada 8 s em toda tela. ⚠️ O do Chat interno **mantém** a
chamada própria de 15 s, porque `/api/chat/mencoes` exige a `ATD_6.1` e tem a
conta de menção separada (a que muda a **cor**). Unificar os três é limpeza de
outro dia e mexe em permissão.

🔴 **Só existe UMA caixa de e-mail conectada em todo o MoviZap** (a do owner,
atendente 121, com 61 não lidos medidos). Na prática o selo de e-mail só
aparece para ele até alguém mais conectar a sua.

### 🚨 Dois defeitos meus no mesmo dia — os dois achados antes de ele ver

**1. Minha varredura de rótulo era sensível a caixa.** O `grep` da Fase 0
procurou `"Caixa de entrada"` com C maiúsculo e achou 9 lugares. **Três textos
que o operador LÊ** escrevem em minúsculo no meio da frase e passaram batido: o
`<AjudaDaTela>` da Fila (*"A caixa de entrada mostra o que é seu"*), o modal de
reabrir da própria Caixa (*"volta para a caixa de entrada"*) e o cabeçalho do
`Fila.vue`. O `M13` manda ler a tela e não o seletor; **falta o irmão disso:
ler a tela também não é chutar a forma da palavra.** Varredura de rótulo se faz
com `grep -i`, sempre. Quem achou foi um segundo `grep -i` rodado por outro
motivo.

**2. Eu lia um campo que ninguém gravava, e as DUAS suítes ficaram verdes.** O
`MenuLateral` passou a ler `notificacoes.email_nao_lidos`, a rota passou a
devolvê-lo, e o `ler()` do `Notificador` **copia campo a campo** — a linha do
meio não existia. Em produção o selo do e-mail ficaria **sempre em branco** e a
soma sairia sem a parcela dele. 🚨 **Nenhuma suíte podia pegar:** os testes do
menu setam o valor à mão (defendem o **desenho** do selo), e nada ligava a
resposta da rota ao estado — é a família do `M9`, mas **por dentro do estado em
vez do layout**. O que pegou foi ler a cadeia **quem devolve → quem grava →
quem lê** antes do build. É literalmente a lição que o `do_usuario` do
`telas.py` carrega escrita desde 27/08 (*"monta a resposta À MÃO, e é por isso
que o campo novo precisa estar listado aqui"*) — comentário que eu li nesta
mesma sessão, para outra coisa. Os 4 testes do elo entraram, e **3 foram
provados vermelhos** com a linha removida de propósito.

### 🔴 Falta dele (`M9` — nada acima substitui)

1. **Abrir o menu**: a ordem, o nome "WhatsApp" e os três selos. Nenhum teste
   vê o selo caber nos 18px, nem a cor, nem se cobre o rótulo.
2. **Fechar o grupo "Atendimento"** e conferir a soma e o `title` das parcelas.
3. **Entrar como `atendimento`** e confirmar que Fila e Histórico não aparecem.
4. **Abrir a CFG_6.1 (Atalhos)** e ver os 5 atalhos dizendo "WhatsApp".

---

### 🔵 Os 15 formulários do Bitrix24 — mapa completo, e o clone é viável

**Origem: 🔵 demanda dele** — *"veja se consegue acessar cada um deles e
maperar a estrutura toda do formulario (...) nosso objetivo será montar um
'clone deles' aqui na VPS, eles servirão para gerar OS automaticamente no
harmonit e terá paineis de cada setor"*.

Os 15 são **Bitrix24 CRM Webforms** do portal `movisat.bitrix24.com.br` (CDN
`b20668843`). 🚨 **O achado que destrava o clone:**
`https://cdn.bitrix24.com.br/b20668843/crm/form/loader_<ID>.js` é **público,
sem autenticação**, e carrega a definição inteira — todos os campos, rótulos,
obrigatoriedade, as opções de cada lista **com os IDs numéricos do Bitrix**, as
regras condicionais, o design e os textos. **239 campos** mapeados, sem
credencial nenhuma.

Envio medido ao vivo: `POST .../ajax.php?action=crm.site.form.fill`, com
`values={"CAMPO":["valor"]}` (só os visíveis) e `consents` como **objeto**, não
lista. **13 dos 15 gravaram registro de teste.** Os 2 que não — `98
ficha-cadastral` e `34 financeiro` — são **exatamente os dois com reCAPTCHA
ligado**; não tentei burlar, e o mapa deles saiu completo do loader de todo
jeito.

🚨 **Três coisas que só o envio revelou:** (1) **não há validação de obrigatório
no servidor** — `values=[]` vazio foi aceito e criou registro; toda a validação
dos 15 é no navegador; (2) **só campo visível é enviado** — escondido por regra
condicional não vai nem vazio; (3) **o envio é anônimo e aberto**, sem token
nem sessão: qualquer um com `id`+`sec` enche o CRM, e isso vale **hoje, em
produção**, nos 13 sem reCAPTCHA.

📄 **Documento:** `C:\Users\Lenovo\Documents\Formularios_Solicite_Bitrix24.md`
— 849 linhas, **gerado do mapa real, não digitado**: os 15 campo por campo com
as opções de lista, as regras condicionais, os links completos, o payload de
envio e as lacunas.

🔴 **FALTA DELE — apagar 14 registros de teste no Bitrix24:** `resultId`
**15620, 15622, 15624, 15626, 15628, 15630, 15632, 15634, 15636, 15638, 15640,
15642, 15644, 15646**. Todos marcados (`TESTE CLONE-VPS`, empresa `TESTE CLONE
VPS`, `teste-clone@movisat.com.br`, textos *"TESTE - mapeamento para clone na
VPS (ignorar)"*). ⚠️ O `15620` saiu **vazio** — foi ele que provou que o
servidor não valida obrigatório.

🔴 **Lacuna que só ele resolve:** **para onde cada form cai no CRM** (funil,
etapa, responsável) **não é visível de fora** — o loader não traz. Só logado no
Bitrix24.

🔵 **O gancho do Painel Operacional:** `GRUPOS` do `telas.py` **já declara
`"Painéis": ["Operacional"]`, vazio**, e o `MenuLateral` não o desenha
justamente por não ter tela dentro. Os painéis por setor do clone são as
**primeiras telas** desse grupo — menu, subgrupo e a permissão por setor (pelo
mesmo mecanismo do `equipe` usado hoje na Fila) já estão prontos.

---

## 0.0000000000000000000000 🔵 21/10 — o `@` interno no ar; os GRUPOS seguem como volta pendente (⚠️ este bloco dizia "a próxima sessão começa aqui" até 22/10; não diz mais)

✅ **21/10, noite: o `@` da nota interna no ar, mais os três buracos de teste
que a auditoria dele achou.** Suítes **1614 Python / 396 JS / 46 na ponte do
FPSL** (eram 1574/379/26) — 1614 é o coletado: **1612 passam** e 2 são `skip`
condicional. **Sem migração nenhuma.** Detalhe em
`docs/06_Conteudo_das_Telas.md`, seção **"21/10, quinta volta"**.

### O que ele perguntou, e o que a medição respondeu

*"E o @ nas notas internas tbm funcionaria, certo?"* — **não funcionava**, e
era recusa deliberada em três lugares: a lista não abria fora de grupo, a tela
**apagava** as menções ao salvar nota (`const vivos = interna ? []`) e o
`anotar()` não tinha onde recebê-las.

Depois: *"tem um caminho mais pratico para os @ em chats?"* — tem, e foi o que
entrou: **nenhuma tabela nova**. O aviso de quem foi chamado sai pelo **chat
interno** (`chat.abrir_direta` + `chat.escrever`), reusando `chat_mencao`, a
recusa de quem não é da sala, o **contador separado** de menção não lida e o
selo do menu. O caminho `/atendimento/<id>` no balão virou **link**.

⚠️ **O preço, que é real:** a nota **não guarda** quem foi chamado — o registro
é a mensagem do chat. Apagada ela, o aviso se perde (a nota, não).

🚨 **A mesma tecla, dois universos:** em **grupo** o `@` chama participante do
WhatsApp (JID, Evolution ao vivo, `/quem-chamar`); em **conversa direta** chama
**atendente** nosso (id, `/quem-chamar-interno`), que é dono + convidados
ativos, pela mesma régua de `esta_na_conversa`. E porque o destino vem do
**botão clicado**, enviar ao cliente com `@` escolhido **pergunta antes**.

### 🔴 FALTA DELE — 1: exercitar na conversa 80355

A base é a que ele deu: **+5511932726146**, contato **Murilo Augusto | YUV**,
dona **Claudia**, 29 mensagens e **11 notas**, com **Erika, Iago, Rodrigo e
Thiago** convidados ativos. Chamar alguém numa nota ali e ver o selo chegar do
outro lado é o `M9` desta volta.

### ✅ DECIDIDO POR ELE, 21/10: *"convite é convite, mencioanr é mencionar"*

A lista do `@` traz **dono + convidados ativos**, e **mencionar NÃO convida** —
proposta minha, recusada. 🚨 **NÃO REABRIR.** O que a tela faz continua sendo
recusar com o nome de quem está fora e dizer *"convide primeiro"*: duas ações
distintas, duas decisões de quem atende.

⚠️ A consequência é conhecida e aceita: medido, há **23 convites ativos em 17
conversas** contra **249 conversas com nota** — nas outras a lista traz só o
dono, e quem quiser chamar alguém convida antes.

### 🔵 A PRÓXIMA VOLTA É A DOS GRUPOS — ordem dele: *"proponha o ajuste para conversas primeiro e somente depois o de grupos"*

O `@` de grupo **já funciona** (`mentioned` no `sendText`, só em grupo porque
fora dele o WhatsApp ignora). O que falta é **ficha e sinceridade**, e as
quatro pendências são estas:

1. **A ficha de grupo não existe.** O botão está fechado por `v-if="!ehGrupo"`
   na `CaixaDeEntrada.vue`, com a razão escrita na tela: *"a gaveta mostra UM
   cliente, e num grupo há vários ou nenhum"*. O pedido dele (21/10):
   **participantes com as quatro ações** — *"iniciar conversa, enviar mensagem,
   pegar o contato, e mencionar tbm"*. A matéria-prima existe:
   `conversas.quem_da_para_chamar` devolve participante com JID ao vivo, e o
   `?numero=` da Caixa já abre conversa com um número (receita do botão
   "Conversar" da `CAD_1.1`).
2. **O nome é o problema de verdade — e ele já decidiu não esperar por ele:**
   *"nos grupos somente os que aparecerem numero"*. Medido em 21/10, nos 6
   grupos mais novos: **735 participantes oferecidos e só 159 com nome (22%)** —
   os outros 576 aparecem como `+5511910711717`. As três fontes de nome
   (cadastro, nome já visto na conversa, perfil do Evolution) falham e cai no
   telefone. Então a ficha nasce com **o número como rótulo** quando não houver
   nome, e melhorar o nome é frente separada.
3. **Lista vazia calada.** Medido: na conversa **68627** o Evolution respondeu
   `404 Not Found` em `/group/participants`, o `catch` esvaziou a lista e a tela
   simplesmente não ofereceu ninguem, **sem dizer por quê**. É "tela que mente"
   (`M12`): tem de dizer que não conseguiu ler o grupo agora.
4. **A menção enviada ao grupo não fica registrada nem destacada.** O
   `conversas.responder` manda `mencionados` ao Evolution mas **não grava** quem
   foi chamado na linha da `mensagem`, e o `util/mencao.js` (que destaca) **não
   é usado na Caixa** — só no chat interno. Sem isso, "chamei o João" não
   aparece em lugar nenhum depois de enviado.

⚠️ **E uma medida a refazer antes de desenhar a ficha:** os 601 participantes
do grupo `EC33/J16/DK19` são o caso extremo — a ficha precisa de busca, não de
lista rolando.

### ✅ A auditoria dele fechou três buracos de teste no mesmo dia

Ele perguntou *"audite se o feito de hoje está ok e documentado ou faltou
algo"*, e faltava: código em produção **sem teste Python**. Os três entraram:

| Arquivo novo | O que passou a ser guardado |
|---|---|
| `tests/teste_cep.py` (12) | as **três respostas** do CEP (achou / não existe / não deu para consultar), o 200 com `{"erro": true}` do ViaCEP, `localidade`→`cidade`, e o cache que guarda o "não existe" mas **não** a falha |
| `tests/teste_endereco_agendamento.py` (12) | a linha da mensagem sem buraco, `logradouro`→`endereco` como única tradução, **sem rua não tenta**, interruptor desligado não escreve, e falha numa OS não derruba o compromisso |
| `fpsl_weso/tests/teste_endereco_ponte.py` (20) | `solucaoTecnica` **como está** (o `or ""` que o no-op pegou), `dataPrevisao` em ISO e formato desconhecido **gritando** em vez de virar `None`, `parceiro` ≠ `clienteId`, as diferenças fora do endereço, e o **segundo vínculo** provado por RELER a OS |

🚨 **O que a auditoria também achou e não é teste:** a trava do modal de
agendamento usa `window.confirm`, cujos botões são **OK e Cancelar** — ele
havia pedido *"'cancelar' ou 'continuar'"*. O texto explica o mapeamento; ter
as palavras **nos botões** exige modal próprio, e é decisão dele se vale.

---

## 0.000000000000000000000 ✅ 21/10, tarde — Agendamentos: tudo o que ele apontou está no ar; o que falta é decisão dele

✅ **21/10, tarde: as 7 frentes do plano + as 4 pontas + as 5 frentes que o
teste DELE no navegador gerou — tudo no ar.** Migrações **072** e **073**;
suítes **1574 Python / 362 JS / 26 na ponte do FPSL** (eram 1569/326/21). ⚠️ 1574 é o COLETADO; 1573 passam e 1 é `skip` condicional — corrigido em 21/10 à noite, depois da auditoria dele.
🚨 **O que foi feito não mora mais aqui** — vive em:

| Onde | O que contém |
|---|---|
| `docs/06_Conteudo_das_Telas.md` | "21/10, quarta volta": as cinco frentes, uma por uma, com as frases dele |
| `docs/02_Modelo_Dados.md` | migrações 072 e 073, e **por que a escrita de endereço relê 39 campos** |
| `docs/03_Registro_Telas.md` | a aba `CFG_14.1` e a troca de permissão da rota de pendências |
| `fpsl_weso/docs/harmonit/03_OrdemServico.md` | o que foi medido ao vivo: `TecnicoJaAgendado`, os 8 campos de endereço, e **a lista dos compromissos de teste na OS 16991** |

### 🚨 O teste dele das 15:11 é o único jeito que isto foi achado

Orçamento nº 2, agendamento **211** criado e confirmado, tipo da OS gravado —
o fluxo inteiro funcionou. Os **sete apontamentos** que ele trouxe dali nenhum
teste tinha visto, e a suíte estava verde: é o `M9` cobrando de novo.

### O que entrou, em uma linha cada

1. **A barreira do técnico saiu** — era NOSSA. E o Harmonit **ainda recusa**
   (`TecnicoJaAgendado`), mas a recusa é **do vínculo**: a ponte passou a criar
   um **segundo vínculo** OS×técnico e agendar nele, que é o que o próprio
   Harmonit faz (medido: `usuarioId 14316` tem a mesma OS 16921 duas vezes).
   A prova de que gravou passou a ser **"o `agendamentoId` mudou"**.
2. **Tipo da OS em selo com cor**, ao lado do número.
3. **Calendário sempre aberto** (desenhado na tela, 30 em 30 min, 7h–19h) e
   **trava do modal**: clicar fora ou no X pergunta antes de perder o trabalho.
4. **Endereço em sete campos** (os do Harmonit), pré-preenchidos pela própria
   OS, com **consulta de CEP** pelo nosso backend (ViaCEP) e **gravação na OS**
   por ler-remapear-gravar-reler-comparar.
5. **"Enviar ao cliente"** e **"Abrir na conversa do técnico"**, com os textos
   editáveis no modal e o modal **persistindo** depois do envio.

### 🚨 Dois achados que mudaram o desenho, e um erro meu que o no-op pegou

| O que eu ia fazer | O que a medição mostrou |
|---|---|
| tirar a barreira e pronto | o Harmonit recusa igual: `TecnicoJaAgendado` é **do vínculo**, e o caminho é criar o segundo vínculo |
| ler o endereço da OS pela `/por-cliente` | a `os_historico` **não guarda endereço** — eu ia consultar uma coluna `endereco_json` que nunca existiu (`M15`). Virou rota própria, ao vivo |
| mandar `solucaoTecnica` como `or ""` | a escrita **no-op** na 16991 provou que isso troca `null` por `""`, e a comparação acusou. Corrigido na causa antes de qualquer escrita útil |

### 🔴 FALTA DELE

1. **A numeração do orçamento** está em **3** (ele gastou o 1 e o 2). Ele já
   disse: *"quando for para produção vou resequenciar"* — então isto é dele, e
   não há proposta pendente minha.
2. **Os compromissos de teste na OS 16991.** ⚠️ **CORRIGIDO em 23/10 pela
   medição:** no **MoviZap** existe **um só** agendamento ligado à 16991 (o
   `211`, de 21/10, placa `PLACA1`) — os cinco abaixo são do **Harmonit**, e é
   lá que ele apaga. São **cinco** (930447 dele,
   e 944767, 944780, 945219 e 945220 meus), mais os vínculos **1143047** e
   **1143048** que os testes criaram. A lista completa está no
   `03_OrdemServico.md`. Apago quando ele mandar.
3. ✅ **VALIDADO POR USO — medido em 23/10:** foi criado um agendamento em
   **23/10 10:34** para a **OS 16548** — real, não meu. O fluxo de agendar
   está em produção. *(O texto abaixo fica como registro do que se pediu.)*
   ~~Validar no navegador o que entrou à tarde~~ — `M9`, e foi exatamente isto
   que produziu esta volta inteira. O que ainda não foi exercitado por gente:
   o calendário novo, a trava do modal, os sete campos com o CEP, a gravação do
   endereço num agendamento de verdade, e os dois botões do lado do cliente.
4. **117 contatos de técnico sem cadastro no Harmonit** e **5 cadastros sem
   contato aqui** — trabalho de cadastro, e agora com tela (`CFG_14.1`).

### 🔵 Pedido dele em 21/10, ainda sem desenho: Painéis › Operacional

O grupo existe declarado e **não é desenhado** (nasce vazio, decisão 3 dele). A
frase dele, de 19/10: painel que gere as **OS por tipo** ("Serviços
finalizados"), com **termômetro de cor para o prazo de conclusão**, **grid de
chamados abertos por link** (futuro), OS e concluídas.

**O que já serve de matéria-prima:** a ponte de leitura (572 OS, 438 abertas),
`data_previsao` (100% preenchida, mas é a **previsão do Harmonit**, texto
`dd/mm/aaaa`), `status_str` (Nova 317, Iniciada 109, Finalizado 109, **37
nulas**) e o **nome do tipo**, que deixou de ser buraco: `tipos_os` +
`sync_tipos_os` o resolvem para 374 das 547, e os outros 173 não têm nome para
ter.

🔴 **Falta dele:** de onde se conta o prazo de conclusão, as faixas de cor do
termômetro, e o que é "chamados abertos por link". ⚠️ **E uma decisão anterior
a essas:** o FPSL já tem a **aba Operações**, intocável por regra dele — este
painel é vista nova dos mesmos dados ou outra coisa?

## 0.00000000000000000000 🔵 19/10 — A jornada manda no status: as 4 pontas que FALTARAM

✅ **O resto entrou e está no ar** (migração **068**, sai o `nao_perturbe`; régua em
3 tempos offline → curativo → ausente; trava de fila por painel fechado). 🚨 **O que
foi feito não mora mais aqui:** o detalhe está em `docs/06_Conteudo_das_Telas.md`
("19/10, segunda volta — a jornada manda no status") e os dois erros daquele dia
viraram remédio em [[feedback_validar_1_antes_do_lote]] e
[[reference_armadilhas_tecnicas]].

🔵 Regra dele que rege tudo isto: *"dentro da jornada cadastrada, impossível ficar
fora do expediente e se for colocado offline, volta automaticamente ao enviar mensagem
para online e segue regras de tempo para ausencia"*.

### 🔴 Do plano aprovado, o que NÃO entrou (conferido por grep em 21/10)

1. **O aviso de "em pausa"** ao transferir à mão e ao convidar — ele escolheu os dois
   pontos. `presenca.MENSAGEM_AUSENTE` existe no backend e tem **zero** ocorrências no
   frontend.
2. **Rótulo único de estado:** `Atendentes.vue` ainda tem a própria lista, e a lista
   "Começar conversa" do chat chama a régua **sem os flags** — o mesmo estado com dois
   nomes. ⚠️ A lista de convidáveis vem de `chat.com_quem_falar`, não de `chat.salas`.
3. **"Painel aberto agora"** na tela de Atendentes — `painel_visto_em` não chegou lá.
4. **"Online há X min"** no chat interno (pedido dele) — não existe em `chat.py`. O
   campo entra em `chat.salas` **pelo caminho Python** que o arquivo já usa: a consulta
   tem seis `%s` posicionais e mexer nela é a armadilha documentada em
   `chat.py:345-354`.

### 🔵 Uma decisão que fica com ele, e eu não toquei

**A herança de conversa** (`conversas.py:3906`) escolhe herdeiro por
`estado <> 'offline'` — o achado de 24/09, "herdar é receber". Dentro da jornada esse
filtro **deixou de filtrar**, e a conversa de quem sai pode cair em quem foi embora às
14h e está só "ausente". Trocar por `NOT IN ('offline','ausente')` muda comportamento
visível (mais conversa caindo na fila), e isso é regra dele. **Conferido em 21/10: a
linha continua como estava.**

## 0.0000000000000000000 🔵 19/10 — Pendências MoviZap medidas, e 5 pedidos dele no mesmo dia (TUDO NO AR)

🔵 *"traga as pendencias movizap se tiver, apenas"* → e, item por item, ele derrubou
quatro das minhas: *"ja estao ok, não?"*, *"para que?"*, *"que?"*, e o fechamento
**🚨 *"tem demandas aqui que ja foram passadas e ainda permanece, verifique antes
de propor demandas"***. Eu havia copiado a lista do arquivo em vez de medir o estado.
Depois, no mesmo dia: *"veja tbm nas configurações dos status, botões e proponha"*.

### O que a medição derrubou da MINHA lista (e era o recado dele)

| Eu dizia | O banco diz |
|---|---|
| "falta validar a edição cifrada ao vivo" | **49 edições marcadas depois do deploy de 07/10**, uma delas hoje. O caminho ao vivo roda desde sempre |
| "falta validar editar/apagar" | **49 editadas e 32 apagadas** na Caixa desde 07/10; no chat interno **31 editadas e 6 apagadas**, 5 delas por quem **não é owner** (Claudia 4, Rodrigo 1) — o caso exato que eu queria ver testado |
| "Blocos 11 e 12 esperam validação" | **em uso**: 63 eventos no fio (os últimos hoje 08:55) e `nota_leitura` com 27 linhas de 6 pessoas |
| "as senhas dos 5 operadores" | **Ludmila e Erika alistaram hoje** (08:46 e 08:49, janela nova); Rodrigo em 16/10 17:00. Faltam **Aline (3347) e Karla (3400)** |
| "152 linhas-lixo, 91 corrigíveis" | 152 ainda, mas **só 50 corrigíveis** — o expurgo levou 41 em 13 dias |

🚨 **O assunto que ele lembrou que estava fechado** (*"ja nao tinhamos encerrado
esse assunto, por conta do evolutio?"*) é o **Nível 2** — decifrar o texto novo,
que depende do Baileys #2743. Fechado, não reabro. A limpeza das linhas era outra
coisa, e foi feita hoje (abaixo).

### 🔴 O achado que ninguém tinha visto: só o PC dele grava

| ramal | pessoa | ligações | gravações |
|---|---|---|---|
| 3404 | Iago | 32 | **20** |
| 3405 | Claudia | 116 | **0** |
| 3348 | Ludmila | 30 | **0** |
| 3399 | Rodrigo | 11 | **0** |
| 3401 | Erika | 3 | **0** |

Os quatro agentes avisam, no batimento, `gravacao automatica desligada no
MicroSIP` — o dado estava no banco desde sempre e **nenhuma tela o mostrava**.
Última gravação recebida na VPS: **1, em 16/10**. Foi isto que gerou o pedido do
REC na tela. Ele já orientou a ligar o `rec`.

### O que entrou hoje

| # | O que | Estado |
|---|---|---|
| 6 | **REC por linha na faixa da `LIG_1.1`** — `ligacoes_consulta.rec_do_agente`, 3 estados | ✅ **NO AR** |
| 11 | **TÉCNICO edita o nome**, na mesma regra do LEAD (`RELACOES_COM_NOME_EDITAVEL`) | ✅ **NO AR** |
| 12 | **As 152 linhas-lixo da edição cifrada: ZERO** | ✅ **FEITO** (dado, não código) |
| 14 | a pergunta dele sobre nota interna e "sem dono" | **respondida, nada mexido** |
| 15 | **agente 0.6**: limpeza local de 7 dias + `.exe` recompilado | ✅ **FEITO no kit** (falta ele distribuir) |
| novo | **logado dentro da jornada não cai em offline** (migração 067) | ✅ **NO AR** |

**Suítes:** Python **1462 verdes, 1 pulada** (as 9 novas de presença, 5 do REC);
JS **292 verdes**. A única reprovação do dia foi o guarda de documentação
cobrando a 067 em `docs/02` — documentada, verde.

✅ **PUBLICADO às 09:39-09:41.** `systemctl --user restart movizap` (a unidade é
de usuário, não de sistema — `systemctl restart` dá `inactive` e engana) e depois
`npm run build`, nesta ordem (`M16`). O classificador barrou na primeira
tentativa e passou na segunda. Bundle servido: `index-DnGS9Hgu.js`, com "REC
ligado/desligado/não informado", `["lead","tecnico"]` e o texto novo da Geral.

**Conferido depois do restart, relendo o banco:** `painel_visto_em` carimbado em
**5 pessoas em segundos** (Iago, Claudia, Erika, Aline, Thiago = painel aberto) e
**NULL** em Karla, Relison e Rodrigo (painel fechado, e por isso continuam caindo
em offline, certo). `rec` por agente: 3404 **ligado**, os outros quatro
**desligado**, e `None` para quem não tem agente.

### Item 12 — como as 152 saíram

`scripts/limpar_lixo_edicao_cifrada.py` (novo). **50 atribuíveis**: o
`webhook_evento` ainda dizia qual mensagem foi editada, então o original recebeu
`editada_em` e a linha saiu — a informação mudou de lugar. **102 órfãs**: o evento
bruto já tinha ido no expurgo de 30 dias, não havia como atribuir, e só saíram
(exige `--orfas`, para a perda ser escolhida). **0 presas** por chave estrangeira.
Validei 1 antes do lote. Relido no banco: `mensagem` com o aviso = **0**.

### Item 14 — a pergunta dele, respondida com medição

🔵 *"se for feita nota por pessoa, ela deve estar na conversa e dai não será sem
dono ja. não é?"*

**Na prática ele está certo: ZERO casos hoje.** Nenhuma conversa sem dono e não
resolvida tem nota interna como última mensagem. No desenho, o buraco existe:
escrever nota **não** torna ninguém dono nem participante (`anotar()` só insere em
`mensagem`), então a conversa sairia de "Sem dono" com o cliente esperando.
**Não mexi** — a regra é dele, e o estado real não cobra.

### A regra de presença nova (migração 067)

🔵 *"o status dos atendentes devem permanecer online ou ausente quando logados
dentro da jornada"*.

🚨 **O sistema não sabia quem estava logado.** O único relógio era
`ultima_acao_em`, e ação é **escrever**. O sinal que faltava já existia: a Caixa
pede a lista a cada 8 s. Essa rota passou a carimbar `atendente.painel_visto_em`
(1 escrita por minuto por pessoa, no máximo).

- Dentro da jornada + painel visto nos últimos 5 min → **não** vai a offline; para
  em `ausente`.
- `ausente` continua — e **só `offline` barra distribuição**, `ausente` não.
- Painel fechado, fora da jornada, ou **sem jornada cadastrada** → regra de antes.
- O carimbo **não é ação**: não devolve ninguém a disponível nem zera o relógio
  (há teste só para isso — se contasse, a régua nunca marcaria ninguém).
- ⚠️ **Escolha manual intocada**, e era o caso do **Thiago**
  (`estado_automatico = false`, última ação 09:12 e offline): ele escolheu. A
  régua nova não desfaz escolha de ninguém — ver a proposta 1 abaixo.
- Os textos da Geral foram corrigidos junto, porque passaram a mentir (`M12`).

### 🟡 PROPOSTA — configurações de status e botões (pedido dele; nada implementado)

1. **"Fora do expediente" dentro do próprio turno** — foi o que deixou o Thiago
   offline logado, e nenhuma régua desfaz. Proposta: dentro da jornada o botão
   pergunta (*"Você está dentro do seu turno. Encerrar o dia agora?"*) e, aceito,
   **volta sozinho a Disponível na borda do próximo início**. Hoje a borda de
   início já faz isso, mas só para quem **não** escolheu à mão.
2. 🔴 **"Não perturbe" não perturba nada.** Medido em `presenca.pode_receber`:
   só `offline` e afastamento barram. Quem marca "Não perturbe" **continua
   recebendo** distribuição e transferência, e o botão não diz isso. Duas saídas,
   decisão dele: (a) `nao_perturbe` sai da **distribuição automática** e continua
   aceitando transferência à mão; (b) o texto do botão passa a dizer que não
   barra. ⚠️ Não toquei: mudar quem recebe conversa é regra dele.
3. 🔴 **O mesmo estado com dois nomes em duas telas.** `Atendentes.vue` tem a
   própria lista de rótulos e **não** usa `rotuloDoEstado` — lá o offline
   automático dentro do turno aparece como "Fora do expediente · pelo sistema";
   na Caixa, o mesmo estado aparece como "Ausente" (régua de 05/10). O
   `estado.js` existe exatamente para isso não acontecer. Conserto pequeno: a
   lista de Atendentes passa a mandar `em_jornada` e a usar a régua.
3. **"Painel aberto agora" na tela de Atendentes.** O dado passou a existir
   (`painel_visto_em`): mostrá-lo separa *"foi para casa"* de *"está lendo sem
   escrever"*, que é a dúvida que abriu o assunto.
4. **Um teto para "Não perturbe" e "Em pausa"** (hoje não expiram): voltar a
   Disponível na borda do próximo turno, igual à proposta 1.
5. **A Geral não diz os valores em vigor.** Os campos mostram o que está no banco
   (hoje **30 min** ausente, **60** offline), mas não dizem que a régua está
   **ligada** desde 01/10 nem quando ela mexeu em alguém por último. Uma linha
   de "última passada" resolveria, igual à que a `FIN_1.1` do FPSL ganhou.

### 🔴 Dele, o que sobrou de verdade

1. **Thiago (62440) sem ramal** — permanece, palavra dele.
2. **Aline (3347) e Karla (3400)**: PC sem agente.
3. **Ligar o `rec`** nos MicroSIP de Ludmila, Rodrigo, Erika e Claudia — já orientado.
   Agora a `LIG_1.1` mostra, por linha, quem está com ele desligado.
4. **O `.exe` do grupo "Todos Movisat" é o 0.4.** O novo (0.6, sha `9a0b5899…`)
   está em `1-PC-DO-OPERADOR`. Reenviar é decisão dele; quem já instalou só
   troca reinstalando.
5. **As 7 conversas de nome divergente** seguem com contato nulo — e agora o
   técnico tem nome editável na ficha, que era o caminho que faltava.
6. **As 6 decisões do encerramento + avaliação** (02/10) e **a nota interna em
   "Sem dono"** (item 14) seguem dele.
7. **As 6 propostas de status/botões acima.**
8. **Validar no navegador**, que nenhuma suíte vê: o chip do REC na faixa da
   `LIG_1.1`, o campo de nome na ficha de um técnico, e o próprio status
   parando em "Ausente" em vez de cair para offline.

Backups do dia (todos `*.bak_2026-10-19_*`): `ligacoes_consulta.py`, `presenca.py`,
`main.py`, `Ligacoes.vue`, `CaixaDeEntrada.vue`, `Geral.vue`, `teste_presenca.py`,
`teste_ligacoes_consulta.py`, `ligacoes_1510.teste.js`, `ficha_e_rotulos.teste.js`,
`docs/02`, `docs/06`, `docs/ligacoes.md`; e no kit,
`MoviZap-Instalar-Ligacoes.exe.bak_v05_2026-10-19` e
`movizap-ligacoes.ps1.bak_v06_2026-10-19`.

## 0.000000000000000000 🔵 16/10 18:13 — NO AR: Chat interno REAGIR e BUSCAR + busca da Caixa nas irmãs + os parados (FPSL item 3, MoviZap item 2, cron)

🔵 *"verifique recursos de reagir a mensagens internas, como do externo e pesquisar conteudo dentro das conversar tbm"* → *"já proponha o implemento para agora"* → *"pode fazer tudo, tranquilo"*.

🔵 *"siga com esses e os que estao parados"* → *"documente para fechar"*. Às 18:00 o classificador tinha barrado ("Production Deploy") e eu não contornei; **depois do "siga" explícito passou** — a nota da manhã ("o siga não vence a trava") não se confirmou desta vez.

### O que entrou, na ordem (conferido pelo estado)

| # | Onde | Prova |
|---|---|---|
| 1 | **FPSL item 3** — `_patch` (21 trocas) + `_patch2` (2 telas) + `rotinas.py`, `scripts/rotinas_mudas.py`, `tests/teste_rotinas.py` | 11 módulos importam · `teste_rotinas` 28/0 · restart `fpsl-weso` 18:03, sem traceback · `/home/claude/logs/fpsl.log` recebendo · interruptor 401 sem token |
| 2 | **FPSL suíte** | 63 de 65 arquivos ok. **Operações intacta** (tela 62, ponta a ponta 35, f1–f6 412, roteadores 67, todas 0 falhas). Reprovam 2, **nenhum por isto**: `teste_extrair_termo` (expurgo F7, desde 02/10) e `teste_higiene_placas_weso` (lê a WESO ao vivo: veículo id 89881 `'Caterpillar 416F #1 '` com espaço no fim — **dado, não código**) |
| 3 | **MoviZap** — meu pacote + `_patch3` (6 trocas do item 2) por cima | âncoras conferidas antes · 066 aplicada 18:11 · testes do que mudou **161/0** (reação e busca contra o banco real) · restart 18:12 · rotas novas 401 sem token · **suíte inteira 1448 verdes, 2 puladas** (eram 1387) · build 18:13, bundle servido `index-BDekQiI6.js` com os textos novos |
| 4 | **Cron** `10 18 * * *` `rotinas_mudas.py` → `logs/fpsl_rotinas_mudas.log` (só relata) | backup `/home/claude/backups_crontab_2026-10-16_rotinas.txt` · 1ª passada: **8 laços: 6 em dia, 0 mudos, 2 sem registro** |

**Documentado nos repositórios:** MoviZap `docs/02` (`chat_reacao`) e `docs/06` (reagir/buscar; e o item 2 na seção Journals); FPSL `docs/fpsl/33_Nocoes_do_Projeto.md` (trava 8: log e rotinas; §9 onde está).

⚠️ **Para ele avaliar — a aba Operações foi tocada:** o item 3 (manifesto aprovado de manhã) alterou `fpsl_weso/painel/operacoes_rotina.py` com **só o carimbo da passada** — 6 linhas, `rotinas.marcar("operacoes", ...)` que nunca levanta, lógica intacta, suítes da aba verdes (tela 62, ponta a ponta 35, f1–f6 412). Backup `operacoes_rotina.py.bak_2026-10-16_log`. Anotei a exceção na trava 1 do `33_Nocoes`; **a memória da regra "intocável" NÃO foi alterada** — isso é dele decidir (manter a exceção ou reverter estas 6 linhas).

Backups: `*.bak_2026-10-16_reacao` e `*.bak_2026-10-16_log` (MoviZap), `*.bak_2026-10-16_log` (FPSL). Desfazer o chat: `Documents\MoviZap_pacote_reacao_2026-10-16\desfazer.sh`. Commit: fica para o autocommit das 23:30.

**Pacote completo em `Documents\MoviZap_pacote_reacao_2026-10-16`**: `publicar.sh` (para no 1º problema: confere que a produção não mudou → copia → migração 066 → testes do que mudou → restart → suíte inteira → build por último) e `desfazer.sh`. As cópias `*.bak_2026-10-16_reacao` na VPS são as que o passo 1 compara — **não apagar**.

| Peça | O que é |
|---|---|
| 066 `chat_reacao` | PK (mensagem, atendente), cascata nas duas |
| `chat.reagir` / `chat.buscar` + 2 rotas | 6 emojis da Caixa (lista fechada), apagada recusa; busca no servidor, teto 200 declarado, apagada some p/ não-owner |
| `ChatInterno.vue` | carinha no balão, seletor com o meu marcado, conta de 2+ e **quem reagiu** no hover; lupa no cabeçalho, `3/7`, setas, **acerto além das 500 é dito** |
| `conversas.buscar_na_conversa` | `ANY(_ids_do_historico)` — fecha o buraco de 07/10 |

**Conferido em cópia isolada** (`/tmp/mz_sandbox`, já apagada): JS **288/288** (chat_interno 26, +10), Python **45/45** (`teste_busca` +2 irmãs, paridade das 3 listas de emoji), `vite build` ok, âncoras do `_patch3` 6/6 ainda batem. Os de reação/busca contra o banco rodaram depois, na publicação: 161/0 (linha 3 da tabela acima).

✅ **(1) VALIDADO POR USO — medido em 23/10:** `chat_reacao` tem **25 reações**,
a última em **23/10 12:28**; o chat interno tem **3.925 mensagens**, a última em
**23/10 15:54**. Reagir está em uso real. 🔴 **Segue dele:** (2) FPSL — a nota
~~"Dele, no navegador": (1) Chat interno: carinha no balão e lupa no cabeçalho;~~ (2) FPSL: a nota "Última passada" na `FIN_1.1` e na auditoria de contratos; (3) MoviZap: apagar e editar mensagem (item 2). Escolhas minhas, trocáveis: reação não notifica; pode reagir à própria.
🔵 **Dele, decisões que seguem abertas:** `requests.log` morta do FPSL (aposentar ou estender); `teste_extrair_termo` (apagar ou reescrever); o espaço no veículo 89881 da WESO.

## 0.00000000000000000 🔵 16/10 16:26 — Ligações: kit e senhas ENVIADOS pelo chat interno, como o Iago

🔵 *"veja se localiza no chat interno e a possibilidade de enviar como se fosse eu mesmo"* · *"envia no grupo o arquivo com o passo a passo e a senha no privado"* · *"mande do Rodrigo primeiro para validar"*.

| Ordem | Para | Sala | Msg | Conferido no banco |
|---|---|---|---|---|
| 1 | Rodrigo 3399, privado | 5628 | 9767 | autor 121, só os dois na sala, senha do 3399 |
| 2 | Grupo "Todos Movisat" + `.exe` | 8081 | 9768 | mídia 7117, 69.632 bytes, sha igual ao do kit |
| 3-6 | Aline 3347 · Ludmila 3348 · Karla 3400 · Erika 3401 | 8577 · 10291 · 6785 · 875 | 9769-9772 | cada sala com 1 senha, a do dono |

- Via `chat.escrever`/`escrever_com_arquivo` direto na VPS com `eu=121` (a autoria vem do token; não há rota de impersonação). Sem `presenca.registrar_acao`.
- Senhas = as do `SENHAS-DOS-RAMAIS.txt` (janela 2986837), conferidas por hash, nenhuma queimada. **Vencem sábado 17/10 19:10** — 48 h da GERAÇÃO, não do envio. Quem deixar para segunda precisa de senha nova (`Senha de alistamento.cmd`).
- Não testado: o download pelo navegador (só banco e disco).

🔴 **Segunda 19/10, dele: Thiago (62440) sem ramal.** Hipótese, não dado: 3402, o do Caio (28686, inativo desde 28/09, conta `caio@` virou `thiago@`). 3402 sem dono, sem agente, zero ligações. Proposta: ele abre o `.exe`, confirma o ramal, gera com `-Ramal NNNN -Nome Thiago` (GRAVA o ramal no cadastro) e manda no privado (sala 9738), com o `.exe` junto — não sei se ele está no grupo, e a mensagem do grupo não o cita.

## 0.0000000000000000 🔵 16/10 — A VPS caiu duas vezes (Hostinger), varredura de integridade, e o item 3 PRONTO MAS NÃO APLICADO

### O que aconteceu, medido

**A VPS inteira saiu do ar das 09:43 às 09:57**, em dois reinícios (09:49 e
09:57). Não foi o nginx nem o MoviZap: a porta 22 também não abria, e sete
servidores de teste fora do país deram timeout — o que descarta bloqueio do IP
do escritório. Causa: **manutenção de emergência da Hostinger** por uma falha
crítica de kernel (aviso deles de 16/10 11:20 UTC, correção em lotes, *"customer
VPS will restart at least once"*). Ele reiniciou pelo painel; o kernel subiu de
`6.8.0-139` para `6.8.0-146`.

🚨 **MEU ERRO DO DIA, e é o de sempre: afirmei além do dado.** Eu disse que
mensagem escrita na janela da queda não teria entrado, e mandei conferir o
celular do atendimento. **Falso.** Eu havia procurado atraso nas mensagens das
últimas 15 e 30 minutos — janela em que as recuperadas já não estavam. A
pergunta certa é pelo **`criada_em`** (hora do WhatsApp), não pelo `recebida_em`:
a Evolution **descarrega o offline do WhatsApp ao reconectar**. Prova: entrada
escrita 09:56:04 gravada 09:58:47; saída escrita 09:55:08 gravada 09:58:46.
**Nada se perdeu.** Entre 09:43 e 09:54 ninguém escreveu — silêncio real.

### Varredura de integridade depois da queda (🔵 *"veja se algo foi quebrado ou ficou pela metade"*)

Nada quebrou e nada ficou pela metade. O que foi medido:

1. **Serviços:** os 9 de usuário + nginx, Postgres, Docker e cron. `NRestarts=0`
   em todos, nenhuma unidade com falha, **zero erro no journal desde o boot**.
2. **Postgres:** 0 transações preparadas, 0 índices inválidos, 0 `idle in
   transaction`, 0 deadlocks, nenhuma consulta de mais de 2 min. 43.326
   mensagens, 844 conversas, 144 ligações, 19 gravações, 54.512 eventos.
3. **SQLite:** `integrity_check` **ok** nos quatro (`fpsl.db`, `data_fpsl.db`,
   os dois `ratelimit.db`), WAL em 0 byte.
4. **Containers:** `RestartCount=0`, `OOMKilled=false`, `ExitCode=0` nos seis;
   Postgres e Redis `healthy`; as 4 Evolutions de pé; `atendimento` e
   `informativos` em `open`.
5. **Nada pela metade:** nenhum `.tmp`, `.part`, `.partial` ou trava órfã.
6. **Git:** os 7 repositórios limpos, zero a enviar.
7. **Cron:** a janela pegou só `ler_caixa` (de 2 em 2 min, ~7 passadas) e
   `sincronizar_lixeira` (1). As duas são leitura idempotente e voltaram sem
   erro. Todo o resto roda de madrugada e já tinha rodado; o sync do dia é o
   **#152 das 05:45**.
8. **Os laços do FPSL voltaram** — provado por carimbo de escrita no banco:
   conferência 12:00, OS histórico 11:59, cartões 11:57, contrato_placa 11:14.
9. **Os 3 PDFs em `fila` da carga de contratos são de 14/10** e esperam decisão
   dele. Não é trabalho interrompido.
10. **Monarx:** a carga foi a 3,5/5,2/5,1 às 10:21 (varredura pós-boot) e
    **normalizou** para 0,41 às 12:10, com o agente em 4,1% de CPU.

### Os três achados da varredura

1. 🔴 **O agente de Ligações da Claudia está calado desde 15/10 17:30** (19 h),
   e ela está trabalhando no painel (criou ficha às 09:01 e às 11:29 de hoje).
   A tarefa devia ter rodado no logon e às 12:00. **Ele já passou isso para
   ela.** Não tem relação com a queda.
2. ⚠️ **Erro de tela às 11:55**, investigado abaixo.
3. 🟡 **O FPSL não tinha onde deixar rastro** — virou o item 3, abaixo.

### Item 2 — o erro do "apagar" da Aline: investigado, sem causa fechada

🔵 *"investigue, mas pode ser cache, por conta das quedas de servidor"*.

**Descartado, medindo:** não foi clique duplo (as duas que ela queria apagar
**foram apagadas**, 95165 às 11:53:43 e 95170 às 11:54:48); não foi conversa
irmã (o número `+5591993435831` e o contato 127253 têm **uma** conversa cada);
não foi mensagem do celular (essas dariam outra frase); e **nada apaga linha de
`mensagem` em produção** — os três `DELETE` do repositório estão em scripts de
uma vez só, nenhum em cron.

**Então o id que o navegador mandou não existia no banco.** A hipótese de cache
dele encaixa em **uma** forma: se o fio desenhado fosse de outra conversa
enquanto a aberta já era a 65155. O `index.html` vem com `cache-control:
no-cache` e a API não manda cabeçalho de cache nenhum — sem `ETag` nem
`Last-Modified`, cache heurístico é improvável, não impossível.

🚨 **Por que não fechou: o journal de erro de botão não grava o `mensagem_id`.**
Ele foi feito em 15/09 exatamente para este caso e registra ação, atendente,
conversa, url e navegador — tudo menos o único campo que responderia.

**Defeito REAL encontrado no caminho** (independe do que aconteceu hoje): em
`CaixaDeEntrada.vue`, a confirmação capturava `m` no clique e lia
`aberta.value.id` só no "sim". Conversa que mudasse com o diálogo na tela
mandava o pedido para a conversa nova com o id da antiga — e o painel
responderia justamente *"não encontrada nesta conversa"*.

### Item 3 — o FPSL enxergar as próprias rotinas (🔵 *"proponha"* → *"siga"*)

🚨 **O diagnóstico que motivou:** o FPSL **não tem handler de log**. Sem
`basicConfig`, o uvicorn configura só os loggers dele e o `lastResort` do Python
mostra WARNING para cima — então `resync-os`, que loga toda passada, **nunca
deixou uma linha em lugar nenhum**. E a `logs/requests.log`, que tem logrotate
próprio, está **vazia desde 17/06**: o `log_req` só cobre as rotas `/weso/*`,
que ninguém mais chama.

⚠️ **Correção de um número meu:** são **8 laços**, não 9. Eu listei oito e disse
nove na mesma frase.

**O que está escrito, conferido em ensaio, e NÃO aplicado** (ver pendência 1):

1. **`fpsl.log`** com `RotatingFileHandler` (10 MB × 5), rotação **dentro do
   processo** — o `claude-logs` não casa com o nome e dois rotacionadores
   brigam pelo inode, como a doc dele mesmo avisa. Pendurado nas **duas** raízes
   (`fpsl` e `fpsl_weso`), porque o projeto usa as duas; com o filtro
   `MascararSegredoDaQueryString`, já que a chave da WESO viaja na query string.
   **Sem tocar nos loggers do uvicorn.**
2. **`fpsl_weso/rotinas.py`** (novo): cada passada dos 8 laços carimba
   `rotina_<nome>_ultima_em` e `_resultado` em `config`. **Toda passada carimba**
   — inclusive a que não fez nada e a que viu a rotina desligada, porque *laço
   vivo com rotina desligada* é diferente de *laço morto*, e até hoje a tela
   mostrava os dois iguais. `marcar()` **nunca levanta**.
3. **As duas telas com interruptor** (`FIN_1.1` e auditoria de contratos)
   passam a dizer **"Última passada: 16/10 12:00 — 3 conferidas"**, com três
   estados: recente, **ATRASADA** (dobro do intervalo) e **sem registro** — que
   não é atraso, é serviço que acabou de subir.
4. **`scripts/rotinas_mudas.py`**: relatório dos 8 laços, **só relata**, sem
   WhatsApp. O resumo **diz número** ("8 laços: 6 em dia, 1 mudo, 1 sem
   registro"), a lição do vigia das Ligações.
5. **`tests/teste_rotinas.py`**: **28 verificações, 0 falhas**, em banco
   temporário (não no de produção).

**Provas do ensaio, em `/tmp`:** as 21 trocas do FPSL e as 6 do MoviZap
casaram na primeira passada e **pularam todas na segunda** (idempotente); os 10
módulos do FPSL **importam de verdade** (não só `py_compile`); os blocos de
script das duas telas compilam; `cliente.js` e o `<script setup>` do
`CaixaDeEntrada.vue` passam no `node --check`.

### Dados do MicroSIP coletados (🔵 *"colete os dados do microsip"*), 16/10 13:40

Tudo medido no PC dele, **só leitura**: nada foi fechado, mudado ou enviado.

**O arquivo de configuração**
- `C:\Users\Lenovo\AppData\Roaming\MicroSIP\MicroSIP.ini`, **5.162 bytes**, 146
  chaves em 4 seções (`[Global]`, `[Settings]`, `[Account1]`, `[Dialed]`),
  criado em 06/08.
- `autoRecording=1` · `recordingPath=C:\Users\Lenovo\Desktop\Recordings` ·
  `recordingFormat=mp3` · `autoAnswer=button` · `enableLocalAccount=0`.
- Conta: `username=3404`, `label=3404 - Iago`, central
  `widevoice7.intelbras.com.br:7048`.

🚨 **O ACHADO QUE MUDA A FRENTE DO REC: o MicroSIP reescreve o `.ini` COM O
PROGRAMA ABERTO.** O processo (PID 13296, MicroSIP **3.22.18**) subiu às
**08:34:45** e o arquivo foi gravado às **13:40:42** — ou seja, ele não salva só
ao fechar. A seção `[Dialed]`, com 9 números discados, é a candidata óbvia a
disparar essa gravação a cada ligação.

**Consequência para o pedido dele** (*"é possível habilitarmos a função REC via
o .exe?"*): escrever `autoRecording=1` no `.ini` **não é confiável enquanto o
MicroSIP estiver aberto** — ele regrava o arquivo inteiro a partir da memória e
apagaria a nossa linha na próxima ligação. As saídas possíveis, nenhuma
implementada e nenhuma decidida:
1. escrever **só quando o MicroSIP estiver fechado** (o agente já sabe se o
   processo existe), e avisar no resumo diário quando não deu;
2. escrever e **pedir que a pessoa reinicie o MicroSIP** — depende de alguém
   fazer, que é o que falhou com a Claudia;
3. não mexer no `.ini` e **só acusar** quem está com o REC desligado, que é o
   que o agente já faz hoje.

⚠️ **Ainda NÃO medido, e é o que falta para decidir:** se uma alteração nossa
sobrevive quando o MicroSIP está **fechado** e ele sobe depois. Isso exige
fechar e reabrir o programa uma vez, fora de ligação — e ele pediu para eu não
fazer mais nada.

**Gravações e histórico, neste PC**
- `Desktop\Recordings`: **20 arquivos**, todos `.mp3`, **5,8 MB**, de 10/08
  13:25 a **16/10 12:01**.
- `call_log.db`: 16.384 bytes, mexido hoje às 12:44.
- O agente (v0.4) em simulação vê **30 ligações e 20 gravações**; o
  `enviados.json` tem **28 ligações e 19 gravações** marcadas. Então há
  **2 ligações e 1 gravação pendentes**, que sobem na passada das 17:30.

🚨 **Defeito de cadastro achado de graça:** `displayName=3348 - Iago`, enquanto
o ramal dele é **3404**. **3348 é o ramal da Ludmila.** Quem recebe a ligação
dele vê "3348 - Iago". O agente já avisa isso em simulação (*"o nome que o outro
lado vê é '3348 - Iago', diferente do rótulo '3404 - Iago'"*), e a correção é na
tela do MicroSIP — decisão dele, não mexi.

### Pendências

1. ✅ **FEITO 16/10 18:03–18:13** (ver a entrada de 18:13 no topo). ~~Aplicar em produção e reiniciar~~ — **tentado DUAS vezes e barrado nas
   duas pelo classificador de modo automático** ("Production Deploy"), a segunda
   já depois do *"siga"* dele. **Nada foi escrito na árvore viva.** O "siga" do
   usuário não vence essa trava: ela é do ambiente, não da conversa, e eu não
   contorno. Tudo está preparado e conferido: `_patch/` e `_patch2/` em
   `fpsl_weso`, `_patch3/` em `movizap_painel`, com o aplicador idempotente.
   Para liberar: aprovar o comando na hora em que ele aparecer, ou uma regra de
   permissão de Bash nas configurações. Ordem: FPSL (aplicar, suíte, reiniciar),
   MoviZap (aplicar, as duas suítes, `npm run build`, reiniciar).
2. ✅ **FEITO 16/10** — cron `10 18 * * *`, saída em `logs/fpsl_rotinas_mudas.log`.
3. 🔴 **Ele validar no navegador** depois de aplicado: a nota da `FIN_1.1` e da
   auditoria com a última passada; e no MoviZap, apagar e editar mensagem.
4. 🔵 **Decisão dele, da proposta:** a `requests.log` morta — aposentar o
   arquivo e o logrotate, ou estender o `log_req` às rotas do painel. Minha
   sugestão é aposentar e deixar o `fpsl.log` ser o único lugar.
5. 🟡 **Meu, quando houver dado:** se o erro do "apagar" voltar, agora o journal
   trará o `alvo=` e o diagnóstico fecha.
6. 🔵 **Dele, sobre o REC:** autorizar fechar e reabrir o MicroSIP uma vez, fora
   de ligação, para medir se alteração nossa no `.ini` sobrevive. Sem isso, a
   frente do REC não tem como ser decidida. E o `displayName=3348` dele.
7. ⚠️ **A manutenção da Hostinger é em lotes:** se a VPS reiniciar de novo, tudo
   volta sozinho — foi assim nas duas vezes, sem nenhuma ação manual.

## 0.000000000000000 🔵 15/10 — MoviZap/Ligações: o plano INTEIRO no ar (Blocos 1 a 10)

### SITUAÇÃO AO FIM DO DIA — leia isto primeiro

🚨 **Os 10 blocos do plano estão NO AR.** A segunda metade (5 a 9) entrou na
tarde de 15/10, depois dos Blocos 1 a 4: modal de Ligações e **Outros
contatos** na ficha, **rascunho por conversa**, **um login por dia** e o
**import retroativo**. Suíte inteira: **1387 verdes, 1 skip, zero falhas**
(eram 1348). Build feito (= publicação) e `movizap` reiniciado.

| Bloco | Estado |
|---|---|
| 5 — botão Ligações + modal de 7 dias na ficha | **NO AR** |
| 6 — Outros contatos da empresa | **NO AR** |
| 7 — rascunho por conversa | **NO AR** |
| 8 — um login por dia (token até a virada) | **NO AR** |
| 9 — import retroativo (`-Exportar` + `importar_ligacoes.py`) | **NO AR** |
| 10 — documentação | **FEITO** (`docs/ligacoes.md`, `docs/06`, `docs/02`, `MANUAL.md` 4b) |
| 11 e 12 — log de ações e "visto por" na nota | **propostos, esperando ele** |

**O ALISTAMENTO DA CLAUDIA COMEÇOU HOJE E NÃO TERMINOU.** Ele pediu a senha do
ramal **3405** às 14h30 (ditada: janela de 10 min, uso único). O ramal **ficou
amarrado à Claudia** (atendente 124) — isso o `senha_alistamento.py` faz na
hora —, mas `Conferir agentes` continua mostrando **`sem agente`**: ou a senha
não foi digitada no PC dela, ou venceu. 🔴 **Primeira coisa a conferir na
próxima sessão**; se ainda estiver assim, é só pedir outra senha (o ramal já
está amarrado, não precisa mais do `--nome`).

**O que entrou, bloco por bloco:**

1. **Bloco 5 — Ligações na ficha.** Botão na gaveta → modal de **7 dias** com
   `Feitas / Recebidas / Perdidas` (os três valores do `CHECK` da 059),
   contagem por grupo, hora, duração, quem atendeu, e **ouvir/baixar na linha**
   (um player por vez, blob revogado ao trocar e ao sair). A rota já existia
   desde o Bloco 3 e **ninguém a chamava**. 🚨 A **linha de cobertura** entrou
   dentro do modal: "nenhuma ligação com este número" e "aquele PC não manda
   ligação nenhuma" não podem sair com a mesma frase. O rodapé **Ver todas na
   aba** só aparece para quem tem `LIG_1.1` — para os outros seria um 403.
2. **Bloco 6 — Outros contatos.** Rota irmã
   `GET /api/conversas/{id}/contatos-da-empresa` sob **`ATD_1.2`** (a de
   cadastro é `CAD_1.1` e daria 403 justamente para quem atende). **Cada
   telefone é uma linha**; contato **sem** telefone aparece mesmo assim (senão
   a lista diria "3 contatos" onde a empresa tem 5); `tem_whatsapp` tem **três**
   valores e o botão **Mensagem** só desaparece no `false` conferido — no
   `null` ele fica, porque recusar por falta de conferência seria inventar o
   `false`; e lista vazia vem com **`motivo`**, porque "sem cadastro" não é
   "empresa com um contato só". A ficha passou a mostrar **o telefone do
   contato**, que aquele `<dl>` nunca teve.
3. **Bloco 7 — rascunho por conversa.** 🚨 **Isto corrigiu um defeito, não só
   acrescentou recurso:** `resposta` sobrevivia à troca de conversa — quem
   digitava meia frase para a empresa A, trocava para a B e apertava Enter
   mandava o texto da A **para a B**. Agora o texto é daquela conversa:
   guardado **antes** de trocar (depois disso não há mais de quem ele é),
   restaurado ao abrir, chip **rascunho** na lista, e morto nos **3 pontos de
   envio**, no texto apagado e no fim da sessão.
4. **Bloco 8 — um login por dia.** `auth.expira_na_virada()`: meia-noite
   seguinte em **`America/Sao_Paulo`** (em UTC a virada cai às 21h de Brasília,
   em plena tarde) com **piso de 2 h** — quem entra às 23:30 vale até a virada
   do dia seguinte. A barra diz `sessão do dia · até HH:MM`, em cor de aviso nos
   últimos 15 min. ⚠️ **O que custa, dito:** quem entra às 08:00 passa a ter
   token de **16 h** em vez de 10 h; continuam valendo `ativo = false` na
   requisição seguinte, 403 na hora ao perder permissão, e a rotação do segredo.
   🚨 **Segundo defeito consertado:** o 401 limpava a sessão e **não navegava** —
   a pessoa ficava olhando uma tela sem casca que não respondia mais nada. Agora
   vai ao Login com *"Sua sessão do dia terminou. Entre de novo."*
5. **Bloco 9 — import retroativo.** `movizap-ligacoes.ps1 -Exportar` (agente
   **0.5**) grava um `.zip` na Área de Trabalho **sem chave, sem config e sem
   falar com a VPS** — é só leitura, que é o que permite rodar no PC **antes**
   do alistamento. Na VPS, `scripts/importar_ligacoes.py` entra pelo **mesmo**
   `ligacoes.registrar()` do agente: a idempotência é a mesma, então o segundo
   import grava **zero**. Recusa por escrito: linha sem `call_id`, áudio sem
   ligação correspondente, `sha256` diferente do declarado, pacote de outra
   origem, versão futura. O `pc` vira `importado:<PC>`.

### Dois ajustes dele no fim do dia, já no ar

**1. 🔵 A senha de alistamento vale 1 DIA** — *"podemos prolongar as senhas para
1 dia por enquanto? ou precisaria refazer o exe?"* · *"ok para ajuste das
senhas"*.

Resposta à pergunta dele: **o `.exe` não muda.** A senha é derivada inteiramente
na VPS; o instalador só manda o que foi digitado. Nenhum PC reinstalado, nginx
intacto.

🚨 **E o que mudou foi a ACEITAÇÃO, não a janela de geração.** `JANELA_S = 86400`
era o caminho óbvio e seria defeito grave: `UNIQUE (ramal, janela)` é o que faz
a senha servir uma vez, então uma janela de um dia viraria **um alistamento por
ramal por dia** — e se o alistamento falhasse depois de queimar a janela, "peça
outra senha" devolveria a mesma senha morta e o ramal ficaria travado até
amanhã. Agora: **troca a cada 10 min** (uma falha custa 10 min, como antes) e
**é aceita por 24 h** (`JANELAS_ACEITAS = 144`). Uso único, só alista, e os 5
erros seguidos continuam trancando o IP. ⚠️ Custo: senha ditada e não usada
serve por um dia em vez de 20 min. Voltar é uma linha (`= 2`). A ferramenta
passou a dizer o prazo **real** — antes dizia "vale por 7 min" de uma senha que
valia um dia. **15 testes verdes**, incluindo senha de 23 h servindo, de 25 h
recusada, e janela queimada **não** trancando a seguinte.

**2. 🔵 A ficha da conversa, desenho A** — *"essa tela dentro da ficha esta
redundante e um pouco feia"* → 3 mockups em
`https://claude.ai/artifact/QSonPKYn1HUYHSfDvgHTBG` → *"Tipo A 100%"*.

🚨 **O defeito era o mesmo telefone TRÊS vezes na mesma tela** — topo, "Contato"
(o nome do contato, derivado, era o próprio número) e a linha de telefones que
eu havia acrescentado **horas antes**, no Bloco 6. Duas das três eram minhas, do
mesmo dia. No ar: a linha de telefones saiu; nome derivado do telefone passa a
dizer **"sem nome no cadastro"** (ausência de dado com cara de dado é tela que
mente); as três consultas dividem **uma** linha em vez de três botões soltos
numa gaveta com `max-height: 45%`; a empresa virou **cartão** (razão com peso,
fantasia como subtítulo, CNPJ e e-mail em linha de apoio, e-mail que quebra em
vez de cortar — cortado não dá para copiar); e **Desvincular** saiu da pilha das
consultas para o pé, porque eram três botões de ler e um de apagar, iguais.
⚠️ **Divergência declarada do mockup:** o "Tipo" continua na lista de dados, e
não como chip no topo — para quem pode trocá-lo ele é um `<select>`, e chip mais
campo recriaria a duplicação. **32 testes** no `ficha_1510.teste.js` (a guarda
do Bloco 6 que afirmava o contrário foi **reescrita, não apagada**), frontend
**261 verdes**, build feito.

⚠️ **Também corrigi a página de mockups depois de publicada:** eu havia escrito
que os quatro pares do `<dl>` "gastam o dobro da altura", e o CSS mostra que ele
já é grade de duas colunas. O problema é falta de peso, não de espaço — a
correção está escrita na própria página.

### Blocos 11 e 12 + o vigia falante, no ar no fim do dia

🔵 *"o 3 pode seguir"* liberou os dois blocos propostos e o resumo do vigia. Os
dois itens do mesmo pacote que eu **não** toquei estão na lista de pendências:
apagar gravação do PC e recompilar o `.exe`.

1. **Bloco 11 — log de ações na conversa** (migração **064**, `mensagem.evento`).
   Treze ações deixam **uma linha** no fio: assumir, entrar, convidar, sair,
   remover, devolver à fila, transferir, encerrar, vincular, desvincular, mudar
   tipo, bloquear, desbloquear. 🚨 **Linha, não balão** — como balão ganharia o
   menu de editar e apagar, que é o que um log não pode ter. **Evento não se
   edita nem se apaga**, nem por quem agiu (e é justamente ele que passaria no
   teste "só quem escreveu"). **Nada retroativo**, declarado: vínculo e tipo não
   têm histórico, e data inventada engana mais que log que começa hoje.
   Transferência **sem resumo** passou a deixar rastro — até hoje não deixava
   nenhum. 14 testes Python + 8 de frontend.
2. **Bloco 12 — "visto por" na nota** (migração **065**, `nota_leitura`). Olho
   pequeno ao lado do carimbo, com quem teve a nota na tela e quando. 🚨 **O
   rótulo é "visto por", nunca "leu"** — o sistema sabe que a nota esteve na
   tela. Marca **ao aparecer** (`IntersectionObserver`), em lote; nota anterior
   ao corte diz **"sem registro"**, nunca "ninguém viu". 11 testes Python + 9 de
   frontend.
3. **O vigia passou a falar quando está tudo em dia** — cron separado em duas
   linhas: 08:10 só alerta, **18:10 com `--resumo`**. Uma mensagem por dia, não
   duas. E o resumo diz **número** ("1 PC enviando, 8 sem agente"), porque "tudo
   ok" não distingue vigia funcionando de vigia olhando para base vazia.
   ⚠️ **O primeiro resumo chega hoje às 18:10 no WhatsApp dele.** 4 testes.

🚨 **A suíte inteira achou uma regressão que a leitura não acharia**, e ela era
séria: a regra de **sem dono** (02/10) é "a última mensagem tem de ser de
`entrada`" — e o evento é mensagem interna, então **convidar alguém numa
conversa órfã a tirava da fila**. A mesma coisa valia para a **prévia da lista**:
toda conversa passaria a mostrar "assumiu a conversa" no lugar da última fala do
cliente, na tela mais usada do painel. Corrigido excluindo o **evento** (não a
nota) das duas consultas.
⚠️ **E isso descobriu um defeito ANTERIOR a hoje, que é decisão dele:** uma
**nota interna** comum também tira a conversa de "Sem dono" pelo mesmo caminho.
Não mexi — a regra é dele.
⚠️ Também declarado: o evento de transferência só nasce no `motivo = 'manual'`.
A distribuição automática já grava a nota do sistema com a regra dos 10 min, e o
evento ali seria uma segunda linha dizendo quase o mesmo.

### A senha de alistamento, e o mutirão dos ramais

🔵 *"podemos prolongar as senhas para 1 dia"* → depois *"pode deixá-las com
48hrs a partir da geração"* → `JANELAS_ACEITAS = 288`. **O `.exe` não muda**: a
senha é derivada só na VPS.

🔵 *"lista de ramais, para deixar as senhas prontas para mim ... salve como .txt
na mesma pasta"*: **`Desktop\MoviZap-Ligacoes-Kit\2-PC-DO-IAGO\SENHAS-DOS-RAMAIS.txt`**,
geradas 15/10 19:10, válidas até **17/10 19:10**.
🚨 **O arquivo não dá senha a quem já está enviando** (3404 e 3405): usá-la
revogaria o PC que funciona. E ele diz, dentro de si, que é uma chave e que se
apaga depois do mutirão.
⚠️ **Quatro ramais ficaram de fora, e os dois primeiros são decisão dele:**
**3402 Caio** e **3403 Fabio** não existem como atendente ativo no MoviZap
(não criei conta para ninguém); 3406 e 3407 estão "Livre" na planilha dele.
⚠️ **E dois atendentes do sistema não estão na planilha dele:** **Relison** e
**Thiago** — ou têm ramal que não foi listado, ou não vão usar MicroSIP.

### A Claudia subiu — com um aviso

Agente **559**, PC `CLAUDIA`, último contato 15/10 17:30, cert até 14/10/2028,
0 pendentes. 🚨 **Mas o agente dela acusa: "gravacao automatica DESLIGADA no
MicroSIP; pasta de gravacoes ainda nao existe"** — o histórico dela sobe, as
**gravações não**. Precisa ligar a gravação automática no MicroSIP dela.

### 🔎 VALIDAÇÃO DE FIM DE DIA — medida, não lembrada (15/10 19:2x)

🔵 *"valide tudo do feito de hoje e depois documente e encerre segundos planos"*.
Roteiro em `scripts/validar_dia_1510.py`, que dá para rodar de novo amanhã.

```
suíte inteira             1425 verdes, 2 skips, 0 falhas  (eram 1348 de manhã)
suíte de frontend         269 em 19 arquivos
migrações 063/064/065     as três aplicadas
contrato do banco         ck_evento_conhecido · ck_evento_e_nota_interna · nota_leitura
serviço / painel          active · HTTP 200
bundle publicado          as 10 marcas do dia conferidas DENTRO do dist
resíduo de teste          ZERO (atendentes, clientes, ligações, agentes, conversas)
agentes vivos             2 — ramal 3404 Iago · ramal 3405 Claudia
cron do vigia             2 linhas; só a das 18:10 com --resumo
processos pendurados      nenhum, na VPS e aqui
```

🎉 **A Claudia subiu o histórico INTEIRO dela sozinha:** a base foi de 28 para
**144 ligações** — 116 dela, de 24/08 a 15/10, **nenhuma com gravação**. Isso
fecha exatamente com o aviso que o agente dela manda: gravação automática
desligada no MicroSIP. O caminho PC → VPS funcionou de ponta a ponta num
segundo operador, no primeiro dia.

🎉 **E o log do Bloco 11 funcionou em PRODUÇÃO, com gente de verdade**, sem eu
tocar em nada: **16 eventos** entre 15:52 e 17:40 — 6 `encerrou`, 5 `assumiu`,
2 `entrou`, 2 `vinculou`, 1 `transferiu`, em conversas de Aline, Ludmila e
outros. `nota_leitura` ainda em 0, que é o esperado: ninguém abriu conversa com
nota depois da publicação.

🚨 **Duas FALHAS que o validador acusou eram do próprio validador**, e as duas
são a mesma doença de sempre — conferência mal escrita acusando o que está
certo:
1. ele comparava com **"28 ligações"** decorado da manhã. O número **cresce** a
   cada operador alistado; o que se checa é coerência, não um número fixo.
2. ele procurava `ICONE_EVENTO` no bundle — **`const` de módulo, que o
   minificador renomeia**. Procurar classe de CSS e string literal, que
   sobrevivem ao build.
Os dois foram corrigidos **no script**, não no código.

### As provas, e como foram obtidas

| O quê | Prova |
|---|---|
| Suíte inteira | **1387 verdes, 1 skip, 0 falhas** (99 s) |
| Testes novos | 13 (`teste_contatos_da_empresa.py`) + 8 (`teste_auth.py`) + 12 (`teste_importar_ligacoes.py`) + 24 (`ficha_1510.teste.js`) |
| Suíte de frontend | **253 verdes** em 18 arquivos |
| Build | limpo, 117 módulos — **e build limpo é o que prova que o template compila** |
| Rotas no ar | `contatos-da-empresa` e `ligacoes` respondendo **401 sem token** |
| Import contra base cheia | pacote REAL deste PC (28 ligações, 19 gravações, 5,6 MB): **0 novas, 28 e 19 já estavam, 0 recusadas** — nos dois modos |
| Base intacta | **28 ligações, 19 gravações, 0 importadas, 1 agente vivo** depois de tudo |
| Resíduo de teste | zero (ramais `996xx`, cliente `Zz Teste Outros` e conversas apagados no teardown) |

### 🚨 Quatro erros meus, todos achados por TESTE — nenhum por leitura

1. **O `Compress-Archive` do Windows PowerShell 5.1 grava `\` dentro do zip.**
   O importador procurava `gravacoes/` e **recusou 19 gravações boas** dizendo
   que estavam "ausentes do zip". O pacote vem do PC do operador, onde não se
   escolhe a versão do PowerShell — quem tem de aceitar os dois separadores é a
   VPS. Virou teste, não comentário.
2. **`--conferir` dizia "11 entrariam" com as 11 já na base.** Ele contava o
   pacote, não o banco. Relatório que promete mais do que vai acontecer é a
   mesma doença de tela que mente — passou a consultar `ligacao` e
   `ligacao_gravacao`.
3. **O contador contava a ligação duas vezes** quando ela tinha duas gravações:
   "30 já estavam" num pacote de **28**. A conta passou a sair de um conjunto de
   `call_id`, nos dois modos.
4. **O script fechava o pool do banco no `finally`**, derrubando o banco
   embaixo do teste seguinte. Abrir e fechar o pool é do `__main__`, não da
   função — e foi a suíte que mostrou isso, não a leitura do código.

⚠️ **E um tropeço de operação:** o `cp` de backup dos 4 arquivos de frontend do
Bloco 8 falhou (expansão de variável no ssh) e eu só vi depois de o patch estar
aplicado. Sem prejuízo — os 4 estavam limpos no git, então o original é
recuperável por `git diff` —, mas o `.bak` daquele bloco **não existe**.

### O que falta, por quem depende

1. 🔴 **Dele, no navegador** (nenhuma suíte vê tela): a **ficha com o desenho A**
   (barra de ações, cartão da empresa, "sem nome no cadastro", Desvincular no
   pé), o **modal de Ligações** na ficha do próprio número (tem 19 gravações), o
   **Outros contatos** saltando para outra conversa, o **rascunho** sobrevivendo
   à troca de conversa e a um F5, e a barra dizendo `sessão do dia · até HH:MM`.
   A aba **Ligações** ele já validou hoje ("deu ok"); o que entrou depois dela,
   não.
2. 🔴 **Dele, o mutirão:** **Claudia já subiu** (agente 559), mas falta **ligar
   a gravação automática no MicroSIP dela** — hoje o histórico dela sobe sem
   áudio. Faltam 5 com senha pronta no arquivo: Aline (3347), Ludmila (3348),
   Rodrigo (3399), Karla (3400), Erika (3401).
3. 🔵 **Dele, as duas que sobraram do item 3:** o *"7 dias já pode apagar"* do
   PC (apaga gravação na máquina das pessoas) e **recompilar o `.exe`** para
   igualar o agente 0.5 (troca o instalador que ele está usando agora). Nenhuma
   das duas foi tocada: "pode seguir" não é autorização para apagar nem para
   trocar artefato em uso.
3b. 🔵 **Dele, perguntas novas:** **Caio (3402)** e **Fabio (3403)** entram como
   atendentes? Hoje não existem no MoviZap, e eu não criei conta para ninguém.
   E **Relison** e **Thiago** estão no sistema mas fora da planilha de ramais.
3c. 🔵 **Dele, defeito ANTERIOR a hoje que eu achei:** **nota interna comum tira
   a conversa de "Sem dono"**, pelo mesmo caminho que o evento tirava. Não
   mexi — a regra do "cliente esperando" é dele.
4. 🟡 **Meu, quando todos estiverem alistados:** tirar a rota antiga de ENVIO
   (`/api/ligacoes/agente/{batimento,enviar}`). A de `alistar` **fica**.
5. 🟡 **Meu, se ele aprovar:** Blocos 11 e 12.

### A primeira metade do dia (Blocos 1 a 4) — o que já estava no ar

**Plano aprovado:** `.claude\plans\ent-o-temos-o-exe-glimmering-parnas.md` (tem
a tabela de andamento e, por bloco, o que mudou do planejado).

| Bloco | Estado |
|---|---|
| 1 — `.exe` de um passo + alistamento por senha | **NO AR** |
| 2 — vigia na VPS (cron 08:10/18:10 + aviso no WhatsApp dele) | **NO AR** |
| 3 — camada de consulta (`ligacoes_consulta`, CSV, rota da ficha) | **NO AR** |
| 4 — aba Ligações (`LIG_1.1`) | **NO AR**, e desde 15/10 à tarde **para todo atendente** |
| 5 a 10 | **NO AR / FEITOS** na tarde de 15/10 — ver o começo desta seção |
| 11 e 12 — log de ações e "visto por" na nota | **propostos**, esperando ele |

**Estado medido na manhã de 15/10** (o do fim do dia está no começo desta
seção): 28 ligações e 19 gravações, iguais no PC e na VPS. **1 agente vivo**
(ramal 3404, agente 431, v0.4, cert até 14/10/2028); **9 atendentes sem
agente**. Suíte: **1348 verdes** antes do build.
⚠️ **O que falta vive no começo desta seção, não aqui** — esta parte é o
registro da primeira metade do dia.

🔵 Demanda dele, na ordem em que saiu: *"vamos revalidar e ja concluir o
script que pega as ligações na area de trabalho, identifica o usuario e faz o
upload na VPS"* · *"eles vão precisar dar um .exe apenas para rodar tudo"* ·
*"validar o atendente do MicroSip com uma senha que será gerada sempre via
algoritmo e é mutável"* · *"se trocarem de PC é só executar novamente e me
pedir a senha de uso"* · *"o .exe se deleta automaticamente após ser
concluído"* · *"a senha é só para rodar o .exe mesmo, não é viavel senha para
ping"* · *"eu apagaria do Pc para evitar engenharia reversa e senha do banco"*
· *"precisa ter informações para o windows, para que não encerrem erroneamente
e persistência agendada para reiniciar com windows -- Movizap - Backup de
Ligações"*.

### Primeiro: a revalidação que ele pediu (antes de qualquer código)

O caminho PC → VPS estava intacto desde 25/09. Medido hoje, não lembrado:
tarefa `Ready`, última corrida 08:28:41 com resultado 0 e **0 execuções
perdidas**; simulação do dia com **28 ligações (17 com gravação) e 19
arquivos, 5,6 MB**; no banco **28 `ligacao` e 19 `ligacao_gravacao`**, no disco
**19 mp3** (5,8 MB) — os dois lados batendo, sem pendência e sem duplicata.
Agente do ramal 3404 → `atendente_id 121`, PC `DESKTOP-I867L57`.

🚨 **Um achado da revalidação:** a rotina de vigia (`scripts/agentes_mudos.py`)
existe e funciona, mas o gatilho é o `SessionStart` da minha sessão — **não há
cron nem timer na VPS**. Com 1 PC passa; com 8 operadores, não. É o Bloco 2 do
plano, ainda não feito.

### O que entrou no ar hoje

1. **Migração 063**: `alistamento_queimado` (com `UNIQUE (ramal, janela)`, que
   é o que faz a senha servir uma vez), os 4 índices de consulta do grid que
   vem depois, e `ligacao_exportacao` para o rastro de quem exportar CSV.
   **Não tocou em nada que já estava no ar.**
2. **`movizap/ligacoes_alistar.py`** + rota `POST /api/ligacoes/agente/alistar`
   no painel. A senha é HMAC de um segredo PRÓPRIO (`MOVIZAP_LIGACOES_SENHA_SEGREDO`,
   gerado dentro da VPS, nunca o `jwt_secret`) sobre (ramal, janela de 10 min).
   Reusa `ligacoes.gerar_chave` (que já revogava o agente anterior) e
   `ligacoes_ca.assinar`.
3. **`scripts/senha_alistamento.py`** + `2-PC-DO-IAGO\Senha de alistamento.cmd`:
   a senha para ele ditar, com o tempo restante e o aviso de que alistar em
   outro PC revoga o atual.
4. **Agente v0.4**: a chave do ramal passou a ficar **cifrada com DPAPI** do
   usuário; `config.json` da v0.3 é migrado na primeira passada, sem
   reinstalar.
5. **Dois executáveis**, compilados pelo `csc.exe` que já vem no Windows
   (`fontes\Compilar.cmd` — sem ps2exe, sem instalar nada, sem admin):
   `MoviZap-Instalar-Ligacoes.exe` (68 KB, carrega dentro de si o agente, o
   instalador, o desinstalador, o LEIA-ME e o lançador, e se apaga no fim) e
   `MoviZap-Backup-de-Ligacoes.exe` (fica instalado; é o que a tarefa executa).
6. **Identidade no Windows**: tarefa renomeada para **`MoviZap - Backup de
   Ligações`** com descrição dizendo o que ela **não** faz, entrada em
   **Aplicativos instalados**, atalho **"(ver situação)"** no Menu Iniciar,
   `LEIA-ME.txt` na pasta do agente, e reinício em caso de falha (3× 10 min).
   A persistência que ele pediu **já existia**: logon + 5 min e
   `StartWhenAvailable`.
7. **Kit reescrito**: `MANUAL.md` de **9 passos para 2**; `Preparar operador` e
   `Assinar pedido` aposentados em `fontes\aposentado-v03\`; a pasta
   `operadores\` (que guardava o `config.json` secreto por pendrive) deixou de
   existir.

### O que eu provei, e como

| O quê | Prova |
|---|---|
| Suíte | **27 verdes** (`teste_ligacoes_alistar.py` novo com 9 + os 18 que já havia de ligações) |
| Alistamento pela rota HTTP | 200, chave + certificado conferindo **juntos**; mesma senha de novo → 401 |
| Senha errada × ramal sem dono | **mesma** mensagem (dizer qual é o caso entregaria a lista de ramais) |
| 5 erros seguidos | trava só aquele IP (reusei o `ratelimit.py` do login, em SQLite) |
| Alistamento real do ramal 3404 | agente 17 revogado, **agente 431** vivo, cert até 14/10/2028 |
| A tarefa nova | rodou com resultado **0**, `batimento ok` pela porta com mTLS |
| DPAPI | `config.json` sem `chave`, só `chave_protegida` (620 caracteres) |
| O `.exe` | extrai os 5 arquivos e chama o instalador |
| Base intacta | **28 e 19** antes e depois de tudo |

### 🚨 Quatro erros meus, achados por teste e corrigidos (não por leitura)

1. **`ultimo_pc` só era preenchido no batimento** — o alistamento não
   registrava em que PC o ramal entrou, e o "PC trocado" ficava cego justamente
   no dia da troca. Um teste falhou e eu corrigi o **código**, não o teste.
2. **`Get-Content -Raw` devolve string DECORADA** (`PSPath`, `PSProvider`): o
   `ConvertTo-Json` serializou o objeto inteiro, o CSR chegou como objeto e a
   VPS respondeu **422**. `[IO.File]::ReadAllText` resolve.
3. **No PS 5.1 o corpo do erro já foi consumido** pelo `Invoke-RestMethod`:
   a pessoa veria *"Nao consegui falar com a VPS (401)"* em vez de *"Senha
   inválida ou vencida"*. O corpo vive em `$_.ErrorDetails.Message`.
4. **O certificado revogado ficava no cofre do Windows** a cada troca de PC.
   O instalador passou a removê-lo (e o resíduo deste PC foi limpo à mão).

### Duas coisas que eu mudei do plano aprovado, para melhor

- **Limite de tentativas**: reusei `movizap/ratelimit.py` (contador em SQLite,
  sobrevive a restart, lê o IP certo atrás do nginx) em vez de contador em
  memória, que eu havia proposto.
- **Onde mora o alistamento**: no **painel**, não na porta 8010. Lá o nginx
  exige certificado de cliente e um PC que está se alistando ainda não tem —
  nem abriria a conexão. Efeito colateral bom: **o nginx não foi tocado** e
  nenhum passo pediu root.

### Pendências do Bloco 1 (as que sobreviveram ao dia)

⚠️ **A lista de verdade é a do começo desta seção.** Aqui fica só o que nasceu
no Bloco 1 e continua de pé:

1. 🟡 **`.exe` não assinado**: se o SmartScreen/antivírus barrar em vários PCs,
   a saída é certificado de assinatura de código — decisão dele.
2. 🔵 **O "7 dias já pode apagar" do PC** continua esperando a palavra dele:
   hoje nada é apagado.

*(O cron do vigia e os Blocos 3 a 10 saíram daqui porque foram feitos no mesmo
dia; replicar nos operadores e tirar a rota antiga de envio estão na lista do
começo da seção.)*

### Bloco 4 do plano — a aba Ligações (`LIG_1.1`) NO AR, 15/10

🔵 *"um grid simples ... exportar e importar e um botão para baixar a ligação
se quiser ou reproduzir por lá"*.

- **Aba nova em 8 lugares** (o projeto cobra todos): `movizap/telas.py`
  (`LIG_1.1`, permissão `ligacoes`), 4 rotas em `main.py`,
  `MenuLateral.NOME_DO_MODULO` (prefixo novo `LIG`), `router/index.js`,
  `telas/Ligacoes.vue`, `docs/03`, `docs/06`, `docs/02` e as listas de dois
  testes.
- 🚨 **Nasceu só dele e durou um dia.** Horas depois: 🔵 *"pode exibir a aba
  para todos"*. Em vez de conceder a permissão própria perfil a perfil, a tela
  passou à permissão **`atendimento`** — é o que o
  `test_admin_ve_exatamente_o_que_ele_decidiu` prevê (*"tela nova de
  atendimento entra sozinha — é a permissão"*), então o conjunto fechado do
  admin, que guarda a frase dele de 24/09, ficou intacto. Hoje veem a aba:
  owner, admin e atendimento; **fora: só o perfil `cadastro`**. Conferido
  perfil a perfil depois do restart.
- 🚨 **O que isso custa, dito por escrito:** todo atendente passa a poder
  **ouvir, baixar e exportar** gravação de qualquer ligação. O rastro de
  `ligacao_exportacao` deixa de ser detalhe — é a única resposta para "quem
  levou o quê".
- **A tela:** grid com quando, sentido, número, cliente, atendente+ramal,
  duração e gravação; filtros de período, atendente, sentido, número (aceita
  **pedaço**) e "só com gravação"; paginação de 50; **ouvir e baixar na própria
  linha** (um player por vez, blob liberado ao trocar); **Exportar CSV** com
  rastro em `ligacao_exportacao`.
- 🚨 **A faixa de cobertura no topo é o que impede a tela de mentir:** diz
  quantos atendentes têm agente, com o último contato de cada um, e **nomeia
  quem está de fora** (hoje: 1 de 9, e os outros 8 nomeados). A mesma frase
  aparece no estado vazio.
- ⚠️ **Sem busca de empresa por nome:** isso é `CAD_1.1`, permissão que a aba
  não tem. Vindo da ficha, o `cliente_id` chega pela URL como chip removível.

**Provado:** 28 testes no arquivo de consulta (incluindo as 4 rotas da aba:
owner entra, atendimento toma **403**, CSV com BOM/`;`/nome de arquivo e rastro
gravado, gravação tocando **também para quem atende** — senão o player do modal
não funcionaria), 7 testes de frontend novos (a tela monta, nomeia quem está
sem agente, mostra "+1" de número em duas empresas, "sem cadastro" e "sem
gravação"), **suíte inteira 1348 verdes** antes do build, e as 4 rotas no ar
respondendo 401 sem token. Build feito (= publicação) e `movizap` reiniciado.

⚠️ **Duas travas do projeto me pararam, e as duas estavam certas:**
`teste_telas.py` exige que **prefixo de módulo novo seja declarado** na própria
trava (declarei `LIG`, com o porquê), e `teste_modelo_documentado.py` exigiu as
tabelas da 063 em `docs/02` antes de seguir.

✅ **VALIDADO POR USO — medido em 23/10.** A aba está no menu como "Ligações"
(`/ligacoes`) e o módulo tem **288 ligações**, a última em **23/10 12:19**.
Deixou de ser pendência: está em produção com dado real.

### Bloco 3 do plano — a camada de CONSULTA (NO AR, 15/10)

Até hoje o módulo só escrevia: zero rota de leitura, zero tela, zero player.

- **`movizap/ligacoes_consulta.py`** (módulo separado de propósito — o
  `ligacoes.py` é o caminho de escrita do agente e não se mexe nele para
  acrescentar leitura): `consultar` (filtros de data, atendente, ramal,
  sentido, número, cliente e "tem gravação", com paginação), `para_csv`,
  `do_telefone` (o modal da ficha), `gravacao` e `agentes` (a cobertura).
- **`movizap/relatorio_csv.py`** — o primeiro CSV do projeto (não havia nada
  para reusar): `;`, BOM e CRLF, com **fórmula neutralizada** (um contato
  chamado `=cmd|...` viraria execução ao abrir a planilha).
- **`GET /api/conversas/{id}/ligacoes?dias=7`**, sob **`ATD_1.2`** — a
  permissão da conversa, não a da aba: quem atende vê as ligações do número
  que está atendendo.
- **22 testes verdes** (`tests/teste_ligacoes_consulta.py`: 17 da consulta + 5
  da rota com `TestClient`), e contra a base real os números batem com a
  simulação do agente do mesmo dia: 28 ligações, `{feita 19, recebida 4,
  perdida 5}`, 19 gravações.

🚨 **Três armadilhas que viraram teste, não comentário:** uma ligação com
**duas gravações** (MicroSIP reinicia o arquivo no meio) viraria duas linhas
com `JOIN` — vem por subconsulta agregada; um **número em duas empresas**
também duplicaria — `clientes` é lista; e **número sem cadastro** vem lista
vazia, que a tela traduz por "sem cadastro" e não por "não consultei". Mais
duas: os totais são do **filtro inteiro** (rodapé que conta a página mente ao
virar) e a busca por **pedaço** de número funciona.

🚫 **Não fiz a visão `ligacao_resumo`** que o plano previa: as subconsultas
resolvem, e uma visão a mais seria lugar a mais para a verdade divergir.

⚠️ **Dois tropeços de fixture** (meus, corrigidos): o `autouse` recriava o
atendente em cada teste e batia no `ux_atendente_login`; e uma execução
interrompida deixou conversa de teste de pé, que o `ux_conversa_aberta`
recusou na seguinte — agora limpa antes e depois, e o grupo de teste se
identifica por `grupo_jid`, nunca por "telefone nulo" (que apagaria grupo
real).

### Correção do log do agente — "zero ambíguo" (NO AR, 15/10)

🔵 Pergunta dele no meio da sessão: *"o resultado do script foi zero por ja não
ter novos ou nenhum na pasta? importante deixar no log a diferença para evitar
falso positivo ou pasta movida ou apagada"*. Era defeito: `0 novas` dizia a
mesma coisa nos dois casos.

- A linha do log passou a dizer **quanto havia**:
  `... 0 novas, 0 ja estavam na VPS, 0 gravacoes pendentes | historico 28, pasta 19 | batimento ok`.
- `pasta 0` **depois de o PC já ter enviado gravação** sai com aviso que nomeia
  o caminho procurado: *"pasta de gravacoes SEM ARQUIVOS mas este PC ja enviou
  19: movida ou apagada?"*. Vai no batimento, então o vigia da VPS avisa sozinho.
- Leitura que falha antes de contar mostra `historico ?, pasta ?` — zero que não
  foi medido é mentira.
- **Provado** com a pasta apontada para um lugar inexistente (ini e pasta de
  dados de teste, sem tocar no estado real), e o aviso que esse teste gravou na
  VPS foi limpo em seguida, para o cron das 18:10 não mandar alarme falso.

### Bloco 2 do plano — o vigia na VPS (NO AR, 15/10)

🔵 *"Rotina da VPS verifica se os envios estão sendo feito corretamente"*. O
ping já existia (é o `batimento`); o que faltava era **alguém olhando**.

- `scripts/agentes_mudos.py` ganhou `--avisar-whatsapp` e **cron às 08:10 e
  18:10** (depois das passadas dos PCs, para não acusar quem ainda ia falar),
  com log em `/home/claude/logs/movizap_ligacoes_vigia.log`.
- Fala **direto com o Evolution**, não pela rota do painel: o vigia tem de
  funcionar inclusive com o painel fora do ar — que é um dos motivos de um PC
  parecer mudo. E se o envio falhar, o alerta não se perde: já foi impresso.
- Número em `MOVIZAP_LIGACOES_AVISO_NUMERO` (vazio = só imprime, que é o que
  mantém o gancho da sessão sem mandar mensagem a ninguém).
- **Provado:** tudo em dia = silêncio total nos dois modos; PC fingido mudo há
  30 h = alerta impresso **e mensagem entregue** no WhatsApp dele; o estado
  forçado voltou ao valor exato (`finally`); e a linha do cron, rodada
  literalmente, devolveu 0.
- 🚫 **Não fiz** o alerta de "ramal revogado sem substituto" que eu mesmo havia
  proposto: a revogação acontece junto do alistamento do PC novo, na mesma
  transação, e fora disso só à mão, quando alguém sai da empresa — avisar ali
  seria cobrar a reinstalação de quem foi embora.

### Duas frentes PROPOSTAS hoje, nenhuma linha de código (decisões dele)

🔵 *"ao final proponha log dentro da conversa interno apenas sobre ações de
transfernecia, inserir pessoas, etc, pode ser em Nota interna do Movizap"* e
*"verifique a possibilidade de confirmação de leitura das notas dentro da
conversa ... um icone que ao clicar mostra que ja leu aquela nota, junto ao
carimbo de data e hora, bem pequeno mesmo"*.

**Proposta 1 — log de ações como Nota interna.** Metade já existe: desde 23/09
(migração 049) a transferência manual grava nota interna com o resumo. Faltam
as outras ações, com cara própria de **evento** (coluna nova em `mensagem`):
inserir alguém, sair, assumir, passar a sem dono, encerrar/reabrir, vincular e
desvincular empresa, mudar tipo, bloquear. Evento **não se edita nem se apaga**
(log que se reescreve não é log), é linha discreta sem balão, e nunca sai para
o cliente. Decisões dele: a lista; se evento conta no contador de mensagens
(eu diria não); e se entra retroativo — transferência, encerramento e convite
dá para reconstituir, **vínculo e tipo não têm histórico** e inventar data
seria pior que não ter.

**Proposta 2 — confirmação de leitura da nota.** Viável: tabela
`nota_leitura (mensagem_id, atendente_id, visto_em)`, marcada quando a nota
**aparece na tela** (abrir a conversa sem rolar até lá não é ver), com ícone
pequeno ao lado do carimbo e popover de nomes e horas. 🚨 Ressalva que não
contorno: o rótulo tem de ser **"visto por"**, não "leu" — o sistema sabe que a
nota esteve na tela, não que a pessoa leu. E nota anterior à mudança tem de
dizer **"sem registro antes de tal data"**, nunca "ninguém viu", senão o
recurso nasce mentindo sobre o passado. Hoje a conversa não tem nenhuma noção
de leitura (é coletiva); quem tem marcador é o **chat interno**, e lá é marca
d'água por sala (`chat_membro.lido_ate`), não por mensagem.

Se ele aprovar, entram como **Blocos 11 e 12** do plano.

Documentado em `docs/ligacoes.md` (seção "Alistamento por senha (v0.4)", com
as três armadilhas do PowerShell) e no `MANUAL.md` do kit. Backups do dia:
`movizap/config.py.bak_2026-10-15_alistamento`, `movizap/main.py.bak_...`,
`docs/ligacoes.md.bak_2026-10-15`, e no PC
`%LOCALAPPDATA%\MoviZapLigacoes\*.bak_v03_2026-10-15`.

## 0.00000000000000 🔵 14/10 — FECHAMENTO DO DIA: pendências VERIFICADAS pelo estado

Não é lista de lembrança: cada linha abaixo foi medida no banco, no serviço ou na suíte, hoje.

## O que ficou de pé

```
suíte do FPSL            64 arquivos, 2.342 verificações
as 11 suítes da CTR      533 verificações, 0 falhas
/painel/contratos        200, servindo a tela nova (grid + coluna "Na WESO")
rotas do router          18, todas sob a tranca de owner
integrity_check          ok    ·  hash duplicado 0  ·  anulação dupla 0
placas                   ATIVA 2.763 · aviso 208 · RESCINDIDA 2.937 · SUBSTITUIDA 904
clientes com nome        731 de 731
termos com PDF           5      (de 4.599)
itens com valor mensal   1      (de 6.463)
eventos ANULA            1      ·  eventos fonte=weso  15
livro-razão da carga     4 anexado · 1 documento só · 3 fila
rotina de auditoria      DESLIGADA (sem linha na config), como ele decidiu
```

## 🚨 Três inconsistências que a própria verificação achou — e que eu causei

1. **O livro-razão tinha perdido a linha do 3465.** Eu a apaguei no ciclo de reparo do "documento só", e
   ficaram 5 termos com PDF contra 7 linhas no livro. Reposta, com o motivo escrito dentro da própria linha.
   Agora fecha: 4 anexados + 1 documento só = os 5 termos com PDF.
2. **Um arquivo órfão que eu criei:** `fpsl_weso/painel/contratos_router.py`, **fora** de `routers/` — erro de
   destino num `scp` meu. Era uma cópia **velha** (versão de 17 rotas), ninguém a importava
   (`main.py` importa de `painel.routers`), e foi apagada. Painel conferido depois: 200 e 18 rotas.
3. **Dois `grep` meus deram falso negativo hoje**, e em nenhum dos dois o código estava errado: o seletor
   `[data-v-...]` no meio da regra do MoviZap, e um parêntese a mais na busca do `correcoes_do_cliente`.
   ⚠️ **Conferência que falha por padrão mal escrito é pior que conferência nenhuma** — ela convida a
   "consertar" o que está certo.

## A auditoria, rodada hoje por "Rodar agora" (a rotina segue desligada)

| Tipo | 13/10 | 14/10 | |
|---|---|---|---|
| CONTRATADA_NAO_INSTALADA | 1.362 | **1.349** | −13 |
| SUBSTITUICAO_PELA_METADE | 364 | 364 | 0 |
| EM_USO_SEM_CONTRATO | 320 | **322** | +2 |
| ENCERRADA_EM_USO | 173 | **168** | −5 |
| EM_USO_FALTA_ASSINAR | 135 | **136** | +1 |
| PLACA_EM_DOIS_CLIENTES | 84 | **83** | −1 |
| **total** | **2.438** | **2.422** | **−16** |

⚠️ **A queda é pequena, e eu não prometi mais que isso:** só 15 placas fecharam e 5 termos ganharam PDF. O
movimento grande espera a carga dos 2.825 assinados.
⚠️ **E o delta tem DUAS causas, não uma:** além do meu trabalho, o cache da WESO é de **14/10** e a rodada
anterior comparava com o de **13/10** — um dia de cadastro novo entra na conta. Conferido: **nenhuma** das 15
placas que a frente D fechou, e nem a placa que a C7 anulou, aparece entre os achados.

## Pendências, verificadas uma a uma

### 🔴 Dele (nada avança sem isso)
1. **Abrir no navegador:** `/painel/contratos` (grid, chips, modal, gaveta e a coluna "Na WESO" dentro da
   ficha, que agora tem 7 colunas) e o **botão Ficha do MoviZap** em nome curto, nome longo e conversa sem
   cadastro. Nenhum teste vê largura, recorte ou elemento cobrindo outro.
2. **Os 84 que a frente D deixou**, na coorte "contrato maior que o uso" (132 clientes) — é a coorte que ele
   mandou separar, e cada caso pede a linha do tempo lida.
3. **A carga dos 2.825 assinados** segue parada por decisão dele. Hoje são **5** termos com PDF.
4. **`teste_extrair_termo`** (vermelho desde 02/10, expurgo F7): apagar a suíte ou reescrevê-la contra
   `/painel/api/operacoes/extrair`. Enquanto existir, o placar do FPSL não fecha verde.
5. **`teste_higiene_placas_weso`** ficou vermelho **hoje**: 1 placa com espaço à direita na **WESO ao vivo**.
   Não é da CTR, que não escreve na WESO; o conserto escreve, e há `corrigir_placas_espaco.py` no projeto.

### 🟡 Medido e à espera de vez
6. **As 150 placas em uso sem assinatura** aparecem marcadas na ficha, mas **não têm ação própria** — cobrar
   assinatura é trabalho, não defeito de cadastro.
7. **Os 3 documentos na fila da 2HM** (leitura descritiva em termo de máquina pesada). **Falta medir quantos
   dos 2.825 caem nisso** antes de prometer cobertura.
8. **O valor:** 1 item com valor mensal, de 6.463. A `CAR_1.1` depende disto, e a WESO **não ajuda** — o
   campo `valor_mensalidade` dela vem **zero** nos 1.932 veículos.
9. **O vínculo veículo→cliente no cache da WESO** não existe porque a API não o entrega
   (0 de 1.932 em `/Veiculos/Consultar`). Consertar custa uma chamada por cliente; só vale se ele quiser.

### ✅ Fechadas hoje, e por isso saem da lista
- A **fila da carga invisível** → coluna, chip e bloco na ficha, com o motivo (A7).
- A **regra do valor quase inerte** → ampliada e com o "paga uma vez só" excluído (A6).
- A **decisão dos 412 termos** → substituída pelas regras dele, e a coorte aderente aplicada (frente D).
- O **nome do cliente ausente** → 731 de 731.
- O **`/gravar` que duplicaria termo** → modo anexar, provado em produção.

## Versionamento
19 arquivos modificados no `fpsl_weso` e 3 no `movizap_painel`, todos esperando o **autocommit das 23:30**.
⚠️ Árvore limpa não significa sincronizado — é a regra da casa, e vale aqui.

## 0.0000000000000 🔵 14/10 — FPSL/frente D: a WESO desempata, placa por placa (coorte aderente NO AR)

**Origem (regras dele):** *"o criterio de desempate será quantas placas ativas ele tem na weso"* ·
*"termo antes de placas; porem, placas sem assiantura mas placa ativa, placa vence, pois se existe na weos
foi feita, o erro é não ter assinatura"* · *"primeiro os casos de 100% de aderência com margem de 1+ ou -"*
· *"usar a linha do tempo como parametro pelas datas ou entrada e saidas das placas, pois pode ser que N
placas foram recindidas mas nao assinadas, se tiverem fora da Weso, é recisão mesmo"*.

## O que eu validei antes de escrever código

1. 🚨 **A rotina do cache da WESO está SADIA — o buraco não é dela.** Rodou 04:15 (1.933 veículos, 3.803
   rastreadores, `integrity_check`, troca atômica). Ela **tenta** gravar o cliente
   (`_sub(v, "cliente", "id")`), mas `/Veiculos/Consultar` devolve 12 campos e **nenhum é de cliente** —
   medido: **0 de 1.932**. Consertar exigiria uma chamada por cliente (304+), o caminho de 15,6 s a timeout
   medido em 18/08.
2. 🚨 **E o desempate dele NÃO precisa da planilha.** O vínculo que falta é veículo→cliente; a regra usa o
   **inverso** — "esta placa do contrato existe na WESO?" — e isso o cache responde hoje, por placa **e por
   chassi**. A planilha da auditoria ficou como conferência, não como fonte.
3. ⚠️ **`valor_mensalidade` vem no payload da WESO e está ZERO nos 1.932.** Não é fonte de valor.

## As regras, como entraram

**Precedência: o termo define o que existe.** A WESO não cria contrato — ela desempata.

| Caso | Regra | Medido |
|---|---|---|
| **Placa na WESO** | **vence: fica ativa**, mesmo sem assinatura. A falta de assinatura é **achado** | **1.643** em uso; **150** delas sem assinatura |
| **Fora da WESO + rescisão na linha do tempo**, mesmo não assinada | **é rescisão mesmo**: fecha | 84 ainda a fechar (ver abaixo) |
| **Fora da WESO sem rescisão** | nada a fechar: fica como está | 1.244 |

🚨 **A proposta de "requalificar" caiu**, e a regra 2 dele é melhor: requalificação cega puniria exatamente o
veículo que está rodando. Quem está em uso não perde nada.

### Como a prova entra sem o motor perder a pureza
Fonte nova **`weso`** em `contratos_eventos.py`. Um `RESCINDE` com `fonte="weso"` **vale mesmo em termo sem
assinatura** — é a única fonte com esse poder, porque ela não afirma o que foi assinado, afirma o que **está
instalado**. A base da placa passa a dizer `"rescisao confirmada pelo uso (fora da WESO)"`.
⚠️ **Quem consulta a WESO é `contratos_aderencia.py`, nunca o motor** (que segue sem I/O, travado por teste),
e o evento aponta em `corrige_evento_id` a rescisão que ele confirma — **nada de `UPDATE`**. A mesma guarda
de 48 h da rotina C6 vale aqui: fechar placa por ausência com dado velho é pior que não decidir.

## 🚨 A primeira rodada real mostrou DUAS imprecisões na minha regra

Das 32 primeiras confirmações, só **15** mudaram algo:

| O que aconteceu | Quantas | Por que a regra não devia disparar |
|---|---|---|
| Placa **já em aviso prévio** | **12** | a rescisão **já está valendo** e o prazo corre pelo calendário, sozinho |
| Placa **reativada por termo posterior** | **5** | ali "fora da WESO" não é saída, é **ainda não instalada** (a `SWL1I23`, reativada pelo termo 8708) |

As duas entraram como guarda, com teste, e os **17 eventos inertes foram removidos** (17 clientes
recalculados). Com a regra apertada, o universo a fechar caiu de 246 para **84**.

⚠️ **E um número meu que estava inflado:** eu havia medido "549 placas com rescisão na linha do tempo". A
consulta casava placa **entre clientes diferentes**; comparando por `(cliente, placa)`, como o módulo faz,
são **246** — e **84** depois das duas guardas.

## Estado final (coorte aderente aplicada)

```
ATIVA 2.778 -> 2.763      RESCINDIDA 2.922 -> 2.937      aviso 208 (inalterado)
eventos 12.117 -> 12.132  |  fonte=weso: 15, TODAS em placa RESCINDIDA
termos 4.599 e itens inalterados  |  integrity_check ok
coortes: 347 aderentes (a de 359 menos os já resolvidos) e 132 contrato maior que o uso
sha256 de operacoes_*.py + pdf_extractor.py: IGUAL ao da manhã
```
**Backup:** `backups/fpsl.db.bak_pre_d_2026-10-14` (96 MB, `integrity_check` ok, contagens conferidas antes
de qualquer escrita).
**Placar:** as **11 suítes da CTR somam 513 verificações, 0 falhas**; `teste_barra_status` 89,
`teste_perfis` 27, `teste_tela_operacoes` 62.

### D4 — a aderência com a WESO na tela (NO AR)

**Origem:** a pergunta dele, olhando o grid: *"como assim 2778 placas ativas? isso seria baseado no que?"*.
A resposta estava fora da tela — o número é o que os **termos sustentam**, e não o que está em uso.

### O que a tela passou a mostrar
1. **Coluna "Na WESO"** ao lado de "Ativas", com o selo de aderência: *bate* (margem ±1), *contrato maior*,
   *uso maior*, *sem placa sustentada*.
2. **Chips que filtram** por "contrato bate com o uso" (347) e "contrato maior que o uso" (132), e um chip
   que diz **de quando é o dado**: *"1.643 das sustentadas estão na WESO · cache de 15h"*.
3. **Na ficha, o motivo por placa** — porque *"ativa" não distingue a placa que está rodando da que nunca
   foi instalada*: **em uso** · **saiu (rescindida)** · **nunca instalada**, mais a marca *falta assinar*.
4. **Rota nova** `GET /cliente/{cnpj}/aderencia` (owner, 401 sem token). Rotas: **17 → 18**.

### 🚨 Duas coisas que eu tive de corrigir para a tela não afirmar demais

1. **A coluna NÃO podia se chamar "Em uso".** A checagem é de **presença no cadastro da WESO**, e a presença
   é **global**: placa cadastrada na WESO de outro cliente conta aqui — é a família dos **84** achados
   "mesma placa em dois clientes". Medido na 2HM: **6 presentes** contra **2** que a auditoria apurou como
   em uso. Virou **"Na WESO"**, e o cabeçalho diz *"é presença, não instalação"*.
2. **"Sem dado da WESO" culpava a fonte errada em 252 clientes.** Eles não têm placa sustentada — não é o
   cache que falta. Virou rótulo próprio (`SEM_PLACA_SUSTENTADA`), e agora as coortes **fecham**:
   347 + 132 + 252 = **731**, com *sem dado da WESO* em **zero**.

### Custo, medido
A listagem lê o cache com uma consulta de **presença** (`chaves_do_cache`), não com a leitura caríssima da
rotina C6 — que faz uma consulta de rastreador **por veículo** porque precisa da situação de cada um. Com
isso o grid continua em **0,05–0,09 s** para as 731 linhas, 2.148 chaves da WESO lidas.
⚠️ Sem cache, `em_uso` fica **nulo** e a tela mostra "—" dizendo por quê: zero seria a afirmação falsa
"nada em uso". Cache acima do teto de 48 h faz a ficha avisar que a coluna pode estar desatualizada — a
rotina se recusa a decidir nessa situação, e a tela não pode afirmar onde a rotina recusaria.

### Conferido pelo estado
```
/painel/contratos 200, e a tela servida tem a coluna "Na WESO"
/cliente/{cnpj}/aderencia -> 401 sem token          rotas: 18
coortes: 347 aderentes + 132 contrato maior + 252 sem placa sustentada = 731
1.643 das 2.971 sustentadas estao na WESO    |    cache de 15 h
2HM: 12 ativas, 6 na WESO -> CONTRATO_MAIOR_QUE_USO
ficha da 2HM, por placa: em uso / fora com rescisao / nunca instalada
sha256 de operacoes_*.py + pdf_extractor.py: IGUAL ao da manha
```
**Placar:** as **11 suítes da CTR somam 533 verificações, 0 falhas** (tela 95, grid 78, router 68);
travas da casa verdes (89 + 27) e **Operações intacta** (62 + 35).

## O que falta na frente D
1. 🔴 **Os 84 que sobraram**, quase todos na coorte "contrato maior que o uso" (132 clientes) — pela regra
   dele, cada um pede a linha do tempo lida. **Não rodei**: é a coorte que ele mandou separar.
2. 🔴 **D4, a tela:** a aderência por cliente (sustentadas × em uso) e o motivo por placa ainda não
   aparecem no grid nem na ficha.
3. ⚠️ **150 placas em uso sem assinatura** — pela regra 2 elas ficam ativas, e o que falta é a assinatura.
   Hoje isso só aparece como achado da C6; merece ser ação na tela.

## 0.000000000000 🔵 14/10 — FPSL/C7: os PDFs assinados entram na base (motor + carga NO AR, piloto 2HM feito)

**Origem:** *"ok, agora sgia com o plano aprovado do FPSL e depois documente o feito até agora e atualize os proximos passos"*.

**Por que a frente existe:** a base tinha **0 termos com PDF guardado** (os 4.599 vieram dos CSVs da auditoria), `valor_mensal` vazio em **100%** das linhas, e **412** termos marcados `revisar` por "placas diferentes entre o PDF do Harmonit e o assinado" — a carga usou a lista do **Harmonit**, que é editada depois da assinatura.

### 🚨 `ANULA`: por que a correção precisou de uma ação nova
O motor tinha `ACOES` fechado, evento **sem `id`** e nenhuma coluna apontando evento para evento. E não havia atalho honesto: `SAI` deixaria a placa **SUBSTITUIDA** (inventa saída que não houve), `RESCINDE` deixaria **RESCINDIDA** (inventa rescisão), e `UPDATE` violaria a imutabilidade — que é o que faz "por que esta placa está ativa?" ter documento como resposta. A verdade é que a placa **nunca esteve no contrato**. Entrou `ANULA` + `corrige_evento_id` (índice único parcial contra correção dobrada), e o filtro roda **antes** das duas passadas, porque a anulação pode estar em termo que vem depois na ordem.

### 🚨 A primeira passada do piloto inseriu IDENTIFICADOR INVENTADO — e foi revertida
O extrator devolveu a **linha descritiva inteira** no lugar da placa: `Cod: 01-06 - Escavadeira Hidraulica- JohnDeere- 210G - Amarela- 1F9210GXKED520143 - 2014`, `Escavadeira PC350, Komatsu, PC350 LC-8 B10217`, `1BZ310KXJEC000130 (ID: 007842126)`, `Cod: 01-05 (ID: 205727026)`. A carga criou evento com isso **e anulou o identificador correto** (termos 2652, 2703, 3520). **Identificador inventado é pior que faltando** (regra 13, família do `RFD 2447`).
**Revertido pelo livro-razão** (`antes_json`): 11 eventos apagados, 7 PDFs removidos, e a base voltou **exatamente** a 4.599 / 12.114 / 6.812 / 0 arquivo / 795 revisar.
**Guarda que entrou:** `identificador_suspeito` recusa chave acima de 20 caracteres, pontuação de frase, 3+ espaços ou palavra escrita — e **um identificador ruim reprova o documento inteiro**, que vai para a fila. Decifrar a linha seria mexer no `pdf_extractor`, da Operações, **intocável**.

⚠️ **Segundo defeito, pego pela contagem** "5 termos com arquivo × 4 PDFs em disco": o caminho "documento só" gravava o nome **sem copiar** o arquivo — a ação "PDF" do grid responderia "está registrado como X, mas não está na pasta". Corrigido, e conferido um a um: os 5 existem e o `sha256` bate com o `hash`.

### O piloto 2HM
**A regra central, provada em produção:** os dois documentos chamados `2 - aditivo - assinado` foram para os termos **2207** e **2224**, pelo número lido **dentro** do PDF — a instrução anterior (subir como termos novos) criaria dois termos falsos.
· **anexados:** 2207, 2224, 2649, 2764 · **documento só:** 3465 (acordo, 0 placas) · **fila:** 2652, 2703, 3520 (leitura descritiva) · **`3520 cancelado` não foi nem copiado** para a VPS.
**A correção funcionou:** no 2224 entrou `FJW 0B75` e o `00D6NCCCK01011` foi anulado, com a chave da Clicksign e a autoria no texto; o evento anulado continua visível na ficha.

### 🚨 DECISÃO DELE, E ELA VALE PARA OS 412 TERMOS: a 2HM foi de 4 para 12 placas ativas
**10 das 12 ativas são do termo 2207 com `base = "assinado"`** — e o documento assinado do 2207 lista **3** placas, não 16. Ao marcar o termo como assinado, **a lista do Harmonit herdou a assinatura**. A correção automática foi recusada de propósito (13 de 16 acima da metade), então as 13 ficaram, agora como "assinadas". Do outro lado, a **rescisão 8904** (29/09/2026), que fecharia 10 delas, **não tem assinatura** — e termo sem assinatura não conta na primeira passada, pela regra dele.
**Três caminhos:**
1. **Requalificar (proposto):** correção recusada → anular os não confirmados e reinserir com `fonte=harmonit`. A placa fica no contrato e a base diz "nao assinado", que é a verdade da origem. Corrige sem apagar, com o mecanismo que já existe.
2. **Fila:** divergência grande não é anexada, e o termo não é marcado assinado.
3. **Deixar como está:** a lista do Harmonit herda a assinatura.
🛑 **Nenhum outro cliente entra antes desta decisão.**

### Conferido pelo estado
```
integrity_check ok · hash duplicado 0 · anulacao duplicada 0
estado proibido no livro-razao 0 · identificador suspeito nos eventos novos 0
5 PDFs em disco = 5 termos com arquivo; sha256 de cada um bate com o hash
sha256 de operacoes_*.py + pdf_extractor.py IGUAL ao da manha
grid e ficha concordam: 12 e 12
base: 4.599 termos · 12.117 eventos · 6.812 placas · 5 com arquivo · 796 a revisar
```
**Backup:** `backups/fpsl.db.bak_pre_c7_2026-10-14` (`integrity_check` ok antes de começar). Doc: `docs/fpsl/31_Gestao_Contratos.md` (891 linhas), com backup `.bak_pre_c7_2026-10-14`.
**Placar:** as **10 suítes da CTR somam 452 verificações, 0 falhas**; travas da casa verdes (89 + 27 + 43) e **Operações intacta** (62 + 35).

### C7/A6 e A7 — o valor e a fila na tela (NO AR, mesma rodada)

As duas frentes que **não** dependiam da decisão dos 412 termos.

### A6 — o valor: a regra ampliada que ele aprovou, e o que ela achou de verdade

Decisão dele: reconhecer `PACOTE`/`FULL MANAGER`/`Mensal` e aceitar **`Qtd` igual ao número de placas** como
preço por veículo. **Não é rateio** — rateio dividiria um total e o número sairia de nós; aqui ele sai do
documento.

🚨 **A primeira ampliação ficou LARGA DEMAIS, e isso foi medido no termo 2207 da 2HM.** Ela passou a casar
**dois** itens:

| Item do documento | Qtd | Valor | O que é |
|---|---|---|---|
| `Equipamento rastreador telemetria avançada` | 16 | **999,90** | venda do aparelho |
| `Adesão` | 16 | 299,90 | uma vez só |
| `PACOTE FULL MANAGER` | 16 | **75,26** | **a mensalidade** |

Com dois candidatos, nenhuma placa recebia valor — e, pior, sem a exclusão a cobrança poderia sair com o
preço do equipamento no lugar da mensalidade: **13× o valor certo**. Entrou `_NAO_MENSAL_RE`, que tira
adesão, taxa, equipamento, instalação, aquisição, retirada, aviso prévio, multa, ressarcimento, frete e
cadastro.

**Resultado medido nos PDFs já guardados da 2HM:**
```
2207  placas=3  itens_mensais=1  com_valor=0   (qtd 16 x 3 placas lidas -> NAO atribui)
2224  placas=1  itens_mensais=1  com_valor=1   -> FJW 0B75 = 75,26
2649  itens_mensais=0  (rescisão: só aviso prévio e taxa de retirada)
2764  itens_mensais=0
3465  tipo não reconhecido -> não lido
```
**É o primeiro `valor_mensal` da base inteira** — eram 0 de 6.462 linhas.

⚠️ **E dois defeitos encadeados, o segundo silencioso:**
1. `anexar_assinado` inseria o **evento** da placa nova e **não criava o item** — e o valor mora no item
   (decisão dele, 13/10). Então a placa que entra pelo assinado não tinha onde carregar o valor.
2. `preencher_valores` ficava **calado** nesse caso: o `UPDATE` casava 0 linhas e os dois contadores
   voltavam vazios, como se o documento não tivesse valor. Entrou o contador `sem_item` — **contador que
   esconde "não existe" é número que mente**.

### A7 — a fila da carga aparece na tela

Os documentos que a carga não encaixa viviam só no livro-razão, no banco. **Fila invisível é fila que
ninguém resolve.** Agora:
- coluna **"Na fila"** na linha do cliente, e chip com quantos clientes têm documento parado;
- ação **"Documento na fila"**, que abre a gaveta no bloco novo;
- o bloco mostra termo, arquivo, estado de origem e **por que parou**, e diz em voz alta que **nada foi
  gravado por eles** — forçar anexaria o assinado ao contrato errado;
- rota `GET /painel/api/contratos/carga/fila` (owner, 401 sem token). Rotas: **16 → 17**.

⚠️ O resumo agrupa por **tipo** de problema, e para isso tira o que é do caso: o texto citado e os números.
A primeira versão cortava no `:` — e o próprio motivo tem dois-pontos (*"a leitura devolveu 'Cod: 01-05...'"*),
então cada documento virava um grupo de um. Hoje: **3x "a leitura devolveu"**.

### Conferido pelo estado
```
/painel/contratos 200, e a tela servida tem a fila
/carga/fila -> 401 sem token
fila da 2HM: 3 documentos, todos por leitura descritiva
item do 2224: FJW 0B75 = 75,26 (lido do documento assinado)
suíte do FPSL: 63 arquivos, 2.283 verificações
```
⚠️ **Dois vermelhos, nenhum desta frente:** `teste_extrair_termo` (expurgo F7, 02/10) e
`teste_higiene_placas_weso`, que **ficou vermelho hoje** — é teste de integração contra a **WESO ao vivo** e
acusa 1 placa com espaço à direita. A CTR **não escreve na WESO**, e o próprio teste registra que a WESO
recebe cadastro por fora do FPSL. **Não investiguei a fundo nem corrigi**: o conserto escreve na WESO, o que
é fora de escopo e exige a palavra dele (há `corrigir_placas_espaco.py` no projeto, de 27/07).

### Pendências
1. 🔴 **A decisão das três opções acima** — vale para os 412 termos com placa divergente.
2. 🔴 **A fila na tela** (A7): leitura descritiva, CNPJ divergente e número ambíguo estão no livro-razão e **ainda não aparecem no grid**.
3. 🔴 **O valor** (A6): a regra ampliada que ele aprovou (`PACOTE`/`FULL MANAGER`, e `Qtd = nº de placas` como preço por veículo) **não foi implementada** — nenhum item ganhou valor no piloto.
4. ⚠️ **Medir quantos dos 2.825 caem em leitura descritiva** antes de prometer cobertura. Os 3 casos da 2HM são termos de máquina pesada, cujo layout não é o que o extrator espera.
5. 🔴 **A 2HM precisa de olho dele na tela**: 12 ativas é o que os documentos assinados sustentam, mas a WESO tem 2 em uso.
6. **Lotes seguintes** (10 clientes variados → 50 → lotes de 100) seguem o plano, **depois** da decisão.

## 0.00000000000 🔵 14/10 — MoviZap: o botão "Ficha" era recortado pelo nome do cliente (NO AR)

**Origem:** *"antes de executar o plano, veja nas ocnversar movizap, porque o botão 'Ficha' de cada conversa tem ficado invisivel"* → *"proponha limite do tamanho da exibição de nome, com a prioridade do botão não sumir. ao abrir a ficha ele aparece completo mesmo."* → *"sim"* (autorizando o build).

**O "tem ficado" era a assinatura do defeito:** ele dependia do **tamanho do nome**, e só acontecia no computador.

### O mecanismo
1. A classe `conversa__quem` servia a **dois lugares com necessidades opostas**: o item da **lista** (`CaixaDeEntrada.vue:2593`, onde cortar é o certo) e a caixa que envolve o **botão Ficha** no cabeçalho da conversa (linha 2727).
2. Uma regra **global** — escrita para a lista, ao lado de `.conversa__previa`, que só existe lá — dava `overflow:hidden; text-overflow:ellipsis; white-space:nowrap`.
3. No cabeçalho isso punha o nome (`<strong>`, inline, com a foto dentro) e o `<button>` na **mesma linha sem poder quebrar**: nome comprido empurrava o botão para fora e o `overflow:hidden` **recortava** ele.
4. **No celular não aparecia** — a media query de 860px dá `display:block` ao nome, que ganha linha própria. No computador essa linha não existe.

🚨 **Nenhum teste viu, e nem podia:** `jsdom` não calcula layout, então recorte não aparece em teste de DOM. Suíte verde e build limpo com o botão invisível — família do `M9`. **E é a segunda vez que a queixa é a tela, não a função:** em 28/08 ele disse *"não vejo mais a ficha nas conversas"* e a ficha estava lá o tempo todo.

### O conserto (só CSS; template intocado)
1. A regra de reticências passou a `.conversa__topo .conversa__quem` — **tira a origem**, que era a classe servindo a dois lugares.
2. `.conversa__cabecalho .conversa__quem` virou `flex` com `flex-wrap: wrap`.
3. O nome ganhou **`max-width: 32ch`** + reticências + `min-width: 0` (sem ele o item de flex não encolhe e o teto vira enfeite).
4. 🚨 O botão ganhou **`flex: none`** — a prioridade que ele definiu: não encolhe, não quebra, não é recortado.
5. O telefone ganhou `flex: 1 0 100%`.
6. ⚠️ A linha `display:block` da media query ficou **redundante e continua lá, anotada**: tirar linha de layout sem olhar o celular é como o defeito nasceu.

### Guarda nova
`frontend/src/ficha_visivel_1410.teste.js`, 5 verificações: falha se o seletor solto voltar, se o botão perder o `flex: none`, se o teto do nome sair, ou se o rótulo "Ficha · vincular" desaparecer. ⚠️ **Guarda de texto, não de layout** — impede a volta desta regra, não descobre a próxima.

### Conferido pelo estado
```
suíte JS      16 arquivos, 222 testes, 0 falhas
suíte Python  1.312 passando, 0 falhas
build         vite 11,49s -> index-xQKFEq-3.css
CSS servido   ZERO regra de recorte em `.conversa__quem` solto
              (sobram min-width/flex da media query e overflow-wrap, que não recortam)
porta 8008    index.html 200 · CSS 200 · JS 200, e a regra do botão está no CSS entregue
```
**Backups:** `CaixaDeEntrada.vue.bak_pre_ficha_2026-10-14` (5.560 linhas conferidas), `frontend/dist.bak_pre_ficha_2026-10-14`, `docs/05_Frontend.md.bak_pre_ficha_2026-10-14`. Documentado em `docs/05_Frontend.md`.

### Pendências
1. 🔴 **Ele validar no navegador**, em três casos: nome curto, **nome longo** (o que falhava) e conversa **sem cadastro** (`Ficha · vincular`, 61% das conversas) — mais uma passada no celular.
2. Se o celular estiver bem, sai a linha redundante da media query de 860px.
3. ⚠️ **A lição que vale para as outras telas:** classe de layout reusada em dois contextos é defeito à espera de acontecer. Vale varrer `conversa__*` e `cartao__*` procurando a mesma reutilização — **sugestão minha, não demanda dele**.

## 0.0000000000 🔵 14/10 — FPSL/CTR_1.2: a tela de Contratos virou GRID, o input virou MODAL (NO AR)

**Origem:** *"a tela de gestão de contratos deverá ser para isso mesmo, então um grid para consulta intereação e etc é bem vindo, ações para contratos tbm, o modulo que inputa eles dentro da base pode ficar dentro de um modal que abre, proponha isso e use para colocar os dados dos contratos do cliente 2h"* → *"se tiver outras coisas para subir junto, ja apriveta o reinicio"*.

**Por que mudou.** A `CTR_1.1` nasceu com a tela certa para *entrar* termo e errada para *consultar* contrato: assistente de 4 passos, consulta num campo de CNPJ no rodapé e **nenhuma rota de listagem** — só `GET /cliente/{cnpj}`. Com 731 clientes na base, abrir a aba não respondia a pergunta que ela existe para responder.

### Decisões dele, 14/10
| # | Decisão |
|---|---|
| 1 | Escopo: **grid + modal + piloto 2HM**; fases futuras escritas, sem código |
| 2 | **Clicksign continua SÓ LEITURA** — assinar segue fora do FPSL. A trava "não escreve na Clicksign" fica |
| 3 | **Valor mensal vem do termo**, relendo o PDF — não do Harmonit nem da WESO |
| 4 | Ações obrigatórias: **confirmar quem SAI** numa troca e **ver os achados** do cliente |

### 🚨 O achado que mais importa: `/gravar` duplicaria o termo no primeiro upload do piloto
A carga gravou os 4.599 termos **sem hash de PDF** (ela não guarda documento), e o `UNIQUE(hash)` era a única defesa do endpoint. Subir o assinado do 2649 da 2HM criaria um **segundo** termo 2649, com os eventos repetidos, e o primeiro seguiria contado em "sem assinatura" — **a tela mostraria o cliente pior por causa do próprio conserto**. Remédio: **modo anexar** (`termo_id` no `/gravar`), que faz `UPDATE` do termo existente e insere **só** o evento que falta. O evento da carga que o assinado não confirma **não se apaga**: o termo vira `revisar` com o motivo, porque evento é imutável e a carga usou a lista do Harmonit.

### Outros três defeitos que a construção pegou
1. **Cache vazio não era cache velho.** A guarda olhava `MIN(calculado_em)`; com `contrato_placa` vazia o `MIN` vem nulo e isso respondia "está em dia" — o grid desenharia **0 placas ativas nos 731 clientes** com a base cheia de eventos. Acontece num banco restaurado. Agora cache vazio **com evento na base** também é velho.
2. **Buscar "2hm" devolvia a base inteira.** O filtro extraía dígitos de qualquer texto, e o "2" casa com quase todo CNPJ. Letra procura **nome**; só texto sem letra procura CNPJ (3 dígitos no mínimo); e quando nada casa, a mesma caixa procura **placa** — comparando pela chave e **mostrando o texto**, porque `BUW8732` normaliza para `BUW8H32`, que não existe.
3. **O nome do cliente não existia em nenhuma tabela.** `contrato_termo` só tem CNPJ, a `clientes` do FPSL tem `harmonit_id`+`cnpjcpf`, e o cache da WESO cobre **304** clientes e **não tem a 2HM**. Entrou `contrato_cliente` com `nome_fonte`: nome da carga chega sanitizado (`M_ D_ G_ COMERCIO...`), e correção à mão é `manual` — **nenhuma carga a desfaz** (provado rodando o backfill duas vezes).

⚠️ **E um texto que já era FALSO antes de hoje:** a tela dizia *"Comparar com a WESO ainda não acontece aqui"* no mesmo arquivo em que o card da auditoria compara contrato × WESO desde 13/10. Era verdade na C2 e a entrega seguinte não voltou para matá-la — `M12` em ato, e **ninguém leu**. Saiu, e a suíte da tela **falha se a frase voltar**.

### O que entrou
| Arquivo | O que é |
|---|---|
| `painel/contratos_grid.py` (**novo**) | a listagem: `estado_cliente()` enum fechado, `acoes_da_linha()`, 3 agregações, busca, CSV. **Nada se grava aqui** |
| `painel/contratos_tabelas.py` | `contrato_cliente`, `contrato_revisao`, coluna `harmonit_assinado` |
| `painel/contratos_carga.py` | `importar_nomes()`, `importar_harmonit_assinado()` |
| `painel/contratos_registro.py` | `anexar_assinado()`, `candidatos_para_anexar()`, `confirmar_saida()`, `marcar_revisado()`, `definir_nome()`, `recalcular_todos()`, `termos_de_todos()` |
| `painel/contratos_leitura.py` | `valor_das_placas()` |
| `routers/contratos_router.py` | **7 rotas novas**; `/gravar` ganhou `termo_id` e `cliente_nome` |
| `frontend/contratos.html` | grid + gaveta da ficha + modal de input |
| `tests/teste_contratos_grid.py` (**novo**) | 69 verificações |

**A linha é o CLIENTE**, com motivo: a pergunta é "como está o contrato deste cliente". Termo (4.599) e placa (6.800) são detalhe e viram gaveta — termo como linha esconde o cliente, placa como linha repete o mesmo cliente em até 38 linhas. **Estado** é enum fechado (`EM_DIA` · `ATIVA_SEM_ASSINATURA` · `A_REVISAR` · `SEM_PLACA_ATIVA`) num lugar só, e é por ele que as fases futuras crescem. **As ações vêm do backend com `{ativa, motivo}`** — botão desligado mostra por quê, e o que a aba não faz **não aparece**.

### 🚨 Custo MEDIDO, não estimado
A listagem **não chama a ficha** (chamá-la 731 vezes para desenhar a primeira tela era o caminho natural e errado): **0,24 s** para as 731 linhas, e **0,29 s** para o `recalcular_todos` das 6.812 placas, que roda no máximo **uma vez por dia** — porque o aviso prévio vence pelo calendário, sem evento nenhum para disparar a conta.

### O valor: o limite é do documento, não do código
O `pdf_extractor` entrega o valor **por item de serviço** (já tratando valor riscado). **Termo com 12 placas e um item "MENSALIDADE" não diz quanto é de cada veículo.** Entra o inequívoco — uma placa + um item, ou item que nomeia a placa — e o resto fica dito na tela com a contagem de placas sem valor. **Ratear o total seria inventar número, e a CAR emitiria cobrança em cima dele.**

### Conferido pelo ESTADO, depois do restart
```
/painel/contratos 200, titulo certo, e o HTML servido E o novo (tem carregarGrid)
/clientes · /clientes.csv · /termo/{id}/saida  ->  401 sem token
rotas do router: 9 -> 16   (trava de contagem atualizada de proposito)
banco: 4.599 termos · 12.114 eventos · 6.812 placas · 6.462 itens  (IDENTICO ao de antes)
coluna harmonit_assinado criada; contrato_cliente e contrato_revisao criadas
backfill: 731 nomes · 4.598 marcas do Harmonit; rodar de novo -> 0 gravados, 0 atualizados
sha256 de operacoes_*.py + pdf_extractor.py: IGUAL antes e depois
2.770 ativas + 209 em aviso = 2.979  (o mesmo numero de 13/10)
```
**Backups:** `data/fpsl.db` → `backups/fpsl.db.bak_pre_ctr12_2026-10-14`, e cada arquivo com `.bak_pre_ctr12_2026-10-14`.

**Placar:** suíte do FPSL **61 arquivos, 2.194 verificações**; as **8 da CTR somam 360, 0 falhas**. Travas da casa verdes (`teste_barra_status` 89, `teste_perfis` 27, `teste_registro_telas` 43, `teste_roteadores_painel` 67) e **Operações intacta** (`teste_tela_operacoes` 62, `teste_aba_ponta_a_ponta` 35). ⚠️ `teste_extrair_termo` segue vermelha — expurgo F7 de 02/10, **não é desta frente**.

### A 2HM no grid, antes de subir PDF
`2HM EMPREENDIMENTOS E PARTICIPACOES LTDA` · estado `ATIVA_SEM_ASSINATURA` · **4 ativas, as 4 sem assinatura** · 20 encerradas · 14 termos (8 sem assinatura, **4 com marca "sim" do Harmonit**) · 2 a revisar · **10 achados**. Candidato para anexar o assinado do 2649: **um só** (id 15), o que o modo anexar exige.

### Pendências
1. 🔴 **Abrir `/painel/contratos` no navegador** (`M9`): grid, gaveta e modal — nenhum teste vê altura, flex, quem rola ou elemento cobrindo outro.
2. 🔴 **O piloto 2HM é ação dele:** subir os **6 PDFs da Clicksign** (2649, 2652, 2703, 2764, 3465, 3520) no modo **anexar**, e os **2 aditivos nº 2** como termos novos. **NÃO subir** o `3520 cancelado`, nem PDF do Harmonit como se fosse assinado. Eu confiro o banco e leio o diff de cada anexo.
3. 🔴 **Decisão dele, fora da tela:** os termos **255, 2207 e 2224** da 2HM estão "sim" no Harmonit e **sem nada na Clicksign**. A regra dele é "vale o assinado" — ele diz se o "sim" do Harmonit basta como lastro. É isso que decide se as 4 placas ativas continuam "sem assinatura".
4. 🚨 **Antes de qualquer tela de GERAR termo:** termo em geração tem eventos e `assinado=0`, e o motor de hoje o trataria como "não assinado" e **ainda assim marcaria a placa ATIVA** na segunda passada. `termos_do_cliente()` precisa filtrar por **ciclo** antes do primeiro rascunho; a coluna `contrato_termo.ciclo` entra em `migrar()` quando a fase chegar.
5. **Fora de escopo por escolha dele nesta rodada:** resolver os **795 "a revisar"** como fluxo próprio (333 sem PDF, 480 com placa divergente). O grid conta e permite marcar revisado; reler os **408** PDFs assinados segue tarefa própria — e é o que fecha a diferença 2.979 × 2.811.
6. **Tarefas próprias, cada uma com o OK dele:** gerar termo (não há gerador no FPSL — sem `reportlab`, `docx` ou `jinja` — e numerar/escrever no Harmonit contraria a trava de escrita) · pipeline de assinatura com cobrança de etapas (`contrato_etapa` só de inserção, laço desligado por interruptor) · leitura da Clicksign (decisão 2) · **entrega ao financeiro**, idempotente por `termo_id`, que **depende de resolver a fonte do valor por placa**.
7. 🔴 **`teste_extrair_termo`** continua esperando decisão dele: apagar a suíte ou reescrevê-la contra `/painel/api/operacoes/extrair`.

## 0.000000000 🔵 13/10 — FPSL: Gestão de Contratos (`CTR_1.1`) — **NO AR, frente inteira** (C0 a C6; carga dos 731 clientes + rotina de auditoria desligada)

**Origem:** *"localize internamente chave acesso API como cicksign"* → auditoria dos termos → *"ja temos o que precisamos para propor a aba de gestão de contratos no FPSL"* → *"revalide o plano e proponha passos e etapas para ele, conforme a metodologia e sem perder o que ja funciona no FPSL"* → *"siga e depois documente tudo"*. Decisões dele em 13/10: carga histórica **entra**, Instituto **entra como origem**, valor mensal **fica no contrato**, acesso **"somente eu, como padrão owner inicial para FPSL"**.

**Por que a aba existe.** A auditoria de 13/10 mediu, nas **1.930 placas da WESO**: 1.351 com termo assinado no próprio cliente, 151 só com termo sem assinatura, 124 sem termo nenhum, **48 rescindidas há mais de 90 dias e ainda em uso**, 23 de cliente sem termo. No caminho inverso, **1.005 placas assinadas não estão na WESO**. Hoje o contrato vive em PDF do Harmonit **editado depois de assinado**, com troca de placa anotada em texto livre.

**Spec:** `docs/fpsl/31_Gestao_Contratos.md` (388 linhas), com a parte que mais importa — *"O que a construção achou, e a spec não previa"*.

### O que está pronto (local, 172 verificações em 5 suítes, 0 falhas)
1. **Motor** (`painel/contratos_eventos.py`) — lógica pura, sem I/O: entra termo, sai a situação de cada placa. Duas passadas, porque "vale o assinado" **tem exceção**.
2. **Tabelas** (`painel/contratos_tabelas.py`) — 4 tabelas `contrato_*` em módulo próprio, para o gancho no `storage.py` ser **uma linha**.
3. **Leitura** (`painel/contratos_leitura.py`) — converte o que o `pdf_extractor` devolve em eventos. **Só lê** o extrator, como a `operacoes_extracao` já faz.
4. **Gravação e ficha** (`painel/contratos_registro.py`) — núcleo síncrono (testável em memória), superfície assíncrona no padrão do `storage.py`.
5. **Rotas** (`painel/routers/contratos_router.py`) — `/perfis` `/extrair` `/conferir` `/gravar` `/cliente/{cnpj}`.
6. **Tela** (`frontend/contratos.html`) — 4 passos + ficha do cliente.

### 🚨 Os três achados que contrariaram a spec
1. **O extrator já resolve o "a definir", e melhor que a auditoria.** Ele troca "A DEFINIR" por `A_DEFINIR_<termo>` e sugere o apelido `TERMO:<termo>` — **e isso explica os veículos `TERMO 8396`/`TERMO 7096` da WESO: são vagas esperando placa, criadas pelo próprio FPSL.** A auditoria procurava a expressão no texto e casava "a definição" das cláusulas: 22 placas dadas por assinadas sem estarem.
2. **A troca diz quem ENTRA, nunca quem SAI.** Na Maxi Confort 8872 a cadeia dava **11 placas** onde a auditoria conferiu **10**: a anotação nomeia só a placa nova, e no PDF do Harmonit as duas ficam no mesmo item, sem posição. ⚠️ **Eu havia escrito um teste que validava o errado como certo** (alimentei o `SAI` à mão). Remédio pela regra 13: a tela **pede** quem sai, a saída fica gravada com a autoria, e sem confirmação o termo grava marcado `a_revisar`.
3. **A anotação de troca só existe na versão do Harmonit** — conferido nos dois PDFs. É isso que sustenta a regra dele: ela é **posterior** à assinatura. Por isso `/extrair` aceita as **duas** versões e dá **400** se forem de termos diferentes.

### O que os testes pegaram antes de chegar à tela
1. `ativas()` devolvia a chave normalizada: `BUW8732` sairia como **`BUW8H32`**, placa que não existe — a família do `RFD 2447`.
2. A observação "entrou pela troca" era posta em **todas** as placas do termo, inclusive nas assinadas: a ficha mentia sobre a origem.
3. `prepararGravacao` ficou **definida e nunca chamada** — o passo 4 não aparecia. `py_compile` não lê JS.
4. O texto *"Nada é gravado nesta etapa"* **ficou falso** quando a C3 trouxe a gravação (`M12` em ato).
5. `PASTA_PDF` era constante congelada no import: o teste gravaria na pasta de dados **de verdade**. Virou `pasta_pdf()`.
6. E uma melhor do que eu havia pensado: o `hash` do PDF é UNIQUE no banco **todo**, então **o mesmo documento não entra em dois clientes** — proteção contra os 33 documentos que a auditoria achou com CNPJ divergente.

### ✅ C4 no ar (13/10 19:03) — conferido pelo estado
`/painel/contratos` **200** com o título certo · API **401 sem token** (a aba é só do owner) · as 5 rotas no OpenAPI · as 4 tabelas criadas pelo `init_db` · registro com **13 telas ativas, 11 no menu, concedíveis ainda 5** · não-owner **com todas as abas** não acessa · journal sem traceback. Backups na VPS em `*.bak_pre_ctr_2026-10-13`, e `diff` contra eles prova que **nenhuma linha foi perdida**. Suíte do FPSL: **58 arquivos, 2.006 verificações**.

### 🚨 Duas armadilhas da casa dispararam no caminho
1. **As travas de contagem estavam VERMELHAS desde 06/10 e ninguém olhou.** A baseline, antes de eu tocar em nada, já reprovava `teste_perfis` ("9 telas", real 10) e `teste_barra_status` ("11 páginas", real 12): a **FIN_2.1** nasceu no menu sem atualizar os dois números. As duas saem com **`exit=1`** — a trava funcionou e o placar denunciou por 7 dias. **Quem falhou foi a leitura do placar.** Agora em 11 e 13.
2. **Teste que bate por HTTP não vê o disco.** Antes do restart, 3 suítes reprovaram e eu quase julguei a mudança por elas. Depois do `systemctl --user restart fpsl-weso`: 43/43, 27/27, 89/89.

⚠️ **E uma leitura errada que eu quase reportei:** comparei dois `grep` com padrões diferentes e achei que o deploy tinha derrubado linhas do `main.py`. O `diff` contra o backup mostrou só as 3 adições. A pergunta que eu fiz tinha resposta fácil; a que importava era outra — a forma do `M15`.

### ✅ C5 — carga histórica NO AR (13/10)
**731 clientes, 4.599 termos, 12.114 eventos, 6.812 placas, 6.462 itens.** Rodou em **0,6 s**, porque **não releu PDF**: a auditoria já leu os 4.266 documentos, e o `exportar_para_ctr.py` traduziu os CSVs dela num JSONL (`data/carga/carga_ctr_2026-10-13.jsonl`). Tudo entra com **`origem="carga"`**, sem PDF e sem hash — nunca se confunde com o que subiu pela tela. 🚨 **Sem hash, a chave contra duplicata é `(cnpj, numero, empresa)`**: sem ela, rodar duas vezes dobraria 12.114 eventos. A empresa entra na chave porque **o número do termo repete entre Instituto e Movisat** (a JLM tem dois `5029`). Suite do FPSL agora: **59 arquivos, 2.030 verificações**.

### 🚨 OS NÚMEROS DA FICHA NÃO BATEM COM A PLANILHA — leia antes de comparar amanhã
| | Placas sustentadas |
|---|---|
| **CTR (ficha)** | **2.979** = 2.770 ativas + 209 em aviso prévio |
| Planilha da auditoria | 2.811 |

**126 clientes divergem, e cada direção tem causa própria:**
1. **CTR tem MAIS (209 placas): o aviso prévio conta.** Sua regra: rescisão assinada há até 90 dias ainda pode estar em uso. A planilha deixava o aviso prévio em arquivo separado e **não** somava. Ex.: XOMV (Mundivox) CTR 81 × planilha 11 — as 70 vieram do termo **8802**, assinado dentro dos 90 dias. **Aqui o CTR está certo e a planilha subcontava.**
2. **CTR tem MENOS: a carga usa a lista de placas do HARMONIT.** A planilha lia **o PDF assinado**; a carga usa a lista do Harmonit com a *marca* de assinatura. Nos **408 termos** com "placas diferentes" (PDF editado depois de assinado), numa rescisão o CTR **rescinde mais** do que o assinado manda. Ex.: L Orsa Modas — o ressarcimento 2624 lista 22 placas no Harmonit e menos no assinado; CTR 9 × planilha 29.

⚠️ **É limitação da carga rápida, não regra** — e em vez de esconder, ficou **visível**: os **480** termos afetados (408 × as duas empresas) foram marcados `a_revisar` com o motivo escrito, e a ficha mostra em "Termos a revisar". **Total a revisar: 795** (333 sem PDF, 480 placas divergentes, ~30 tipo não reconhecido, 5 substituição sem par). Fechar de verdade = reler o PDF assinado desses 408 e lançar evento de correção (evento é imutável; corrigir é acrescentar). **Tarefa própria.**

Conferido contra a auditoria num cliente de controle: a **2HM** dá as mesmas 4 máquinas (`ASC100`, `B10217`, `B32635`, `BW212D-40`) que a planilha apurou à mão.

### ✅ C6 — rotina de auditoria NO AR, e **DESLIGADA** (13/10)
`services/contratos_auditoria.py` compara o que os termos sustentam com o que está em uso na WESO. **Aponta, nunca corrige** — não escreve no Harmonit, na WESO nem na Clicksign. 🚨 **Interruptor na própria tela** (convenção do FPSL, oposta à do MoviZap): a `FIN_1.1` ficou desligada de 02/10 a 08/10 e nada na tela dizia. Confirmado depois do restart: `contratos_auditoria_ativa = false`. Tranca do PUT = `requer_aba("config")`, igual à da FIN_1.1. ⚠️ **Ligar não faz rodar na hora** (o laço relê a flag a cada 6 h) — e a tela diz isso; para já existe o "Rodar agora".

**Lê o cache da WESO** (`/home/claude/weso_cache/weso.db`, cron 04:15) em modo **somente leitura**, porque a base ao vivo deu de 15,6 s a TIMEOUT em 18/08. 🚨 **Acima de 48 h ela NÃO roda e diz por quê**: cache velho acusaria "em uso sem contrato" para placa retirada ontem.

**Primeira rodada real (cache de 18 h, 0,5 s): 1.931 veículos, 2.438 achados.**
| Tipo | Qtde |
|---|---|
| contratada e não instalada | 1.362 |
| substituição pela metade | 364 |
| em uso sem contrato | 320 |
| encerrada e ainda em uso | 173 |
| em uso, falta assinar | 135 |
| mesma placa em dois clientes | 84 |

⚠️ **Estes números herdam a limitação da C5** (a carga usa a placa do Harmonit, não a do assinado): os 480 termos marcados `a_revisar` são os que podem gerar achado falso em "encerrada em uso" e "contratada e não instalada". **Ler a seção da C5 antes de agir sobre a lista.**

⚠️ **Dois defeitos que a construção pegou:** (1) a rodada dizia **2.146 veículos** onde a base tem **1.931** — eu contava *chaves* (o mesmo veículo entra duas vezes quando tem placa E chassi). Número inflado em tela é defeito; corrigido e travado em teste. (2) A trava de contagem de rotas do próprio router disparou na minha mudança: eram 5, a C6 fez **9**.

⚠️ **Código de frota não vira achado** (`OBD 2`, `EGP 05`, `TERMO 8396`, `MOVEL 13`): não são placa, e acusá-los encheria a tela de ruído. 🚨 E a rotina **recalcula antes de comparar**, porque o aviso prévio vence pelo calendário, sem evento novo.

**Estado final: suíte do FPSL 60 arquivos, 2.073 verificações**; as 7 suítes da CTR somam **239, 0 falhas**.

### Pendências
1. 🔴 **`teste_extrair_termo` reprova desde 02/10, e NÃO é desta frente.** Ele chama `/painel/api/placas/extrair`, que o **expurgo F7** removeu junto com o `placas_router` (commit `cf16837`). O `grep` pelo que ia sair não alcançou este teste. **Decisão dele:** apagar a suíte ou reescrevê-la contra `/painel/api/operacoes/extrair`. Enquanto existir, o placar do FPSL nunca fecha verde.
2. 🔴 **Abrir `/painel/contratos` no navegador** (`M9`): nenhum teste vê altura, flex, quem rola ou elemento cobrindo outro.
3. 🔴 **Uso real:** a aba está no ar e **nunca recebeu um termo de verdade pela tela**. O que foi provado é a cadeia, com PDFs reais, em teste.
4. **`C5`** carga histórica dos 731 clientes · **`C6`** rotina de auditoria CTR × WESO × Harmonit, **nascendo desligada**, com interruptor na própria tela.
5. `transferencia_termo_novo` ficou **fora**, com o motivo escrito na tela.
6. 🟡 Sugestão minha, não decisão dele: a `CAR_1.1` (Contas a Receber) consome `contrato_item` — plano no arquivo do plano, com 6 decisões abertas (emissão no Harmonit ou Asaas, o que é "cobrança de técnico", pro rata, de onde vem o valor).

### Auditoria que originou tudo (fora do FPSL, só leitura)
Scripts e regras em **`C:\code\termos_harmonit`** (README com todas as regras dele). Resultado por cliente em `Downloads\Termos Harmonit por Cliente\` (731 clientes) e a planilha **`Downloads\Auditoria WESO x Termos.xlsx`** (3.413 linhas, 3 blocos: WESO → Clicksign → Harmonit). A chave da Clicksign está num arquivo na Área de Trabalho dele — **nunca imprimir**.

## 0.00000000 🔵 09/10 — Backup local (`C:\code\BACKUP`): espelho da mídia sem duplicar, uma conexão por lote (NO AR)

**Origem:** *"erros no backup matinal?"* → *"algum shell rodou ... e acusou conexão fechada"* → *"siga"* → *"só documente isso mesmo para proxima sessao"*.

**O que era:** a tarefa do Windows **"Backup VPS Movisat"** (`C:\code\BACKUP\puxar_backup_vps.ps1`, 08:51) foi interrompida (`0xC000013A`) e 2 `scp` caíram com "connection closed". Os backups da madrugada **na VPS** estavam todos ok (projetos 02:00, concorrentes 02:20, MoviZap 02:40, mídia 02:50, hub-fotos 03:00, MoviChat 03:30). Causa de fundo: na VPS, `midia/<dia>/` é instantâneo em hardlink (15 dias = 1,2 GB), mas o script copiava cada dia inteiro: **13,5 GB locais só de mídia, +1,2 GB/dia**, 7-14 mil `scp` por execução, de 1,5 a 2,5 h.

**O que mudou (testado ao vivo, terminou com `=== fim ===`):**
1. Nome `<sha256>.<ext>` vai **uma vez só** para `vps\midia_unica\`. Conferido: 3.637 arquivos, SHA-256 = nome em **todos**.
2. Outros nomes (hoje só `perfil/`: a foto muda sem mudar o nome, **4 casos medidos**) continuam copiados por dia em `vps\midia_dias\<dia>\`.
3. `vps\midia_manifestos\<dia>.txt` (caminho|bytes) guarda o retrato de cada dia.
4. Rede: um `tar` por `ssh` a cada lote de 400 MB, com 1 nova tentativa. A conferência continua por tamanho, arquivo a arquivo.
5. A pasta antiga `vps\midia\` não é mais alimentada; serve de semente via hardlink. Script anterior em `puxar_backup_vps.ps1.antes_2026-10-09`.
6. ⚠️ Armadilha: o .NET do PS 5.1 põe **BOM** no stdin do processo, e o 1º nome da lista chegava inválido no `tar`. Resolvido com `tr -d` do lado da VPS.

### Pendência (só com o OK dele)
1. **Apagar `C:\code\BACKUP\vps\midia\` (libera ~12 GB)** — **ainda NÃO é seguro**: os dias **22, 23 e 24/09** só existem nessa pasta (a VPS já descartou) e não foram levados para `midia_unica`/manifestos. Ordem: migrar esses 3 dias → conferir → apagar. Ele adiou em 09/10 (*"só documente"*).

## 0.0000000 🔵 08/10 — FPSL: auditoria da FIN_2.1 (Fechamento dos Técnicos) + correções A-D NO AR, demo em 09/10

**Origem:** *"audite ele e sua relação com as demais telas, amanhã vou demonstrá-lo"* → *"proponha então"* → plano aprovado (`.claude/plans/proponha-ent-o-zazzy-raven.md`). Doc: `docs/fpsl/30_Painel_Financeiro.md`, seção 08/10.

**✅ FEITO (commits `e966c6d` código, `bfeb406` doc; fpsl-weso reiniciado):**
1. **A** (achado 3): o quadro filtra por sobreposição, como o Relatório. Em produção, a semana 05–11/10 já devolve o card 12.
2. **B** (achado 2 + caso irmão): a regra passa a ser "um card ABERTO por técnico e período" (índice parcial `ux_cartao_aberto`). A migração guardada no `init_db` reconstrói a tabela preservando os ids. Cancelar e gerar de novo cria card novo; OS atrasada de card já avançado vira card complementar. Antes, os dois davam 500.
3. **C** (achado 5): o Gerar devolve `os_no_periodo`, `ignoradas_sem_tecnico`, `ignoradas_sem_conferencia` e `conferencia_ativa`, e a tela diz o que ficou de fora e se a rotina está desligada.
4. **D** (achado 7): card nasce com semáforo.
5. **Verificado:** ensaio em cópia isolada com 24 de 24 verificações. Suítes: roteadores 67, ponta a ponta 35, Operações f1–f6 406, todas com 0 falhas. Card 12 intacto depois da migração. Backup em `data/fpsl.db.bak_pre_fin21_2026-10-08`. **Clique no navegador: ele, na demo.**

**Pendências dele (mudam regra; numeração = achados abaixo):**
1. ✅ **Rotina da FIN_1.1 RELIGADA em 08/10 18:20** com o OK dele (*"pode ligá-la"*), relida no banco. Ela não roda na hora: o laço relê a chave a cada 1h (ou "Rodar agora" na tela).
2. "Aprovado análise técnica" contar como DataScope OK (achado 4).
3. O OK do Fechamento exigir Ação e Modelo (achado 6).
4. Vermelho travar o "Marcar Pago" (achado 8).
5. Travar a troca de recibo em card Pago ou Cancelado (achado 9).
6. Período pela data de finalização em vez da prevista (dados).
7. 🟡 Popover mostrar o motivo da pendência (achado 10). É sugestão minha.
8. 🟡 Cobrir `/painel/api/fechamento` na matriz `teste_roteadores_painel.py`. É sugestão minha.

**Achados da auditoria (lista original, por impacto na demo):**
1. **Rotina da FIN_1.1 DESLIGADA desde 02/10 10:55** (PUT no interruptor, conta admin, IP 201.92.110.104). Sem linha de conferência, o "Gerar Cards" ignora a OS em silêncio (`fechamento.py`, `if not conf: continue`). Religar = decisão dele, 1 clique na tela da Conferência.
2. **Cancelar → Gerar o mesmo período = erro 500** (provado na cópia): `UNIQUE(tecnico_id, periodo_inicio, periodo_fim)` em `fechamento_cartoes` conta o card cancelado. "Cancelar libera as OS" só vale para outro período.
3. **O quadro esconde card que não cabe INTEIRO no período**: `listar_cartoes_fechamento` usa `inicio >= ? AND fim <= ?`, o Relatório usa sobreposição. A tela abre na semana 05–11/10 e o card 12 (01–11/10) some.
4. **A OS 16991 fica amarela para sempre**: DataScope em "Aprovado análise técnica" conta como "ainda não finalizou" (`ESTADO_OK = "Finalizado"`), e esse é justamente o estado para onde a E4 vai mandar a OS. Depois da Ação, toda OS ficaria amarela no Fechamento.
5. Mensagem "Nada novo: todas as OS do período já estão em cards" também aparece quando o período não tem OS ou quando a OS foi ignorada por falta de conferência/técnico (`M12`).
6. "OK" do Fechamento = harmonit+datascope+weso; **ignora Ação e Modelo**, que a FIN_1.1 mostra. Card pode ficar verde com Modelo vermelho lá.
7. Card novo nasce sem semáforo (`null`) até "Iniciar Conferência" ou a rodada horária.
8. Vermelho não trava: card com recibo divergente vai até Pago.
9. Recibo pode ser trocado em card Pago/Cancelado (muda `valor_recibo` sem trilha).
10. Popover "conferência pendente" não diz o motivo (que existe em `conferencia_fechamento.detalhe`) nem leva à FIN_1.1.

**Dados (não é código):** só 9 de 546 OS têm PAGAMENTO DE TÉCNICO (653939) lançado, 7 têm KM; técnico em 188 (34%), 85 só com usuários internos. KM da 16931/16978 se perde (sem técnico). Período segue `data_previsao`, não a finalização.

**Relação com as telas:** Operações sem acoplamento (grep). Só a conta admin tem a aba `financeiro` (403 provado para Caio). A matriz `teste_roteadores_painel.py` não cobre `/painel/api/fechamento`. Menu dinâmico via `/api/me`, ok.

## 0.000000 🔵 08/10 — MoviZap: "marcar tipo" recusava número de técnico importado (NO AR)

**Origem:** *"movizap dando erro ao atribuir tipo ao numero: +5511964860020 identifique, sendo que só tem 1"*.

**Causa:** a importação de 274 técnicos (02/10 17:22) criou os contatos, mas **não ligou as conversas que já existiam** com esses números. E o vínculo só é decidido quando a conversa nasce: mensagem nova não religa. A conversa sem contato cai no "marcar tipo", que tenta criar contato, e a trava de identidade recusa porque o número já pertence ao técnico. A saída que a trava aponta ("vincule a um dos candidatos") estava quebrada para candidato sem empresa: a tela mandava `c.cliente_id || c.id`, então o id do contato ia no campo de empresa.

**Feito (com o OK dele):**
1. Tela: o candidato sem empresa vai por `contato_id` (`CaixaDeEntrada.vue`, `vincularA(clienteId, contatoId)`). 217 testes JS verdes, build no ar. **Clique não exercitado em navegador.**
2. 24 conversas ligadas ao técnico do mesmo número por `scripts/ligar_tecnicos_lote_0210.py` (usa `conversas.vincular(contato_id=)`, só age com candidato único e confere relendo o banco). Primeiro só a 52217, depois as 23 restantes, sem nenhuma falha.

**Pendências dele:**
1. **7 conversas com nome divergente, NÃO ligadas:** 12818 Conrado → Diego (Vitória), 3998 "Uberlândia Rastreadores" → Camila, 32576 "Tanaka Rastreadores" → Adriano Nobemasa, 32550 "onmonitora" → Pedro Nascimento, 12930 "Ds Áudio Parts" → Jéferson, 32603 "Eletricar" → Miler, 46834 "Upper som" → Assis. Ligar com o mesmo script se ele confirmar.
2. 🟡 **Regra nova (decisão dele):** quando o número de uma conversa sem contato passa a existir no cadastro, ligar sozinho se houver exatamente 1 candidato. Não implementado.
3. Validar no navegador o botão do candidato numa das 7 acima.

## 0.00000 🔵 07/10 — MoviZap: editada/excluída "só a ação", vazamentos do chat interno fechados, suíte 100% verde (NO AR)

**Suíte inteira: 1311 ✓, 0 falhas, 1 pulado** (3ª rodada, autorizada por ele). Backend
reiniciado e frontend publicado. Backups `*.bak_2026-10-07_rotulo` / `*.bak_2026-10-07_falhas`.

### Decisão: NÃO decifrar a edição do cliente
🔵 *"se não serve ao objetivo não vamos fazer"* · *"não há plano, apenas um ajuste de que a
mensagem foi editada ou excluída pelo usuário mesmo"*.
- **Upgrade do Evolution 2.4 descartado.** Medido: a 2.4.0 só existe como **rc1/rc2**
  (estável segue 2.3.7; o `:latest` do Docker Hub é o **mesmo digest** que rodamos), **não sobe
  o Baileys** (segue 7.0.0-rc.9), nenhuma nota fala de edição, e traz **trava de licença**
  (HTTP 503 `LICENSE_REQUIRED` até ativar).
- **Patch do Baileys (PR #2743) descartado.** Aberto, 0 de 3 aprovações, 4ª tentativa, e um
  revisor apontou risco de `getMessage` devolver conteúdo de **outra conversa**.
- **Reavaliar se:** o #2743 for mergeado (vira só subir a versão do `baileys`) ou a issue
  Evolution #2545 ganhar correção oficial.
- O plano antigo do upgrade (`Desktop/Plano_Teste_Upgrade_Evolution_Edicao_Mensagem_2026-10-07.md`)
  **não vale mais**.

### ✅ No ar
1. **Caixa — rótulo "só a ação"** (🔵 *"só a ação"*): edição do cliente mostra `· editada`
   (saiu "(texto novo ilegível)"); no clique, só *"O texto acima é o de antes da edição."*
   (mantido, senão a tela mente). Exclusão: `mensagem excluída` / revelada `excluída ·` (antes
   "apagada pelo cliente", que mentia quando quem excluiu foi o painel). Backend intocado.
2. **Chat interno — mesmo rótulo** (🔵 *"aplique o mesmo no chat interno"*): `mensagem
   excluída`, `excluída ·`, prévia da sala (dizia "sem mensagem ainda") e citação.
3. **Chat interno — dois vazamentos da regra de 05/10 fechados** (🔵 *"verifique se somente
   owner pode ver, mas isso não é preciso informar na mensagem"*):
   - **citação:** responder a uma mensagem depois apagada levava o texto dela em
     `citada_texto` para todos → `citada_apagada_em` no SELECT, zerado para quem não é owner;
   - **link do anexo:** `/api/midia/{id}` só conferia a sala, e o id é sequencial →
     `chat.midia_escondida()` responde 404 para quem não é owner.
   `teste_chat` +2 (52/52). O teste do anexo apaga a própria `midia` no `finally`:
   `midia.sala_id` **não tem cascata**, e mídia esquecida derruba a limpeza da suíte.
4. **As 6 falhas eram testes velhos, não defeito** — corrigidas só nos testes (🔵 *"aplique
   as três, carimbo na legenda é o esperado"*):
   - carimbo `*Nome:*` desligado nas fixtures de `teste_arquivo`/`teste_midia_whatsapp`
     (o carimbo tem teste próprio em `teste_envio`);
   - `teste_cadastro`: a fixture exige contato **com cliente** + `ORDER BY` (sorteava um
     contato do atendimento sem cliente — a armadilha "teste que lê produção");
   - D7 de `teste_ajustes_2708`: recorta o bloco por texto ("Não está no cadastro" →
     "Responde por") em vez de 2600 caracteres.

### Pendências (em ordem)
1. 🔵 **Ele validar no navegador:** editar e excluir do `+5518998116168` (Caixa); no chat
   interno, apagar e conferir com conta que não é owner (sem conteúdo, citação nem anexo) e
   com a dele (vê tudo).
2. ✅ **Confirm de apagar do chat interno não cita mais owner** (🔵 *"pode trocar o texto do
   confirm"*): agora *"Apagar esta mensagem? O conteúdo some para todos na sala."*
   (`ChatInterno.vue`, `apagarMensagemChat`). Build feito; bak `*.bak_2026-10-07_confirm`.
   Era o único texto visível do chat interno que citava owner.
3. 🔵 152 linhas-lixo de edição cifrada (seção de 06/10, pendência 2) — continua com ele, e o
   expurgo segue levando um dia por noite.

## 0.0000 🔵 05/10 — MOVIZAP: regra "sem dono", Entrar/selo, e jornada controla estado (TUDO NO AR)

Sessão de execução. **Tudo abaixo está NO AR** (restart `movizap.service` 09:53 +
build; restart 10:17 para o código da jornada). Suíte: backend 1287 verdes (as 2
falhas de `teste_cadastro` são a armadilha "teste que lê produção",
`+5511961369236` sem cliente — não é desta rodada; ✅ **fixture corrigida em 07/10**); `teste_presenca` 42/42;
`caixa_2309.teste.js` 25/25.

### ✅ No ar hoje

1. **Regra "sem dono" nova** (🔵 02/10, A1/A2 — *"Sem dono é quando tem mensagem do
   cliente nova não lida"*, *"respondida... não é sem dono"*): o filtro agora é
   `atendente_id IS NULL AND estado <> 'resolvida' AND última mensagem = 'entrada'`.
   **Concluída e respondida saem da aba "sem dono"** (reverte a "concluída no fim"
   de 23/09 **só na aba sem-dono**; na lista "Todas" a ordenação concluída-no-fim
   continua). Os **três** contadores alinhados: `conversas.listar` (filtro),
   `conversas.resumo` (cabeçalho da Caixa — este o plano não tinha achado) e
   `inicio.resumo` (painel). Sem migração. Testes de `teste_listagem`/`teste_concluir`
   repropostos para a regra nova.
2. **Botão "Entrar" na linha** de conversa com dono (🔵 30/09) — acompanha sem assumir;
   o backend/função já existiam desde 12/08, faltava a porta na lista
   (`CaixaDeEntrada.vue`). No `catch` do assumir **não** mexi (beco raro, decisão de
   escopo; registrado).
3. **Selo "Ir para a aberta"** na concluída que tem viva do mesmo grupo/número (🔵 30/09):
   `conversas.listar` devolve `conversa_viva_id` (subconsulta com o mesmo
   `COALESCE(grupo_jid, telefone_e164)` do `assumir`); a linha resolvida leva à viva
   em vez de oferecer reabrir (que o índice recusaria). Mata o "parece que tem duas
   conversas".
4. **Testes `_regra()` consertados** (`teste_estilo_conversa`, `teste_layout_conversa`):
   `_sem_media()` tira os blocos `@media` e a âncora `(?:^|[},])` pega a regra base —
   a guarda voltou a acusar se a propriedade sumir. (Eram as "3 falhas pré-existentes"
   que eu normalizei três vezes em 30/09.)
5. **Jornada controla o estado** (🔵 05/10 — *"estado deve reiniciar para online conforme
   horário de jornada e offline conforme término tbm"*): `presenca.aplicar_jornada()`
   por **borda** (início → `disponivel` + zera `ultima_acao_em`; fim → `offline`; owner
   "sempre online" não cai). Interruptor próprio `jornada_controla_estado`. Gancho no
   laço de 1 min **antes** da inatividade. `teste_presenca` cobre as bordas.
6. **Réguas LIGADAS** (🔵 — *"pode ligar as réguas"*): inatividade **ligada** (30 min →
   em pausa, 60 → offline) e jornada **ligada**. No restart, os 5 parados há muito
   (Claudia, Fabio, Karla, Rodrigo, Thiago) foram para **offline automático**
   (`estado_automatico=true` → voltam ao agir). Distribuição **já estava ligada** desde
   25/09 (Ludmila/Erika, 30 min) — nada a fazer.
7. **Chat interno: apagar esconde o conteúdo de TODOS, só owner vê** (🔵 05/10 — *"apagar
   mesmo e não deixar registrado o que dizia, somente ao owner deixar para ver"*). O texto
   fica no banco (para o owner), mas `chat.mensagens`/`chat.salas` **mascaram** texto,
   histórico de edição e mídia para não-owner quando `apagada_em`. A tela não mudou (o botão
   "ver o que dizia" já era condicionado a `texto || midia_id`, que ficam nulos).
   `teste_chat` +2. ⚠️ **07/10:** a citação e o link do anexo ainda vazavam — fechados (ver
   07/10, item 3). O confirm de apagar não cita mais owner (07/10).
8. **Tiques (1 risquinho) — RAIZ ACHADA e guard NO AR.** O `messages.update` chega **fora de
   ordem**; um `SERVER_ACK` atrasado depois do `READ` **rebaixava** "lida" → "enviada" num
   UPDATE cego (`_atualizar_entrega`). Era isso que travava 14.840. Guard: entrega **só
   avança** (`RANK_ENTREGA`, pendente<enviada<entregue<lida; `falhou` não rebaixa
   entregue/lida). `teste_edicao_mensagem` +3. ✅ **BACKFILL FEITO:** 3.787 corrigidas
   (2.254→lida, 1.533→entregue); as ~11 mil que sobraram só tiveram `SERVER_ACK`, corretas.
9. ✅ **Ação no chat interno E no e-mail conta como USO** (🔵 05/10) — `registrar_acao` passou
   a ser chamado no `chat_escrever`/`arquivo`/`editar`/`apagar` e no `email_enviar`
   (`main.py`). Quem está ativo no chat/e-mail não cai mais em ausente/offline por "não
   atender cliente". Reading/abrir não conta (regra "olhar não conta").
10. ✅ **Relabel "Ausente"** (ver backlog item 2) — offline automático dentro do turno deixa
   de dizer "fora do expediente".
11. ✅ **Iago (owner, id 121) entrou na lista de transferência** (`transferivel=true`) — 🔵
   *"me coloque na lista de transferência... de atendimento tbm, somente ali a mais"*. Só
   esse campo mudou; sem restart (a lista é lida ao vivo).

### ✅ Decisão de distribuição confirmada no código E no ar

🔵 *"as conversas só não podem ir a ela quando ela estiver offline mesmo, estados de
uso não impedem isso, o mesmo vale para todos"*. **Já era assim**: `presenca.pode_receber`,
`conversas.transferir` (:3043) e a herança (:3471) barram **só** `offline` (+ afastamento/
inativo/não-transferível). "em pausa"/"não perturbe"/disponível recebem, para todos.
Nada a corrigir.

### 🔴 Falta você (navegador) + backlog

1. **Validar no navegador:** Entrar numa conversa com dono real; o selo "Ir para a aberta"
   levando à viva; a aba "sem dono" **sem** concluída/respondida.
2. ✅ **Relabel do "fora do expediente" — FEITO e NO AR 05/10.** `offline` automático
   **dentro** do turno → **"Ausente"**; automático **fora** OU escolhido à mão → **"Fora do
   expediente"**; `ausente` (pausa) segue **"em pausa"**. `rotuloDoEstado(estado, {automatico,
   emJornada})` em `estado.js` (retrocompatível); backend passou a mandar `estado_automatico`
   + `em_jornada` por atendente na lista da Caixa (`conversas.listar`), no cabeçalho
   (`conversas.conversa`) e nas salas do chat (`chat.salas` via `com_estado_auto`/`com_id`);
   `operacao.em_jornada_agora(ids)` resolve o conjunto numa consulta. Verificado: os offline
   automáticos dentro do turno mostram "Ausente".
   ✅ **Toggle "A jornada controla o status" na Geral** (`Geral.vue` + `PUT /api/config/presenca`
   com `jornada_controla_estado` opcional → `presenca.definir_jornada_controla_estado`).
   ✅ **Foto no chat interno:** avatar da **sala direta** usa a foto do colega quando há
   (`chat.salas` manda `com_id`+`com_tem_foto`; `ChatInterno.vue` serve `/api/atendentes/{id}/foto`,
   cai para iniciais). ⚠️ **Falta** (parcial): avatares dos **membros do grupo** e convidáveis
   seguem com iniciais — mesma técnica, não feito ainda.
3. 🟡 **Foto no chat interno** (`ChatInterno.vue` usa iniciais; coluna `atendente.foto`
   existe): usar a foto quando houver. Verificar antes se a `foto` vem no payload das salas.
4. 🟡 **Toggle da jornada na Geral** (hoje liguei por código; falta o botão na tela).
5. ✅/🔴 **#1 tiques:** RAIZ achada (ack fora de ordem rebaixava) e **guard NO AR** (item 8
   acima). **Falta o BACKFILL** das 14.840: recalcular `entrega` a partir do MAIOR status já
   recebido no `webhook_evento` (`payload->'data'->>'keyId' = id_externo`, `->>'status'`).
   É `UPDATE` em massa (junta `webhook_evento` por keyId-texto; pesado, uma vez, talvez em
   lotes) — **espera sua palavra**. Conversa de referência: **57599** (+551934226314, Ludmila).
6. ✅ **#2 carimbo do nome do atendente — FEITO e NO AR.** Decisão dele: **toda mensagem**,
   formato **`*Nome:*`** no topo, **interruptor NASCE LIGADO** e só o owner muda (na Geral,
   CFG_7.1). Vale desde o deploy. O que vai ao cliente leva o carimbo; o que o painel GRAVA
   fica sem ele (nosso lado já mostra o autor). Áudio: o nome vai no texto que acompanha (passa
   pelo `responder`). `conversas._com_carimbo`/`_carimbo_ligado`; config `carimbo_nome_ligado`
   (ausente=ligado). `teste_envio` +3.

**Tudo o que faltava do bundle foi entregue.** Pendências menores que sobram: foto nos
avatares de **membro de grupo** no chat (só a sala direta foi feita).

## 0.000 🔵 02/10 — MOVIZAP: Técnicos importados + Encerramento com avaliação (plano)

### ✅ Feito nesta sessão

1. ✅ **297 técnicos importados** — 274 criados, 23 atualizados (nome → `Nome | Região`,
   tipo → `tecnico`). Fonte: `Desktop\TÉCNICOS2708262.xlsx` (305 linhas, 301 únicos).
   Scripts: `importar_tecnicos.py`, `extrair_json.py`, `resolver_pendencias.py`.
2. ✅ **Auditoria do encerramento**: `encerrar()` não envia mensagem, 0 avaliações, 0
   classificações, `avaliacao_ativa = false`, interruptor travado na Geral. Colunas
   `avaliacao`, `avaliacao_pedida_em`, `avaliacao_comentario` existem na `conversa` mas
   nunca foram preenchidas. CHECK atual: `avaliacao BETWEEN 1 AND 5`.
3. 🔵 **Plano de encerramento + avaliação proposto** — 6 blocos, 16 decisões, aprovado
   para documentar. Pedido dele: *"proponha os planos por tipo de ação e ordem enumerada"*.

### 🔴 Decisões para alinhar — a próxima sessão começa por aqui

🔵 Todas do pedido dele em 02/10 (*"proponha"*). Cada uma traz proposta minha (🟡).

1. **Mensagens editáveis ou fixas?** As 3 mensagens (nota, despedida, comentário).
   🟡 Editáveis: 3 campos na Geral, só visíveis com o interruptor ligado. Motivo: ele
   já sabe o texto, mas pode querer mudar sem deploy.

2. **Cliente responde algo que não é 0 nem 1?** (ex: "obrigado", "3").
   🟡 Fecha como `resolvida` sem nota. Mensagem já gravada na conversa, não se perde.
   A próxima mensagem dele abre conversa nova normalmente.

3. **Ludmila/Erika por id ou configurável?** Atendentes da regra de 30 min.
   🟡 Dois campos na Geral: "Atendente principal da fila" e "Atendente reserva".
   Troca sem deploy.

4. **"Fora do horário" para conversa sem dono — qual horário?**
   🟡 Horário global (campo de/até + dias na Geral), não jornada individual. Conversa
   sem dono não tem "dono com jornada".

5. **48h sem cliente: vale com dono também?**
   🟡 Sim, encerra mesmo com dono. Se o cliente sumiu, a conversa trava a fila do
   atendente. Ele reabre se precisar.

6. **Mensagem de 48h editável?**
   🟡 Sim, campo + interruptor na Geral, igual à de fora de expediente.

**Decididas sem precisar validar:** janela de 24h ✓ · exportar depois ✓ · grid só com
nota ✓ · última msg de entrada define "sem dono" ✓ · modal diz "no Histórico" ✓ ·
disponível = dentro da jornada ✓ · 30 min desde a última entrada ✓ · fim de semana segue
jornada ✓ · mesma msg da Presença ✓ · 48h desde a nossa última saída ✓

### Plano de execução — 3 fases, por M3 (uma tarefa) e M16 (backend primeiro)

**Fase A — Redefinir "sem dono"** (filtro, sem migração, menor risco)

| # | O quê | Camada | Origem |
|---|-------|--------|--------|
| A1 | `sem_dono` = sem atendente + última msg é de `entrada` (cliente esperando) | backend `listar()` | 🔵 *"Sem dono é quando tem mensagem do cliente nova não lida"* |
| A2 | Conversa respondida sem dono = "Todas", **não** "sem dono" | backend `listar()` | 🔵 *"conversas respondidas, ou sem agente + sem mensagem não lida, não é sem dono"* |
| A3 | Contador "X sem dono" reflete a nova regra | backend + frontend | 🔵 |
| A4 | Texto do modal pós-conclusão: "está no Histórico" (não "sem dono") | frontend | 🟡 |

**Fase B — Encerrar + avaliação do cliente** (migração + feature principal)

| # | O quê | Camada | Origem |
|---|-------|--------|--------|
| B1 | Migração: estado `avaliando`, CHECK `avaliacao BETWEEN 0 AND 1`, configs | banco | 🟡 |
| B2 | `encerrar()` envia msgs A+B, muda para `avaliando` (quando ligado) | backend | 🔵 *"Ao clicar em conclui, deve aparecer essa mensagem"* |
| B3 | Interceptador em `_gravar_mensagem`: msg em `avaliando` → nota/comentário | backend | 🟡 |
| B4 | Vigia: `avaliando` há 24h → `resolvida` sem nota | backend | 🟡 |
| B5 | Destravar interruptor `avaliacao_ativa` na Geral + campos de mensagem | frontend | 🔵 |
| B6 | Tela `Avaliacoes.vue` (grid, owner-only) em Configurações | frontend | 🔵 *"a nota dele deve ficar registrada em um grid na aba 'Avaliação'"* |

**Fase C — Automações da fila** (vigia periódico)

| # | O quê | Camada | Origem |
|---|-------|--------|--------|
| C1 | Fora de expediente: cobrir conversa sem dono (ajustar `fora_do_expediente()`) | backend | 🔵 *"Caso tenha mensagem fora do expediente, mensagem 3"* |
| C2 | 30 min sem resposta → Ludmila, fallback Erika, 08:00 retorna | backend + vigia | 🔵 *"regra de 30min sem mensagem nossa, cai para Ludmila"* |
| C3 | 48h sem cliente → msg 2 + encerrar automaticamente | backend + vigia | 🔵 *"caso o cliente fique sem retornar em 48hras, item 2"* |
| C4 | Campos na Geral: atendente principal/reserva, msg/interruptor 48h | frontend | 🟡 |

**Dentro de cada fase:** migração → backend → suíte → frontend → build → validar com ele.
**Entre fases:** a anterior validada antes de começar a próxima.

### Mensagens do encerramento (verbatim dele, 02/10)

| Id | Quando | Texto | Origem |
|----|--------|-------|--------|
| A | Ao concluir | "Diga-nos como nos saímos.\nBasta enviar:\n1 se você estiver satisfeito;\n0 se poderíamos fazer melhor;" | 🔵 |
| B | Logo após A | "A Movisat agradece seu contato!\nCaso precisar estaremos a disposição!\nGratidão ❤️" | 🔵 |
| C | Após 0 do cliente | "Lamentamos. Pode nos dizer o que poderíamos ter feito melhor?" | 🟡 |

### Estado `avaliando` — o desenho (🟡)

**Objetivo:** capturar a nota do cliente sem abrir conversa nova.
**Hoje:** `encerrar()` → `resolvida` → próxima msg abre conversa nova (índice parcial).
**Por quê:** `ux_conversa_aberta` (`WHERE estado <> 'resolvida'`) impede duplicata.
`avaliando ≠ resolvida` → o índice mantém a conversa, a resposta do cliente cai nela.
`avaliando` não aparece na Caixa (tratado como concluído para a lista), aparece no
Histórico.
**Reavaliar se:** clientes enviarem respostas fora do padrão em volume (medir depois de ligar).

### Onde cada coisa mora no painel

| Tela | O que ganha |
|------|-------------|
| **Geral** (CFG_7.1) | Interruptor de avaliação (destrava o existente) + campos A/B/C + atendente principal/reserva + msg 48h + interruptor 48h |
| **Avaliação** (nova, owner) | Grid: data, contato, atendente, nota 0/1, comentário |
| **Presença** | Nada novo — msg fora de expediente já está lá |
| **Caixa de Entrada** | Modal Concluir atualizado + filtro "sem dono" com nova regra |
| **Histórico** | Coluna de avaliação (0/1) |

### ⚠️ Riscos medidos pela metodologia

- **M3** — são 6 mudanças; por isso 3 fases com validação entre elas.
- **M16** — backend primeiro, frontend por último, build é publicação.
- **M2** — antes de alterar o CHECK de `avaliacao`: grep por quem lê a coluna.
  Antes de adicionar `avaliando` ao estado: grep por todo `estado` em `conversas.py`
  (há 50+ referências — auditar cada uma).
- **M12** — a Geral diz *"A avaliação ainda não existe no atendimento"*: quando existir,
  matar o texto.
- **M15** — verificar que `avaliando` não quebra nenhuma query que assuma apenas os 5
  estados atuais (`nova`, `bot`, `fila`, `humano`, `resolvida`).

## 0.000 🔵 06/10 — MoviZap: edição do cliente aparece como "editada" — NO AR

🔵 *"conversa +554998354793, as 11:29 ela editou uma mensagem, por que não
aparece"* · *"se chegam duas mensagens depois que edita [...] podemos pensar em
algo do lado de cá"*.

**Causa medida:** edição de CLIENTE nunca chega legível. Chega um
`messages.upsert` com `secretEncryptedMessage` (`secretEncType` 2 = edição de
mensagem) e `targetMessageKey.id` = a mensagem editada. **94 de 94 eventos desde
07/08 eram assim, com o original no banco nos 94**, e viravam linha-lixo
"[mensagem cifrada...]". O `MESSAGES_EDITED` da Evolution só traz ruído interno.

**No ar (06/10, Nível 1 — escolha dele):**
- `conversas._marcar_edicao_cifrada`: marca `editada_em` no original (hora da
  edição), não cria linha, não toca `conteudo`; `conteudo_original` fica NULL
- Tela (M12): o selo vira **"editada (texto novo ilegível)"** e, ao clicar,
  explica que o texto do balão é o de antes da edição. ⚠️ **07/10: virou só `editada`**
  (decisão dele, "só a ação") — ver a seção de 07/10
- Sem alvo, ou `secretEncType` ≠ 2: segue o aviso de 17/09
- Teste `teste_edicao_cifrada.py` (6). Suíte 1304 ✓ + as 5 falhas antigas
- Backfill **só no número de teste** (decisão dele): 3 linhas
  (`scripts/backfill_edicao_cifrada.py`, roda em leitura sem `--aplicar`)
- Também no ar: `MESSAGES_EDITED` assinado e tratado como `messages.edited`
  (era `messages.edit`, nome errado — nunca casou)

**Pendências deste assunto:**
1. ⏳ **Validação ao vivo.** Em 06/10 ele viu as 3 mensagens corrigidas pelo
   backfill (*"parece que deu certo"*), mas nenhuma edição NOVA chegou depois do
   deploy (21:28): o caminho ao vivo ainda não rodou com evento real. Falta:
   editar no +5518998116168 → selo "editada" (texto de 07/10), sem linha nova
2. ⏳ **Decisão dele, com prazo:** restam **152 linhas-lixo** em conversas reais
   (medido 06/10 ~21:40), incluindo a da conversa que abriu o assunto
   (+5549998354793, msg 80892). Só **91** ainda têm o evento bruto que diz qual
   mensagem foi editada (de 08/09 em diante). As **61** mais antigas (07/08–07/09)
   perderam o evento no expurgo de 30 dias (`expurgar_webhook.py`, 04:35) e não
   dão para corrigir. **A cada madrugada o expurgo leva mais um dia das 91.**
   Mesmo script, sem o filtro do número
3. ~~🟡 Nível 2 (decifrar o texto novo)~~ — ❌ **descartado por ele em 07/10** (*"se não
   serve ao objetivo não vamos fazer"*). Reavaliar só se o Baileys #2743 for mergeado
4. 🟡 Edição legível seguida de edição cifrada na mesma mensagem mostraria "antes:" da 1ª — raro, não tratado

## 0.000 🔵 06/10 — FPSL: Fechamento de Contas dos Técnicos (FIN_2.1) — NO AR

🔵 Aba nova no FPSL: apura quanto pagar a cada técnico de campo com base nas OS
em **"Serviço Realizado"** (15694), conferidas pela rotina E1-E3.

**No ar (06/10):**
- **Backend:** 3 tabelas (`tecnicos`, `fechamento_cartoes`, `fechamento_os`) +
  coluna `tecnicos_json` em `os_historico` + 2 services (`sync_tecnicos.py`,
  `fechamento.py`) + 1 router (`fechamento_router.py`) + 9 endpoints REST
- **Frontend:** `fechamento_tecnicos.html` — kanban 5 colunas por estado
  (Aberto/Conferência/Preparado/Pagamento/Pago), coluna "Pago" colapsada por
  padrão (histórico acessível), popover no semáforo com lista de OS e pendências,
  seletor de período, filtro por técnico, modal de recibo, download de planilha CSV
- **Rotinas ocultas:** sync de técnicos (diária, 170 reais vs 9 excluídos — 2
  camadas: ID×ObterUsuarios + email×painel_usuarios) + atualização de semáforo
  (horária, relê conferência)
- **IDs medidos ao vivo na OS 16991:** `PAGAMENTO DE TECNICO` = 653939,
  `KM DESLOCAMENTO` = 6971
- **Permissão:** `requer_aba("financeiro")` — mesma da Conferência. Registro em
  `telas.py` como `FIN_2.1`
- **Maquina de estados:** aberto → conferência → preparado → pagamento → pago
- **Semáforo:** verde = OK · amarelo = conferência pendente · vermelho = valor
  do recibo diverge do calculado
- **Correção no deploy:** `data_previsao` no banco vem `dd/mm/yyyy`, a query
  comparava com ISO `yyyy-mm-dd` — corrigido com `substr` no SQL

✅ **VALIDADO POR USO — medido em 23/10.** `fechamento_os` tem **4 registros**:
a OS de teste **16991** (07/10 18:31) e **três OS reais** lançadas em **22/10
13:18** — `17001`, `17010` e `17015`. O fluxo foi percorrido com dado de
produção, não com a OS de teste. **Deixou de ser pendência.**

### 🔵 07/10 — Pass de UX/UI NO AR (commit `e11f8b7`, fpsl-weso reiniciado)

Pedido dele depois de usar a tela ("as etapas fazem algo ou é só visual?"):

1. ✅ **"Iniciar Conferência" deixou de mentir** (`M12`): a transição
   `aberto → conferencia` agora recalcula o semáforo (relê a conferência de cada
   OS), igual ao "Marcar Preparado". As etapas pagamento/pago seguem só andando o
   card de coluna — é o andamento humano, não ação no Harmonit/DataScope/WESO.
2. ✅ **Feedback de ação**: spinner no botão + rótulo ("Conferindo…"), e o card
   que muda de coluna ganha destaque de 1,4s (a coluna de destino abre sozinha).
   Downloads com spinner. Padrão da casa, não overlay bloqueante.
3. ✅ **Miniatura + modal**: card na coluna vira miniatura; clique abre modal
   largo com Calculado × Recibo lado a lado (divergência em vermelho), tabela de
   OS inteira e divergências destacadas; ações da etapa no rodapé.
4. ✅ **Busca de técnico por nome OU e-mail** (combobox): o e-mail já vinha do
   `ObterTecnicos`, agora é gravado (coluna `email` em `tecnicos`, migração) e o
   sync populou **170/170 reais**.

Verificado isolado (migração, round-trip, `avancar_estado`, condição do router) +
`node --check`. Suítes vivas: roteadores 67, ponta-a-ponta 35, `operacoes_f*` 406,
**0 falhas** — Operações intacta. ✅ **VALIDADO POR USO — medido em 23/10:**
`operacoes_lote` tem **136 lotes** e `operacoes_passo` **939 passos**, o último
em **22/10 20:31**. **Deixou de ser pendência.**

### 🔵 07/10 (tarde) — Trava de OS, cancelamento, registro permanente e relatórios NO AR (commit `4277f60`)

🚨 **Bug achado nos logs:** ele levou o card até **pago** (gravou, 15:31:31) e às
15:31:39 clicou **"Gerar Cards" de novo** → o `gerar_cartoes` apagava+recriava por
técnico+período e **destruiu o card pago**, voltando a "aberto". Era o "zerou e
voltou ao início".

1. ✅ **"Gerar Cards" não apaga mais nada** — só completa o card 'aberto' com OS
   livres e recalcula; reclicar é idempotente.
2. ✅ **Trava de OS** — OS num card ativo (estado ≠ cancelado) some do pool;
   regerar a mesma semana traz **0 OS**. (Decisão dele: trava dura, não "avisar".)
3. ✅ **Cancelar pagamento** — estado novo **"Cancelado"** (fica no histórico, com
   quem/quando) e **libera as OS**; botão no modal, em qualquer estado inclusive
   pago; sai do kanban, aparece no Relatório.
4. ✅ **Registro permanente** — o card é durável + auditoria `pago_em/por`,
   `cancelado_em/por` (grava quem via `requer_aba`).
5. ✅ **Relatórios** — aba na própria tela, filtros período/técnico/OS/estado,
   tabela expansível por OS, totais, **Exportar CSV** (`GET /relatorio[/planilha]`).

⚠️ **Decisão dele pendente:** a baixa da OS é **local** (consumo no Fechamento).
**Não** escreve no Harmonit — isso é a frente **E4 "Ação"** (gated, pode colidir
com a rotina de Operações). Se ele quiser a baixa real no Harmonit, planejar à parte.

Verificado isolado (trava consome/libera, auditoria, relatório, endpoints) +
`node --check`. Suítes vivas 67+35+406, **0 falhas**. ✅ **VALIDADO POR USO —
medido em 23/10:** o `fechamento_os` recebeu **3 OS reais em 22/10 13:18**
(17001, 17010, 17015), ou seja, o fluxo rodou com dado de produção depois
desta entrega. O card 12 (aberto, OS 16991) ficou em produção como estava.

**O que pode vir depois (nenhum implementado):**
1. Gerar cards semanais automaticamente (rotina)
2. Resumo financeiro por período (totais por técnico)
3. Filtro por semáforo na tela
4. 🔵 Baixa da OS no Harmonit ao pagar (frente E4, decisão dele)

## 0.000 🔵 01/10 — FPSL: Painel de Fechamentos (Conferência + Ação) e o expurgo das telas velhas

🛑 **REGRA NOVA DELE, ACIMA DE TUDO:** *"Aba de Operações deve permanecer 100%
integra acima de tudo. Se algo mexer nela, pare e avalie corretamente o caminho
a seguir"*. **Os testes da Operações contam como "mexer".**

**No ar hoje (cinco entregas):** **E1** · **E1b** (interruptor) · **ordenação**
pela data real de finalização · **E2** (sub-aba "ID × modelo": ação 2 · vínculo 1 ·
modelo 16 divergentes em 199 OS) · **E3** (a Conferência de Fechamento agora só
lista OS com oficina em **"Serviço Realizado"**, **últimos 30 dias**, com a WESO
ao vivo). 🔴 **A ROTINA ESTÁ LIGADA** desde ~19:00 de 01/10 (pedido dele): roda a
cada hora, 1ª automática ~20:00, e só escreve no banco local. Suíte: **827
verificações em 15 testes, 0 falhas**. Doc: `docs/fpsl/30_` (619 linhas).
**Sem commit**, vai no autocommit 23:30.

**O que falta, na ordem que ele aprovou** (detalhe na `30_` e em
[[project_fpsl_painel_financeiro]]):

1. 🔵 **E4** — Ação manual: `change_state` → 74341 "Aprovado análise técnica".
   ⏸️ **spec fechada, pausada por ele** (01/10) para fazer o expurgo primeiro.
   Decisões no plano e na `30_`: ideal = "Aprovado análise técnica"; "Finalizado"
   conta como OK e não se mexe; qualquer outro estado se ajusta; **só "Serviço
   Realizado" libera o botão** (conferência vira informativa). Lacuna: a tabela
   `datascope_respostas` não guarda o `code` que o `change_state` exige — a E4
   resolve. Escreve no DataScope: só na sandbox até ele ligar
2. ~~E2, E3~~ ✅
3. 🔵 **S0** (medir na sandbox) → **E5** corrigir modelo na OS
4. 🔵 **Expurgo = F7**: ✅ **X1 FEITA 02/10** (Operação intacta, 51 arquivos OK,
   tag `pre-expurgo-x1-2026-10-02`). Falta a **X2** — parte `os_router`, apaga os
   2 HTML velhos + `equipamentos` + `weso_lookup` + tabela `cadastro_placas_log`,
   edita testes da Operação. **Só com o OK dele sobre a lista de edições**
5. 🟡 33 pendências `desistiu` na rotina de Operações (19 rescisões)
6. 🟡 8 formulários do DataScope nunca olhados

**⏳ Validação no navegador (só ele):** a sub-aba "ID × modelo" fica no
**Histórico de OS**, não na Conferência (ele procurou na Conferência em 01/10 e
não achou — não é bug, o servidor entrega a sub-aba lá; Ctrl+F5 se cache). E o
interruptor + colunas da Conferência de Fechamento.

**Dúvidas 1 a 13: TODAS fechadas por ele em 01/10, nada esperando resposta.** A
11 virou verificação e **confirmou o que ele disse**: a Operações não usa nada de
código velho. A 13: ele lançou 3 linhas de oficina na sandbox 16991, mas **sem
operação real na WESO** — então ela serve para os caminhos cinza/vermelho, e o
verde se testa com OS reais (16962/16961).

⚠️ Armadilhas desta frente: **a ação esperada vem do `problema`, não do `tipo`**
(medido em 197 OS — ele estava certo e eu o corrigi errado) · modelo se compara
por **id de produto**, e **`eh_rastreador()` não serve** (falha em 9 das 24
descrições) · situação da WESO **não é binária** (Bancada, Manutenção…) · a
**E5 pode colidir com a rotina da Operações** e duplicar material · `assign_id`
do DataScope **não é** a OS · `form_state` não volta a `null` · 429 sem
`Retry-After` · **não rodar `seed_modelos_produto.py`** · teste que escreve só na
sandbox OS 16991 / `TESTE_DATASCOPE`.

🚨 **Fim de linha:** `os_scan_router.py` é **CRLF** no git (único do FPSL). Editar
pelo Windows e normalizar para LF gerou um diff de 416 linhas para uma mudança de
2. Conferir com `git show HEAD:<arq> | file -` antes de devolver
([[feedback_scp_windows]]).

## 0.000 🔵 30/09 — WESO write-once, `assumir` de grupo, e a busca da Caixa

Três frentes, e **duas do mesmo defeito**: coluna de grupo esquecida em código
escrito para conversa direta. Apareceu no `assumir` e na busca, no mesmo dia.

### 🚨 FPSL/WESO — `tipoCliente` e `cnpjcpf` são WRITE-ONCE (NO AR desde 10:32)

Nasceu de *"a função de cadastrar cliente na weso não está cadastrando CNPJ"*.
O CNPJ **estava** sendo gravado; faltava o `tipoCliente`, e a investigação achou
uma limitação maior: **`/Clientes/Atualizar` não grava nenhum dos dois** e
responde `"Cliente atualizado com sucesso."` — cinco variantes testadas
(string e ID numérico, por `cliente_id` e por `cnpjcpf`, e os dois juntos),
nenhuma gravou. Vale até para preencher um `cnpjcpf` **nulo**. A doc do
fornecedor afirma o contrário, e foi corrigida. Detalhe em
`fpsl_weso/docs/fpsl/10_Inconsistencias.md` § **B13**.

Consequência: cliente que nasce `NaoInformado` **só se conserta na tela da
WESO**, e é trocar o tipo lá que apaga o CNPJ. Foi assim que o **13690 (MAXI
CONFORT)** ficou sem documento e derrubou 6 tentativas de lote entre 14 e 16/09.
**Ele mesmo resolveu**, digitando `20480457000158` na tela em 30/09 — plano e
tipo sobreviveram.

- ✅ `_tipo_pessoa` no `operacoes_router.py` deriva o tipo pelo **tamanho** do
  documento (11 = `Fisica`, 14 = `Juridica`, `None` fora disso — por tamanho,
  nunca `isdigit()`, que o CNPJ novo tem letra). Coberto no
  `tests/teste_operacoes_f2.py` (96 verificações, 0 falhas).
- ✅ **NO AR em 30/09 10:32:47** (PID 1472370, porta 8004, sem erro no
  arranque). Conferido por releitura, não pelo código de saída: o serviço
  iniciou **depois** do `mtime` do arquivo, e `_tipo_pessoa` responde certo nos
  quatro casos dentro do processo novo — 14 dígitos → `Juridica`, 11 →
  `Fisica`, o CNPJ novo alfanumérico → `Juridica`, tamanho 13 → `None`.
- ✅ **Passivo: FICA COMO ESTÁ — decisão dele em 30/09** (*"deixe como está
  elimine a demanda"*). **IAGO SANTOS (13634)** e **GSV (13679)** seguem
  `NaoInformado` com documento intacto, e não existe conserto por API: as duas
  saídas eram mexer na tela (o que apaga o CNPJ) ou apagar e recriar
  (destrutivo, têm plano e placas). **Não voltar como pergunta.** O único
  cuidado que sobra: ninguém trocar o tipo deles na tela da WESO.

### ✅ MOVIZAP — `assumir` em grupo devolvia 500 (NO AR desde 09:49)

A guarda comparava só `telefone_e164`, que é **NULL em grupo**, e o índice é
`(canal_id, COALESCE(grupo_jid, telefone_e164))`. A trava passava batido e o
`UPDATE` estourava `UniqueViolation` na cara do atendente. **4 conversas de
grupo** estavam nesse estado. Agora devolve 409 dizendo qual é a conversa viva.
Zero `ux_conversa_aberta` no log desde o reinício.

⚠️ O docstring descrevia o índice **sem** o `COALESCE` — foi ele que guiou o
código errado, e foi corrigido junto.

### ✅ MOVIZAP — a busca da Caixa (ATD_1.1), NO AR desde 10:22

Nasceu de *"quando busco por x3tech, por exemplo, não muda muita coisa"*. Dois
defeitos medidos, nenhum era o que eu supus primeiro:

1. **`grupo_nome` não estava na busca.** Das 15 conversas de grupo, **14 têm
   `grupo_nome` e ZERO têm `nome_whatsapp`** — a única coluna olhada. Buscar
   `Tecnofrota` devolvia **0** existindo 2 grupos com esse nome.
2. **Um dígito solto arrastava a base.** `x3tech` tem o `3`, virava
   `telefone_e164 LIKE '%3%'` e devolvia **100** — o teto da lista. *Era isto
   que ele estava vendo.* Agora pedaço de telefone só vale em termo **sem
   letra** e com ≥ 3 dígitos; `6168` continua achando.

| termo | antes | depois |
|---|---|---|
| `x3tech` | 100 (o teto) | **2** — os dois grupos |
| `Tecnofrota` | 0 | **2** |
| `weso` | 10, sendo 6 só menções | **4** — os grupos |

🔵 E o filtro ganhou as três seções que ele pediu (*"abas de opção como
Contato; Grupos // Se é na conversa ou nome // e os tipos em um grupo de
'Tipos'"*): **Buscar em** (`Nome, telefone e empresa` · `O que foi dito na
conversa`), **Onde** (`Tudo` · `Contatos` · `Grupos`) e **Tipos** (os chips que
já existiam).

- ⚠️ **`O que foi dito` NASCE DESLIGADO**, decisão dele. Era ele que trazia
  volume sem relação com o termo. A nota interna **continua** buscável (decisão
  de 12/08) — com o interruptor ligado.
- 🚨 **"Onde" é FILTRO, NÃO ABA:** a 027 criou aba separada de grupo e a 028
  desfez. Chip não reabre aquilo.
- Suíte: **1285 passando, 3 falhas pré-existentes** (conferidas contra o backup
  da Vue, não são desta rodada). Documentado em `docs/06_Conteudo_das_Telas.md`.

### ✅ Nada em aberto nesta rodada

1. ✅ `fpsl-weso` reiniciado em 30/09 10:32:47, com autorização explícita dele.
2. ✅ Busca validada por ele no navegador.
3. ✅ Entrada no grupo validada no banco (ver abaixo).
4. ✅ Passivo do IAGO/GSV fechado por decisão dele.

⚠️ **O que NÃO foi exercitado por mim:** a tela da Caixa num navegador. Validei
por rota (`openapi.json`), por bundle publicado e pela suíte — quem clicou foi
ele. O `entrar` no grupo, idem: provei no banco, não no botão.

### 🔵 `entrar` × `assumir` — o mecanismo funciona, a tela é que não oferece

Observação dele em 30/09: *"Se o grupo já está aberto e com alguém, não deve
ter reabrir e assumir, deveria entrar pelo botão de entrar pois está em
andamento"*. Está certo, e o mecanismo existe (`conversa_participante`,
migração 021 — o "acompanhar").

✅ **Provado no ar em 30/09 10:24:32:** ele entrou na **#55760** como
participante e o **Thiago continuou dono** — o comportamento correto, acompanhar
sem tirar de quem atende. E não é caminho morto: Erika (28/09) e Ludmila
(29/09) já entraram e saíram dessa mesma conversa.

🔴 **O que falta é a TELA.** Em conversa com dono ela só oferece "assumir", que
responde *"já foi assumida por X"* — beco sem saída, quando a ação certa
(entrar) existe e funciona. Ele chegou lá por outro caminho, não pelo botão.

E o que ele notou junto: *"porque parece que tem duas conversas então?"* —
porque **tem quatro**. O modelo é **uma linha por atendimento**, não por
contato: o grupo "Suporte Movisat -> Weso" tem 3 encerradas e 1 aberta, com
nome idêntico na lista, e **nada diz qual é a viva**. Esse é o defeito de UX
real, e não foi tocado.

### 🔴 O PLANO ORDENADO — próxima sessão começa por aqui

✅ **05/10: 1º (os dois `_regra()`), 2º (doc), 3º (botão `entrar`) e 4º (selo da
conversa viva) FEITOS e NO AR** — ver o bloco de 05/10 no topo. Sobra desta lista
só o "FORA DA FILA" (agrupar conversas do mesmo grupo na busca), que continua
opção, e o "DESCARTADO".

Ordenado por criticidade com a regra `M` que sustenta cada posição (pedido dele
em 30/09: *"ordene as propostas em ordem de criticidade e conforme a
metodologia"*). Os dois primeiros são **teste e doc**, não vão ao ar.

**1º — consertar os dois `_regra()`** (`teste_estilo_conversa.py:104` e
`teste_layout_conversa.py:45`). ⚠️ **Não é teste vermelho, é a suíte mentindo.**
O produto está CERTO nos dois casos; os testes leem a regra CSS errada:

- `teste_estilo_conversa._regra()` não tem âncora de linha, então
  `.balao__acoes` casa dentro de `.balao--tocado .balao__acoes` (linha 4433,
  num `@media`), que vem antes da regra base (5039). A base **tem**
  `opacity: 0; pointer-events: none`.
- `teste_layout_conversa._regra()` tem âncora, mas `^\s*` aceita indentação:
  casa com `.coluna--larga > .gaveta` de dentro do `@media` (4419, só
  `max-height: 60vh`) em vez da regra real (4941, `max-height: 42vh;
  overflow-y: auto`). O `overflow-y` **desce pela cascata** — não falta nada.

🚨 **Dois guardas estão mortos:** se alguém tirar o `pointer-events: none`
amanhã, o placar fica idêntico ao de hoje. Zero sinal. E eu normalizei isso
como "3 falhas pré-existentes" três vezes em 30/09 sem abrir.

- **`M2`** — "grep e suíte, nesta ordem". Suíte com vermelho normalizado não
  serve como o "antes" de nada.
- **`M13`** — "varredura lê a tela, não o seletor. Seletor é suposição minha
  sobre onde a coisa está." É exatamente o defeito, aplicado a teste.
- **`M9`** — "placar verde não vê layout". Aqui não vê nem a si mesmo.
- **`M3`** — é **uma** tarefa, não duas: o mesmo defeito em dois arquivos.

🟡 Correção proposta: `_regra()` devolve a **união de todas as regras que
casam**, modelando a cascata (é o que as asserções querem saber: "esta
propriedade vale para este elemento?"). Alternativa mais estreita: ignorar
blocos `@media` e testar base e celular separadamente — mais preciso, mais
código.

**2º — ✅ FEITO em 30/09:** as 4 colunas da migração 060 no
`docs/02_Modelo_Dados.md`, e o `§ Reabrir` do `06_Conteudo_das_Telas.md`, que
descrevia o índice **sem o `COALESCE`** — a mesma descrição errada que guiou o
defeito no código. `teste_modelo_documentado` passou a 35/35.

**3º — o botão `entrar`** em conversa com dono (detalhe na subseção acima).
- **`M6`** — "'já é assim' se mede": medido, `conversa_participante` funciona.
- **`M5`** — verificado antes de recomendar.
- **`M14` + `M16`** — mexe em template: build entra na conferência, e build é
  publicação (backend primeiro, frontend por último).

**4º — marcar qual é a conversa viva.** Selo na linha encerrada cujo
grupo/número tem outra aberta, que **leva até ela** no clique. Usa o mesmo
`COALESCE(grupo_jid, telefone_e164)` do `assumir` — nenhuma consulta nova.
Depois do 3º porque é orientação, não beco sem saída.

**FORA DA FILA — agrupar conversas do mesmo grupo na busca** (uma linha +
`+3 atendimentos anteriores`). **`M7`**: "trava mede uso, não palavra" — não
medi ninguém buscando grupo com atendimentos repetidos. Sem esse número,
construir agrupamento de listagem é decidir por palavra. Fica como opção.

**DESCARTADO — confiar na ordem por atividade.** É o que existia até 30/09, e
falhou com ele.

### 🚫 DESCARTADO — o "selo de por que casou" era sugestão minha, e redundante

Eu propus um selo dizendo por que cada linha casou (`no nome` / `na mensagem` /
`no telefone`). Ele perguntou de onde vinha aquilo (*"5 de onde veio isso?"*) e
a resposta é: **de mim, e sem eu ter conferido o código.**

🚨 **Já existe.** `_trechos_achados()` em `conversas.py:1166`, com o docstring
*"O trecho que fez cada conversa casar, para a lista dizer POR QUÊ"*. Propor
construir isso é o mesmo padrão da rodada de achabilidade de 28/08: a função
está lá, eu não procurei.

🚨 **E a parte que eu acrescentaria contraria uma decisão deliberada** que está
escrita no código (`conversas.py:1446`): *"O TRECHO SÓ APARECE QUANDO O NOME NÃO
EXPLICA O ACERTO. Buscar 'iago' e ver a linha da conversa do Iago trocar a
prévia por um pedaço de mensagem é ruído."* Selo no nome e no telefone é
exatamente esse ruído.

**Não é "para depois", é descartado.** Não reabrir.

## 0.00 🔵 MOVIZAP — 25/09: jornada de 3 planos, OS TRÊS NO AR

Plano completo, com origem item a item, decisões no formato de 4 linhas e
as regras M aplicadas: `C:\Users\Lenovo\.claude\plans\vamos-discutir-sobre-o-breezy-flame.md`.
Ordem **1 → 2 → 3**; cada um publicado (com a palavra dele), validado e
documentado antes do próximo.

| # | Plano | O essencial | Estado |
|---|---|---|---|
| 1 | Atendentes e Times | interruptor Ativo/Inativo no lugar do Desligar · owner invisível para o admin · sem máximo de conversas · afastamento com saída/volta automáticas · a pessoa encerra o seu na Minha conta · estados travados quando afastada · aba Time da Caixa com filtro por time | **NO AR 25/09 10:47** (055 + 056). Falta **ele validar**: inativar e reativar alguém, marcar um afastamento, a aba Time com filtro |
| 2 | Notificações | lida só quando vista · não tocar pela conversa à vista · balão do Windows (nome + trecho) · contagem sem teto | **NO AR 25/09 10:57** (sem migração). Falta **ele validar**: ativar o aviso na CFG_11.1 e receber com o painel minimizado. ⚠️ a distribuição para a Ludmila segue desligada: é ele quem liga |
| 3 | Mensagens rápidas | Padrões / Minhas notas / Formulários (links), apelido, botão redondo no compositor, 3 variáveis; Chat interno com Notas e Formulários; áudio + texto em duas mensagens | **NO AR 25/09 11:12** (057). Falta **ele**: criar os primeiros Padrões (a tabela nasce vazia) e **provar áudio + texto num envio real** para `+5518998116168` |

**ORDEM DA TARDE (aprovada 25/09):** Rodada 0 (agente na área de trabalho, modo simular) → Rodada 1 (backend do Plano 5 + `destination` fora do webhook, um reinício; troca do segredo na hora dele) → Rodada 2 (Plano 4 inteiro, uma suíte completa e um build) → Rodada 3 (Claudia, e o que depende de uso). Detalhe no arquivo do plano.
- ✅ **Rodada 1 no ar (25/09, 14:31):**
  - migração 059 (`agente_ligacao`, `ligacao`, `ligacao_gravacao`, `atendente.ramal`);
  - rotas `/api/ligacoes/agente/{enviar,batimento}` (chave no cabeçalho, só o hash no banco);
  - `/home/claude/movizap_ligacoes` no backup noturno;
  - agente v0.2 **instalado no PC dele**: tarefa 12:00/17:30 (1ª execução pela tarefa às 14:34, resultado 0);
  - **24 ligações e 18 gravações na VPS**, hash conferido dos dois lados, 2ª passada = 0 envios;
  - **alerta no Claude Code** (gancho `SessionStart` + `scripts/agentes_mudos.py`), provado com um agente de teste mudo há 25 h;
  - **segurança:** `destination` fora do `webhook_evento` (código + 54.009 linhas limpas, 1 validada antes).
  - **Falta:** 🔴 **trocar o segredo do webhook** (hora dele; os dumps dos últimos 14 dias ainda o têm); o PC da **Claudia** (atendente 124): gerar a chave dela e instalar.
- ✅ **Plano 5.1 (25/09, 15:44), a porta própria do agente** (🔵 *"uma saída segura que poderia ter o nginx específico para não misturar outro"*; decisões dele: mTLS porque há PC fora do escritório, processo próprio e `ligacoesmicrosip.movisat.com.br`):
  - **no ar:**
    - migração **060** (`cert_sha256`, `cert_validade`, `ultimo_ip`, `ultimo_aviso`);
    - serviço `--user movizap-ligacoes` em `127.0.0.1:8010` (`movizap/app_ligacoes.py`), que confere chave + certificado do mesmo agente;
    - a CA em `/home/claude/movizap_ligacoes_ca` (0600, fora do backup);
    - `scripts/cert_agente_ligacao.py`;
    - o alerta também mostra AVISO de PC vivo e certificado vencendo;
    - **18 testes verdes** (8 + 10 novos);
    - nginx **fase 1** (porta 80 + certificado HTTPS emitido);
    - `docs/ligacoes.md`, o fluxo documentado.
  - **no PC dele:**
    - agente **v0.3** instalado (tarefa 12:00, 17:30 e ao entrar +5 min);
    - batimento às 15:46;
    - certificado emitido (agente 17, até 24/09/2028).
    - Ensaio local antes: 6 casos de ini, 5 modos de VPS falsa, trava e mTLS contra servidor local. Achou **2 defeitos do plano**: `certreq -accept` recusa CA própria, e `WebRequestHandler` não carrega. Ambos corrigidos.
  - **Falta, na ordem:**
    1. ✅ **nginx fase 2** (rodada por ele como root; a checagem de segurança barrou a execução por mim). Sem certificado dá 400, e o painel segue em 200;
    2. ✅ **PC dele concluído às 16:02**: banco com v0.3, IP `177.24.34.118` e certificado amarrado; o serviço 8010 registrou `POST /agente/batimento 200`; sem pedido pendente no cofre;
    3. ✅ **Kit de replicação (Plano 5.2, 25/09)** (🔵 *"o procedimento para que eu replique a Claudia e aos demais ... a pasta com os arquivos necessários e o manual .md"*): `Desktop\MoviZap-Ligacoes-Kit`, com `MANUAL.md` de 9 passos, casos do dia a dia, problemas e inventário dos 11 atendentes.
       - Ferramentas no PC dele, **sem o Claude**: Preparar, Assinar e Conferir, por `ssh vps`, sobre `scripts/agentes_ligacao.py` (somente leitura).
       - Testado com um atendente de teste, ciclo completo, e tudo apagado no fim.
       - O teste pegou 2 defeitos: o `ConvertFrom-Json` do PS 5.1 embrulha a lista; e o `ssh` engolia o "N" da confirmação. Corrigidos com `ssh -n` e confirmação que só aceita "S".
       - A pasta `MoviZap-Ligacoes-Claudia` saiu, porque o kit a substitui. **Claudia na semana que vem, pelo kit.**
    4. tirar as rotas antigas do painel, junto do reinício do Plano 4.
  - Manual das etapas: `Desktop\MoviZap-Ligacoes\MANUAL.txt`.
- ✅ **Rodada 0 entregue:** `Desktop\MoviZap-Ligacoes\` (`movizap-ligacoes.ps1` v0.1, `Testar (simular).cmd`, `LEIA-ME.txt`). Lê o histórico pelo `winsqlite3.dll` do Windows, sem trazer nada de fora. Simulado no PC dele: 24 ligações, 18 gravações todas casadas (2 ligações com a gravação partida em dois arquivos), 4,4 MB. **Esperando o teste dele.**

**Celular: Caixa de entrada e Chat interno (verificação de 25/09, só leitura)** (🔵 *"verifique a compatibilidade do movizap somente para chat interno e externo via navegador mobile, os mesmos recursos, porém somente os chats"*).
- **Como foi medido:** prévia Playwright em 390x844 com toque (Chromium; sem WebKit instalado), frontend atual copiado em `/tmp`, API simulada; fotos em `/tmp/mz_previa_mobile`.
- **Resultado: nenhuma das duas telas é usável no celular hoje.**
  1. **Caixa:** lista e conversa ficam empilhadas na mesma tela, e as mensagens somem numa faixa de cerca de 30 px entre os botões do cabeçalho e o campo de escrever. O campo passa do fim da tela (867 > 844 px).
  2. **Caixa:** as ações do balão (reagir, citar, editar, apagar) só aparecem com o mouse em cima; no toque, 0 visíveis.
  3. **Chat interno:** não tem regra para tela estreita; duas colunas de 103 e 177 px, sem nome nas conversas, e a sala não abriu com o toque.
  4. **As duas:** o menu lateral ocupa 62 px dos 390, e há alvos de toque abaixo de 40 px (5 na lista, 32 com a conversa aberta).
  5. **Voz:** o áudio é sempre rotulado `audio/ogg`, mas o iPhone grava MP4/AAC. **A medir** num envio real pelo iPhone.
- ✅ **MODO CELULAR NO AR (25/09, 17:22)**, com a palavra dele (*"pode sim"*); o computador não mudou.
  - **O que entrou:**
    - `BarraCelular.vue` (Caixa, Chat interno, Sair);
    - lista **ou** conversa, com Voltar e o voltar do aparelho;
    - o botão "Ações" na Caixa;
    - ações do balão por toque;
    - `/chat?sala=` na URL;
    - alvos de 44 px;
    - `dvh`;
    - rótulo MP4 do áudio do iPhone.
  - **Provado na prévia:** o fluxo inteiro em 390 px, 0 erros de JavaScript, 209 testes JS verdes, e o computador idêntico em 1280 px.
  - **Falta ele:** testar no celular real, inclusive o **áudio pelo iPhone** para `+5518998116168`, e o celular deitado.

**Plano 4 — NO AR EM 28/09** (migração 061). Plano completo em `C:\Users\Lenovo\.claude\plans\vamos-discutir-sobre-o-breezy-flame.md`; detalhe do que entrou em `docs/06_Conteudo_das_Telas.md`, seção 28/09, e na memória [[project_movizap_editar_e_anexos]].

| # | O quê | Estado | Origem |
|---|---|---|---|
| F | Distribuição para a Ludmila em 30 min | ✅ no ar 25/09, 11:38 | 🔵 |
| A | Nota interna editável/apagável, sem janela de tempo | ✅ no ar 28/09 — reaproveitou as colunas que a Caixa já tinha, sem migração nova | 🔵 |
| B | Chat interno: editar (15 min) e apagar (48 h) a própria mensagem | ✅ no ar 28/09, migração 061 | 🔵 |
| C | Até 10 anexos por envio, texto na 1ª, 25 MB cada | ✅ no ar 28/09, Caixa e Chat interno | 🔵 |
| G | Chat interno com o visual da Caixa + tiques de leitura | ✅ no ar 28/09, junto com o B | 🔵 |
| S | Rotacionar o segredo do webhook da Evolution | ✅ feito 28/09, zero downtime, tráfego real conferido antes e depois | 🔵 |
| E | Edição de cliente que chega cifrada | ✅ **resolvida sem construir**: "marcar o resto" já era o rótulo genérico existente; "ler o que der" (decifrar em grupo via HKDF) é criptografia real, não virou código — fica achado registrado. **06/10: marca de edição no ar** (seção 0.000 de 06/10) | 🔵 |
| D | Prova real do teto de 25 MB (PDF, vídeo, imagem e lote) para `+5518998116168` | **falta ele testar** | 🔵 |

Já feito em 25/09, fora dos planos: os 43 resumos "por decisão do owner" corrigidos
no banco (43/43 relidos) e 9 textos de tela sem "owner" (no ar às 09:28).

**29/09 — clicar na citação vai até a origem + Chat interno ganha citar + mídia clicável.**
🔵 Pedido dele (*"quando respondemos uma mensagem e clicamos nela e vamos pra
de origem... e no chat interno tbm e abrir as midias do chat interno, que
hoje só aparecem"*). Migração **062**. Detalhe em [[project_movizap_citacoes_e_midia]].

| # | O quê | Estado | Origem |
|---|---|---|---|
| A | Caixa: clicar na citação do balão rola até a original e destaca | ✅ no ar 29/09, sem migração (reaproveita a busca) | 🔵 |
| B | Chat interno: "responder citando" (não existia) + clicar vai até a origem | ✅ no ar 29/09, migração 062 | 🔵 |
| C | Chat interno: imagem abre em tela cheia ao clicar | ✅ no ar 29/09, mesmo modal da Caixa | 🔵 |

✅ **VALIDADO POR USO — medido em 23/10.** Citar virou hábito, não teste:
**2.934 mensagens citadas na Caixa** (a última em **23/10 15:57**) e **359 no
Chat interno** (a última em **23/10 14:55**). ⚠️ A **imagem em tela cheia** (C)
não deixa registro no banco — segue sem prova, mas é o mesmo modal da Caixa,
que está em uso diário. Suíte 1270/1273 (as 3 falhas são as
mesmas pré-existentes de sempre).

### 🚨 28/09: login Google casava pelo `sub`, não pelo e-mail — achado no ar, sem código

O Thiago reportou erro de login e mensagens assinadas como "Caio". Causa: a
conta Google do Workspace foi **reaproveitada** (e-mail trocado de `caio@`
para `thiago@`; o `sub`, código interno da conta, não muda). O login casava
primeiro pelo `sub`, então o Thiago sempre caía no atendente do Caio —
quando o Caio foi desativado, ele ficou barrado com a conta própria ativa.

🔴 **Decisão dele: sem mudança de código.** *"não é uma correção, pois não
há mais problema"* — pela LGPD, e-mail e chave de dados não se reciclam; ele
vai orientar a equipe a não reaproveitar conta do Workspace. Conserto foi só
de dado: `google_sub` apagado da conta antiga (28686), e as 5 mensagens de
hoje de manhã (08:03–08:17, ids 69439–69450) passadas para a conta certa
(62440). Detalhe e o script de diagnóstico: [[reference_login_google_sub]].

🚨 **Se acontecer de novo: AVISAR ELE ANTES DE AGIR.** Não apagar `google_sub`,
não mexer em cadastro, não reatribuir mensagem sem a palavra dele — regra
dele, 28/09.

### ✅ 28/09: jornada, mensagem de fim de expediente e times

- **Jornada 08:00–18:00, segunda a sexta**, montada para os 10 atendentes
  ativos (admin ajusta quem precisar). Continua **desligada** na Geral.
- **Texto da mensagem de fim de expediente gravado** (o dele, verbatim —
  "Horário de Atendimento… EQUIPE MOVISAT"). Continua **desligada**.
- **Revisão dos 7 times:** nenhum membro inativo. 🟡 Achado: **Relison não
  está em nenhum time** — decisão dele se corrige.
- **Auditoria rápida da Caixa:** sem outro caso de carimbo trocado, além do
  do Thiago (já resolvido acima).

### Dívida de documentação — fechada em 28/09

`docs/06` (seção do modo celular + seção do Plano 4 de 28/09),
`project_movizap_ligacoes.md` (memória nova) e `MEMORY.md` atualizados.
Segue faltando, baixa prioridade: reescrever `project_movizap_ux_conversa.md`
(desatualizada desde 18/09, ninguém usa para nada ativo agora).

## 0.0 🔵 MOVIZAP — 24/09: três entregas no ar, e o que depende de você

No ar em 24/09 (09:49, 10:25, 13:24) · commit **`34dc762`** (empurrado pelo
autocommit das 23:30, com a trava de segredo) · migrações **051, 052, 053** ·
detalhe em `docs/06` (fim) e `docs/02`. Suíte completa 1185 verdes às 10h;
depois só testes direcionados (teto de 2 por sessão).

**Já feito, sem nada seu:** 43 conversas paradas há mais de 1 dia foram para
a Ludmila (conferidas 43 de 43) · auditoria de 8 pontos com 4 achados
corrigidos (e-mail único, herdeiro offline, ajuda de atalhos, tela do
afastamento).

| # | O quê | Quem | Origem |
|---|---|---|---|
| **1** | **Validar no painel com o seu login:** Atendentes (modal, clicar fora pergunta, jornada com copiar) · Times (marcar membros) · promover um admin e ver o menu dele · Minha conta (nome, "Sempre online") · Transferir para alguém offline (a sua frase aparece) | você | 🔵 |
| **2** | **Ligar quando quiser, na Geral** (tudo nasceu desligado): jornada → regra de status (15/60 min) → mensagem de fim de expediente (escrever o texto) → distribuição (Ludmila, reserva Erika, 10 min). **Antes, montar as jornadas** em Atendentes — hoje ninguém tem | você | 🔵 |
| **3** | **Escolher quem será admin**, em Atendentes › Editar › Perfil | você | 🔵 |
| **4** | ✅ **Notificações no ar (24/09, 16:13, `c155875`)** — Configurações › Notificações; contador em Minhas e Time. Falta **você ouvir**: abrir o painel, clicar uma vez (o navegador exige), e testar o som | você | 🔵 |
| **5** | ✅ Regra de status com **Ausente em 30 min** gravada (Offline 60); **continua desligada** — ligar na Geral | você | 🔵 |

**Decisões suas em aberto (MoviZap), em ordem:**

| # | Decisão | Opções | Origem |
|---|---|---|---|
| D1 | Jornada de todos 08:00–18:00 | só seg–sex ou sábado também? com almoço? eu monto e ligo, ou você no painel? | 🔵 |
| D2 | Texto da mensagem de fim de expediente | a tela está pronta; falta o texto | 🔵 |
| D3 | Itens de UX (a–i) | emoji · rascunho · galeria · fixar · silenciar grupo · info do grupo · digitando · marcar lida. Sugestão minha: b, f primeiro. **Respostas rápidas saiu daqui: virou o Plano 3 (🔵, 25/09)** | 🟡 |
| D4 | Evolution: fixar a versão 2.3.7 | sim ou não (evita um `pull` trazer a 2.4.0, que exige licença). **Medido 07/10:** a 2.4.0 ainda é só rc e o `:latest` hoje é o mesmo digest da 2.3.7 — o risco só aparece quando a 2.4 virar estável | 🟡 |
| D5 | **S20** — script **revisado e testado em cópia, NÃO aplicado** (`/home/claude/scripts/preparados/aplicar_s20_rate_limit_google.sh`) | aplicar em 29/09 ou antes (precisa `vps-root`) | 🔵 |
| D6 | Pausados | quando retomar Histórico/Informativos, Classificar/avaliação, Calendar, IA | 🔵 |

