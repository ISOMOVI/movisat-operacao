"""Remove a chave DeepSeek do PROJETO.md do MoviChat.

Monta o texto novo em memoria, VALIDA o candidato e so entao grava -- nunca
o contrario. Nao imprime nenhum valor: so a contagem e o sha256[:8].

Nao commita e nao empurra nada. So corrige o arquivo de trabalho.
"""
import hashlib
import re
import sys
from pathlib import Path

ALVO = Path("/home/claude/IA_agente_Movichat/PROJETO.md")
CHAVE = re.compile(r"sk-[A-Za-z0-9_\-]{16,}")
SUBSTITUTO = "**[ler do .env: DEEPSEEK_API_KEY]**"

original = ALVO.read_text(encoding="utf-8")
achados = CHAVE.findall(original)

if not achados:
    print("Nada a fazer: nenhuma chave sk- em PROJETO.md")
    sys.exit(0)

for a in sorted(set(achados)):
    print(f"  encontrada  sha256[:8]={hashlib.sha256(a.encode()).hexdigest()[:8]}"
          f"  tamanho={len(a)}")

# O candidato: chave trocada pelo ponteiro para o .env, e a crase que a
# envolvia removida junto (senao sobra `**[ler...]**` dentro de codigo).
candidato = CHAVE.sub("SEGREDO", original)
candidato = candidato.replace("`SEGREDO`", SUBSTITUTO)
candidato = candidato.replace("SEGREDO...", SUBSTITUTO)
candidato = candidato.replace("SEGREDO", SUBSTITUTO)

# ---- validar ANTES de gravar ----
falhas = []
if CHAVE.search(candidato):
    falhas.append("ainda ha chave sk- no candidato")
if "DEEPSEEK_API_KEY" not in candidato:
    falhas.append("o ponteiro para o .env sumiu")
if len(candidato.splitlines()) != len(original.splitlines()):
    falhas.append("o numero de linhas mudou -- substituicao comeu quebra de linha")
if SUBSTITUTO not in candidato:
    falhas.append("o substituto nao entrou")

if falhas:
    print("\nNAO GRAVEI. O candidato falhou na validacao:")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)

ALVO.write_text(candidato, encoding="utf-8")
print(f"\nPROJETO.md limpo: {len(achados)} ocorrencia(s) substituida(s)")
print("Historico do git NAO foi tocado -- a chave continua no commit ja empurrado.")
print("A unica correcao que vale para isso e ROTACIONAR a chave.")
