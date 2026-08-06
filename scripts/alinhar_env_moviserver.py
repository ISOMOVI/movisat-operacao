"""Realinha PAINEL_ADMIN_LOGIN/SENHA do .env com o owner que esta no banco.

Uso:  alinhar_env_moviserver.py <login> <arquivo_com_a_senha>

Por que isto existe: no MoviServer o .env NAO e so semente. Os testes de
regressao (tests/*.py) leem PAINEL_ADMIN_LOGIN/SENHA para autenticar como
owner. Trocar o dono no banco sem realinhar o .env quebra os 111 testes.

⚠️ Isso significa que a senha do owner vive em texto puro no .env. E o
desenho atual, nao uma escolha feita aqui. O conserto de verdade e os testes
usarem conta propria de teste -- anotado como pendencia.

Valida ANTES de gravar. Nao imprime a senha.
"""
import re
import sys
from pathlib import Path

ENV = Path("/home/claude/moviserver/.env")

if len(sys.argv) < 3:
    sys.exit("uso: alinhar_env_moviserver.py <login> <arquivo_com_a_senha>")

login = sys.argv[1].strip()
arquivo_senha = Path(sys.argv[2])

if not login or " " in login:
    sys.exit("login invalido")
if not arquivo_senha.exists():
    sys.exit(f"nao encontrei {arquivo_senha}")

senha = arquivo_senha.read_text(encoding="utf-8").strip()
if len(senha) < 8:
    sys.exit("senha vazia ou curta demais")

original = ENV.read_text(encoding="utf-8")
for chave in ("PAINEL_ADMIN_LOGIN", "PAINEL_ADMIN_SENHA"):
    if not re.search(rf"^{chave}=", original, re.M):
        sys.exit(f"{chave} nao existe no .env -- abortando")

candidato = re.sub(r"^PAINEL_ADMIN_LOGIN=.*$", f"PAINEL_ADMIN_LOGIN={login}",
                   original, flags=re.M)
candidato = re.sub(r"^PAINEL_ADMIN_SENHA=.*$", f"PAINEL_ADMIN_SENHA={senha}",
                   candidato, flags=re.M)

# ---- validar ANTES de gravar ----
falhas = []
if f"PAINEL_ADMIN_LOGIN={login}" not in candidato:
    falhas.append("o login nao entrou")
if f"PAINEL_ADMIN_SENHA={senha}" not in candidato:
    falhas.append("a senha nao entrou")
if "PAINEL_JWT_SECRET=" not in candidato:
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

# destroi o temporario
tamanho = arquivo_senha.stat().st_size
with open(arquivo_senha, "wb") as f:
    f.write(b"\x00" * tamanho)
arquivo_senha.unlink()

print(f"PAINEL_ADMIN_LOGIN -> {login!r}")
print("PAINEL_ADMIN_SENHA -> trocada (nao impressa)")
print(f"modo do .env: {oct(ENV.stat().st_mode)[-3:]}")
print(f"arquivo temporario destruido: {arquivo_senha}")
