#!/bin/bash
# Backup diário dos projetos que não tinham nenhum.
#
# Motivo (2026-07-28): existiam backups automáticos só de hub-fotos e movichat.
# `base_manuais` é CÓPIA ÚNICA — os PDFs vieram do usuário e três deles já
# sumiram do Downloads dele no mesmo dia. Se o disco falhar, não se reconstrói.
#
# Não inclui venv (reconstrói com pip) nem __pycache__.
set -euo pipefail

DESTINO="/home/claude/backups/projetos"
RETENCAO_DIAS=14
HOJE=$(date +%Y-%m-%d)
mkdir -p "$DESTINO"

erros=0

empacotar() {
    local nome="$1"
    local origem="/home/claude/$nome"
    local alvo="$DESTINO/${nome}_${HOJE}.tar.gz"

    if [ ! -d "$origem" ]; then
        echo "  $nome: pasta nao existe — pulando"
        return
    fi

    # --ignore-failed-read para não abortar tudo se um arquivo sumir no meio
    # 🚨 `.env` NAO ENTRA NO BACKUP (28/08, decisao dele). Os tars carregavam
    # 7 arquivos `.env` -- movizap, moviserver, fpsl (2), movichat (2) e
    # prospeccao --, e com 15 copias diarias eram ~105 arquivos de credencial
    # parados em disco. O diretorio e `drwx------`, entao o risco nao e leitor
    # local: e o tar SAIR DA MAQUINA (copia, download, restauracao em outro
    # lugar) levando senha de banco e chave de API junto.
    #
    # ⚠️ O QUE ISSO CUSTA, E E PRECISO SABER: restaurar um projeto a partir do
    # backup NAO traz o `.env`. A aplicacao nao sobe ate alguem recriar o
    # arquivo. O segredo passa a existir em UM lugar so -- o `.env` vivo, que e
    # `-rw-------` -- e a recuperacao dele deixou de ser problema do backup.
    if tar -czf "$alvo.parcial" \
            --exclude='venv' \
            --exclude='__pycache__' \
            --exclude='*.pyc' \
            --exclude='node_modules' \
            --exclude='.git' \
            --exclude='.env' \
            --exclude='.env.*' \
            --ignore-failed-read \
            -C /home/claude "$nome" 2>/dev/null; then
        # só promove a definitivo se o tar abrir — backup corrompido é pior que nenhum
        if tar -tzf "$alvo.parcial" >/dev/null 2>&1; then
            mv "$alvo.parcial" "$alvo"
            echo "  $nome: $(du -h "$alvo" | cut -f1)"
        else
            rm -f "$alvo.parcial"
            echo "  $nome: FALHOU — arquivo gerado nao abre"
            erros=$((erros + 1))
        fi
    else
        rm -f "$alvo.parcial"
        echo "  $nome: FALHOU ao empacotar"
        erros=$((erros + 1))
    fi
}

echo "=== backup $(date '+%Y-%m-%d %H:%M:%S') ==="
empacotar base_manuais
empacotar moviserver
empacotar fpsl_weso
empacotar suntech-diag
empacotar IA_agente_Movichat
empacotar movizap_painel

# 🚨 NOVO EM 07/08: projeto de prospeccao (webhook da Cloud API da Meta).
# Ainda NAO tem repositorio git -- depende de o usuario criar o remoto na
# ISOMOVI, como fez com os outros seis. Ate la, este backup e a UNICA copia:
# app.py, .env e o sqlite com os payloads crus.
empacotar prospeccao

# 🚨 NOVO EM 07/08: Evolution dedicada a prospecao. O .env dela guarda a chave
# global QUE FOI ENTREGUE ao servico externo e a senha do banco -- perder isso
# e perder o acesso ao proprio container. Nao tem git ainda.
empacotar evolution_prosp

# 🚨 A rede de protecao tambem precisa de rede. `scripts/` guarda o gate de
# segredo, este proprio backup e as ferramentas de auditoria; `docs/` guarda a
# documentacao transversal.
#
# 🚨 MUDOU EM 06/08: as duas pastas foram MOVIDAS para movisat-operacao (6o
# repositorio), e /home/claude/docs e /home/claude/scripts viraram LINKS
# SIMBOLICOS. `tar` nao segue link: `empacotar docs` passaria a guardar o link
# e nao o conteudo -- um backup de 21 arquivos viraria um backup de 2 bytes,
# sem erro nenhum. Empacotar a pasta real resolve os dois de uma vez.
empacotar movisat-operacao

# Bancos SQLite: cópia consistente com .backup, não cp — cp durante escrita
# pode gerar arquivo corrompido.
for db in /home/claude/moviserver/data/moviserver.db /home/claude/fpsl_weso/data/fpsl.db; do
    if [ -f "$db" ]; then
        nome=$(basename "$db" .db)
        alvo="$DESTINO/${nome}_${HOJE}.db"
        if sqlite3 "$db" ".backup '$alvo'" 2>/dev/null; then
            # confirma que o backup abre e responde
            if sqlite3 "$alvo" "PRAGMA integrity_check;" 2>/dev/null | grep -q '^ok$'; then
                echo "  $nome.db: $(du -h "$alvo" | cut -f1) (integridade ok)"
            else
                echo "  $nome.db: FALHOU integrity_check"
                erros=$((erros + 1))
            fi
        else
            echo "  $nome.db: FALHOU no .backup"
            erros=$((erros + 1))
        fi
    fi
done

# retenção
apagados=$(find "$DESTINO" -type f \( -name '*.tar.gz' -o -name '*.db' \) \
    -mtime +$RETENCAO_DIAS -print -delete | wc -l)
[ "$apagados" -gt 0 ] && echo "  retencao: $apagados arquivo(s) com mais de ${RETENCAO_DIAS}d removido(s)"

echo "  total em disco: $(du -sh "$DESTINO" | cut -f1)"
if [ "$erros" -gt 0 ]; then
    echo "=== CONCLUIDO COM $erros ERRO(S) ==="
    exit 1
fi
echo "=== ok ==="
