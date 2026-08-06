"""Triagem dos achados: mostra a LINHA com o valor mascarado.

Serve para decidir se um casamento e segredo de verdade ou nome de variavel.
Um exemplo por sha256 distinto -- se o hash se repete, a linha e a mesma
classe de coisa.
"""
import re
import subprocess
import hashlib
from pathlib import Path

REPOS = [
    "/home/claude/IA_agente_Movichat",
    "/home/claude/fpsl_weso",
    "/home/claude/moviserver",
    "/home/claude/movibot",
    "/home/claude/movizap_painel",
]

PADRAO = re.compile(
    r"(?i)\b(senha|password|passwd|secret|api_key|apikey|token)\s*[=:]\s*"
    r"['\"]?([^\s'\"#,;)]{8,})")
IGNORAR = re.compile(
    r"(?i)(<oculto>|xxxx|\.\.\.|troque|exemplo|placeholder|your[_-]|seu[_-]|"
    r"os\.environ|getenv|_ler\(|settings\.|\{\{|\$\{|f\"|%s)")

vistos = {}

for repo in REPOS:
    nome = Path(repo).name
    if not Path(repo, ".git").exists():
        continue
    commits = subprocess.run(["git", "-C", repo, "log", "--all", "--format=%H"],
                             capture_output=True, text=True).stdout.split()
    for c in commits:
        arquivos = subprocess.run(["git", "-C", repo, "ls-tree", "-r", "--name-only", c],
                                  capture_output=True, text=True).stdout.splitlines()
        for arq in arquivos:
            if arq.endswith((".png", ".jpg", ".woff", ".woff2", ".pdf", ".ico", ".map")):
                continue
            texto = subprocess.run(["git", "-C", repo, "show", f"{c}:{arq}"],
                                   capture_output=True, text=True, errors="replace").stdout
            for n, linha in enumerate(texto.splitlines(), 1):
                if IGNORAR.search(linha):
                    continue
                m = PADRAO.search(linha)
                if not m:
                    continue
                valor = m.group(2)
                sha = hashlib.sha256(valor.encode()).hexdigest()[:8]
                if sha in vistos:
                    vistos[sha]["vezes"] += 1
                    continue
                mascarada = linha.replace(valor, "<VALOR:" + sha + ">").strip()
                vistos[sha] = {
                    "onde": f"{nome}/{arq}:{n}",
                    "linha": mascarada[:150],
                    "vezes": 1,
                }

print(f"{len(vistos)} valor(es) distinto(s):\n")
for sha, d in sorted(vistos.items(), key=lambda x: -x[1]["vezes"]):
    print(f"  {sha}  ({d['vezes']}x)  {d['onde']}")
    print(f"      {d['linha']}")
    print()
