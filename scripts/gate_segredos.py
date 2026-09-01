"""Trava de segredo do commit automatico.

Uso:  gate_segredos.py <caminho_do_repo>
Sai 0 = pode commitar.  Sai 1 = tem segredo, NAO commitar.

Varre exatamente o que `git add -A` colocaria no commit: todo arquivo
rastreado ou novo que o .gitignore NAO exclui. Arquivo ignorado nao entra
no commit, entao nao interessa aqui.

🚨 So padroes de ALTA confianca. A tentacao e varrer `senha=` tambem, mas
isso da 44 falsos positivos nos 5 repositorios -- e trava que sempre grita
vira trava que todo mundo ignora.

Nunca imprime o valor: so arquivo, linha e sha256[:8].
"""
import hashlib
import re
import subprocess
import sys
from pathlib import Path

PADROES = [
    ("chave LLM",          re.compile(r"\bsk-[A-Za-z0-9_\-]{16,}")),
    ("token Meta",         re.compile(r"\bEA[A-Za-z0-9]{60,}")),
    ("token GitHub",       re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}")),
    ("chave AWS",          re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("chave privada",      re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("URL com senha",      re.compile(r"://[^/\s:@]+:[^/\s:@]{6,}@[a-zA-Z0-9.-]+")),
    # Linha estilo .env. O NOME da variavel precisa dizer que aquilo e segredo:
    # sem isso, `LLM_PROCESSING_MODEL=llama-3.3-70b-versatile` vira alarme, e
    # trava que grita a toa e trava que todo mundo aprende a ignorar.
    ("linha .env com segredo", re.compile(
        r"^[A-Z][A-Z0-9_]*(KEY|TOKEN|SECRET|PASSWORD|SENHA|PASSWD|CREDENTIAL|DSN)"
        r"[A-Z0-9_]*=[^\s#]{16,}$")),
]

# `sk-...` e `sk-XXXX` sao exemplo em documentacao, nao chave.
# `{...}` e `${...}` sao template: `MOVIZAP_JWT_SECRET={secrets.token_urlsafe(48)}`
# e o CODIGO que gera o segredo, nao o segredo. `<...>` e lacuna a preencher.
EXEMPLO = re.compile(
    r"(?i)(\.\.\.|xxxx|<oculto>|abc123|troque|exemplo|placeholder|"
    r"\{[^}]*\}|\$\{|<[a-z_ ]+>|cole a chave)")

# 🚨 Adicionado em 31/08, autorizado por ele. "PUBLISHABLE_KEY" e o nome que
# o proprio Supabase da a metade do par que e SEGURA DE EXPOR -- vai no
# bundle do navegador por desenho (o oposto de "secret key"). Sem isto, todo
# projeto remixado do Lovable ficava bloqueado para sempre, so por isso.
#
# Restrito de proposito: so afasta o alarme da regra generica de "linha .env
# com segredo" (abaixo). Um `sk-...`, token de GitHub, chave AWS ou chave
# privada de verdade numa linha assim CONTINUAM sendo pegos -- essa excecao
# nao os desliga, so tira o falso positivo do nome da variavel.
LINHA_PUBLICA = re.compile(r"(?i)PUBLISHABLE_KEY=")

BINARIOS = (".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2",
            ".ttf", ".zip", ".gz", ".bundle", ".map", ".lock")

if len(sys.argv) < 2:
    sys.exit("uso: gate_segredos.py <repo>")

repo = Path(sys.argv[1])

listagem = subprocess.run(
    ["git", "-C", str(repo), "ls-files", "-co", "--exclude-standard"],
    capture_output=True, text=True,
)
if listagem.returncode != 0:
    print(f"  !! gate: nao consegui listar os arquivos de {repo}")
    sys.exit(1)   # falha fechado: na duvida, nao commita

achados = []
for relativo in listagem.stdout.splitlines():
    if relativo.endswith(BINARIOS):
        continue
    arquivo = repo / relativo
    try:
        if not arquivo.is_file() or arquivo.stat().st_size > 5_000_000:
            continue
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
    except OSError:
        continue
    for n, linha in enumerate(texto.splitlines(), 1):
        if EXEMPLO.search(linha):
            continue
        for rotulo, padrao in PADROES:
            m = padrao.search(linha)
            if m:
                if rotulo == "linha .env com segredo" and LINHA_PUBLICA.search(linha):
                    continue  # nome da variavel diz explicitamente "seguro expor"
                achados.append((relativo, n, rotulo,
                                hashlib.sha256(m.group(0).encode()).hexdigest()[:8]))
                break

if achados:
    print(f"  !! GATE BLOQUEOU {repo.name}: {len(achados)} segredo(s) no que seria commitado")
    for arq, n, rotulo, sha in achados[:10]:
        print(f"     {arq}:{n}  {rotulo}  sha256[:8]={sha}")
    if len(achados) > 10:
        print(f"     ... e mais {len(achados) - 10}")
    print("     Nada foi commitado neste repositorio. Corrija e rode de novo.")
    sys.exit(1)

sys.exit(0)
