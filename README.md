# movisat-operacao

A rede que protege os outros cinco repositórios — e que até 2026-08-06 era a
única coisa **desprotegida**.

Aqui vivem os documentos transversais e os scripts que operam a VPS. Não é um
sistema: é a caixa de ferramentas que mantém os sistemas de pé.

## Por que este repositório existe

Estes 21 arquivos ficaram até 06/08 em **uma cópia só**, fora do git e fora do
`backup_projetos.sh` — que empacota os sete projetos e não a si mesmo.

O modo de falha era o pior possível:

> Se o `gate_segredos.py` sumisse, o `git_autocommit.sh` **falharia fechado** e
> pararia de commitar tudo. Em silêncio, num log que ninguém abre.

Ou seja: perder a ferramenta que protege os repositórios faria os repositórios
pararem de ser protegidos, **sem avisar**.

## O que tem aqui

### `docs/` — o que vale para todos os projetos

| | |
|---|---|
| `00_Commit_e_Segredos.md` | como se commita, e a trava de segredo |
| `01_Seguranca_Login.md` | limite de tentativas, enumeração de usuário |
| `02_Padrao_Visual.md` | paleta, tipografia, o campo de 16px e o zoom do iOS |
| `03_Painel_Rapido.md` | o quadro compartilhado por link, sem login |

### `scripts/` — as ferramentas, e o que dói se sumirem

| Arquivo | Se sumir |
|---|---|
| `gate_segredos.py` | 🚨 o commit automático **para de barrar segredo** — e falha fechado, então para de commitar |
| `git_autocommit.sh` | o trabalho do dia deixa de ser versionado, em silêncio |
| `backup_projetos.sh` | **o backup dos sete projetos para**, e ninguém é avisado |
| `auditar_vps.py`, `auditar_segredos.py` | a varredura que achou os dois vazamentos de 04/08 |
| `verificar_paineis.py`, `verificar_login.py` | a prova de que os quatro painéis estão de pé |
| `trocar_owner_moviserver.py`, `trocar_login_movizap.py` | trocar senha sem passar por linha de comando |
| `alinhar_env_moviserver.py` | manter o `.env` coerente sem editar na mão |
| `conferir_estado.py` | confere o MIOLO do `Proximos_Passos.md` contra a realidade |
| `scrub_valor.py`, `limpar_deploy_md.py`, `limpar_projeto_md.py` | tirar valor vazado de arquivo versionado |
| `triar_achados.py`, `ignorar_wal.py`, `corrigir_hubfotos.py` | utilitários de faxina pontual |

## 🚨 Onde estas pastas moram de verdade

O conteúdo **mora aqui**. `/home/claude/docs` e `/home/claude/scripts` são
**links simbólicos** para cá, criados em 06/08 porque o crontab usa caminho
absoluto:

```
/home/claude/docs    -> /home/claude/movisat-operacao/docs
/home/claude/scripts -> /home/claude/movisat-operacao/scripts
```

⚠️ **Não apague os links.** O `backup_projetos.sh` e o `git_autocommit.sh` são
chamados pelo cron por esses caminhos. Quebrar o link não dá erro visível: o
cron simplesmente não roda, e o aviso vai para um log que ninguém abre — que é
exatamente o problema que este repositório existe para resolver.

## A regra desta caixa

**Ferramenta, nunca dado nem segredo.** Script que precisar de credencial lê do
`.env` do projeto que ele opera. Nada de valor entra aqui — nem "só para
testar", nem "é interno".
