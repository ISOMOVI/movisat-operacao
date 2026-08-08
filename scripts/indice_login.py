"""Índice único em lower(login) nos painéis que guardam usuário em sqlite.

🚨 POR QUE ISTO PRECISA EXISTIR AGORA

Em 07/08 as buscas de login dos quatro painéis passaram a IGNORAR MAIÚSCULA --
correção certa, porque exigir a caixa exata recusava o dono do sistema com a
senha certa e sem dar pista.

Mas ignorar a caixa na LEITURA sem garantir unicidade na ESCRITA cria um
buraco novo: nada impede criar `Admin` ao lado de `admin`, e aí a autenticação
fica ambígua -- duas contas, senhas diferentes, e a consulta devolve a
primeira que o banco entregar. O sintoma seria "às vezes entra, às vezes não".

⚠️ Conferido antes de criar: zero colisões nos dois bancos. Se houvesse, o
índice falharia -- e falhar aqui é melhor que escolher uma conta por sorteio.

Uso:  ./venv/bin/python indice_login.py [--aplicar]
"""
import argparse
import sqlite3
import sys

BANCOS = [
    ("FPSL", "/home/claude/fpsl_weso/data/fpsl.db", "painel_usuarios"),
    ("MoviServer", "/home/claude/moviserver/data/moviserver.db", "painel_usuarios"),
]
NOME_INDICE = "ux_painel_usuarios_login"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--aplicar", action="store_true")
    args = parser.parse_args()

    for nome, caminho, tabela in BANCOS:
        con = sqlite3.connect(caminho, timeout=15)
        colisoes = con.execute(
            f"SELECT lower(login), COUNT(*) FROM {tabela} "
            f"GROUP BY 1 HAVING COUNT(*) > 1").fetchall()
        ja = con.execute(
            "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?",
            (NOME_INDICE,)).fetchone()

        print(f"{nome}: {con.execute(f'SELECT COUNT(*) FROM {tabela}').fetchone()[0]} "
              f"usuário(s), {len(colisoes)} colisão(ões), "
              f"índice {'já existe' if ja else 'ausente'}")

        if colisoes:
            print(f"   🚨 NÃO aplico: {colisoes} -- resolva a duplicidade antes")
            con.close()
            continue
        if ja or not args.aplicar:
            con.close()
            continue

        con.execute(f"CREATE UNIQUE INDEX {NOME_INDICE} ON {tabela}(lower(login))")
        con.commit()
        # A única prova é reler.
        conferido = con.execute(
            "SELECT sql FROM sqlite_master WHERE type='index' AND name=?",
            (NOME_INDICE,)).fetchone()
        print(f"   criado e conferido: {bool(conferido)}")
        con.close()

    if not args.aplicar:
        print("\n(simulação -- rode com --aplicar)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
