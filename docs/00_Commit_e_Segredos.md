# 00 — Commit e segredos

**Documento transversal.** Vale para os 5 repositórios da Movisat, não para um
projeto. Escrito em 2026-08-05, depois de um alerta do GitGuardian e de dois
erros meus na mesma sessão.

Cada item aqui é uma coisa que **já deu errado**, com o que fazer no lugar.
Nenhum é hipotético.

---

## 1. `.gitignore` não protege arquivo já rastreado

**Quebrou em 04/08.** `movibot/.env.bak_2026-07-22` estava dentro do histórico
com 4 credenciais. O `.gitignore` tinha `*.bak_*` — e não adiantou: a regra só
vale para arquivo **novo**. O que já está rastreado continua sendo commitado.

```bash
# antes de qualquer primeiro push:
git ls-files | grep -iE 'env|secret|senha|key|\.bak'
git log --all --name-only | sort -u | grep -iE 'env|secret'
```

Para tirar: `git rm --cached <arquivo>` — e o histórico continua com ele.

## 2. 🚨 `.gitignore` protege o NOME, não o CONTEÚDO

**Quebrou em 04/08, descoberto em 05/08.** Os dois vazamentos reais não
estavam em `.env`. Estavam em **documentação**:

| Segredo | Onde | Alertou? |
|---|---|---|
| Chave DeepSeek | `IA_agente_Movichat/PROJETO.md:21`, numa tabela de credenciais | sim, GitGuardian |
| Chave WESO | `fpsl_weso/docs/fpsl/06_Deploy.md:98`, num passo de deploy | **não** — não existe detector para ela |

O `.gitignore` mirava `.env`, `*.pem`, `*.key`. Nenhum `.md` foi olhado.

**Confiar no `.gitignore` é confiar que ninguém vai colar uma credencial num
`.md`.** É uma aposta contra a natureza humana, e ela se perde.

**Correção aplicada:** `scripts/gate_segredos.py`, chamado por
`git_autocommit.sh` **antes** do `git add`. Repositório com segredo é pulado;
os outros seguem. Falha do próprio gate também bloqueia — falha fechado.

```bash
python3 /home/claude/scripts/gate_segredos.py /home/claude/<repo>   # 0 = pode
```

⚠️ A trava só usa padrões de **alta confiança**. A tentação é varrer `senha=`
também — isso dá 44 falsos positivos nos 5 repositórios, e **trava que grita à
toa vira trava que todo mundo aprende a ignorar**.

## 3. 🚨 Aspas na mensagem de commit quebram o `ssh "..."`

**Quebrou em 05/08, erro meu.** A mensagem citava o comando errado que se
estava corrigindo:

```
    ssh vps "cat > /home/.../.env << 'EOF'
```

As aspas duplas de dentro **fecharam** as aspas do `ssh "..."` de fora. O
resto virou comando solto, e o shell tentou executar um `cat > .env`. O `.env`
sobreviveu por sorte, não por desenho.

É a mesma armadilha já conhecida do PowerShell, com outro nome.

```bash
# ERRADO
ssh vps "cd repo && git commit -m 'texto com \" aspas'"

# CERTO — mensagem vai por ARQUIVO
scp msg.txt vps:/home/claude/msg_commit.tmp
ssh vps "cd repo && git commit -F /home/claude/msg_commit.tmp && rm -f /home/claude/msg_commit.tmp"
```

**Regra: mensagem de commit com mais de uma linha, ou com qualquer `"`, `` ` ``,
`$`, `\` ou `()`, vai por arquivo + `scp`. Sem exceção.**

## 4. Editar pelo GitHub enquanto há mudança local = divergência

**Aconteceu em 05/08.** O usuário apagou a chave pela interface web; a VPS
tinha a correção local. Resultado: `1 1` na divergência e push recusado com
`non-fast-forward`.

🚨 **Não resolver com `push --force`.** Isso apaga o commit da outra ponta.

```bash
git fetch origin
git rev-list --left-right --count HEAD...origin/main   # esquerda=local, direita=remoto
git show origin/main:<arquivo>                          # ver a versão do outro ANTES

