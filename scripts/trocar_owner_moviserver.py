"""Troca o login e a senha do OWNER do MoviServer.

Uso:  trocar_owner_moviserver.py <novo_login> <arquivo_com_a_senha>

A senha vem de ARQUIVO, nunca de argumento -- argumento aparece no `ps`, no
histórico do shell e no log. O arquivo e destruido ao final.

Mesmo padrao do gerar_env.py do MoviZap. Nada de senha ou hash e impresso.
"""
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/moviserver")
from passlib.context import CryptContext  # noqa: E402

BANCO = Path("/home/claude/moviserver/data/moviserver.db")

if len(sys.argv) < 3:
    sys.exit("uso: trocar_owner_moviserver.py <novo_login> <arquivo_com_a_senha>")

novo_login = sys.argv[1].strip()
arquivo_senha = Path(sys.argv[2])

if not novo_login or " " in novo_login:
    sys.exit("login invalido: vazio ou com espaco")
if not arquivo_senha.exists():
    sys.exit(f"nao encontrei {arquivo_senha}")

senha = arquivo_senha.read_text(encoding="utf-8").strip()
if len(senha) < 8:
    sys.exit("senha vazia ou curta demais -- abortando sem tocar no banco")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

conn = sqlite3.connect(BANCO)
conn.row_factory = sqlite3.Row

owners = conn.execute("SELECT login FROM painel_usuarios WHERE owner = 1").fetchall()
if len(owners) != 1:
    conn.close()
    sys.exit(f"esperava exatamente 1 owner, encontrei {len(owners)} -- abortando")

antigo = owners[0]["login"]

# Colisao de caixa: com a busca em COLLATE NOCASE, 'Admin' e 'admin' coexistindo
# tornariam o login ambiguo. Recusar antes de criar o problema.
colisao = conn.execute(
    "SELECT login FROM painel_usuarios WHERE login = ? COLLATE NOCASE AND owner = 0",
    (novo_login,),
).fetchall()
if colisao:
    conn.close()
    sys.exit(f"ja existe conta nao-owner com esse nome (ignorando caixa): {novo_login!r}")

novo_hash = pwd_ctx.hash(senha)

conn.execute(
    "UPDATE painel_usuarios SET login = ?, senha_hash = ? WHERE owner = 1",
    (novo_login, novo_hash),
)
conn.commit()

# ---- confirmar RELENDO o estado, nunca pelo retorno do UPDATE ----
linha = conn.execute(
    "SELECT login, senha_hash, owner, admin, ativo FROM painel_usuarios WHERE owner = 1"
).fetchone()
conn.close()

ok = (
    linha is not None
    and linha["login"] == novo_login
    and linha["owner"] == 1
    and linha["ativo"] == 1
    and pwd_ctx.verify(senha, linha["senha_hash"])
)

# destroi o temporario: sobrescreve antes de remover
tamanho = arquivo_senha.stat().st_size
with open(arquivo_senha, "wb") as f:
    f.write(b"\x00" * tamanho)
arquivo_senha.unlink()

if not ok:
    sys.exit("!! o estado relido NAO confere -- verifique o banco a mao")

print(f"owner: {antigo!r} -> {novo_login!r}")
print("senha: trocada e conferida contra o estado relido")
print(f"admin={linha['admin']} owner={linha['owner']} ativo={linha['ativo']}")
print(f"arquivo temporario destruido: {arquivo_senha}")
print("nenhum segredo foi impresso")
