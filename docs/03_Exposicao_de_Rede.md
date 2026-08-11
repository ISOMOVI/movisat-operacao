# 03 — Exposição de rede: o que está aberto, e por quê

> Levantado em **2026-08-11**, depois de achar a API do Evolution respondendo
> na internet. Vale para a VPS inteira, não só para o MoviZap.

---

## 🚨 O incidente: a API do WhatsApp estava aberta

**Como estava:**

```
ufw:   8082/tcp ALLOW Anywhere        # Evolution Manager (dev)
nginx: listen 8082; server_name _;  →  proxy_pass 127.0.0.1:8081
```

Um `curl` de fora da VPS devolvia **HTTP 200**, com versão (`2.3.7`),
`clientName` e a URL do manager. Sem SSL, sem restrição de IP, sem limite.

**O que salvou:** os endpoints de dados exigem a `apikey` — `fetchInstances` e
`connectionState` responderam **401**. Não houve acesso a conversa nenhuma.

**O que ainda assim era risco:** superfície para força bruta na chave **sem
rate limit**, vazamento de versão (útil para procurar CVE), e a chave viajando
**em texto puro** para quem usasse aquela porta.

**Já estava sendo varrida:**

```
182.119.227.58   10/08 23:58   GET /
139.226.161.43   10/08 23:59   GET /favicon.ico
139.170.72.157   10/08 23:59   GET /
94.231.206.134   11/08 12:49   \x16\x03\x03…   ← handshake TLS numa porta HTTP
```

**A correção:** `ufw delete allow 8082/tcp`. Nada legítimo usava — 11
requisições em 5 dias, todas de scanner. O MoviZap fala com a Evolution por
`localhost:8081`, e não há uma linha de código citando 8082.

### ⚠️ A lição, que vale além deste caso

**Regra de firewall com `(dev)` no comentário é dívida.** Foi aberta para uma
necessidade temporária e ficou. O `nginx -t` não reclama, o serviço funciona, e
nada no dia a dia aponta para ela — só um teste **de fora da VPS** revela.

🚨 **Auditoria de exposição não se faz de dentro do servidor.** De dentro,
`curl localhost` responde igual estando aberto ou fechado. A prova é chamar o
**IP público a partir de outra máquina**.

---

## O estado depois de 11/08

| Site | Porta interna | Proteção |
|---|---|---|
| `movizap.movisat.com.br` | 8008 | SSL · `limit_req` 4 zonas · nega `.bak`/`.env`/`.py` |
| `fpsl.movisat.com.br` | 8004 | SSL · `limit_req` no login |
| `movichat.movisat.com.br` | 8002 | SSL · `limit_req` 3 zonas |
| `ia-agente-movichat` | 8002 | `limit_req` 3 zonas |
| `prospeccao.movisat.com.br` | 8009/8083 | SSL · `limit_req` |
| `moviserver.movisat.com.br` | 8007 | SSL · `limit_req` **(11/08)** |
| `imagohub.com.br` | 8001 | SSL · `limit_req` **(11/08)** |
| `movibot.movisat.com.br` | 8006 | SSL · `limit_req` **(11/08)** |
| `evolution.movisat.com.br` | 8081 | SSL · **`allow 127.0.0.1` + 1 IP · `deny all`** |
| ~~`movizap_evolution` (8082)~~ | 8081 | 🚨 **porta fechada no firewall em 11/08** |

**Portas abertas no UFW:** 22 (SSH), 80, 443. Política padrão `DROP`.

---

## Como dimensionar `limit_req` — pelo tráfego, não por chute

Medido em 11/08, do `access.log`:

```
movizap      1.748 req/dia · pico 42/min   ← o único com volume
access.log     121 req/dia
fpsl            24 req/dia
moviserver       2 req/dia
imagohub/movibot 0
```

Zonas do MoviZap, e o porquê de cada número:

| Zona | Taxa | Burst | Por quê |
|---|---|---|---|
| `mz_hook` | 1200r/m | 200 | 🚨 **é por aqui que a mensagem do cliente entra.** O webhook do Evolution usa a **URL pública**, então passa pelo nginx. 429 aqui é mensagem perdida, e mensagem perdida no webhook não volta |
| `mz_api` | 300r/m | 60 | a tela conversando com a API |
| `mz_pages` | 60r/m | 20 | navegação |
| `mz_login` | 5r/m | 3 | força bruta de senha |

Os outros sites levaram `60r/m burst 20` — ~30× o pico observado no maior deles.

---

## 🚨 Dois erros cometidos ao aplicar isso, e como não repetir

**1. O limite caiu no server da porta 80.** O `location / {` do bloco HTTP é o
**primeiro** do arquivo, então um `replace(..., 1)` acerta ele. Pior que
inofensivo: aquele bloco passou a fazer `proxy_pass`, e `/api/` **deixou de ser
redirecionado para HTTPS**.

> Verificar sempre que a posição do `limit_req` é **depois** do `listen 443`:
> ```python
> if candidato.index("zone=x") < candidato.index("listen 443"): abortar
> ```

**2. O limite protegia `/api/login`, que não existe.** A rota é
`/api/sessao/login`. O `nginx -t` passava, o `grep` mostrava proteção, e o
endereço protegido não era usado por ninguém.

> **Limite no endereço errado é pior que limite nenhum** — parece proteção em
> toda verificação superficial. A prova é disparar requisições até tomar 429.

---

## O roteiro de verificação, para repetir

```bash
# 1. o que escuta, e em qual interface
ss -lntp | grep -v 127.0.0.1

# 2. o que o firewall deixa entrar
ufw status numbered
grep DEFAULT_INPUT_POLICY /etc/default/ufw     # tem que ser DROP

# 3. 🚨 DE FORA DA VPS, uma porta por vez
curl -s -o /dev/null -w "%{http_code}" http://<ip-publico>:<porta>/

# 4. o limite morde de verdade?
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code} " https://<site>/; done
```
