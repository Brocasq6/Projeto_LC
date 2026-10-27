# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.16.5",
#     "pandas",
#     "pysmt",
# ]
# ///

import marimo

__generated_with = "0.16.5"
app = marimo.App(width="full")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # Testes automáticos — Exercício 1 (Game of Life como FSM)

    _TODO: indicar quem escreveu os testes (e, se houver, o prompt e a conversa
    com o LLM usados para os gerar)._

    Cada teste está, por agora, marcado como ignorado (`skipTest`). Substituir
    o `skipTest` pela verificação descrita na docstring à medida que as funções
    do notebook principal (`automato_celular.py`) forem implementadas.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## O que verifica cada teste

    ### Geometria e estado inicial

    | Teste | O que verifica |
    | --- | --- |
    | `test_numero_de_celulas` | Quantidades de células normais, iniciais e finais pedidas no enunciado. |
    | `test_conjuntos_disjuntos` | Nenhuma célula é ao mesmo tempo normal, inicial e/ou final. |
    | `test_cantos_da_moldura_sao_finais` | (0, N+1) e (N+1, 0) são células finais (decisão da secção 3). |
    | `test_vizinhanca` | Número e identidade dos vizinhos numa célula interior e numa de canto. |
    | `test_estado_inicial` | Células normais vivas e mortas no estado inicial. |
    | `test_sorteio_reproduzivel` | A mesma semente dá as mesmas células iniciais. |

    ### Regra e transições

    | Teste | O que verifica |
    | --- | --- |
    | `test_regra_nascimento` | Célula morta com 3 vizinhos vivos nasce; com outro número não nasce. |
    | `test_regra_sobrevivencia_e_morte` | Célula viva sobrevive com 2 ou 3 vizinhos e morre nos restantes casos. |
    | `test_fronteira_constante` | Células iniciais e finais não mudam ao longo de uma execução. |
    | `test_sincrona_coincide_com_simulador` | A transição síncrona simbólica e o simulador concreto dão o mesmo estado seguinte. |
    | `test_assincrona_muda_uma_celula` | No modo assíncrono cada transição muda exatamente uma célula normal (ou nenhuma, se o estado for estável). |
    | `test_parametro_seleciona_transicao` | `trans` usa a relação indicada por `modo`. |

    ### BMC genérico

    | Teste | O que verifica |
    | --- | --- |
    | `test_bmc_always_programa_da_ficha7` | No programa da ficha 7, `bmc_always` não encontra contra-exemplo para $G\,(x \ge 0)$ e encontra um para $G\,(x \ne 1)$. |
    | `test_bmc_eventually_programa_da_ficha7` | No programa da ficha 7, `bmc_eventually` não encontra contra-exemplo para $F\,(pc = 2)$ e encontra um lacete para $F\,(x < 0)$. |

    ### Propriedades

    | Teste | O que verifica |
    | --- | --- |
    | `test_contra_exemplos_sao_tracos_validos` | Qualquer contra-exemplo devolvido é uma execução válida (confirmado pelo simulador). |
    | `test_resultados_reproduziveis` | A mesma semente e o mesmo modo dão o mesmo resultado. |
    | `test_outro_tamanho_de_grelha` | O modelo funciona com outro valor de N (> 16) sem alterar o código. |
    """
    )
    return


@app.cell
def _(mo):
    import io
    import unittest

    # TODO: importar do notebook principal as funções a testar, p. ex.:
    # from automato_celular import (
    #     celulas_normais, celulas_iniciais, celulas_finais, vizinhos,
    #     sortear_iniciais, construir_fronteira, estado_inicial_concreto,
    #     passo_concreto, traco_e_valido, trans, fabricar_fsm,
    #     bmc_always, bmc_eventually,
    #     verificar_nunca_erro, verificar_todas_celulas,
    # )

    class TestesAutomatoCelular(unittest.TestCase):
        # --- Geometria e estado inicial ---
        def test_numero_de_celulas(self):
            """N×N normais, 2N+1 iniciais e 2N+3 finais."""
            self.skipTest("TODO")

        def test_conjuntos_disjuntos(self):
            """Os três conjuntos de células não se intersetam."""
            self.skipTest("TODO")

        def test_cantos_da_moldura_sao_finais(self):
            """(0, N+1) e (N+1, 0) pertencem às células finais e não às iniciais."""
            self.skipTest("TODO")

        def test_vizinhanca(self):
            """Célula interior e célula de canto têm os vizinhos esperados."""
            self.skipTest("TODO")

        def test_estado_inicial(self):
            """Só as células normais com i, j <= 3 estão vivas no início."""
            self.skipTest("TODO")

        def test_sorteio_reproduzivel(self):
            """sortear_iniciais com a mesma semente devolve o mesmo resultado."""
            self.skipTest("TODO")

        # --- Regra e transições ---
        def test_regra_nascimento(self):
            """B3: nascimento só com exatamente 3 vizinhos vivos."""
            self.skipTest("TODO")

        def test_regra_sobrevivencia_e_morte(self):
            """S23: sobrevivência com 2 ou 3 vizinhos vivos; morte nos outros casos."""
            self.skipTest("TODO")

        def test_fronteira_constante(self):
            """Células iniciais e finais mantêm o valor em todos os passos."""
            self.skipTest("TODO")

        def test_sincrona_coincide_com_simulador(self):
            """Modelo simbólico e simulador concreto concordam num passo síncrono."""
            self.skipTest("TODO")

        def test_assincrona_muda_uma_celula(self):
            """Uma transição assíncrona altera exatamente uma célula normal (lacete se estável)."""
            self.skipTest("TODO")

        def test_parametro_seleciona_transicao(self):
            """O parâmetro de modo escolhe a relação de transição correta."""
            self.skipTest("TODO")

        # --- BMC genérico ---
        def test_bmc_always_programa_da_ficha7(self):
            """bmc_always: G(x >= 0) sem contra-exemplo; G(x != 1) com contra-exemplo (programa da ficha 7)."""
            self.skipTest("TODO")

        def test_bmc_eventually_programa_da_ficha7(self):
            """bmc_eventually: F(pc = 2) sem contra-exemplo; F(x < 0) com lacete (programa da ficha 7)."""
            self.skipTest("TODO")

        # --- Propriedades ---
        def test_contra_exemplos_sao_tracos_validos(self):
            """Contra-exemplos das propriedades passam em traco_e_valido."""
            self.skipTest("TODO")

        def test_resultados_reproduziveis(self):
            """Duas execuções com os mesmos parâmetros dão o mesmo resultado."""
            self.skipTest("TODO")

        def test_outro_tamanho_de_grelha(self):
            """O modelo corre com outro N > 16."""
            self.skipTest("TODO")

    saida = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestesAutomatoCelular)
    resultado = unittest.TextTestRunner(stream=saida, verbosity=2).run(suite)
    estado_testes = "passou" if resultado.wasSuccessful() else "falhou"
    mo.md(
        f"## Resultado dos testes: {estado_testes}\n\n"
        f"Testes executados: {resultado.testsRun}; falhas: {len(resultado.failures)}; "
        f"erros: {len(resultado.errors)}; ignorados: {len(resultado.skipped)}.\n\n"
        "```text\n" + saida.getvalue() + "\n```"
    )
    return


if __name__ == "__main__":
    app.run()
