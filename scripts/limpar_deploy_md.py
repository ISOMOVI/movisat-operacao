"""Tira a chave WESO do 06_Deploy.md do FPSL e conserta o metodo que a colocou la.

Dois problemas na mesma linha:
  1. o VALOR da chave estava escrito no doc versionado;
  2. o metodo ensinado era `ssh vps "cat > .env << EOF ... "` -- ou seja, a
     chave passando pela LINHA DE COMANDO, exatamente o que a regra do
     projeto proibe (feedback_no_secrets_in_shell).

Corrigir so o (1) deixa o (2) para reintroduzir o (1) na proxima vez.

Monta em memoria, VALIDA, e so entao grava. Nao imprime valor.
"""
import hashlib
import re
import sys
from pathlib import Path

ALVO = Path("/home/claude/fpsl_weso/docs/fpsl/06_Deploy.md")
ENV = Path("/home/claude/fpsl_weso/.env")

original = ALVO.read_text(encoding="utf-8")

# A chave real, lida do .env -- nunca digitada, nunca impressa.
chave = ""
for linha in ENV.read_text(encoding="utf-8").splitlines():
    if linha.startswith("WESO_API_KEY="):
        chave = linha.split("=", 1)[1].strip().strip('"').strip("'")
        break

if not chave:
    sys.exit("nao encontrei WESO_API_KEY no .env -- abortando sem tocar no doc")

if chave not in original:
    print("O doc ja nao contem a chave. Nada a fazer.")
    sys.exit(0)

print(f"  chave encontrada no doc  sha256[:8]={hashlib.sha256(chave.encode()).hexdigest()[:8]}")

BLOCO_ANTIGO = re.compile(
    r"```bash\nssh vps \"cat > /home/claude/fpsl_weso/\.env << 'EOF'\n"
    r"WESO_API_KEY=" + re.escape(chave) + r"\n"
    r"(WESO_BASE_URL=[^\n]*)\n"
    r"EOF\"\n```"
)

MOLDE_NOVO = """> 🚨 **A chave NUNCA passa pela linha de comando.** O `ssh vps "cat > .env
> << EOF"` que estava aqui colocava o valor no comando, no histórico do shell
> e — como se descobriu em 05/08 — dentro deste documento versionado.

Monte o arquivo **localmente**, envie por `scp` e destrua o original:

```bash
# conteudo do arquivo temporario  env_fpsl.txt
WESO_API_KEY=<cole a chave aqui>
{base_url}
```

```powershell
scp env_fpsl.txt vps:/home/claude/fpsl_weso/.env
Remove-Item env_fpsl.txt
```

```bash
ssh vps "chmod 600 /home/claude/fpsl_weso/.env"
```"""

# Funcao como substituto, nao string: o texto novo tem `\\` e `<...>`, que o
# motor de regex tentaria interpretar como escape e grupo.
candidato, trocas = BLOCO_ANTIGO.subn(
    lambda m: MOLDE_NOVO.format(base_url=m.group(1)),
    original,
)

if trocas == 0:
    # O bloco nao casou exatamente. Nao improvisar: apagar so o valor e avisar.
    candidato = original.replace(chave, "<cole a chave aqui -- nunca versionar o valor>")
    print("  ! o bloco de instrucao nao casou com o formato esperado;")
    print("    substitui apenas o VALOR e mantive o resto intacto.")
    print("    O metodo ainda ensina segredo em linha de comando -- corrigir a mao.")

# ---- validar ANTES de gravar ----
falhas = []
if chave in candidato:
    falhas.append("a chave AINDA esta no candidato")
if len(candidato) < len(original) * 0.5:
    falhas.append("o candidato encolheu demais -- a regex comeu documento")
if "WESO_BASE_URL" not in candidato:
    falhas.append("WESO_BASE_URL sumiu do doc")

if falhas:
    print("\nNAO GRAVEI. O candidato falhou na validacao:")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)

ALVO.write_text(candidato, encoding="utf-8")
print(f"\n06_Deploy.md limpo ({trocas} bloco(s) reescrito(s)).")
print("O historico do git NAO foi tocado: a chave continua no commit empurrado.")
print("A unica correcao que vale para isso e ROTACIONAR a chave na WESO.")
