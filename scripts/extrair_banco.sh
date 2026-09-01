#!/bin/bash
# Extrai o esquema completo de um projeto Supabase, direto da fonte.
#
# USO:  extrair_banco.sh <projeto>
#   <projeto> = nome do diretorio em /home/claude
#   a conexao fica em /home/claude/.conexao_<projeto>, modo 600
#
# A senha NUNCA entra em argv: e convertida para PGPASSFILE + PGSERVICEFILE
# dentro do processo. O auditd grava argv; por isso este cuidado.

set -u
PROJETO="${1:-}"
if [ -z "$PROJETO" ]; then echo "uso: $0 <projeto>"; exit 1; fi

REPO="/home/claude/$PROJETO"
CONEXAO="/home/claude/.conexao_${PROJETO}"
SAIDA="$REPO/docs"

[ -d "$REPO" ] || { echo "ERRO: $REPO nao existe"; exit 1; }
[ -f "$CONEXAO" ] || { echo "ERRO: falta $CONEXAO"; exit 1; }
chmod 600 "$CONEXAO"
mkdir -p "$SAIDA"

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
chmod 700 "$TMP"

python3 - "$CONEXAO" "$TMP" << 'PYFIM'
import sys, urllib.parse, pathlib
uri = pathlib.Path(sys.argv[1]).read_text().strip()
tmp = pathlib.Path(sys.argv[2])
u = urllib.parse.urlparse(uri)
host = u.hostname or ""
port = u.port or 5432
user = urllib.parse.unquote(u.username or "")
pwd = urllib.parse.unquote(u.password or "")
db = (u.path or "/postgres").lstrip("/") or "postgres"
(tmp / "pgpass").write_text("%s:%s:%s:%s:%s\n" % (host, port, db, user, pwd))
(tmp / "pgservice.conf").write_text(
    "[alvo]\nhost=%s\nport=%s\nuser=%s\ndbname=%s\nsslmode=require\n"
    % (host, port, user, db))
(tmp / "resumo.txt").write_text(
    "host=%s port=%s db=%s user=%s\n" % (host, port, db, user))
PYFIM

chmod 600 "$TMP/pgpass" "$TMP/pgservice.conf"
export PGPASSFILE="$TMP/pgpass"
export PGSERVICEFILE="$TMP/pgservice.conf"
export PGSERVICE=alvo

echo "=== destino (sem senha) ==="
cat "$TMP/resumo.txt"

echo
echo "=== 1. conexao e versao ==="
VER=$(psql -w -tAc "SHOW server_version" 2>&1)
if [ $? -ne 0 ]; then echo "FALHOU: $VER"; exit 1; fi
echo "servidor: $VER"
CLI=$(pg_dump --version | awk '{print $3}')
echo "cliente : $CLI"

MAJ_S=$(echo "$VER" | cut -d. -f1)
MAJ_C=$(echo "$CLI" | cut -d. -f1)
PULAR_DUMP=0
if [ "$MAJ_S" -gt "$MAJ_C" ]; then
  echo "AVISO: servidor $MAJ_S > cliente $MAJ_C. O pg_dump vai recusar."
  echo "       Sigo so com o catalogo; o DDL sai por outro caminho."
  PULAR_DUMP=1
fi

echo
echo "=== 2. DDL completo ==="
if [ "$PULAR_DUMP" = "0" ]; then
  if pg_dump -w --schema-only --schema=public --no-owner \
       --file="$SAIDA/DB_SCHEMA.sql" 2> "$TMP/erro"; then
    echo "gravado docs/DB_SCHEMA.sql: $(wc -l < "$SAIDA/DB_SCHEMA.sql") linhas"
  else
    echo "pg_dump falhou:"
    cat "$TMP/erro"
  fi
else
  echo "pulado"
fi

CAT="$SAIDA/DB_CATALOGO.md"
Q() { psql -w -X --pset=border=2 --pset=format=markdown -c "$1"; }

