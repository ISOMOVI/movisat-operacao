"""Acrescenta os arquivos-satelite do SQLite WAL ao .gitignore dos repositorios.

Achado em 05/08, ao conferir o `git status` antes de commitar: o .gitignore
tinha `*.db`, mas o modo WAL cria TAMBEM `.db-wal` e `.db-shm`, que `*.db`
nao casa. Eles iam entrar no commit -- carregando IP e nome de login de quem
errou a senha, e sujando todo diff com dado de runtime.

Valida antes de gravar. Idempotente: rodar duas vezes nao duplica.
"""
import sys
from pathlib import Path

REPOS = [
    "/home/claude/movizap_painel",
    "/home/claude/fpsl_weso",
    "/home/claude/moviserver",
    "/home/claude/IA_agente_Movichat",
    "/home/claude/movibot",
]

BLOCO = """
# ---- satelites do SQLite em modo WAL ----
# `*.db` NAO casa com estes. Sao estado de runtime e, no caso do contador de
# tentativas de login, carregam IP e nome de conta.
*.db-wal
*.db-shm
*.db-journal
"""

for caminho in REPOS:
    alvo = Path(caminho) / ".gitignore"
    if not alvo.exists():
        print(f"  {Path(caminho).name}: sem .gitignore -- pulado")
        continue

    original = alvo.read_text(encoding="utf-8")
    if "*.db-wal" in original:
        print(f"  {Path(caminho).name}: ja tinha")
        continue

    candidato = original.rstrip("\n") + "\n" + BLOCO

    falhas = []
    if "*.db-wal" not in candidato or "*.db-shm" not in candidato:
        falhas.append("os padroes nao entraram")
    if not candidato.startswith(original.rstrip("\n")[:40]):
        falhas.append("o conteudo original se perdeu")
    if len(candidato) <= len(original):
        falhas.append("o arquivo encolheu")

    if falhas:
        print(f"  {Path(caminho).name}: NAO GRAVEI -- {'; '.join(falhas)}")
        sys.exit(1)

    alvo.write_text(candidato, encoding="utf-8")
    print(f"  {Path(caminho).name}: 3 padroes acrescentados")
