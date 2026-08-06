#!/bin/bash
# Commit automatico diario dos projetos Movisat -- criado 2026-08-04.
# Nao substitui commit manual: so garante que o trabalho do dia nao se perca.
#
# 2026-08-05: ganhou TRAVA DE SEGREDO. Em 04/08 este script empurrou a chave
# DeepSeek dentro do PROJETO.md do MoviChat e o GitGuardian avisou no dia
# seguinte. O `.gitignore` protegia .env -- e nao adiantou, porque o segredo
# estava numa TABELA DE DOCUMENTACAO. Confiar no .gitignore e confiar que
# ninguem vai colar uma credencial num .md.
#
# A trava roda ANTES do `git add`. Repositorio bloqueado e pulado; os outros
# seguem. Falha do proprio gate tambem bloqueia -- falha fechado.

REPOS="/home/claude/moviserver /home/claude/movibot /home/claude/IA_agente_Movichat /home/claude/fpsl_weso /home/claude/movizap_painel"
GATE="/home/claude/scripts/gate_segredos.py"
HOJE=$(date +%Y-%m-%d)
TS=$(date +'%Y-%m-%d %H:%M:%S')
BLOQUEADOS=0

for REPO in $REPOS; do
    NOME=$(basename "$REPO")

    if ! cd "$REPO" 2>/dev/null; then
        echo "$TS  $NOME: diretorio inacessivel"
        continue
    fi

    if [ -z "$(git status --porcelain)" ]; then
        echo "$TS  $NOME: sem mudancas"
        continue
    fi

    # ---- trava de segredo ----
    if ! python3 "$GATE" "$REPO"; then
        echo "$TS  $NOME: BLOQUEADO PELA TRAVA DE SEGREDO -- nada commitado"
        BLOQUEADOS=$((BLOQUEADOS + 1))
        continue
    fi

    git add -A
    if git commit -q -m "auto: $HOJE"; then
        if git push -q origin main 2>/dev/null; then
            echo "$TS  $NOME: commit + push OK"
        else
            echo "$TS  $NOME: commit OK, push FALHOU (rede? credencial?)"
        fi
    else
        echo "$TS  $NOME: commit falhou"
    fi
done

if [ "$BLOQUEADOS" -gt 0 ]; then
    echo "$TS  !! $BLOQUEADOS repositorio(s) bloqueado(s) por segredo -- OLHE ESTE LOG"
fi
