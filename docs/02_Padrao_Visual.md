# 02 — Padrão visual dos painéis

**Documento transversal.** MoviZap, MoviServer, FPSL e MoviChat usam **o mesmo
visual**. Escrito em 2026-08-05, quando os quatro foram alinhados.

A referência é o **MoviChat** — decisão do usuário: *"é o melhor, como pedi"*.
Onde este documento e o `theme.css` do MoviChat divergirem, **o `theme.css`
ganha**, e este documento é que está desatualizado.

---

## 1. A fonte dos valores

`/home/claude/IA_agente_Movichat/frontend/static/css/theme.css`

🚨 **Copiar o valor, não "algo parecido".** O MoviZap nasceu em 04/08 com a
paleta do MoviServer (GitHub: `#0d1117`, `#1f6feb`) — próxima, mas diferente.
O resultado é pior que painéis assumidamente distintos: **"quase a mesma cor"
lê como defeito, não como escolha.**

| Token | Valor | Papel |
|---|---|---|
| `--bg` | `#F8FAFC` | fundo da página |
| `--bg2` / `--bg3` | `#F1F5F9` / `#E2E8F0` | hover, cabeçalho de tabela, pressionado |
| `--card` | `#FFFFFF` | superfície elevada |
| `--text` / `--text2` | `#0F172A` / `#64748B` | texto e apoio |
| `--border` | `#E2E8F0` | divisória |
| `--blue` | `#2563EB` | acento; hover `#1D4ED8` |
| `--green` / `--red` / `--yellow` | `#16A34A` / `#DC2626` / `#D97706` | estado |
| `--sidebar-bg` / `--sidebar-tx` | `#0F172A` / `#94A3B8` | menu lateral |
| `--radius` | `8px` | raio padrão |
| fonte | `'Inter', 'Segoe UI', system-ui` | — |

## 2. 🚨 O menu lateral é ESCURO mesmo no tema claro

É a assinatura do MoviChat e o que mais distingue os painéis à primeira vista.
Por isso os tokens `--menu-*` / `--sidebar-*` **não seguem claro/escuro**:
existem separados de propósito.

## 3. 🚨 Campo de formulário: 16px e 44px não são estética

| Valor | Motivo |
|---|---|
| `font-size: 16px` | **abaixo de 16px o iOS dá zoom sozinho** ao focar o campo, e a tela fica torta |
| `min-height: 44px` | alvo de toque mínimo |
| `min-height: 48px` no login | maior que o padrão, a pedido do usuário |

Um campo de 14px "fica mais elegante" no desktop e quebra o celular. Não é
troca aceitável num painel que se usa em campo.

## 4. Tela de login — a mesma nos quatro

```
     [ logo Movisat, 76px, centralizada ]
     subtítulo: o que é este painel
     ┌───────────────────────────────┐
     │ Acesse sua conta              │
     │  Login   [ campo 48px      ]  │
     │  Senha   [ campo 48px      ]  │
     │  [ erro, quando houver     ]  │
     │  [      Entrar (48px)      ]  │
     │  [ Esqueci minha senha     ]  │  <- desabilitado
     └───────────────────────────────┘
```

- **logo a 76px** (a do MoviChat original tinha 52px) — aumentada a pedido;
- **marca fora do cartão**, centralizada acima dele;
- **"Esqueci minha senha" existe mas está desabilitado**, com o motivo no
  `title`. Depende de envio de e-mail (e, no MoviZap, do `CAD_2.1`). **Botão
  desabilitado que diz por que não funciona é honesto; link que não faz nada é
  o contrário.**
- em tela baixa (`max-height: 640px`) a marca encolhe **antes** de espremer o
  cartão.

**Logo:** `movisat_logo.png`, 732×252, 32 KB. Existe uma versão 2400×826 em
`/var/www/html/movisat-logo.png` — mesma arte, 313 KB. Para tela de login a
menor basta; a grande é para impressão.

## 5. Onde mora o CSS de cada painel

| Painel | Arquivo | Observação |
|---|---|---|
| MoviChat | `frontend/static/css/theme.css` | **a referência** |
| FPSL | `frontend/estilo.css` | **criado em 05/08** — ver abaixo |
| MoviServer | `frontend/estilo.css` + `painel.css` | mesma cópia do FPSL |
| MoviZap | `src/estilo/{tokens,base,componentes}.css` | Vue; tokens em vez de valores |

### ⚠️ O FPSL não tinha CSS nenhum

Até 05/08, **as 10 telas do FPSL carregavam cada uma o seu próprio bloco
`<style>`**, com os mesmos valores copiados dez vezes. A cor já era a certa —
alguém copiou do MoviChat — mas não havia um lugar para mudar, então divergir
era questão de tempo.

`frontend/estilo.css` é o primeiro arquivo de estilo do projeto.

🚨 **Como adotar nas 9 telas restantes:** o `<link>` entra **antes** do
`<style>` de cada tela. Assim o inline continua vencendo e nada muda de
aparência hoje; a migração é apagar o inline aos poucos, tela por tela.
Trocar tudo de uma vez em 10 telas de produção é como se quebra painel.

## 6. Como conferir

`/home/claude/scripts/verificar_paineis.py` — bate nos quatro e confere logo,
cartão, trava de login e mensagem única.

⚠️ O MoviZap é SPA: o HTML servido só tem `<div id="app">`, e as marcas estão
no bundle. Um teste que procure o texto no HTML dá falso negativo nele.

⚠️ **O MoviChat usa `movisat_logo.png` com underscore**; os outros usam
`movisat-logo.png` com hífen. Já produziu um falso negativo neste script.

---

## Decisões

### Padrão visual único, referência MoviChat (05/08)
```
Objetivo:     quatro painéis que pareçam o mesmo produto
Hoje:         = o objetivo. Paleta, fonte, raio e tela de login iguais
Por quê:      "quase a mesma cor" lê como defeito; e escolha do usuário --
              o MoviChat é o que ele considera melhor
Reavaliar se: o MoviChat mudar de visual. Aí ele continua sendo a fonte, e os
              outros três seguem
```

### Logo e campos maiores que o original (05/08)
```
Objetivo:     tela de entrada legível e confortável de tocar
Hoje:         = o objetivo. Logo 76px (era 52), campos 48px, fonte 16px
Por quê:      pedido do usuário na logo; os 16px são iOS, não gosto -- abaixo
              disso o navegador dá zoom sozinho
Reavaliar se: — fechado
```

### CSS compartilhado no FPSL, adoção incremental (05/08)
```
Objetivo:     um lugar só para mudar a aparência das 10 telas
Hoje:         contorno -- o arquivo existe e só o login usa; as outras 9
              seguem com o <style> inline vencendo
Por quê:      trocar 10 telas de produção de uma vez é como se quebra painel
Reavaliar se: cai quando cada tela tiver o inline removido e testado. Até lá,
              é contorno declarado, não desenho
```