git reset --soft origin/main    # reposiciona sobre o commit do outro
git add <arquivo>               # a versão boa, já na árvore de trabalho
git commit -F msg.txt           # entra EM CIMA, sem apagar nada
git push origin main            # fast-forward, sem force
```

**Quem edita pela web precisa avisar**, e quem edita na VPS precisa dar
`git fetch` antes de começar.

## 5. Apagar do arquivo não apaga do histórico

Vale para os dois vazamentos. `96ca6df` continua no GitHub com as chaves, e
**objeto de git segue alcançável por SHA mesmo depois de reescrito** — o
GitHub só o remove por garbage collection, que pode nunca rodar.

```
Apagar do arquivo   = tira do HEAD.  Bom para não piorar.
Reescrever histórico = tira do branch. Não tira do SHA.
ROTACIONAR          = a única coisa que realmente resolve.
```

**Segredo que apareceu em repositório é segredo queimado.** Trata-se como
comprometido a partir do minuto do push, não a partir do alerta.

## 6. Segredo nunca passa pela linha de comando

Já era regra, e foi **exatamente o método que produziu o vazamento da WESO**:
o `06_Deploy.md` ensinava criar o `.env` por heredoc dentro de um `ssh`. Do
comando, a chave foi parar no documento.

Na linha de comando o valor aparece em: `ps` de qualquer usuário, histórico do
shell, log do sudo, e — como se viu — na documentação que copia o comando.

**Padrão certo:** montar o arquivo local → `scp` → o script lê do arquivo →
o arquivo temporário é sobrescrito e removido. Ver `movizap_painel/gerar_env.py`
e `scripts/trocar_owner_moviserver.py`.

## 7. Diff antes de subir — inclusive o que você acabou de escrever

**Pegou um erro meu em 05/08.** Uma classe de teste nova foi parar **no meio**
de outra classe, deixando um teste órfão dentro dela. Passaria nos testes e
ficaria errado para sempre.

```bash
diff -u <(sed 's/\r$//' arquivo.py.vps) <(sed 's/\r$//' arquivo.py)
```

O `sed` normaliza CRLF; sem ele o diff acusa o arquivo inteiro. E **`py_compile`
não pega import faltando nem símbolo errado** — depois do diff, rodar os testes.

## 8. Confirmar relendo o estado, nunca pelo retorno

Vale para git como vale para o Harmonit e para a WESO.

```bash
git push ...                                  # não prova nada sozinho
git fetch -q origin
git rev-list --left-right --count HEAD...origin/main   # 0 0 = em sincronia
git show origin/main:<arquivo> | grep ...     # o segredo saiu MESMO?
```

---

## 9. 🚨 Árvore limpa não significa sincronizado (2026-08-14)

O `git_autocommit.sh` das 23:30 fazia `continue` assim que via
`git status --porcelain` vazio. Consequência: **commit feito à mão nunca era
empurrado**. O `fpsl_weso` acumulou **13 commits que existiam só na VPS**, e o
log dizia `sem mudancas` todo dia — parecia estar tudo em ordem.

⚠️ **A automação media a coisa errada.** "Nada para commitar" e "nada para
enviar" são perguntas diferentes, e só a primeira estava sendo feita. Quem lia o
log não tinha como perceber: a linha de sucesso e a linha do buraco eram a
mesma.

Corrigido: com a árvore limpa, o script ainda confere
`git rev-list --count @{u}..HEAD` e **empurra se estiver adiantado**. E ganhou
contador próprio de `NAO_EMPURRADOS`, com aviso no fim do log — falha de push
antes só aparecia numa linha no meio, fácil de não ver.

**Como conferir à mão, em qualquer repositório:**

```bash
git rev-list --count @{u}..HEAD   # commits que ainda não saíram daqui
```

## Antes de todo primeiro push de um repositório novo

1. `git ls-files | grep -iE 'env|secret|senha|key|\.bak'`
2. `python3 /home/claude/scripts/gate_segredos.py <repo>`
3. `python3 /home/claude/scripts/auditar_vps.py` — pega o que está fora do git
4. `.gitignore` com `.env*`, `alembic.ini`, `*.pem`, `*.key`, `backups/`, `*.bak*`
5. Ler os `.md` do repositório procurando tabela de credenciais

O passo 5 é o que faltou em 04/08.

---

## Decisões

### Trava de segredo no commit automático (05/08)
```
Objetivo:     nunca mais empurrar credencial para o GitHub sem perceber
Hoje:         = o objetivo. gate_segredos.py roda antes do git add, nos 5
              repositórios; repositório bloqueado é pulado e os outros seguem
Por quê:      o .gitignore protege o NOME do arquivo, e os dois vazamentos de
              04/08 estavam em .md -- tabela de credenciais e passo de deploy
Reavaliar se: — fechado. O que muda com o tempo são os padrões, não a trava
```

### A trava só usa padrões de alta confiança (05/08)
```
Objetivo:     a trava ser levada a sério quando disparar
Hoje:         = o objetivo. sk-, gsk_, EA…, ghp_, AKIA, chave privada, URL
              com senha, e linha .env cujo NOME diga que é segredo
Por quê:      varrer `senha=` também dá 44 falsos positivos nos 5 repositórios
              -- e trava que grita à toa vira trava que todo mundo ignora
Reavaliar se: escapar um segredo de formato novo. Aí entra o padrão dele,
              não uma varredura genérica
```

### Falha do gate bloqueia o commit (05/08)
```
Objetivo:     na dúvida, não empurrar
Hoje:         = o objetivo. Erro do próprio gate faz o repositório ser pulado
Por quê:      commit perdido se recupera no dia seguinte; segredo empurrado
              não se recupera -- só se rotaciona
Reavaliar se: começar a bloquear por engano com frequência. O sintoma aparece
              em logs/git_autocommit.log, que ninguém lê sozinho -- por isso
              o script grita "OLHE ESTE LOG" no fim
```

⚠️ **Contorno declarado:** ninguém é avisado ativamente quando a trava
bloqueia. O aviso está no log, e log só ajuda quem abre. Cai quando o
`NOTIFICACAO_EMAIL` for ligado ao cron.
