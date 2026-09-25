#!/bin/bash
# S20 -- separar /api/auth/google/ de /api/sessao/login no rate limit do nginx.
#
# PREPARADO em 15/09, REVISADO em 24/09 (auditoria). NAO EXECUTAR sem
# autorizacao dele -- esta na lista de decisoes dele ("corrija o script do S20
# mas nao implante ainda, fica aguardando decisao minha com as demais").
#
# Precisa de vps-root (edita /etc/nginx/nginx.conf e o site do movizap).
# Rodar assim, quando ele autorizar:
#   ssh vps-root 'bash -s' < aplicar_s20_rate_limit_google.sh
#
# O que faz: cria a zona mz_google (mesma taxa 5r/m da mz_login, memoria
# propria), tira /api/auth/google/ da zona mz_login e poe nela. /api/sessao/
# login fica sozinha na mz_login -- e o unico endpoint que mede senha errada.
#
# Por que: um login pelo Google gasta 3 requisicoes (~6s: disponivel, inicio,
# callback) contra um balde que so recarrega 1 a cada 12s. Duas ou tres
# pessoas entrando pelo Google em sequencia do mesmo IP de escritorio faziam a
# ultima levar 429 -- e o pior lugar pra isso e no callback, porque o codigo
# do Google ja foi usado e nao da pra tentar de novo sem recomecar do zero.
#
# Nao muda teto (ja subiu para burst=10 em 09/09) -- so separa quem disputa
# com quem.
#
# REVISAO DE 24/09 -- os dois defeitos que a auditoria achou:
#   1. NAO ERA IDEMPOTENTE. Rodar duas vezes duplicava a zona mz_google; o
#      `nginx -t` falhava e o `set -e` parava o script DEIXANDO O ARQUIVO
#      QUEBRADO NO DISCO. O nginx seguia no ar com a versao antiga, mas o
#      proximo reload de qualquer pessoa derrubaria todos os sites.
#      Agora: se ja estiver aplicado, nao faz nada.
#   2. NAO VOLTAVA SOZINHO. Se o `nginx -t` falhasse, os arquivos ficavam
#      editados. Agora: falhou o teste, restaura o backup e testa de novo.
#   Tambem: os backups saem de /etc/nginx/sites-enabled/ para uma pasta
#   propria. Hoje eles nao seriam carregados (o include e `*.conf` e o backup
#   termina em outra coisa), mas nao depende mais desse detalhe.

set -euo pipefail

NGINX_CONF=/etc/nginx/nginx.conf
SITE_CONF=/etc/nginx/sites-enabled/movizap.movisat.com.br.conf
DATA=$(date +%Y-%m-%d_%H%M%S)
BACKUP_DIR=/root/backup_nginx_s20_${DATA}

# 0. ja aplicado? -- a zona nova existe E o location do google ja a usa.
if grep -q 'zone=mz_google:' "$NGINX_CONF" \
   && sed -n '/location \/api\/auth\/google\/ {/,/}/p' "$SITE_CONF" | grep -q 'zone=mz_google'; then
    echo "S20 ja estava aplicado. Nada a fazer."
    exit 0
fi

# 0b. o que o script espera encontrar -- se o nginx mudou, para antes de mexer.
grep -q 'limit_req_zone \$binary_remote_addr zone=mz_login:10m rate=5r/m;' "$NGINX_CONF" \
    || { echo "PARO: nao achei a zona mz_login esperada em $NGINX_CONF"; exit 1; }
sed -n '/location \/api\/auth\/google\/ {/,/}/p' "$SITE_CONF" \
    | grep -q 'limit_req zone=mz_login burst=10 nodelay;' \
    || { echo "PARO: o location do google nao usa mz_login como esperado"; exit 1; }

mkdir -p "$BACKUP_DIR"
cp -p "$NGINX_CONF" "$BACKUP_DIR/nginx.conf"
cp -p "$SITE_CONF" "$BACKUP_DIR/movizap.movisat.com.br.conf"

restaurar() {
    echo "nginx -t FALHOU -- restaurando o backup de $BACKUP_DIR"
    cp -p "$BACKUP_DIR/nginx.conf" "$NGINX_CONF"
    cp -p "$BACKUP_DIR/movizap.movisat.com.br.conf" "$SITE_CONF"
    nginx -t && echo "Backup restaurado e valido. Nada foi recarregado."
    exit 1
}

# 1. nova zona, logo depois da mz_login existente (so se ainda nao existir)
grep -q 'zone=mz_google:' "$NGINX_CONF" \
    || sed -i '/limit_req_zone \$binary_remote_addr zone=mz_login:10m rate=5r\/m;/a\    limit_req_zone $binary_remote_addr zone=mz_google:10m rate=5r/m;' "$NGINX_CONF"

# 2. o location do google passa a usar a zona nova
sed -i '/location \/api\/auth\/google\/ {/,/}/ s/limit_req zone=mz_login burst=10 nodelay;/limit_req zone=mz_google burst=10 nodelay;/' "$SITE_CONF"

nginx -t || restaurar
systemctl reload nginx

echo "S20 aplicado. Backups em $BACKUP_DIR"
echo "Conferir pelo estado: curl -s -o /dev/null -w '%{http_code}\n' https://movizap.movisat.com.br/api/auth/google/disponivel"
