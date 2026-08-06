"""Troca o MOVIZAP_ADMIN_LOGIN no .env, preservando o hash da senha.

Uso:  trocar_login_movizap.py <novo_login>

Monta em memoria, VALIDA e so entao grava. Nunca imprime o hash.
"""
import re
import sys
from pathlib import Path

ENV = Path("/home/claude/movizap_painel/.env")

if len(sys.argv) < 2:
    sys.exit("uso: trocar_login_movizap.py <novo_login>")

novo = sys.argv[1].strip()
if not novo or " " in novo:
    sys.exit("login invalido: vazio ou com espaco")

original = ENV.read_text(encoding="utf-8")

antes = re.search(r"^MOVIZAP_ADMIN_LOGIN=(.*)$", original, re.M)
if not antes:
    sys.exit("MOVIZAP_ADMIN_LOGIN nao existe no .env -- abortando")

candidato = re.sub(
    r"^MOVIZAP_ADMIN_LOGIN=.*$", f"MOVIZAP_ADMIN_LOGIN={novo}", original, flags=re.M
)

# ---- validar ANTES de gravar ----
falhas = []
if f"MOVIZAP_ADMIN_LOGIN={novo}" not in candidato:
    falhas.append("o novo login nao entrou")
if "MOVIZAP_ADMIN_SENHA_HASH=$2" not in candidato:
    falhas.append("o hash da senha sumiu ou deixou de ser bcrypt")
if "MOVIZAP_JWT_SECRET=" not in candidato:
    falhas.append("o segredo do JWT sumiu")
if len(candidato.splitlines()) != len(original.splitlines()):
    falhas.append("o numero de linhas mudou")

if falhas:
    print("NAO GRAVEI:")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)

ENV.write_text(candidato, encoding="utf-8")
ENV.chmod(0o600)

print(f"login: {antes.group(1)!r} -> {novo!r}")
print("senha: INTACTA (o hash nao foi tocado)")
print(f"modo do .env: {oct(ENV.stat().st_mode)[-3:]}")
