# 04 — Segredo em log: o que aconteceu em 2026-08-12 e o que ficou

Vale para a VPS inteira, não para um projeto só. Nasceu de um deslize meu e
virou uma varredura que achou quatro classes de vazamento, nenhuma delas
pontual.

---

## O gatilho

Rodei `journalctl --user -u movizap -n 5` só para conferir se o serviço tinha
subido. A saída trouxe o segredo do webhook do Evolution em texto puro, e ele
foi parar no histórico de uma conversa — que não é retirável.

🚨 **O DESLIZE ERA A METADE MENOR.** Medindo, o segredo já estava sendo escrito
no journal **2.527 vezes por dia**: ele vive no *caminho* da URL e o uvicorn
registra a linha de requisição de todo webhook. Não era vazamento pontual, era
contínuo, em disco, rotacionado — e portanto dentro do backup.

**Regra que saiu daí:** quando eu expuser um segredo, procurar se o sistema já
o expunha sozinho. A causa raiz costuma ser estrutural.

---

## O que a varredura achou

| Classe | Onde | Linhas |
|---|---|---|
| Segredo do webhook do Evolution | `movizap_access` + 6 rotacionados, `movizap_error`, `syslog`, journald | **7.711** |
| Token do Painel Rápido (FPSL) | `fpsl_access` + 5 rotacionados | **2.083** |
| Token do Painel Rápido (MoviZap antigo) | `movizap_access.log.7.gz` | **24** |
| `code=` e `state=` do OAuth Google | `movizap_access` ×3 | **9** |

⚠️ **A TERCEIRA SÓ APARECEU PORQUE INSISTI DEPOIS DE DAR POR LIMPO.** O Painel
Rápido nasceu no MoviZap e foi movido para o FPSL em 05/08 — o token ficou nos
logs dos **dois**. Higienizar só `fpsl_access*` deixava metade.

---

## O que ficou de correção

### 1. Mascarar na origem, sem desligar o log

`/etc/nginx/mz_mascara_segredo.conf`, incluído pelo `nginx.conf` **antes** de
`sites-enabled` — `map` e `log_format` precisam existir quando o site é lido.

⚠️ **O `conf.d/` NÃO é incluído neste servidor.** Descoberto com `nginx -t`, na
primeira tentativa.

⚠️ **NÃO se usa `access_log off`.** São endpoints públicos: perder o registro é
perder a prova de varredura, de 429 do `limit_req` e de quem bateu na porta.
Log que some para proteger segredo troca um problema por outro.

🚨 **O REFERER TAMBÉM CARREGA O TOKEN.** Quem abre `/demandas/<token>` faz a
tela chamar `/demandas/api/<token>`, e o navegador manda a origem no `Referer`
— mascarar só o caminho o deixaria na coluna ao lado, na **mesma linha**.

O formato `seguro` é o padrão global do nginx e vale para todos os sites.

⚠️ **Ele usa `$uri`, que não traz a query string.** É perda de observabilidade
e é deliberada: foi na query que apareceu o `code=` do OAuth, e nos painéis a
query carrega termo de busca — que tem nome e telefone de cliente. Se um dia
faltar, o caminho é acrescentar `$args` já filtrado, não voltar para
`$request`.

### 2. Filtro no uvicorn

`MascararSegredoDoCaminho`, em `movizap/main.py`, reescreve `record.args`
**antes** de a linha ser escrita. Mexer na mensagem final não pegaria nada — o
`uvicorn.access` guarda os campos separados e só os junta na hora de escrever.

### 3. Higienização do que já estava escrito

**9.827 registros** reescritos, **sem apagar uma linha**, conferindo a contagem
antes e depois de cada arquivo e só então substituindo o original.

### 4. Rotação sem queda

`movizap_painel/scripts/rotacionar_webhook.py`.

