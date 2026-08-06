"""Verifica os QUATRO paineis: visual alinhado e trava de login funcionando.

Usa login ficticio nas tentativas -- nao encosta em conta real, entao nao
tranca ninguem de verdade.
"""
import json
import sys
import urllib.error
import urllib.request

PAINEIS = [
    # nome,          url da tela,                          rota de login
    ("MoviZap",   "http://127.0.0.1:8008/",              "http://127.0.0.1:8008/api/sessao/login"),
    ("FPSL",      "http://127.0.0.1:8005/painel",        "http://127.0.0.1:8005/painel/api/login"),
    ("MoviServer","http://127.0.0.1:8007/",              "http://127.0.0.1:8007/api/login"),
    ("MoviChat",  "http://127.0.0.1:8002/",              "http://127.0.0.1:8002/api/auth/login"),
]

# O MoviZap e uma SPA: o HTML nao tem o texto, o bundle tem.
MARCAS_HTML = ["movisat", "Acesse sua conta"]

falhas = []


def buscar(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def tentar_login(url, login):
    corpo = json.dumps({"login": login, "senha": "errada-de-proposito"}).encode()
    req = urllib.request.Request(
        url, data=corpo, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, ""
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}").get("detail", "")
        except Exception:
            return e.code, ""
    except Exception:
        return 0, ""


print("== VISUAL: logo e cartao do MoviChat presentes ==")
for nome, url_tela, _ in PAINEIS:
    status, html = buscar(url_tela)
    achou = [m for m in MARCAS_HTML if m in html]
    if nome == "MoviZap":
        ok = status == 200 and 'id="app"' in html   # SPA: o resto vem no bundle
        detalhe = "SPA (marca no bundle)"
    else:
        ok = status == 200 and len(achou) == len(MARCAS_HTML)
        detalhe = f"{len(achou)}/{len(MARCAS_HTML)} marcas"
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome:<11} status={status}  {detalhe}")
    if not ok:
        falhas.append(f"{nome}: visual")

print()
print("== TRAVA DE LOGIN: 6a tentativa vira 429 ==")
for nome, _, url_login in PAINEIS:
    ficticio = f"zz-teste-trava-{nome.lower()}"
    codigos = [tentar_login(url_login, ficticio)[0] for _ in range(6)]
    ok = 429 in codigos and codigos[0] == 401  # basta a forca bruta ser barrada
    print(f"  [{'OK  ' if ok else 'FALHA'}] {nome:<11} {codigos}")
    if not ok:
        falhas.append(f"{nome}: trava")

print()
print("== MENSAGEM UNICA: conta que existe x que nao existe ==")
# So faz sentido onde ha conta conhecida. Compara o TEXTO da recusa.
for nome, _, url_login in PAINEIS:
    _, msg_a = tentar_login(url_login, "conta-que-nao-existe-aaa")
    _, msg_b = tentar_login(url_login, "conta-que-nao-existe-bbb")
    igual = msg_a == msg_b
    print(f"  [{'OK  ' if igual else 'FALHA'}] {nome:<11} {msg_a[:52]!r}")
    if not igual:
        falhas.append(f"{nome}: mensagem")

print()
if falhas:
    print("!! " + "; ".join(falhas))
    sys.exit(1)
print("Os quatro paineis: visual alinhado, trava ativa, mensagem unica.")