echo
echo "=== 3. catalogo ==="
{
  echo "# Catalogo do banco - $PROJETO"
  echo
  echo "Extraido direto do Postgres em $(date '+%Y-%m-%d %H:%M')."
  echo "Servidor: $VER. Nao editar a mao: regerar com scripts/extrair_banco.sh."
  echo
  echo "## RLS por tabela"; echo
  Q "SELECT tablename AS tabela, rowsecurity AS rls_ligada FROM pg_tables WHERE schemaname='public' ORDER BY 1"
  echo; echo "## Policies"; echo
  Q "SELECT tablename AS tabela, policyname AS policy, cmd AS operacao, array_to_string(roles,', ') AS papeis, coalesce(qual,'-') AS using_expr, coalesce(with_check,'-') AS with_check FROM pg_policies WHERE schemaname='public' ORDER BY tablename, policyname"
  echo; echo "## Constraints -- PK, FK com ON DELETE, UNIQUE, CHECK"; echo
  Q "SELECT conrelid::regclass AS tabela, conname AS nome, CASE contype WHEN 'p' THEN 'PK' WHEN 'f' THEN 'FK' WHEN 'u' THEN 'UNIQUE' WHEN 'c' THEN 'CHECK' ELSE contype::text END AS tipo, pg_get_constraintdef(oid) AS definicao FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY 1,3,2"
  echo; echo "## Indices"; echo
  Q "SELECT tablename AS tabela, indexname AS indice, indexdef AS definicao FROM pg_indexes WHERE schemaname='public' ORDER BY 1,2"
  echo; echo "## Triggers"; echo
  Q "SELECT c.relname AS tabela, t.tgname AS gatilho, pg_get_triggerdef(t.oid) AS definicao FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid JOIN pg_namespace n ON n.oid=c.relnamespace WHERE NOT t.tgisinternal AND n.nspname='public' ORDER BY 1,2"
  echo; echo "## Funcoes -- assinatura, seguranca e search_path"; echo
  Q "SELECT p.proname AS funcao, pg_get_function_identity_arguments(p.oid) AS argumentos, pg_get_function_result(p.oid) AS retorno, CASE WHEN p.prosecdef THEN 'DEFINER' ELSE 'INVOKER' END AS seguranca, coalesce(array_to_string(p.proconfig,', '),'-') AS config FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' ORDER BY 1"
  echo; echo "## GRANTs por tabela e papel"; echo
  Q "SELECT table_name AS tabela, grantee AS papel, string_agg(privilege_type, ', ' ORDER BY privilege_type) AS permissoes FROM information_schema.role_table_grants WHERE table_schema='public' AND grantee IN ('anon','authenticated','service_role') GROUP BY 1,2 ORDER BY 1,2"
  echo; echo "## Colunas -- tipo, nulo e default"; echo
  Q "SELECT table_name AS tabela, column_name AS coluna, data_type AS tipo, is_nullable AS nulo, coalesce(column_default,'-') AS padrao FROM information_schema.columns WHERE table_schema='public' ORDER BY 1, ordinal_position"
  echo; echo "## Extensoes"; echo
  Q "SELECT extname AS extensao, extversion AS versao FROM pg_extension ORDER BY 1"
  echo; echo "## Linhas por tabela -- o que esta populado"; echo
  Q "SELECT relname AS tabela, n_live_tup AS linhas_aprox FROM pg_stat_user_tables WHERE schemaname='public' ORDER BY 2 DESC, 1"
  echo; echo "## Agendamentos (pg_cron)"; echo
  Q "SELECT jobid, schedule, command, active FROM cron.job ORDER BY 1" 2>/dev/null || echo "_pg_cron nao instalado ou sem permissao._"
  echo; echo "## Buckets de storage"; echo
  Q "SELECT id, name, public FROM storage.buckets ORDER BY 1" 2>/dev/null || echo "_sem acesso a storage.buckets._"
} > "$CAT" 2>&1
echo "gravado docs/DB_CATALOGO.md: $(wc -l < "$CAT") linhas"

echo
echo "=== 4. corpo das funcoes ==="
FUN="$SAIDA/DB_FUNCOES.md"
echo "# Corpo das funcoes do banco - $PROJETO" > "$FUN"
echo "" >> "$FUN"
psql -w -X -tA -c "SELECT '### ' || p.proname || chr(10) || chr(10) || '\`\`\`sql' || chr(10) || pg_get_functiondef(p.oid) || chr(10) || '\`\`\`' || chr(10) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='public' ORDER BY p.proname" >> "$FUN" 2>&1
echo "gravado docs/DB_FUNCOES.md: $(wc -l < "$FUN") linhas"

echo
echo "=== 5. varredura de segredo na saida ==="
ACHOU=0
for f in "$SAIDA/DB_SCHEMA.sql" "$CAT" "$FUN"; do
  [ -f "$f" ] || continue
  n=$(grep -ciE "(api[_-]?key|secret|token|password|senha|bearer)[^a-z]{0,3}[=:][^=:]" "$f" 2>/dev/null)
  n=${n:-0}
  if [ "$n" -gt 0 ]; then
    echo "  ATENCAO em ${f##*/}: $n linha(s) com padrao de segredo"
    grep -niE "(api[_-]?key|secret|token|password|senha|bearer)[^a-z]{0,3}[=:][^=:]" "$f" | head -5 | cut -c1-120
    ACHOU=1
  fi
done
[ "$ACHOU" = "0" ] && echo "  limpo: nenhum padrao de segredo na saida"

echo
echo "=== RESUMO ==="
ls -l "$SAIDA" | grep DB_