🚨 **SEGREDO ERRADO DEVOLVE 404, E O EVOLUTION TRATA 404 COMO FALHA.** Trocar o
valor e reiniciar recusaria todo evento entre o restart e o reapontamento. Por
isso o `.env` aceita `MOVIZAP_WEBHOOK_SEGREDO_ANTERIOR` durante a troca:

```
--abrir     gera o novo, move o atual para _ANTERIOR  -> as DUAS URLs valem
restart
reapontar   scripts/configurar_webhook_evolution.py
--conferir  pergunta ao EVOLUTION qual URL ele tem, E se há tráfego
--fechar    tira o _ANTERIOR
restart
```

⚠️ **O `--conferir` mentia na primeira versão.** Ele contava eventos e dizia
"pode fechar" — mas durante a rotação os **dois** segredos valem, então
eventos chegariam igual se o Evolution ainda estivesse na URL velha. Rótulo
fixo ao lado de um número que não responde à pergunta. Agora ele pergunta ao
Evolution qual URL está gravada.

Foram **três rotações** em 12/08: a primeira planejada, a segunda porque a
primeira ficou nos logs antigos, a terceira porque eu queimei a segunda (ver
abaixo).

---

## O erro que se repetiu quatro vezes no mesmo dia

A regra "nunca segredo em linha de comando" existia e cobria o que eu **digito**.
Ela tinha dois buracos:

🚨 **1. Comando de LEITURA também vaza.** `journalctl`, `cat` de log, `curl -v`,
`env`, `docker inspect` despejam configuração. **Filtrar na origem**
(`| sed "s|$s|<OCULTO>|g"`), nunca imprimir bruto e conferir depois.

🚨 **2. Substituição de shell para dentro de `argv` é o mesmo erro que digitar.**
Auditando se o segredo aparecia em algum log, rodei:

```
s=$(grep ^MOVIZAP_WEBHOOK_SEGREDO= .env | cut -d= -f2)
grep -rl -- "$s" /var/log/
```

O `auditd` registra `EXECVE` com argv inteiro: **o comando que procurava o
segredo nos logs escreveu o segredo num log**. `ps` e o histórico veem igual.

**Ferramenta certa:** `movizap_painel/scripts/auditar_segredo_em_log.py`, que
lê o `.env` **dentro do processo** e nunca põe o valor em argv. Imprime só a
contagem.

---

## Cabeçalhos de segurança

`/etc/nginx/snippets/security_headers.conf` — `Referrer-Policy:
strict-origin-when-cross-origin` é o que impede o token do Painel Rápido de ir
para o **Google Fonts**, que a página do quadro carrega.

⚠️ Conferido site a site pela RESPOSTA, não pela configuração. `prospeccao` era
o único sem o snippet. Corrigido.

---

## Painel Rápido — o que foi e não foi rotacionado

| Quadro | Vazou onde | Ação |
|---|---|---|
| #2 *Cronograma de Tarefas* | **transcrição de conversa** + log | **rotacionado** |
| #1 *Comercial Interno × Externo* | só o log, que exige root | **intocado** — em uso diário, e derrubar o link custa mais |

`fpsl_weso/rotacionar_quadros.py --aplicar --quadro N`. O link novo vai para
`~/links_painel_rapido.txt` (modo 600) e **nunca é impresso na tela**.

⚠️ **O script mentiu no relatório da primeira vez**: imprimiu "2 quadros
rotacionados" quando só um mudou, porque contava o total relido em vez do que
mudou. Rótulo que não vem da mesma medida da ação é a verificação que mente —
o erro que este projeto mais repete, cometido dentro do script feito para
consertar um vazamento.

---

## O que continua aberto

- **O token do Painel Rápido segue no caminho da URL.** Rotacionar troca o
  valor; não transforma o quadro em algo com login. É inerente a "compartilhar
  por link", que é o produto. O vazamento automático (log e referer) está
  fechado.
- **Nenhum outro site tem segredo em URL** — varrido por padrão, não por
  configuração: nenhum parâmetro sensível em query, nenhum token longo em
  caminho fora de `acme-challenge` e hashes de build.
