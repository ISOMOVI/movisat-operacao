# 01 — Segurança da tela de login

**Documento transversal.** Vale para os quatro painéis — MoviZap, MoviServer,
FPSL e MoviChat — não para um projeto. Escrito em 2026-08-05, depois de uma
auditoria das quatro telas de login.

Companheiro de `00_Commit_e_Segredos.md`. Mesma regra: cada item aqui é uma
coisa que **já estava errada**, com o que foi feito no lugar.

---

## Estado, depois da correção

| Painel | Limite no nginx | Limite na aplicação | Mensagem única | SQL |
|---|---|---|---|---|
| MoviZap | ❌ (a fazer) | ✅ | ✅ | sem SQL |
| MoviServer | ❌ (a fazer) | ✅ desde 28/07 | ✅ | parametrizado |
| FPSL | ✅ `5r/m burst=3` | ✅ | ✅ | parametrizado |
| MoviChat | ✅ `5r/m burst=3` | ✅ | ✅ | ORM |

**Nenhum dos quatro tem SQL injection.** Todos usam consulta parametrizada
(`?`) ou ORM. Não há concatenação de string em consulta em lugar nenhum.

---

## 1. 🚨 Auditar código de aplicação não é auditar o sistema

**Erro cometido em 05/08.** A primeira auditoria leu os `routers/*.py` dos
quatro painéis e concluiu: *"FPSL e MoviChat não têm nenhuma proteção contra
força bruta"*. **Estava errado.** Os dois tinham — em
`/etc/nginx/nginx.conf`:

```nginx
limit_req_zone $binary_remote_addr zone=ia_login:10m   rate=5r/m;
limit_req_zone $binary_remote_addr zone=fpsl_login:10m rate=5r/m;
```

O que denunciou o engano foi o corpo do 429: veio como **HTML do nginx**, não
como o JSON do FastAPI. Se o teste só tivesse olhado o código de status, o
erro teria passado.

**Regra: defesa pode estar em qualquer camada.** Antes de dizer que não
existe, olhar nginx, firewall e systemd — e conferir **quem respondeu**, não
só o que respondeu.

## 2. As duas camadas, e por que as duas

O nginx e a aplicação não são redundância: protegem de coisas diferentes.

| Camada | Protege de | Cega para |
|---|---|---|
| **nginx** `limit_req` | volume bruto, antes de gastar Python | quem alcança a porta da aplicação direto |
| **aplicação** | tentativa por conta, mesmo com pouco volume | ataque que nem chega ao handler |

⚠️ O FPSL e o MoviBot escutam em **`0.0.0.0`**, não em `127.0.0.1` — hoje só
o firewall (`deny incoming`, aberto em 80/443/22) impede alcançá-los direto.
Uma regra de ufw errada e o `limit_req` do nginx deixa de existir. Por isso a
camada de aplicação entrou nos quatro.

## 3. O limite roda ANTES do bcrypt

```python
resta = ratelimit.bloqueado_por(chave)
if resta:
    raise HTTPException(429, ...)     # antes de qualquer verificação
usuario = validar_login(...)          # ~250ms de bcrypt
```

Se rodasse depois, a própria verificação viraria o custo do ataque: 250 ms de
CPU nossa por tentativa, de graça para o atacante. Bcrypt é caro **de
propósito** — e essa é exatamente a arma que se vira contra o servidor.

## 4. A chave é `IP + conta`, com `casefold`

```python
chave = f"{ip}|{login.casefold()}"
```

- **só por IP** puniria um escritório inteiro atrás de um NAT por causa de uma
  pessoa que errou a senha;
- **só por conta** deixaria passar ataque distribuído;
- **`casefold`, não `lower`**: desde 05/08 o login ignora maiúscula, então
  `Admin` e `ADMIN` são a MESMA conta. Contá-las separado daria 5 tentativas
  para cada variação de caixa — tentativas de graça só alternando o Shift.

## 5. 🚨 Atrás do nginx, `request.client.host` é sempre 127.0.0.1

Foi um defeito real, introduzido e corrigido no mesmo dia.

Sem tratar isso, **todo mundo compartilha um balde só**: o primeiro atacante a
estourar 5 tentativas tranca todos os usuários junto. É negação de serviço
embrulhada como proteção.

```python
conexao = request.client.host
if conexao not in PROXIES_CONFIAVEIS:   # {"127.0.0.1", "::1"}
    return conexao                      # veio direto: o endereço é verdade
return request.headers.get("x-real-ip") or conexao
```

🚨 **Confiar no cabeçalho sem checar a origem é pior que não ter limite
nenhum**: quem manda um `X-Forwarded-For` diferente a cada requisição ganha
tentativas infinitas. O cabeçalho só vale vindo do proxy local.

## 6. 🚨 Contador em memória não sobrevive a mais de um worker

**Medido em 05/08.** O MoviChat roda com `--workers 2`. Com o contador em
`dict` de processo, cada worker contava separado: **6 tentativas seguidas não
bloquearam nada**, porque foram 3 para cada.

O contador foi para **SQLite**, que serializa a escrita entre processos sem
depender de Redis.

