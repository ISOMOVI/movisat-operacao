"""Prova que o LOGIN e encontrado, sem conhecer a senha.

O truque e o TEMPO. Quando o nome nao existe, `buscar_usuario` devolve None e
a rota responde em ~1ms -- nem chega no bcrypt. Quando o nome existe, o bcrypt
roda antes de recusar, e a resposta leva dezenas de milissegundos.

Foi exatamente essa assinatura (401 em 1ms) que identificou o problema de
05/08. Aqui ela vira teste.

Uso:  verificar_login.py <base_url> <nome_configurado>
"""
import json
import sys
import time
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8008"
NOME = sys.argv[2] if len(sys.argv) > 2 else "Admin"
ROTA = sys.argv[3] if len(sys.argv) > 3 else "/api/sessao/login"

SENHA_ERRADA = "senha-propositalmente-errada-para-medir-tempo"
LIMITE_MS = 20   # abaixo disso, o bcrypt nao rodou


def tentar(login):
    corpo = json.dumps({"login": login, "senha": SENHA_ERRADA}).encode()
    req = urllib.request.Request(
        BASE + ROTA, data=corpo,
        headers={"Content-Type": "application/json"}, method="POST",
    )
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        e.read()
    ms = (time.perf_counter() - inicio) * 1000
    return status, ms


print(f"Alvo: {BASE}{ROTA}   nome configurado: {NOME!r}")
print("Todas as tentativas usam senha errada de proposito -- o sinal e o TEMPO.\n")

# Primeira chamada aquece o processo; nao entra no julgamento.
tentar("aquecimento-" + NOME)

falhas = []
variantes = [NOME, NOME.upper(), NOME.lower(), NOME.swapcase()]
for v in dict.fromkeys(variantes):
    status, ms = tentar(v)
    achou = ms >= LIMITE_MS
    marca = "OK  " if achou and status == 401 else "FALHA"
    print(f"  [{marca}] {v!r:<12} -> {status} em {ms:6.1f}ms   "
          f"{'nome ENCONTRADO (bcrypt rodou)' if achou else 'nome NAO encontrado'}")
    if not achou:
        falhas.append(v)

status, ms = tentar("nome-que-nao-existe-mesmo")
esperado = ms < LIMITE_MS
marca = "OK  " if esperado else "FALHA"
print(f"  [{marca}] {'inexistente':<12} -> {status} em {ms:6.1f}ms   "
      f"{'recusado antes do bcrypt, correto' if esperado else 'demorou demais'}")
if not esperado:
    falhas.append("controle negativo")

print()
if falhas:
    print("!! FALHOU para: " + ", ".join(map(repr, falhas)))
    sys.exit(1)
print("O login e encontrado em qualquer caixa, e nome inexistente continua recusado.")
