"""Substitui um valor lido de .env por um placeholder, dentro de um arquivo.

Uso:  scrub_valor.py <arquivo_env> <CHAVE> <arquivo_alvo> <placeholder>

O valor NUNCA e digitado nem impresso: sai do .env e vai direto para o
replace. Valida antes de gravar e confirma relendo o arquivo.
"""
import hashlib
import sys
from pathlib import Path

if len(sys.argv) < 5:
    sys.exit("uso: scrub_valor.py <arquivo_env> <CHAVE> <arquivo_alvo> <placeholder>")

env, chave, alvo, placeholder = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3]), sys.argv[4]

valor = ""
for l in env.read_text(encoding="utf-8").splitlines():
    if l.startswith(chave + "="):
        valor = l.split("=", 1)[1].strip()
        break

if not valor:
    sys.exit(f"{chave} nao encontrada em {env}")

original = alvo.read_text(encoding="utf-8")
if valor not in original:
    print(f"{alvo.name}: o valor ja nao esta la. Nada a fazer.")
    sys.exit(0)

vezes = original.count(valor)
print(f"  {alvo.name}: {vezes} ocorrencia(s)  "
      f"sha256[:8]={hashlib.sha256(valor.encode()).hexdigest()[:8]}")

candidato = original.replace(valor, placeholder)

falhas = []
if valor in candidato:
    falhas.append("o valor continua no candidato")
if len(candidato.splitlines()) != len(original.splitlines()):
    falhas.append("o numero de linhas mudou")
if placeholder not in candidato:
    falhas.append("o placeholder nao entrou")

if falhas:
    print("NAO GRAVEI:")
    for f in falhas:
        print(f"  - {f}")
    sys.exit(1)

alvo.write_text(candidato, encoding="utf-8")

# confirma RELENDO, nunca pelo retorno da escrita
if valor in alvo.read_text(encoding="utf-8"):
    sys.exit("!! releitura ainda encontra o valor -- verifique a mao")

print(f"  {alvo.name}: limpo e confirmado por releitura")
