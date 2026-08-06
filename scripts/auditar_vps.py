"""Auditoria de exposicao de segredo em TODA a VPS, nao so nos repositorios.

A auditoria de 05/08 olhou o que estava no git. Este script olha o resto:
projetos sem versionamento, logs, backups, unidades systemd, cron, e as
PERMISSOES -- um .env correto com modo 644 e exposicao tambem.

Nunca imprime valor: so caminho, linha, tipo e sha256[:8].

Uso:  auditar_vps.py
"""
import hashlib
import os
import re
import stat
import subprocess
import sys
from pathlib import Path

RAIZ = Path("/home/claude")

# Diretorios que nao interessam: dependencia de terceiro e ruido puro.
PULAR_DIR = {
    "venv", "node_modules", "__pycache__", ".git", ".pytest_cache",
    "site-packages", ".cache", ".npm", "base_manuais", ".vite",
}
PULAR_EXT = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2",
    ".ttf", ".zip", ".gz", ".xz", ".bundle", ".map", ".so", ".pyc",
    ".db", ".sqlite", ".sqlite3", ".xls", ".xlsx", ".whl",
}

PADROES = [
    ("chave LLM",       re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("chave Groq",      re.compile(r"\bgsk_[A-Za-z0-9]{20,}")),
    ("token Meta",      re.compile(r"\bEA[A-Za-z0-9]{60,}")),
    ("token GitHub",    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("chave AWS",       re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave privada",   re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("URL com senha",   re.compile(r"://[^/\s:@]+:[^/\s:@]{6,}@[a-zA-Z0-9.-]+")),
    ("var de segredo",  re.compile(
        r"^[A-Z][A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|SENHA|PASSWD|CREDENTIAL|DSN)"
        r"[A-Z0-9_]*=[^\s#]{16,}$")),
]
EXEMPLO = re.compile(
    r"(?i)(\.\.\.|xxxx|<oculto>|abc123|troque|exemplo|placeholder|cole a chave|"
    r"\{[^}]*\}|\$\{|<[a-z_ ]+>|your[_-]|seu[_-])")

# Onde segredo PODE morar. Aqui o problema nao e existir, e a permissao.
LEGITIMOS = re.compile(r"(^|/)\.env(\.|$)|/\.ssh/|\.pem$|\.key$")

achados = []
permissoes = []
digerir = lambda v: hashlib.sha256(v.encode()).hexdigest()[:8]


def varrer(base: Path, rotulo: str):
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in PULAR_DIR]
        for nome in filenames:
            caminho = Path(dirpath) / nome
            rel = str(caminho)
            if caminho.suffix.lower() in PULAR_EXT:
                continue
            try:
                if not caminho.is_file() or caminho.stat().st_size > 3_000_000:
                    continue
                modo = stat.S_IMODE(caminho.lstat().st_mode)
                texto = caminho.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            legitimo = bool(LEGITIMOS.search(rel))
            if legitimo:
                # o problema aqui nao e o conteudo, e quem consegue ler
                if modo & 0o077:
                    permissoes.append((rel, oct(modo)[-3:]))
                continue

            for n, linha in enumerate(texto.splitlines(), 1):
                if EXEMPLO.search(linha):
                    continue
                for tipo, padrao in PADROES:
                    m = padrao.search(linha)
                    if m:
                        achados.append((rotulo, rel, n, tipo, digerir(m.group(0))))
                        break


print("== varrendo /home/claude ==")
varrer(RAIZ, "projeto")

print("== unidades systemd do usuario ==")
sysd = Path.home() / ".config/systemd/user"
if sysd.exists():
    varrer(sysd, "systemd")

print("== crontab ==")
cron = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
for n, linha in enumerate(cron.splitlines(), 1):
    if EXEMPLO.search(linha):
        continue
    for tipo, padrao in PADROES:
        m = padrao.search(linha)
        if m:
            achados.append(("cron", "crontab -l", n, tipo, digerir(m.group(0))))
            break

print()
if achados:
    print(f"!! {len(achados)} SEGREDO(S) FORA DE LUGAR -- valor nunca impresso\n")
    for rotulo, arq, n, tipo, sha in sorted(achados):
        print(f"  [{rotulo}] {arq}:{n}")
        print(f"      {tipo}  sha256[:8]={sha}")
else:
    print("Nenhum segredo fora de .env / .ssh / chave privada.")

print()
if permissoes:
    print(f"!! {len(permissoes)} ARQUIVO(S) DE SEGREDO LEGIVEL POR OUTROS:\n")
    for arq, modo in sorted(permissoes):
        print(f"  {modo}  {arq}")
else:
    print("Todo arquivo de segredo esta restrito ao dono (modo 600 ou 700).")

sys.exit(1 if (achados or permissoes) else 0)
