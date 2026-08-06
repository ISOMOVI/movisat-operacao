"""Tira a senha do banco do codigo-fonte e do .env.example do hub-fotos.

Achado em 05/08: a MESMA DATABASE_URL, com senha de producao, estava em tres
lugares -- .env (certo), .env.example (modo 664, qualquer um le) e fixa no
backend/database.py como valor padrao do os.getenv.

O hub-fotos ainda nao e versionado. Se fosse, teria vazado junto com os
outros. Corrigir antes e mais barato que rotacionar depois.

Depois da correcao:
  - .env.example passa a ter placeholder;
  - database.py FALHA ALTO se DATABASE_URL nao existir, em vez de conectar
    silenciosamente com credencial embutida. Falha fechado.

Valida ANTES de gravar. Nao imprime valor.
"""
import hashlib
import re
import sys
from pathlib import Path

BASE = Path("/home/claude/hub-fotos")
ENV = BASE / ".env"
EXEMPLO = BASE / ".env.example"
CODIGO = BASE / "backend/database.py"

def val(caminho: Path, chave: str) -> str:
    if not caminho.exists():
        return ""
    for l in caminho.read_text(encoding="utf-8").splitlines():
        if l.startswith(chave + "="):
            return l.split("=", 1)[1].strip()
    return ""

real = val(ENV, "DATABASE_URL")
if not real:
    sys.exit("DATABASE_URL nao esta no .env -- abortando, nao vou quebrar o app")

print(f"  senha de producao  sha256[:8]={hashlib.sha256(real.encode()).hexdigest()[:8]}")

PLACEHOLDER = "postgresql://USUARIO:SENHA@localhost/hubfotos"
falhou = []

# ---------- 1. .env.example ----------
ex_original = EXEMPLO.read_text(encoding="utf-8")
ex_candidato = ex_original.replace(real, PLACEHOLDER)
if real in ex_candidato:
    falhou.append(".env.example: a senha continua no candidato")
elif "DATABASE_URL=" not in ex_candidato:
    falhou.append(".env.example: a chave DATABASE_URL sumiu")

# ---------- 2. database.py ----------
cod_original = CODIGO.read_text(encoding="utf-8")
NOVO_TRECHO = (
    "DATABASE_URL = os.getenv('DATABASE_URL')\n"
    "if not DATABASE_URL:\n"
    "    # Falha fechado: antes havia uma credencial de producao embutida aqui\n"
    "    # como valor padrao, o que fazia o app conectar mesmo sem .env -- e\n"
    "    # deixava a senha no codigo. Melhor nao subir do que subir assim.\n"
    "    raise RuntimeError(\n"
    "        'DATABASE_URL ausente. Defina no .env -- nunca no codigo.'\n"
    "    )"
)
cod_candidato = re.sub(
    r"^DATABASE_URL = os\.getenv\('DATABASE_URL',\s*'[^']*'\)$",
    NOVO_TRECHO, cod_original, flags=re.M,
)
if real in cod_candidato:
    falhou.append("database.py: a senha continua no candidato")
elif cod_candidato == cod_original:
    falhou.append("database.py: a linha nao casou com o formato esperado")
elif "create_engine(DATABASE_URL" not in cod_candidato:
    falhou.append("database.py: o resto do arquivo se perdeu")
else:
    import ast
    try:
        ast.parse(cod_candidato)
    except SyntaxError as e:
        falhou.append(f"database.py: o candidato nao compila ({e})")

if falhou:
    print("\nNAO GRAVEI NADA:")
    for f in falhou:
        print(f"  - {f}")
    sys.exit(1)

EXEMPLO.write_text(ex_candidato, encoding="utf-8")
CODIGO.write_text(cod_candidato, encoding="utf-8")

print("\n.env.example    : senha -> placeholder")
print("database.py     : padrao embutido -> falha alta se faltar DATABASE_URL")
print(f".env            : INTACTO (modo {oct(ENV.stat().st_mode)[-3:]})")
