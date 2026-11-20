
# 07 — O canal `atendimento` surdo (18–19/11/2026)

🔵 Pedido que abriu o caso, 19/11: *"veja se há erro de envio no movizap -
conversa entre aline e +5515996234109"*.

## 1. Não havia erro em lugar nenhum — faltava a CONFIRMAÇÃO

As duas respostas da Aline (08:16:17 e 08:16:21) saíram com `200`, o Evolution
confirmou cada uma com `send.message`, e ficaram em **"enviada"**.

📏 E o MoviZap não perdeu nada: **entre 08:16:21 e 08:51:27 o Evolution não
enviou um único webhook** — 35 minutos de silêncio. Todos os POSTs do dia
responderam 200, zero erro, zero ignorado por defeito.

🚨 **A mensagem dele das 08:23 não estava nem no banco do Evolution.** A perda
era no socket do Evolution com o WhatsApp, **antes de qualquer coisa nossa**.

## 2. Duas hipóteses descartadas COM MEDIDA

- **Não foi o deploy.** O serviço só reiniciou às 19:38:33 e as primeiras falhas
  são de **17:58:20**; reiniciar o nosso app não interrompe o socket do
  Evolution.
- **Não era o LID.** Havia **1007 chats em LID** no Evolution contra 651 por
  número, e os LID entregavam normalmente até 18/11.

## 3. A escada que resolveu, degrau por degrau (19/11)

| hora | o quê | resultado |
|---|---|---|
| 09:09:52 | `POST /instance/restart/atendimento` (o `PUT` não existe nesta versão) | rajada às 09:10: as duas da Aline passaram a **entregue**, confirmadas 5 → 10. **Voltou a congelar** |
| ~09:14 | mensagem de teste dele de +5518998116168 | **não chegou** — socket surdo confirmado |
| 09:16:17 | `docker restart movisat_evolution` | 12 upserts: as 4 mensagens de 08:22–08:23 entraram; entradas recuperadas até 08:30:46 |
| 09:19:58 | logout dele pelo painel | `desconectado por owner` |
| 09:20:16 / 09:21:14 | QR pedido por owner (duas vezes) | `aguardando_qr` → `pareando` |
| **09:21:23** | QR lido | **`conectado`** |
| 09:21:54 | primeira entrada nova (+5511954252906) | **recebendo de novo** |

## 4. ✅ A cura foi o QR — e o ruído de fundo não é o apagão

🔵 Ele, 19/11: *"a cura foi o recall via QR code mesmo, talvez há periodicidade
na ação"* · *"já está ok então, certo? não há novos incidentes"*.

📏 **Medido às 14:40, e confirma os dois:**

| medida | valor |
|---|---|
| eventos de canal desde **10:10:59** | **nenhum** — 4h27 limpas, a maior sequência do mês |
| saídas desde **10:44** | **25 entregues + 33 lidas, zero presa** |
| webhooks na última hora | **47**, último às 14:35:08 |

⚠️ **A fronteira é 10:44:** a última presa é de **10:43:14** e a primeira limpa
de **10:44:08**. O QR foi às 09:21:23, e o socket levou ~22 minutos para
assentar.

### 🚨 Correção de uma conclusão minha

Eu havia escrito que a escada *"devolveu o canal, não curou o socket"*, apoiado
nas quedas curtas que o `canal_evento` registra. **Medido depois, está errado:**

- **cada queda curta dura 12 a 58 segundos** e volta sozinha — as 20 últimas,
  sem exceção;
- **elas existem desde 03/11, em dias em que nada quebrou:** 03/11 **3** ·
  04/11 **8** · 05/11 **6** · 06/11 **8** · **11/11 19** (o pior do mês) ·
  12/11 **4** · 13/11 **4** · 17/11 **2** · 18/11 **12** · 19/11 **4**;
- **sem período:** o intervalo entre quedas vai de **3,8 min a 89 h**, e a
  distribuição por hora (7h–22h, pico às 9h) só acompanha o movimento do dia.

🚨 **O apagão é de OUTRA natureza:** o socket ficou **`conectado` e surdo**, e
**nenhum** evento de queda foi registrado enquanto ele durava. Ruído de 30 s que
se cura sozinho não é a mesma coisa que 13 h sem confirmação, e somar os dois foi
o meu erro.

⚠️ **A periodicidade do apagão não se mede com UMA ocorrência.** O que se pode
fazer é o alerta de silêncio de webhook, que mede o **sintoma** em vez de
adivinhar o período — com 4h27 de calma agora, ele não daria falso positivo.

**As saídas presas, que é o que não se resolveu:**

| | presas em *enviada* |
|---|---|
| 18/11 | **13**, e as 13 continuavam presas em 19/11 14:15 |
| 19/11 | **6** — três de 08:52–08:54 (Mayara, Cristina) e **três de 10:25:39, 10:25:41 e 10:43:14** |

⚠️ As três das 10h caem **dentro dos 22 minutos de assentamento** depois do QR —
a última é 10:43:14, e de **10:44:08** em diante nada mais ficou preso.

🚨 **As 19 não mudam sozinhas** e ficam como estão: foram enviadas em sessão que
não existe mais. Saber se chegaram é **perguntar ao destinatário ou reenviar**.

📏 O canal estava de pé no fim da medição: conectado, **638 webhooks no dia**,
último às 14:35:08, zero erro e zero ignorado.

## 5. O achado de endereço, corrigido pela medida

O diário de 19/11 anotou que o contato tinha **dois chats** no Evolution —
`5515996234109@s.whatsapp.net` (50 mensagens, todas nossas) e
`137001286254646@lid` (16, as dele).

🚨 **Medido no nosso banco, o problema não é nosso:** das **1.284 conversas, as
1.284 são por número** e **nenhuma** está em `@lid`. O LID aparece só em
`mensagem.remetente_jid` (9 em 19/11; entre 75 e 208 por dia desde 10/11).
Existem **12 contatos com mais de um endereço**, e são **dois NÚMEROS**
diferentes, não número × LID.

⚠️ Portanto o desencontro *"escrevemos num endereço e ele fala pelo outro"* vive
**dentro do Evolution**, e é lá que se conserta. 🔵 Ele pediu medir antes de
propor como unificar — está medido.

## 6. A vigília de forma das mensagens

🔵 *"monitore diferenças nas mensagens tbm, pode haver alguma att"*.

`/home/claude/vigia_canal_1911.py`, log em `/home/claude/vigia_canal_1911.log`.
Linha de base de **53 marcas de forma** tirada das 24 h anteriores. Acusa:
evento novo, campo novo no `data`, tipo de mensagem novo, formato de
`remoteJid` novo, e evento com erro / ignorado / não processado.

📏 O que pegou no repareamento — **as três são de pareamento, não do WhatsApp**:

```
initialSecurityNotificationSettingSync
appStateSyncKeyShare
historySyncNotification
```

Chegam rotuladas como `messages.edited` (18 no total) e o MoviZap as processa
sem erro; nenhuma vira mensagem na tela, que é o certo. **Nenhum campo novo em
mensagem de verdade, nenhum tipo novo, nenhum endereço novo.**

⚠️ **A vigília encerrou às 11:20:58 e não roda mais.** Era de uma sessão só.

## 7. O que ninguém avisa hoje

Quem viu o problema foi ele, olhando a tela. 🟡 **Proposta, não construída:**
alerta para saída parada em *"enviada"* além de X minutos, e para silêncio de
webhook além de Y minutos. Com a oscilação medida na seção 4, o segundo alerta
teria disparado 15 vezes em dois dias.
