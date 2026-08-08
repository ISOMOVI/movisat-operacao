"""Prova que o LOGIN é encontrado nos QUATRO painéis, sem conhecer a senha.

O truque é o TEMPO. Quando o nome não existe, a busca devolve None e a rota
responde em poucos ms -- nem chega no bcrypt. Quando o nome existe, o bcrypt
roda antes de recusar e a resposta leva centenas de ms.

🚨 POR QUE ESTE ARQUIVO FOI REESCRITO EM 07/08

A versão anterior fazia o teste certo e **só olhava um alvo por vez**, com o
MoviZap como padrão. Foi escrita em 05/08 por causa deste mesmo defeito no
MoviZap -- e nunca foi apontada para os outros três. Resultado: em 07/08 o
dono do sistema ficou de fora do FPSL com a senha certa, e o MoviChat estava
com o mesmo defeito em três caminhos, atingindo 6 logins de clientes reais.

O defeito não escapou da auditoria. Escapou do ALCANCE dela.

A regra que ficou: **defeito achado em um painel vira verificação nos outros
três, na mesma sessão** -- os quatro compartilham a linhagem do código.

🚨 SEGUNDA CORREÇÃO: a versão anterior lia **404 como "usuário não
encontrado"**. Ao errar a rota do MoviServer e do MoviChat, ela gritou FALHA
com confiança total. Auditoria que confunde "endereço errado" com "defeito"
gasta o próprio crédito, e aí ninguém mais roda. Agora 404 e 429 têm nome.

Uso:
    verificar_login.py                 # os quatro painéis
    verificar_login.py MoviChat        # só um
"""
import json
import sys
import time
import urllib.error
import urllib.request

# ⚠️ O `login` é um nome que EXISTE naquele painel -- o teste precisa dele para
# comparar com o caso "inexistente". Nenhuma senha aqui: o sinal é o tempo.
# O MoviChat não tem `admin` na tabela de administradores; usa-se um login de
# empresa real, que é o caminho que mais importa (são 6 clientes).
PAINEIS = [
    {"nome": "MoviZap",    "base": "http://127.0.0.1:8008", "rota": "/api/sessao/login",  "login": "admin"},
    {"nome": "FPSL",       "base": "http://127.0.0.1:8004", "rota": "/painel/api/login",  "login": "admin"},
    {"nome": "MoviServer", "base": "http://127.0.0.1:8007", "rota": "/api/login",         "login": "admin"},
    {"nome": "MoviChat",   "base": "http://127.0.0.1:8002", "rota": "/api/auth/login",    "login": "xomv"},
]

SENHA_ERRADA = "senha-propositalmente-errada-para-medir-tempo"
LIMITE_MS = 20      # abaixo disso, o bcrypt não rodou
INEXISTENTE = "nome-que-nao-existe-em-painel-nenhum"


def tentar(base: str, rota: str, login: str) -> tuple[int, float]:
    corpo = json.dumps({"login": login, "senha": SENHA_ERRADA}).encode()
    req = urllib.request.Request(
        base + rota, data=corpo,
        headers={"Content-Type": "application/json"}, method="POST")
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status = e.code
        e.read()
    except urllib.error.URLError:
        return 0, 0.0
    return status, (time.perf_counter() - inicio) * 1000


def verificar(painel: dict) -> bool:
    print(f"=== {painel['nome']}  ({painel['base']}{painel['rota']}) ===")
    login = painel["login"]
    ok = True

    for variante in (login, login.upper(), f"  {login}  "):
        status, ms = tentar(painel["base"], painel["rota"], variante)

        # 🚨 Cada um destes tem NOME próprio. Tratar todos como "não encontrado"
        # foi o furo da versão anterior.
        if status == 0:
            print(f"  [ERRO ] {variante!r:14} -> serviço não respondeu")
            ok = False
        elif status == 404:
            print(f"  [ROTA ] {variante!r:14} -> 404: a rota está errada, "
                  f"não é defeito de login")
            ok = False
        elif status == 429:
            print(f"  [TRAVA] {variante!r:14} -> 429: limite de tentativas. "
                  f"Resultado INCONCLUSIVO, espere e rode de novo")
            ok = False
        elif ms < LIMITE_MS:
            print(f"  [FALHA] {variante!r:14} -> {status} em {ms:6.1f}ms   "
                  f"nome NÃO encontrado (bcrypt não rodou)")
            ok = False
        else:
            print(f"  [OK   ] {variante!r:14} -> {status} em {ms:6.1f}ms   "
                  f"nome encontrado (bcrypt rodou)")

    status, ms = tentar(painel["base"], painel["rota"], INEXISTENTE)
    if status in (404, 429, 0):
        print(f"  [?    ] {'inexistente':14} -> {status}, inconclusivo")
    elif ms < LIMITE_MS:
        print(f"  [OK   ] {'inexistente':14} -> {status} em {ms:6.1f}ms   "
              f"recusado antes do bcrypt, correto")
    else:
        # Não é defeito de segurança, mas é sinal de que o teste do tempo
        # deixou de valer para este painel -- e alguém precisa saber.
        print(f"  [AVISO] {'inexistente':14} -> {status} em {ms:6.1f}ms   "
              f"demorou: o sinal do tempo não separa mais os casos aqui")
    print()
    return ok


def main() -> int:
    alvos = PAINEIS
    if len(sys.argv) > 1:
        pedido = sys.argv[1].casefold()
        alvos = [p for p in PAINEIS if p["nome"].casefold() == pedido]
        if not alvos:
            return print(f"painel desconhecido: {sys.argv[1]}") or 2

    print("Todas as tentativas usam senha errada de propósito -- o sinal é o TEMPO.")
    print("⚠️ Cada execução gasta 4 tentativas por painel; o limite trava em 5 "
          "por 5 min.\n")

    falharam = [p["nome"] for p in alvos if not verificar(p)]

    if falharam:
        print("!! PRECISA DE OLHO: " + ", ".join(falharam))
        return 1
    print("Os quatro painéis encontram o login em qualquer caixa, com ou sem "
          "espaço, e nome inexistente continua recusado antes do bcrypt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
