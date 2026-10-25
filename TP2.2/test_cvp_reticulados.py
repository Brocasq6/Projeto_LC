# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.16.5",
#     "numpy",
#     "pandas",
#     "cvxpy",
#     "clarabel",
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
    # Testes automáticos do CVP com programação cónica

    > **Código gerado por LLM.** Os testes deste notebook (a classe
    > `TestesCVP`) foram gerados pelo **Claude** a partir da estrutura de funções
    > de `cvp_reticulados.py`. No código, o bloco gerado está delimitado pelos
    > comentários `INÍCIO DO CÓDIGO GERADO POR LLM` e `FIM DO CÓDIGO GERADO POR LLM`.
    >
    > *(a preencher: link da conversa e prompt usado)*

    Os testes tratam as funções como caixas pretas: só usam as assinaturas e os
    formatos de retorno descritos nas docstrings do notebook principal. Os testes
    que precisam de um solver são ignorados (skip) se o solver escolhido em
    `METODO` não estiver instalado.

    ## O que verifica cada teste

    ### Geração da instância

    | Teste | Regra | O que verifica |
    | --- | --- | --- |
    | `test_gerar_base_dimensoes_e_intervalo` | C4 | G tem forma k × m e entradas em [0, 1]. |
    | `test_verificar_base_aceita_independente` | C1 | Uma base claramente independente é aceite. |
    | `test_verificar_base_rejeita_dependente` | C1 | Uma base com uma linha repetida é rejeitada. |
    | `test_verificar_base_rejeita_combinacao_linear` | C1 | Uma linha que é soma de outras é rejeitada. |
    | `test_gerar_target_formula_e_positivo` | C5 | t = Gᵀu, u ∈ [0, ell] e t ≥ 0. |
    | `test_gerar_instancia_campos_e_dimensoes` | C1, C5 | Chaves do dicionário, m = 2k, base válida. |
    | `test_gerar_instancia_m_explicito` | — | O parâmetro m é respeitado. |
    | `test_reprodutibilidade_com_semente` | — | A mesma semente dá a mesma instância. |
    | `test_sementes_diferentes_dao_instancias_diferentes` | — | Sementes diferentes dão instâncias diferentes. |

    ### Funções auxiliares e validador

    | Teste | Regra | O que verifica |
    | --- | --- | --- |
    | `test_distancia_caso_conhecido` | O1 | dist((0,0), (3,4)) = 5. |
    | `test_e_inteira` | C2 | Deteta vetores inteiros e fracionários (com tolerância). |
    | `test_escolher_variavel` | C2 | Devolve um índice fracionário, ou None se não houver. |
    | `test_construir_solucao_campos_e_coerencia` | O1 | x = Gᵀz e distância coerente. |
    | `test_validador_aceita_solucao_valida` | C1–C5 | Uma solução válida feita à mão não tem erros. |
    | `test_c2_validador_deteta_nao_inteiro` | C2 | Um z fracionário é detetado. |
    | `test_c3_validador_deteta_acima_do_limite` | C3 | z_i > ell é detetado. |
    | `test_c3_validador_deteta_negativo` | C3 | z_i < 0 é detetado. |
    | `test_validador_deteta_x_incoerente` | — | Um x que não é Gᵀz é detetado. |
    | `test_validador_deteta_distancia_incoerente` | O1 | Uma distância errada é detetada. |

    ### Modelo e resolução

    | Teste | O que verifica |
    | --- | --- |
    | `test_montar_problema_e_cvxpy_valido` | O problema é um `cp.Problem` e o objetivo é de minimização. |
    | `test_montar_problema_e_dcp` | O problema segue as regras DCP do cvxpy (convexo/cónico). |
    | `test_resolver_cvp_solucao_valida` | Uma instância pequena é resolvida e passa na validação. |
    | `test_caso_pequeno_contra_forca_bruta_ell1` | Com k = 4 e ell = 1, o ótimo coincide com a enumeração de todos os z. |
    | `test_caso_pequeno_contra_forca_bruta_ell5` | Com k = 3 e ell = 5, idem. |
    | `test_relaxacao_e_limite_inferior` | A relaxação contínua nunca é pior do que o ótimo inteiro. |
    | `test_otimo_nao_pior_que_arredondado` | O ótimo inteiro nunca é pior do que o arredondamento. |
    | `test_arredondada_e_valida` | A solução arredondada respeita C2 e C3. |

    ### Comparação e experiências

    | Teste | O que verifica |
    | --- | --- |
    | `test_comparar_metodos_campos` | As linhas têm todas as colunas e gap ≥ 0. |
    | `test_tabela_markdown` | Cabeçalho e uma linha por resultado. |
    | `test_correr_experiencias_grelha_pequena` | Uma linha por (k, ell, método) numa grelha pequena. |
    | `test_apresentar_solucao_dataframe` | Devolve um DataFrame não vazio. |
    """
    )
    return


@app.cell
def _(mo):
    import io
    import itertools
    import sys
    import unittest
    from pathlib import Path

    import cvxpy as cp
    import numpy as np
    import pandas as pd

    pasta_projeto = Path(__file__).resolve().parent
    if str(pasta_projeto) not in sys.path:
        sys.path.insert(0, str(pasta_projeto))

    import cvp_reticulados as nb
    from cvp_reticulados import (
        apresentar_solucao,
        comparar_metodos,
        construir_solucao,
        correr_experiencias,
        distancia,
        e_inteira,
        escolher_variavel,
        gerar_base,
        gerar_instancia,
        gerar_target,
        montar_problema,
        resolver,
        resolver_cvp,
        solucao_arredondada,
        tabela_markdown,
        validar_solucao,
        verificar_base,
    )

    METODO = getattr(nb, "METODO", "mosek")
    SOLVER_NECESSARIO = "MOSEK" if METODO == "mosek" else "CLARABEL"
    SOLVER_DISPONIVEL = SOLVER_NECESSARIO in cp.installed_solvers()
    TOL = 1e-5

    # ==================================================================
    # INÍCIO DO CÓDIGO GERADO POR LLM (Claude)
    # ==================================================================

    def instancia_manual(G, u, ell):
        """Instância construída à mão (sem passar por gerar_instancia)."""
        G = np.asarray(G, dtype=float)
        u = np.asarray(u, dtype=float)
        return {
            "k": G.shape[0], "m": G.shape[1], "ell": ell,
            "G": G, "t": G.T @ u, "u": u, "semente": None,
        }

    def forca_bruta(instancia):
        """Melhor distância por enumeração de todos os z ∈ {0..ell}^k (só para k pequeno)."""
        G, t, ell, k = instancia["G"], instancia["t"], instancia["ell"], instancia["k"]
        return min(
            np.linalg.norm(G.T @ np.array(z) - t)
            for z in itertools.product(range(ell + 1), repeat=k)
        )

    precisa_solver = unittest.skipUnless(
        SOLVER_DISPONIVEL, f"solver {SOLVER_NECESSARIO} não instalado"
    )

    class TestesCVP(unittest.TestCase):

        # ---------------- Geração da instância ----------------

        def test_gerar_base_dimensoes_e_intervalo(self):
            G = gerar_base(6, 12, np.random.default_rng(1))
            self.assertEqual(G.shape, (6, 12))
            self.assertTrue(np.all(G >= 0) and np.all(G <= 1))

        def test_verificar_base_aceita_independente(self):
            G = np.hstack([np.eye(4), np.zeros((4, 4))])
            self.assertTrue(verificar_base(G))

        def test_verificar_base_rejeita_dependente(self):
            G = gerar_base(5, 10, np.random.default_rng(2))
            G[4] = G[0]
            self.assertFalse(verificar_base(G))

        def test_verificar_base_rejeita_combinacao_linear(self):
            G = gerar_base(5, 10, np.random.default_rng(3)) / 2
            G[4] = G[0] + G[1]
            self.assertFalse(verificar_base(G))

        def test_gerar_target_formula_e_positivo(self):
            G = gerar_base(5, 10, np.random.default_rng(4))
            for ell in (1, 5):
                t, u = gerar_target(G, ell, np.random.default_rng(5))
                self.assertEqual(u.shape, (5,))
                self.assertEqual(t.shape, (10,))
                self.assertTrue(np.all(u >= 0) and np.all(u <= ell))
                self.assertTrue(np.all(t >= 0))
                np.testing.assert_allclose(t, G.T @ u)

        def test_gerar_instancia_campos_e_dimensoes(self):
            inst = gerar_instancia(k=7, ell=5, semente=0)
            for chave in ("k", "m", "ell", "G", "t", "u", "semente"):
                self.assertIn(chave, inst)
            self.assertEqual(inst["m"], 2 * inst["k"])
            self.assertEqual(inst["G"].shape, (7, 14))
            self.assertEqual(inst["t"].shape, (14,))
            self.assertTrue(verificar_base(inst["G"]))
            np.testing.assert_allclose(inst["t"], inst["G"].T @ inst["u"])

        def test_gerar_instancia_m_explicito(self):
            inst = gerar_instancia(k=4, ell=1, semente=0, m=9)
            self.assertEqual(inst["G"].shape, (4, 9))

        def test_reprodutibilidade_com_semente(self):
            a = gerar_instancia(k=6, ell=1, semente=42)
            b = gerar_instancia(k=6, ell=1, semente=42)
            np.testing.assert_array_equal(a["G"], b["G"])
            np.testing.assert_array_equal(a["t"], b["t"])

        def test_sementes_diferentes_dao_instancias_diferentes(self):
            a = gerar_instancia(k=6, ell=1, semente=1)
            b = gerar_instancia(k=6, ell=1, semente=2)
            self.assertFalse(np.array_equal(a["G"], b["G"]))

        # ---------------- Auxiliares e validador ----------------

        def test_distancia_caso_conhecido(self):
            self.assertAlmostEqual(distancia(np.array([0.0, 0.0]), np.array([3.0, 4.0])), 5.0)
            self.assertAlmostEqual(distancia(np.array([1.0, 2.0]), np.array([1.0, 2.0])), 0.0)

        def test_e_inteira(self):
            self.assertTrue(e_inteira(np.array([0.0, 1.0, 5.0])))
            self.assertTrue(e_inteira(np.array([1e-9, 0.9999999999])))
            self.assertFalse(e_inteira(np.array([0.0, 0.5, 1.0])))

        def test_escolher_variavel(self):
            self.assertIsNone(escolher_variavel(np.array([0.0, 1.0, 2.0])))
            self.assertEqual(escolher_variavel(np.array([0.0, 0.4, 2.0])), 1)
            i = escolher_variavel(np.array([0.3, 1.0, 2.7]))
            self.assertIn(i, (0, 2))

        def test_construir_solucao_campos_e_coerencia(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([1.0, 0.0, 1.0, 0.0]), inst, "optimal", 0.1)
            for chave in ("z", "x", "distancia", "estado", "tempo", "nos"):
                self.assertIn(chave, sol)
            np.testing.assert_allclose(sol["x"], inst["G"].T @ sol["z"])
            self.assertAlmostEqual(sol["distancia"], np.linalg.norm(sol["x"] - inst["t"]))

        def test_validador_aceita_solucao_valida(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([1.0, 0.0, 1.0, 1.0]), inst, "optimal", 0.0)
            self.assertEqual(validar_solucao(sol, inst), [])

        def test_c2_validador_deteta_nao_inteiro(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([1.0, 0.0, 1.0, 1.0]), inst, "optimal", 0.0)
            sol["z"] = np.array([1.0, 0.5, 1.0, 1.0])
            sol["x"] = inst["G"].T @ sol["z"]
            sol["distancia"] = np.linalg.norm(sol["x"] - inst["t"])
            self.assertTrue(validar_solucao(sol, inst))

        def test_c3_validador_deteta_acima_do_limite(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([2.0, 0.0, 0.0, 0.0]), inst, "optimal", 0.0)
            self.assertTrue(validar_solucao(sol, inst))

        def test_c3_validador_deteta_negativo(self):
            inst = gerar_instancia(k=4, ell=5, semente=0)
            sol = construir_solucao(np.array([-1.0, 0.0, 0.0, 0.0]), inst, "optimal", 0.0)
            self.assertTrue(validar_solucao(sol, inst))

        def test_validador_deteta_x_incoerente(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([1.0, 0.0, 1.0, 1.0]), inst, "optimal", 0.0)
            sol["x"] = sol["x"] + 1.0
            self.assertTrue(validar_solucao(sol, inst))

        def test_validador_deteta_distancia_incoerente(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            sol = construir_solucao(np.array([1.0, 0.0, 1.0, 1.0]), inst, "optimal", 0.0)
            sol["distancia"] = sol["distancia"] + 1.0
            self.assertTrue(validar_solucao(sol, inst))

        # ---------------- Modelo e resolução ----------------

        def test_montar_problema_e_cvxpy_valido(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            problema, z = montar_problema(inst, inteiro=False)
            self.assertIsInstance(problema, cp.Problem)
            self.assertIsInstance(problema.objective, cp.Minimize)
            self.assertEqual(z.shape, (4,))

        def test_montar_problema_e_dcp(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            problema, _ = montar_problema(inst, inteiro=False)
            self.assertTrue(problema.is_dcp())

        @precisa_solver
        def test_resolver_cvp_solucao_valida(self):
            inst = gerar_instancia(k=5, ell=1, semente=0)
            sol = resolver_cvp(inst)
            self.assertIn(sol["estado"], ("optimal", "optimal_inaccurate"))
            self.assertEqual(validar_solucao(sol, inst), [])

        @precisa_solver
        def test_caso_pequeno_contra_forca_bruta_ell1(self):
            for semente in (0, 1, 2):
                inst = gerar_instancia(k=4, ell=1, semente=semente)
                sol = resolver_cvp(inst)
                self.assertAlmostEqual(sol["distancia"], forca_bruta(inst), delta=TOL)

        @precisa_solver
        def test_caso_pequeno_contra_forca_bruta_ell5(self):
            for semente in (0, 1):
                inst = gerar_instancia(k=3, ell=5, semente=semente)
                sol = resolver_cvp(inst)
                self.assertAlmostEqual(sol["distancia"], forca_bruta(inst), delta=TOL)

        @precisa_solver
        def test_relaxacao_e_limite_inferior(self):
            inst = gerar_instancia(k=5, ell=5, semente=0)
            problema, z = montar_problema(inst, inteiro=False)
            resolver(problema)
            dist_relaxada = np.linalg.norm(inst["G"].T @ z.value - inst["t"])
            sol = resolver_cvp(inst)
            self.assertLessEqual(dist_relaxada, sol["distancia"] + TOL)

        @precisa_solver
        def test_otimo_nao_pior_que_arredondado(self):
            for ell in (1, 5):
                inst = gerar_instancia(k=6, ell=ell, semente=0)
                otimo = resolver_cvp(inst)
                arredondada = solucao_arredondada(inst)
                self.assertLessEqual(otimo["distancia"], arredondada["distancia"] + TOL)

        @precisa_solver
        def test_arredondada_e_valida(self):
            inst = gerar_instancia(k=6, ell=5, semente=0)
            sol = solucao_arredondada(inst)
            self.assertTrue(e_inteira(sol["z"]))
            self.assertTrue(np.all(sol["z"] >= 0) and np.all(sol["z"] <= inst["ell"]))
            self.assertEqual(validar_solucao(sol, inst), [])

        # ---------------- Comparação e experiências ----------------

        @precisa_solver
        def test_comparar_metodos_campos(self):
            inst = gerar_instancia(k=5, ell=1, semente=0)
            linhas = comparar_metodos(inst)
            self.assertGreaterEqual(len(linhas), 2)
            for linha in linhas:
                for chave in ("k", "m", "ell", "metodo", "estado", "tempo",
                              "distancia", "gap", "nos", "erros"):
                    self.assertIn(chave, linha)
                self.assertGreaterEqual(linha["gap"], -TOL)
                self.assertEqual(linha["erros"], 0)

        def test_tabela_markdown(self):
            linhas = [
                {"k": 30, "m": 60, "ell": 1, "metodo": "A", "estado": "optimal",
                 "tempo": 0.1, "distancia": 1.0, "gap": 0.0, "nos": 1, "erros": 0},
                {"k": 30, "m": 60, "ell": 1, "metodo": "B", "estado": "optimal",
                 "tempo": 0.2, "distancia": 1.5, "gap": 0.5, "nos": None, "erros": 0},
            ]
            texto = tabela_markdown(linhas)
            self.assertIsInstance(texto, str)
            self.assertEqual(len([l for l in texto.splitlines() if l.startswith("|")]), 4)

        @precisa_solver
        def test_correr_experiencias_grelha_pequena(self):
            linhas = correr_experiencias(valores_k=[4, 5], valores_ell=[1], semente=0)
            pares = {(l["k"], l["ell"]) for l in linhas}
            self.assertEqual(pares, {(4, 1), (5, 1)})
            self.assertTrue(all(l["m"] == 2 * l["k"] for l in linhas))

        @precisa_solver
        def test_apresentar_solucao_dataframe(self):
            inst = gerar_instancia(k=4, ell=1, semente=0)
            tabela = apresentar_solucao(resolver_cvp(inst), inst)
            self.assertIsInstance(tabela, pd.DataFrame)
            self.assertFalse(tabela.empty)

    # ==================================================================
    # FIM DO CÓDIGO GERADO POR LLM (Claude)
    # ==================================================================

    saida = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestesCVP)
    resultado = unittest.TextTestRunner(stream=saida, verbosity=2).run(suite)
    estado_testes = "passou" if resultado.wasSuccessful() else "falhou"
    mo.md(
        f"## Resultado dos testes: {estado_testes}\n\n"
        f"Solver usado: `{SOLVER_NECESSARIO}` (disponível: {SOLVER_DISPONIVEL}).\n\n"
        f"Testes executados: {resultado.testsRun}; falhas: {len(resultado.failures)}; "
        f"erros: {len(resultado.errors)}; ignorados: {len(resultado.skipped)}.\n\n"
        "```text\n" + saida.getvalue() + "\n```"
    )
    return


if __name__ == "__main__":
    app.run()