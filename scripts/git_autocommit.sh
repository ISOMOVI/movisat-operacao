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
#
# 2026-08-14: ARVORE LIMPA NAO SIGNIFICA SINCRONIZADO. Ate hoje o script
# fazia `continue` assim que via `git status` vazio, e commit feito a mao
# nunca era empurrado: o fpsl_weso acumulou 13 commits so na VPS, e o log
# dizia "sem mudancas" todo dia -- parecia estar tudo em ordem. Agora, arvore
# limpa com commit local adiantado ainda faz push.

# movisat-operacao entrou em 06/08: e o 6o repositorio, e guarda ESTE script.
# 2026-08-24: os dois CACHES entraram. Eles nao guardam codigo do
# painel, guardam os scripts que refazem as bases lidas por ele -- e
# eram copia unica na VPS, fora do git e fora do backup_projetos.sh.
# O banco de cada um fica de fora pelo .gitignore: e dado gerado.
# 🚨 ENQUANTO NAO HOUVER REMOTO NA ISOMOVI, ELES FICAM SO AQUI E O
# LOG NAO RECLAMA: sem upstream o  devolve 0,
# entao o script diz "sem mudancas" e nunca tenta empurrar. E o
# mesmo ponto cego de 14/08 -- arvore limpa nao significa
# sincronizado -- agora pelo lado de quem nem tem para onde sincronizar.
REPOS="/home/claude/moviserver /home/claude/IA_agente_Movichat /home/claude/fpsl_weso /home/claude/movizap_painel /home/claude/movisat-operacao /home/claude/prospeccao /home/claude/weso_cache /home/claude/harmonit_cache"
GATE="/home/claude/scripts/gate_segredos.py"
HOJE=$(date +%Y-%m-%d)
TS=$(date +'%Y-%m-%d %H:%M:%S')
BLOQUEADOS=0
NAO_EMPURRADOS=0

for REPO in $REPOS; do
    NOME=$(basename "$REPO")

    if ! cd "$REPO" 2>/dev/null; then
        echo "$TS  $NOME: diretorio inacessivel"
        continue
    fi

    # Commits que existem aqui e nao no remoto. Sem upstream, conta 0.
    ADIANTADO=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo 0)

    if [ -z "$(git status --porcelain)" ]; then
        if [ "$ADIANTADO" -gt 0 ]; then
            if git push -q origin main 2>/dev/null; then
                echo "$TS  $NOME: sem mudancas, $ADIANTADO commit(s) local(is) -- push OK"
            else
                echo "$TS  $NOME: sem mudancas, $ADIANTADO commit(s) local(is) -- push FALHOU"
                NAO_EMPURRADOS=$((NAO_EMPURRADOS + 1))
            fi
        else
            echo "$TS  $NOME: sem mudancas"
        fi
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
            NAO_EMPURRADOS=$((NAO_EMPURRADOS + 1))
        fi
    else
        echo "$TS  $NOME: commit falhou"
    fi
done

if [ "$BLOQUEADOS" -gt 0 ]; then
    echo "$TS  !! $BLOQUEADOS repositorio(s) bloqueado(s) por segredo -- OLHE ESTE LOG"
fi

if [ "$NAO_EMPURRADOS" -gt 0 ]; then
    echo "$TS  !! $NAO_EMPURRADOS repositorio(s) com commit que NAO saiu da VPS"
fi
