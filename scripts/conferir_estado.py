"""Confere o estado real contra o que o Proximos_Passos afirma.

Existe porque afirmar de memoria e o erro que o Bloco 1 item 4 proibe:
"memoria e retrato, nao estado ao vivo".
"""
import sys

print("== migracoes do MoviZap ==")
sys.path.insert(0, "/home/claude/movizap_painel")
from movizap import banco  # noqa: E402
banco.abrir()
for r in banco.varios("SELECT versao, descricao FROM schema_migracao ORDER BY versao"):
    print(f"  {r['versao']}  {r['descricao'][:56]}")
canais = banco.varios("SELECT nome, instancia FROM canal")
print(f"  canais cadastrados: {len(canais)} -- "
      + ", ".join(c["instancia"] for c in canais))
ev = banco.um("SELECT COUNT(*) AS n FROM canal_evento")
print(f"  eventos de canal: {ev['n']}")
banco.fechar()

print("\n== quadros do painel rapido ==")
sys.path.insert(0, "/home/claude/fpsl_weso")
from fpsl_weso import demandas as d  # noqa: E402
for q in d.listar_quadros():
    qq = d.quadro(q["token"])
    print(f"  {q['titulo']:<32} modo={qq['modo']:<9} "
          f"{qq['total']:>2} tarefas  {qq['concluidos']} ok  "
          f"{len(qq['pessoas'])} pessoas")

print("\n== documentacao ==")
from pathlib import Path  # noqa: E402
for base in ("/home/claude/docs", "/home/claude/movizap_painel/docs"):
    arquivos = sorted(Path(base).glob("*.md"))
    print(f"  {base}: {len(arquivos)} doc(s)")
    for a in arquivos:
        print(f"     {a.name}")
