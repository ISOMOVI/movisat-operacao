# 03 — Painel rápido

**Padrão criado em 2026-08-05**, no quadro *Comercial Interno × Externo*.

Um **painel rápido** é um quadro compartilhado por link, sem login, para
acompanhar um punhado de tarefas entre poucas pessoas. Nasce em minutos, vive
enquanto o assunto durar, e some sem deixar dívida.

> **O segundo painel rápido é uma LINHA no banco, não um projeto novo.**
> Se alguém estiver copiando código para fazer outro, parou de ser um painel
> rápido.

---

## 1. Quando usar — e quando não

| Use quando | Não use quando |
|---|---|
| poucas dezenas de tarefas, poucas pessoas | precisa de histórico auditável |
| todo mundo pode ver tudo | tem informação que só alguns podem ver |
| o assunto tem fim | vira processo permanente da empresa |
| a fila é simples: um depois do outro | as dependências formam grafo, não fila |

🚨 **Não tem login.** Quem tem o link escreve. Isso é a virtude e o limite:
serve para acompanhamento interno, **nunca** para dado de cliente, valor ou
qualquer coisa cujo vazamento importe.

## 2. Duas vistas, um motor só

O campo `demanda_quadro.modo` escolhe **como o quadro é desenhado**. Os dados,
as travas, o cadastro de pessoas e as regras são os mesmos.

| Vista | Cara | Boa para |
|---|---|---|
| `esteira` | cards horizontais em raia, um por assunto | acompanhar de quem é a vez |
| `planilha` | tabela Nº · Prazo · Tarefa · Responsável · Status | cronograma, muitas linhas, leitura rápida |

**Na esteira** a cor do card é da pessoa da vez. **Na planilha** o que colore é
o **status**, e a coluna Prazo mostra `aguardando ⓷` quando a linha está
travada — o número diz **qual linha** está segurando, e ele muda sozinho
conforme a fila anda.

### Status da planilha

| | Quando |
|---|---|
| 🟢 **OK** | todas as etapas concluídas |
| 🔵 **NO PRAZO** | tem data futura |
| 🟠 **PENDENTE** | liberada, sem data |
| 🔴 **ATRASADO** | data venceu |
| ⚫ **CANCELADO** | não vai acontecer |
| ⚪ **AGUARDANDO N** | espera a linha N |

⚠️ **Desvio consciente da referência.** O print que originou a vista mostrava
`ATRASADO` em amarelo e `PENDENTE` em vermelho. Aqui é o contrário: vermelho é
o que **já venceu**, porque essa é a instrução anterior do usuário e é o alarme
certo.

🚨 **Cancelado não é concluído.** A tarefa não vai acontecer, então **não
libera a de baixo** — tratar como concluída faria a fila andar sobre nada. Ela
fica riscada, apagada, e segura a sequência.

## 3. Como nasce o próximo

```python
from fpsl_weso import demandas
demandas.criar_quadro("Nome", modo="planilha", gerente="Iago")
```

`modo` é `esteira` (padrão) ou `planilha`. Depois é montar pela tela.
As pessoas, as cores, o semáforo e as travas **vêm de graça** — o esquema é
multi-quadro desde o começo, e toda consulta filtra por `quadro_id`.

O link é `https://fpsl.movisat.com.br/demandas/<token>`.

⚠️ **O cadastro de pessoas é POR QUADRO.** Iago no quadro 1 e Iago no quadro 2
são registros diferentes, com cores independentes. É proposital: quadros podem
ter times diferentes. Quem copia dados entre quadros liga por **nome**.

## 4. Os quadros em uso (2026-08-05)

| Quadro | Vista | Link |
|---|---|---|
| **Comercial Interno × Externo** | esteira | `/demandas/1d84a81a…` |
| **Cronograma de Tarefas** | planilha | `/demandas/73d3761a…` |

🚨 **São CÓPIAS independentes, não duas vistas do mesmo dado.** Decisão do
usuário: ele quis os mesmos itens nos dois formatos. Marcar concluído num
**não** mexe no outro, e eles vão divergir conforme forem usados.

⚠️ Se um dia incomodar, a saída é **um quadro com duas vistas** —
`/demandas/<token>` e `/demandas/<token>/planilha` sobre o mesmo dado. Não foi
feito porque não foi pedido, mas é o desenho sem essa dívida.

## 5. Onde mora, e por quê

Hospedado no **FPSL** — decisão do usuário em 05/08, depois de eu ter posto no
MoviZap primeiro.

⚠️ **Foi erro meu.** Pus no MoviZap porque o domínio e o Postgres já estavam
lá. O usuário corrigiu: *"não tem nada a ver com o MoviZap"*. **Hospedar por
conveniência é como um sistema vira depósito** — daqui a um ano ninguém sabe
por que o comunicador tem tabela de demanda comercial.

Regra que fica: **painel rápido não escolhe casa por conveniência de infra.**
Vai onde o assunto pertence, ou num lugar declaradamente genérico.

| Peça | Onde |
|---|---|
| lógica | `fpsl_weso/demandas.py` |
| rotas | `fpsl_weso/painel/routers/demandas_router.py` |
| vista esteira | `fpsl_weso/frontend/demandas.html` |
| vista planilha | `fpsl_weso/frontend/planilha.html` |
| dados | 5 tabelas `demanda_*` em `data/fpsl.db` |

O esquema evolui sozinho: `preparar()` roda em todo arranque e acrescenta
coluna que faltar (`modo`, `gerente`, `cancelado`, `pessoa_id`) sem migração
manual. É idempotente.

🚨 **Nenhuma rota daqui toca tabela do FPSL.** É rota pública num serviço
autenticado: a separação é o que impede um link vazado virar acesso ao painel.

