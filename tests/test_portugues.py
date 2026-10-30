"""O que este fork acrescenta: o agente trabalha em portugues.

Um Harvey traduzido so no prompt continua surdo em portugues — quem responde
"me tira da lista" nao sai da lista, e "clique aqui" passa pelo porteiro. Estes
testes prendem o comportamento em PT-BR para que ele nao se perca num merge
com o upstream.
"""
import pytest

from harvey.agents.handler import (
    BARE_OPT_OUTS, ESCALATION_PATTERNS, _opt_out_reason,
)
from harvey.config import ComplianceConfig
from harvey.gate import BANNED_PHRASES, pre_send_check

CORPO = ("Vi que a Acme contratou dois instaladores esse mes. "
         "Como voces estao agendando as visitas hoje?")


def _barra(corpo):
    r = pre_send_check("ana@acme.example", "agenda de visitas", corpo)
    return [m for m in r.reasons if "banned phrases" in m]


@pytest.mark.parametrize("frase", [
    "clique aqui", "ultima chance", "última chance",
    "oferta imperdível", "100% gratis", "ganhe dinheiro",
    "espero que esteja bem", "imagine só", "divisor de águas",
])
def test_o_porteiro_barra_a_frase_em_portugues(frase):
    assert frase in BANNED_PHRASES
    assert _barra(f"{CORPO} {frase.capitalize()}.")


def test_um_email_limpo_em_portugues_passa():
    assert not _barra(CORPO)


@pytest.mark.parametrize("resposta", [
    "Não quero mais receber esses e-mails.",
    "nao quero mais receber",
    "Me tira da lista, por favor.",
    "Pare de enviar e-mail pra mim.",
    "Favor me remover.",
    "Quero descadastrar esse endereco.",
    "Apague meus dados, por favor.",
])
def test_pedido_de_saida_em_portugues_e_reconhecido(resposta):
    assert _opt_out_reason(resposta, resposta) is not None


@pytest.mark.parametrize("resposta", [
    "Não.",
    "nao",
    "Nao, a gente ja resolveu isso internamente.",
    "Nao uso esse tipo de ferramenta.",
])
def test_um_nao_seco_nao_e_pedido_de_saida(resposta):
    """Responder "nao" a uma pergunta nao tira a pessoa da lista para sempre:
    isso e not_interested, que encerra a conversa sem queimar o contato."""
    assert "nao" not in BARE_OPT_OUTS
    assert _opt_out_reason(resposta, resposta) is None


def test_o_rodape_em_portugues_passa_na_validacao():
    linha = 'Não quer mais receber? Responda "sair" que eu não mando de novo.'
    assert ComplianceConfig(opt_out_line=linha).opt_out_line == linha


def test_o_rodape_sem_palavra_de_saida_continua_sendo_recusado():
    with pytest.raises(ValueError):
        ComplianceConfig(opt_out_line="Abraco e ate a proxima.")


@pytest.mark.parametrize("termo", ["advogado", "procon", "lgpd", "anpd",
                                   "notificação extrajudicial"])
def test_ameaca_juridica_em_portugues_sobe_para_um_humano(termo):
    assert termo in ESCALATION_PATTERNS
