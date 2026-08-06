"""Auditoria de segredo nos 5 repositorios versionados.

Nunca imprime valor. Para cada achado mostra arquivo, linha, tipo e as 8
primeiras letras do sha256 -- o suficiente para dizer se dois lugares tem o
MESMO segredo sem revelar nenhum dos dois.

Varre o HEAD e todo o historico alcancavel.
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPOS = [
    "/home/claude/IA_agente_Movichat",
    "/home/claude/fpsl_weso",
    "/home/claude/moviserver",
    "/home/claude/movibot",
    "/home/claude/movizap_painel",
]

# Cada padrao: (rotulo, regex). Deliberadamente largos: falso positivo custa
# uma olhada, falso negativo custa uma rotacao que nao acontece.
PADROES = [
    ("chave LLM (sk-)",        re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("token Meta/Bearer",      re.compile(r"\bEA[A-Za-z0-9]{40,}")),
    ("token GitHub",           re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("chave AWS",              re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave privada",          re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("URL com senha",          re.compile(r"://[^/\s:@]+:[^/\s:@]{4,}@")),
    ("atribuicao de senha",    re.compile(
        r"(?i)\b(senha|password|passwd|secret|api_key|apikey|token)\s*[=:]\s*"
        r"['\"]?([^\s'\"#,;)]{8,})")),
]

# Ruido conhecido: placeholder, exemplo, nome de variavel sem valor.
IGNORAR = re.compile(
    r"(?i)(<oculto>|xxxx|\.\.\.|troque|exemplo|placeholder|your[_-]|seu[_-]|"
    r"os\.environ|getenv|_ler\(|settings\.|\{\{|\$\{|f\"|%s)")


def digerir(valor: str) -> str:
    return hashlib.sha256(valor.encode()).hexdigest()[:8]


def rodar(repo: str, *args: str) -> str:
    r = subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True, text=True, errors="replace",
    )
    return r.stdout


achados = []

for repo in REPOS:
    nome = Path(repo).name
    if not Path(repo, ".git").exists():
        print(f"[--] {nome}: sem .git, pulado")
        continue

    commits = rodar(repo, "log", "--all", "--format=%H").split()
    arquivos = set()
    for c in commits:
        for linha in rodar(repo, "ls-tree", "-r", "--name-only", c).splitlines():
            arquivos.add((c, linha))

    vistos = set()
    for commit, arquivo in arquivos:
        if arquivo.endswith((".png", ".jpg", ".woff", ".woff2", ".pdf", ".ico", ".map")):
            continue
        conteudo = rodar(repo, "show", f"{commit}:{arquivo}")
        if not conteudo:
            continue
        for n, linha in enumerate(conteudo.splitlines(), 1):
            if IGNORAR.search(linha):
                continue
            for rotulo, padrao in PADROES:
                m = padrao.search(linha)
                if not m:
                    continue
                valor = m.group(2) if padrao.groups >= 2 else m.group(0)
                chave = (nome, arquivo, n, rotulo)
                if chave in vistos:
                    continue
                vistos.add(chave)
                achados.append({
                    "repo": nome, "arquivo": arquivo, "linha": n,
                    "tipo": rotulo, "sha": digerir(valor),
                    "no_head": commit == commits[0] if commits else False,
                })

    print(f"[ok] {nome}: {len(commits)} commit(s), {len(arquivos)} caminho(s) varrido(s)")

print()
if not achados:
    print("Nenhum segredo encontrado nos repositorios versionados.")
    sys.exit(0)

print(f"!! {len(achados)} ACHADO(S) -- valor nunca impresso, so o sha256[:8]\n")
larg = max(len(a["repo"]) for a in achados)
for a in sorted(achados, key=lambda x: (x["repo"], x["arquivo"], x["linha"])):
    marca = "HEAD" if a["no_head"] else "hist"
    print(f"  [{marca}] {a['repo']:<{larg}}  {a['arquivo']}:{a['linha']}")
    print(f"         {a['tipo']}  sha256[:8]={a['sha']}")

print("\nsha256 igual em dois lugares = MESMO segredo nos dois.")
