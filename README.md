# harvey-br

**Um vendedor autônomo que roda na sua assinatura do Claude Code, em português.**

Ele acha empresas que vale a pena abordar, descobre algo específico sobre cada uma, escreve o e-mail frio citando aquilo, manda, lê a resposta e conduz a conversa até uma reunião. Roda na sua máquina, em loop, sozinho.

A parte incomum: **não tem conta de API.** Ele usa a sua assinatura do Claude Pro ou Max pelo Claude Code, ou a sua do ChatGPT pelo Codex. As chamadas de modelo saem do plano que você já paga, sem chave de API e sem cobrança por token.

> Este repositório é um **fork** de [ethanplusai/harvey](https://github.com/ethanplusai/harvey) (licença MIT), adaptado para quem vende no Brasil. O crédito do projeto é de lá; o que mudou aqui está listado abaixo, linha por linha.

---

## O que já está em português

| Arquivo | O que é | Estado |
|---|---|---|
| `prompts/system.md` | a identidade do agente | **reescrito em PT**, com a regra de tratar por "você" |
| `prompts/writer.md` | as regras de escrita do e-mail frio | **reescrito em PT** — ver abaixo |
| `prompts/scout.md` | pontuação e personalização do lead | **reescrito em PT** |
| `prompts/handler.md` | como responder quem respondeu | **reescrito em PT** |
| `harvey/gate.py` | o porteiro que barra o e-mail antes de sair | **64 frases em português** somadas às 30 originais |
| `harvey/agents/handler.py` | lê a resposta do lead | reconhece pedido de saída e ameaça jurídica **em português** |
| `harvey/config.py` | valida a configuração | aceita rodapé de descadastro em português |
| `harvey/trainer.py` | o `harvey train` | reconhece o lugar-vazio do template em português |
| `harvey.yaml` | a configuração | **padrões do Brasil**: fuso `America/Sao_Paulo`, cargos e setores em PT, nota sobre a LGPD |
| `tests/test_portugues.py` | novo | prende tudo isso |

## O que estava quebrado em português

Traduzir só o prompt não resolve. Rodando a suíte do upstream com a configuração em português, três coisas quebraram — e as três são do tipo que você só descobre depois de queimar um domínio:

1. **Quem pedia para sair não saía.** As frases que o sistema sempre honra como descadastro (`OPT_OUT_PATTERNS`) eram todas em inglês. "Me tira da lista", "pare de enviar", "não quero mais receber", "apague meus dados" não batiam em nada: o pedido ficava na mão do classificador do modelo, sem a rede de segurança. Agora batem, com e sem acento.
2. **Ameaça jurídica brasileira não subia para um humano.** `ESCALATION_PATTERNS` conhecia "lawyer", "gdpr", "can-spam". Não conhecia **advogado, Procon, LGPD, ANPD, notificação extrajudicial**. Um e-mail desses teria recebido resposta automática.
3. **O `harvey train` deixaria o remetente de exemplo.** Ele só troca a persona quando a empresa ainda é o lugar-vazio do template — e procurava por `"Your Company"`. Com o template em português (`"Sua Empresa"`), achava que já estava configurado, e o primeiro e-mail sairia assinado por `harvey@suaempresa.com.br`.

Um detalhe de propósito: responder só **"não"** a uma pergunta **não** tira a pessoa da lista. Isso é falta de interesse, que encerra a conversa sem queimar o contato — o upstream toma o mesmo cuidado com "no", e o fork mantém.


### O writer.md não é tradução

As regras do upstream são contra as marcas de IA **do inglês** ("not X, but Y", travessão, "picture this"). Essas marcas não são as mesmas em português. O `prompts/writer.md` daqui tem as nossas:

- o contraste "não é X, é Y" e o fecho dramático de uma linha ("É isso." "Simples assim.")
- o verbo inflado de LinkedIn: alavancar, potencializar, impulsionar, destravar, revolucionar
- a abertura batida: "espero que esteja tudo bem", "venho por meio deste", "só passando pra saber"
- o gerúndio pendurado no fim da frase ("..., ajudando você a crescer")
- a tradução que denuncia o inglês: "deixe-me saber", "sinta-se livre para", "no final do dia"
- e as palavras que derrubam no spam em português: grátis, garantido, últimas vagas, clique aqui, última chance, renda extra

As mesmas listas estão no `harvey/gate.py`, porque **prompt pode ser ignorado pelo modelo e o gate não.** Como a comparação ali é por texto cru, toda frase acentuada entra também sem acento (`última chance` e `ultima chance`).

## O que **não** está em português

Seja direto sobre isso antes de ligar o envio:

- **`skills/` (11 arquivos, 66 KB)** — a biblioteca de método de venda continua em inglês. O agente lê esses arquivos como conhecimento; os e-mails saem em português pelo `writer.md`, mas o raciocínio de venda ainda é o americano (frameworks de e-mail, venda para startup, LinkedIn).
- **O resto do código** — mensagem de CLI, painel e log estão em inglês.
- **`README.en.md`** — o README original, inteiro, preservado.

## Lei brasileira

A LGPD não proíbe e-mail frio B2B, mas pede base legal (legítimo interesse, art. 7º, IX), transparência sobre a origem do dado e um caminho fácil de oposição. Na prática: diga quem está mandando, diga de onde veio o contato quando perguntarem, e atenda o pedido de saída na hora — o agente já faz isso, é regra dura dele.

O `compliance.precleared` do upstream checa a lei de envio do Reino Unido, Estados Unidos, Canadá, Alemanha e França. **Não cobre o Brasil**, e por isso vem desligado aqui.

Isto é a leitura de quem fez o fork, não é parecer jurídico.

## Começando

Pré-requisitos: Python 3.11+, assinatura Claude Pro ou Max com o CLI logado (`claude login`), e uma caixa de e-mail para enviar — de preferência um domínio secundário.

**Aqueça a caixa antes do primeiro e-mail frio.** O projeto original recomenda o [TrulyInbox](https://trulyinbox.com/?via=harvey) (link de afiliado do autor do Harvey, mantido aqui de propósito): ele aquece o domínio novo, segura a caixa fora do spam depois, e o `harvey warmup` lê a taxa de entrega dele para dizer quando você pode começar.

```bash
git clone https://github.com/BFmidia/harvey-br.git
cd harvey-br
claude
```

E diga: **"configura o Harvey pra mim"**. O repositório traz um `CLAUDE.md` que transforma o Claude Code no assistente de instalação.

Ou na mão:

```bash
python3.13 -m venv .venv && source .venv/bin/activate && pip install -e .
cp .env.example .env && $EDITOR .env
harvey train https://a-sua-empresa.com.br
harvey signals --confirm free
harvey discover
harvey dashboard
harvey run
```

O passo a passo completo, o painel, o Docker, o Codex e a solução de problema estão no [README.en.md](README.en.md).

## Licença e crédito

MIT, igual ao original. O `LICENSE` do upstream continua aqui, como manda a licença.

Projeto original: **[ethanplusai/harvey](https://github.com/ethanplusai/harvey)** — todo o crédito de engenharia é de lá.