## 6. As decisões de desenho que valem repetir

### Fila dentro da raia, não no quadro
Cada assunto tem sua fila; os assuntos correm em paralelo. Fila única faria a
Karla esperar o Rodrigo terminar coisa que não é dela.

### A cor do card é de QUEM É A VEZ
Sai da **primeira etapa não concluída**. A faixa inteira responde "de quem é a
bola?" sem ninguém ler nome. Quando a etapa fecha, a cor muda sozinha.

Duas exceções mandam mais que a pessoa: **atrasado** (vermelho, com anel) e
**concluído** (verde) — no concluído não há pendente, então não há vez.

### Cor é cadastro, não hash
Na primeira versão a cor saía de um hash do nome. Estável, mas **ninguém
escolhia e duas pessoas podiam colidir**. Hoje a pessoa tem cor própria e o
**banco** impede repetição (`UNIQUE` em nome e em cor, por quadro) — não a
tela.

🚨 **A paleta não tem verde nem vermelho.** Essas duas já significam
"concluído" e "atrasado" no card; pessoa de cor verde faria o card parecer
pronto sem estar.

### Responsável se escolhe, não se digita
Nome digitado cria pessoa nova a cada erro de grafia — "Iago", "iago", "Iago "
seriam três, cada uma levando uma cor da paleta.

### "Atrasado" é derivado, nunca gravado
`prazo < hoje AND NOT concluído`, calculado na leitura. Prazo que vence de
madrugada fica vermelho sozinho. Coluna `atrasado` precisaria de alguém para
virá-la, e esse alguém não existe.

### "Sem prazo ainda" é decisão, não ausência
Campo próprio, diferente de prazo vazio. Um é "combinamos que não tem data"; o
outro é "ninguém olhou".

## 7. 🚨 A trava é no backend, sempre

Card em espera tem campo desabilitado na tela **e** a rota devolve **409**.
Quem tem o link tem o endereço da rota — **desabilitar no HTML nunca impediu
ninguém**.

Vale igual para: pessoa que não existe (404), cor em uso (409), nome repetido
(409), campo em branco (422), excesso de escrita (429).

⚠️ **Toda recusa diz o motivo.** "Não deu" faz a pessoa tentar de novo igual.

## 8. Segurança de rota pública

- **o link é a credencial**: token de 64 hex, e a página não o repete no HTML;
- **token errado, mesmo por um caractere, devolve 404** e a página sozinha não
  entrega nada;
- **todo texto do banco é escapado** antes de ir para a tela — qualquer um
  escreve na observação, e observação com `<script>` dentro não pode virar
  script;
- **teto em todo campo** e limite de escrita por IP, lendo `X-Real-IP` (atrás
  do nginx todo mundo chega como `127.0.0.1`);
- **a página é a mesma para qualquer token** — devolver 404 nela diria a quem
  adivinha que aquele token não existe.

## 9. O que este padrão NÃO tem

Escrito para não ser redescoberto como surpresa:

- **sem login e sem permissão** — quem tem o link faz tudo, inclusive apagar;
- **sem histórico de alteração** — só "último toque"; não dá para saber o que
  o card tinha ontem;
- **sem notificação** — ninguém é avisado de nada;
- **sem reordenar arrastando** — a ordem é a de criação;
- **sem anexo**;
- **sem grafo de dependência** — a fila é linear dentro da raia.

Se algum desses passar a fazer falta, **o assunto deixou de caber num painel
rápido** e merece tela de verdade, com conta e permissão.

---

## Decisões

### Painel rápido é um padrão, não um projeto (05/08)
```
Objetivo:     acompanhar um assunto pequeno sem construir sistema
Hoje:         = o objetivo. Quadro novo é uma linha; o resto vem pronto
Por quê:      o custo de um quadro tem que ser menor que o de uma planilha,
              senão vira planilha
Reavaliar se: alguém copiar o código para fazer o segundo -- é o sinal de que
              o padrão falhou
```

### Mora no FPSL, e não onde a infra era mais fácil (05/08)
```
Objetivo:     cada coisa na casa a que pertence
Hoje:         = o objetivo. Saiu do MoviZap na migração 005
Por quê:      hospedar por conveniência é como um sistema vira depósito
Reavaliar se: nascer um lugar declaradamente genérico para ferramenta interna
              -- aí o painel rápido muda de casa e o FPSL fica só com o dele
```

### Sem login, com link como credencial (05/08)
```
Objetivo:     qualquer um do time abrir e mexer, sem cadastro
Hoje:         = o objetivo. Token de 64 hex na URL
Por quê:      exigir conta para 13 tarefas mata o uso; e o conteúdo é
              acompanhamento interno, não dado sensível
Reavaliar se: entrar no quadro qualquer informação que não possa vazar --
              aí precisa de conta, e deixa de ser painel rápido
```

### Vista é campo do quadro, não projeto novo (05/08)
```
Objetivo:     o mesmo motor desenhar cronograma ou esteira
Hoje:         = o objetivo. `modo` escolhe a página; dados e travas iguais
Por quê:      duplicar o código para mudar a aparência é o começo de dois
              sistemas que divergem em silêncio
Reavaliar se: uma vista precisar de dado que a outra não tem
```

### Os dois quadros são cópias, e vão divergir (05/08)
```
Objetivo:     ver os mesmos itens em cronograma e em esteira
Hoje:         contorno -- são DOIS quadros com dados copiados, não um com
              duas vistas. Marcar concluído num não mexe no outro
Por quê:      decisão do usuário: ele quis os dados nos dois formatos, e a
              cópia entregou isso hoje
Reavaliar se: começarem a discordar e alguém perguntar qual está certa --
              aí vira um quadro com duas rotas de vista
```
