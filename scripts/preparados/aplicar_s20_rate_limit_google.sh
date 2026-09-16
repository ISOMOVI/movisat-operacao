#!/bin/bash
# S20 -- separar /api/auth/google/ de /api/sessao/login no rate limit do nginx.
#
# PREPARADO em 15/09, NAO EXECUTAR sem autorizacao dele -- o sistema estava em
# uso quando isto foi escrito ("pode preparar, mas nao suba ainda").
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
# callback) contra um balde que só recarrega 1 a cada 12s. Duas ou tres
# pessoas entrando pelo Google em sequencia do mesmo IP de escritorio faziam a
# ultima levar 429 -- e o pior lugar pra isso e no callback, porque o codigo
# do Google ja foi usado e nao da pra tentar de novo sem recomecar do zero.
#
# Nao muda teto (ja subiu para burst=10 em 09/09) -- so separa quem disputa
# com quem.

set -euo pipefail

NGINX_CONF=/etc/nginx/nginx.conf
SITE_CONF=/etc/nginx/sites-enabled/movizap.movisat.com.br.conf
DATA=$(date +%Y-%m-%d_%H%M%S)

cp "$NGINX_CONF" "${NGINX_CONF}.bak_s20_${DATA}"
cp "$SITE_CONF" "${SITE_CONF}.bak_s20_${DATA}"

# 1. nova zona, logo depois da mz_login existente
sed -i '/limit_req_zone \$binary_remote_addr zone=mz_login:10m rate=5r\/m;/a\    limit_req_zone $binary_remote_addr zone=mz_google:10m rate=5r/m;' "$NGINX_CONF"

# 2. o location do google passa a usar a zona nova
sed -i '/location \/api\/auth\/google\/ {/,/}/ s/limit_req zone=mz_login burst=10 nodelay;/limit_req zone=mz_google burst=10 nodelay;/' "$SITE_CONF"

nginx -t
systemctl reload nginx

echo "S20 aplicado. Backups em ${NGINX_CONF}.bak_s20_${DATA} e ${SITE_CONF}.bak_s20_${DATA}"
echo "Conferir pelo estado: curl -s -o /dev/null -w '%{http_code}\n' https://movizap.movisat.com.br/api/auth/google/disponivel"