```
Objetivo:     limite de 5 valer de verdade, independente de quantos workers
Hoje:         = o objetivo. Contador em sqlite, WAL, nos quatro painéis
Por quê:      contador em memória é 5 x número de workers, e ninguém percebe
              -- o teste passa com 1 worker e mente em produção
Reavaliar se: o volume fizer o sqlite virar gargalo. Aí vai para Redis, que
              já existe no host por causa do Evolution
```

**Efeito colateral aceito:** o bloqueio agora **sobrevive ao restart**. Antes,
reiniciar zerava tudo — o que só ajudava o atacante, já que ele não controla o
restart. Para soltar alguém preso por engano existe `ratelimit.zerar()`.

⚠️ **Nunca zerar apagando o arquivo com o serviço no ar.** Em 05/08 fiz isso e
o processo continuou escrevendo num inode removido: a contagem passou a não
fazer sentido e o diagnóstico foi atrás de um fantasma. `zerar()` faz `DELETE`,
que é o certo.

## 7. Falha do contador libera, não bloqueia

```python
except sqlite3.Error:
    return 0      # sem bloqueio
```

Parece contraintuitivo num documento de segurança. O raciocínio: o pior caso
de liberar é ficar alguns instantes sem limite — e o nginx continua na frente.
O pior caso de bloquear é **o painel inteiro fora do ar** porque um arquivo de
contador ficou ilegível. Falha de mecanismo acessório não pode derrubar o
acesso.

⚠️ É a exceção consciente ao "falha fechado" do projeto, que continua valendo
para **permissão** — lá, conta nova nasce sem nada.

## 8. Mensagem única — não entregar quem existe

**O MoviChat entregava a lista de logins válidos.** Cinco mensagens
diferentes: `"Senha incorreta"` (conta existe), `"Usuário não encontrado"`
(não existe), `"Usuário administrador desativado"`, `"Usuário desativado"`,
`"Empresa inativa"`. Bastava varrer nomes e ler a resposta.

Agora toda falha de autenticação responde **exatamente igual**, e o motivo
real vai para o log:

```python
def recusar(motivo: str):
    ratelimit.registrar_falha(chave)
    logger.info("login recusado (%s): login=%r", motivo, body.login)
    return HTTPException(401, "Login ou senha inválidos.")
```

⚠️ **A mensagem do 429 também não pode variar** entre conta que existe e
conta que não existe — senão o vazamento volta pela porta do limite. Há teste
para isso.

## 9. Teto de tamanho no corpo

```python
login: str = Field(min_length=1, max_length=64)
senha: str = Field(min_length=1, max_length=256)
```

Sem teto, um POST de 10 MB no campo senha vira trabalho de bcrypt em cima de
lixo. O bcrypt ignora além de 72 bytes de qualquer jeito — aceitar mais é só
custo.

## 10. O que estes painéis NÃO têm

Escrito para não ser redescoberto como surpresa:

- **sem 2FA** e sem segundo fator de nenhum tipo;
- **sem CAPTCHA** — o limite é a única barreira automática;
- **sem aviso ao usuário** de que a conta foi bloqueada ou de tentativa
  suspeita (não há envio de e-mail no MoviZap, FPSL nem MoviServer);
- **sem expiração de senha** e sem exigência de complexidade;
- **sem registro de auditoria de login bem-sucedido** — só a falha vai para o
  log;
- **o MoviChat compara a senha de admin do `.env` em texto puro**
  (`hmac.compare_digest(body.senha, settings.admin_senha)`). Não é o `compare_digest`
  que é o problema: é a senha existir sem hash no arquivo. Consertar exige
  migrar o `.env` e a semente.

Boa parte disso melhora quando o **Google OAuth** entrar — mas *melhora* não é
*resolve*: o login local continua existindo como caminho de recuperação.

---

## Decisões

### Limite de tentativas nas quatro telas de login (05/08)
```
Objetivo:     força bruta ser barrada mesmo se o nginx sair do caminho
Hoje:         = o objetivo. 5 falhas / 5 min por IP+conta, antes do bcrypt
Por quê:      o limite do nginx é por IP e cego para quem alcança a porta da
              aplicação direto -- e FPSL e MoviBot escutam em 0.0.0.0
Reavaliar se: o Google OAuth virar o único caminho de entrada. Enquanto o
              login local existir, isto fica
```

### Login ignora maiúscula (05/08)
```
Objetivo:     ninguém ficar de fora por causa da tecla Shift
Hoje:         = o objetivo. casefold no MoviZap, COLLATE NOCASE no MoviServer
Por quê:      em 05/08 o painel recusou acesso em 1ms -- rápido demais para
              ter chegado no bcrypt. Login identifica a pessoa; quem protege
              é a senha, e ela continua sensível à caixa
Reavaliar se: — fechado. O contador de tentativas usa a mesma normalização,
              senão alternar caixa renderia tentativas de graça
```

### Contador de tentativas em sqlite, não em memória (05/08)
```
Objetivo:     o limite de 5 ser 5, e não 5 x número de workers
Hoje:         = o objetivo, nos quatro painéis
Por quê:      medido: com --workers 2 o MoviChat não bloqueou em 6 tentativas
Reavaliar se: virar gargalo -- aí vai para o Redis que já roda no host
```
