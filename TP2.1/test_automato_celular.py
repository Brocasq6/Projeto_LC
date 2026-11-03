# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.16.5",
#     "pandas",
#     "pysmt",
#     "z3-solver",
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

    > **Código gerado por LLM.** Os testes da geometria da grelha
    > (`TestesGeometria`) e do estado inicial, da regra e das transições
    > (`TestesEstadoETransicoes`) foram gerados pelo **Claude**. O nosso
    > trabalho foi integrá-los no projeto, executá-los e confirmar que passam.
    > No código, cada bloco gerado está delimitado pelos comentários
    > `INÍCIO DO CÓDIGO GERADO POR LLM` e `FIM DO CÓDIGO GERADO POR LLM`.

    **Prompt usado (transcrito tal como foi escrito):**

    > gera me agora os testes, so para confirmar que o codigo esta correto

    Os testes das funções ainda não implementadas estão na classe
    `TestesPorImplementar`, marcados como ignorados (`skipTest`). Substituir o
    `skipTest` pela verificação descrita na docstring à medida que essas
    funções forem feitas.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## O que verifica cada teste

    ### Geometria da grelha (implementados)

    Todos correm para vários tamanhos de grelha (`n` = 2, 3, 5, 17 e 20), para
    confirmar que as funções usam o parâmetro `n` e não a constante `N`.

    | Teste | Função | O que verifica |
    | --- | --- | --- |
    | `test_numero_de_celulas` | as três | $n^2$ normais, $2n+1$ iniciais e $2n+3$ finais, sem repetidos. |
    | `test_indices_das_normais` | `celulas_normais` | Os dois índices estão entre 1 e `n`. |
    | `test_indices_das_iniciais` | `celulas_iniciais` | Um dos índices é 0 e nenhum sai da moldura. |
    | `test_indices_das_finais` | `celulas_finais` | Um dos índices é `n+1`, nenhum sai da moldura e nenhuma é inicial. |
    | `test_conjuntos_disjuntos` | as três | Os três conjuntos não se intersetam e, juntos, cobrem a moldura de $(n+2)^2$ posições. |
    | `test_cantos_da_moldura` | iniciais e finais | Cada canto da moldura pertence ao conjunto imposto pelas contagens do enunciado. |
    | `test_vizinhanca` | `vizinhos` | Numa célula interior e nos quatro cantos da grelha normal: quantos vizinhos são normais, iniciais e finais. |
    | `test_vizinhos_segundo_a_definicao` | `vizinhos` | Para todas as células normais: 8 vizinhos distintos, sem a própria célula, todos com $\max(\lvert\Delta i\rvert, \lvert\Delta j\rvert) = 1$ e dentro da moldura. |
    | `test_vizinhanca_simetrica` | `vizinhos` | Se `b` é vizinha de `a` (ambas normais), `a` é vizinha de `b`. |

    ### Estado inicial, regra e transições (implementados)

    | Teste | Função | O que verifica |
    | --- | --- | --- |
    | `test_estado_inicial` | `init` | Só as células com $i, j \le 3$ estão vivas, e `init` não admite outro estado (N = 5 e 17). |
    | `test_sorteio_reproduzivel` | `sortear_iniciais`, `construir_fronteira` | A mesma semente dá a mesma moldura, os valores são 0/1, as finais estão a 0 e sementes diferentes dão molduras diferentes. |
    | `test_regra_nascimento` | `proximo_valor` | Célula morta nasce só com exatamente 3 vizinhos vivos (0 a 8 vizinhos). |
    | `test_regra_sobrevivencia_e_morte` | `proximo_valor` | Célula viva sobrevive com 2 ou 3 vizinhos vivos e morre nos restantes casos. |
    | `test_regra_com_vizinhos_da_moldura` | `proximo_valor` | Na célula (1, 1) as vizinhas iniciais vivas entram na contagem. |
    | `test_fronteira_constante` | `declarar_estado`, `valor_celula` | Iniciais e finais não são variáveis: valem sempre a constante da moldura. |
    | `test_assincrona_muda_uma_celula` | `trans_assincrona` | A partir do estado inicial muda exatamente uma célula; num estado estável a única transição é o lacete. |
    | `test_parametro_seleciona_transicao` | `trans` | `modo` escolhe a relação certa e um modo inválido dá `ValueError`. |

    ### Por implementar

    | Teste | O que vai verificar |
    | --- | --- |
    | `test_sincrona_coincide_com_simulador` | A transição síncrona simbólica e o simulador concreto dão o mesmo estado seguinte. |
    | `test_bmc_always_programa_da_ficha7` | No programa da ficha 7, `bmc_always` não encontra contra-exemplo para $G\,(x \ge 0)$ e encontra um para $G\,(x \ne 1)$. |
    | `test_bmc_eventually_programa_da_ficha7` | No programa da ficha 7, `bmc_eventually` não encontra contra-exemplo para $F\,(pc = 2)$ e encontra um lacete para $F\,(x < 0)$. |
    | `test_contra_exemplos_sao_tracos_validos` | Qualquer contra-exemplo devolvido é uma execução válida (confirmado pelo simulador). |
    | `test_resultados_reproduziveis` | A mesma semente e o mesmo modo dão o mesmo resultado. |
    """
    )
    return


@app.cell
def _(mo):
    import io
    import unittest

    from pysmt.shortcuts import FALSE, TRUE, And, Equals, Iff, Int, Ite, Not, Plus, Solver

    from automato_celular import (
        celulas_finais,
        celulas_iniciais,
        celulas_normais,
        construir_fronteira,
        declarar_estado,
        init,
        proximo_valor,
        sortear_iniciais,
        trans,
        trans_assincrona,
        trans_sincrona,
        valor_celula,
        vizinhos,
    )

    # ==================================================================
    # INÍCIO DO CÓDIGO GERADO POR LLM (Claude)
    # Toda a classe TestesGeometria foi gerada pelo Claude a partir do
    # prompt transcrito no início deste notebook.
    # ==================================================================
    TAMANHOS = (2, 3, 5, 17, 20)  # inclui grelhas pequenas (verificáveis à mão) e N > 16

    def moldura(n):
        """Todas as posições (i, j) com i, j em 0..n+1: normais, iniciais e finais juntas."""
        return {(i, j) for i in range(n + 2) for j in range(n + 2)}

    def como_lista(resultado):
        """Converte o resultado (lista, conjunto ou gerador) numa lista, para contar repetidos."""
        return list(resultado)

    class TestesGeometria(unittest.TestCase):
        def test_numero_de_celulas(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    normais = como_lista(celulas_normais(n))
                    iniciais = como_lista(celulas_iniciais(n))
                    finais = como_lista(celulas_finais(n))
                    self.assertEqual(len(normais), n * n)
                    self.assertEqual(len(iniciais), 2 * n + 1)
                    self.assertEqual(len(finais), 2 * n + 3)
                    self.assertEqual(len(set(normais)), len(normais), "células normais repetidas")
                    self.assertEqual(len(set(iniciais)), len(iniciais), "células iniciais repetidas")
                    self.assertEqual(len(set(finais)), len(finais), "células finais repetidas")

        def test_indices_das_normais(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    for i, j in celulas_normais(n):
                        self.assertTrue(1 <= i <= n and 1 <= j <= n, f"({i}, {j}) não é normal")

        def test_indices_das_iniciais(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    for celula in celulas_iniciais(n):
                        self.assertIn(celula, moldura(n), f"{celula} fora da moldura")
                        self.assertEqual(min(celula), 0, f"{celula} não tem nenhum índice 0")

        def test_indices_das_finais(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    iniciais = set(celulas_iniciais(n))
                    for celula in celulas_finais(n):
                        self.assertIn(celula, moldura(n), f"{celula} fora da moldura")
                        self.assertEqual(max(celula), n + 1, f"{celula} não tem nenhum índice n+1")
                        self.assertNotIn(celula, iniciais, f"{celula} é inicial e final")

        def test_conjuntos_disjuntos(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    normais = set(celulas_normais(n))
                    iniciais = set(celulas_iniciais(n))
                    finais = set(celulas_finais(n))
                    self.assertFalse(normais & iniciais, "células normais e iniciais em comum")
                    self.assertFalse(normais & finais, "células normais e finais em comum")
                    self.assertFalse(iniciais & finais, "células iniciais e finais em comum")
                    self.assertEqual(normais | iniciais | finais, moldura(n), "a moldura não fica completa")

        def test_cantos_da_moldura(self):
            # Com 2n+1 iniciais e 2n+3 finais, só (0, 0) pode ser inicial;
            # os outros três cantos têm de ser finais para as contagens baterem certo.
            for n in TAMANHOS:
                with self.subTest(n=n):
                    iniciais = set(celulas_iniciais(n))
                    finais = set(celulas_finais(n))
                    self.assertIn((0, 0), iniciais)
                    self.assertIn((0, n + 1), finais)
                    self.assertIn((n + 1, 0), finais)
                    self.assertIn((n + 1, n + 1), finais)

        def test_vizinhanca(self):
            n = 17
            normais = set(celulas_normais(n))
            iniciais = set(celulas_iniciais(n))
            finais = set(celulas_finais(n))

            def contar(celula):
                """Quantos vizinhos da célula são (normais, iniciais, finais)."""
                vs = set(vizinhos(*celula, n=n))
                return len(vs & normais), len(vs & iniciais), len(vs & finais)

            casos = {
                (5, 5): (8, 0, 0),  # interior: só vizinhos normais
                (1, 1): (3, 5, 0),  # canto junto às células iniciais
                (1, n): (3, 2, 3),  # canto entre células iniciais e finais
                (n, 1): (3, 2, 3),  # canto entre células iniciais e finais
                (n, n): (3, 0, 5),  # canto junto às células finais
            }
            for celula, esperado in casos.items():
                with self.subTest(celula=celula):
                    self.assertEqual(contar(celula), esperado)

        def test_vizinhos_segundo_a_definicao(self):
            for n in TAMANHOS:
                with self.subTest(n=n):
                    for i, j in celulas_normais(n):
                        vs = como_lista(vizinhos(i, j, n=n))
                        self.assertEqual(len(vs), 8, f"({i}, {j}) tem {len(vs)} vizinhos")
                        self.assertEqual(len(set(vs)), 8, f"({i}, {j}) tem vizinhos repetidos")
                        self.assertNotIn((i, j), vs, f"({i}, {j}) é vizinha de si própria")
                        for a, b in vs:
                            self.assertEqual(max(abs(a - i), abs(b - j)), 1, f"({a}, {b}) não é vizinha de ({i}, {j})")
                            self.assertIn((a, b), moldura(n), f"({a}, {b}) fora da moldura")

        def test_vizinhanca_simetrica(self):
            n = 17
            normais = set(celulas_normais(n))
            for a in normais:
                for b in set(vizinhos(*a, n=n)) & normais:
                    self.assertIn(a, set(vizinhos(*b, n=n)), f"{b} é vizinha de {a}, mas não o contrário")

    # ==================================================================
    # FIM DO CÓDIGO GERADO POR LLM (Claude)
    # ==================================================================

    # ==================================================================
    # INÍCIO DO CÓDIGO GERADO POR LLM (Claude)
    # Toda a classe TestesEstadoETransicoes foi gerada pelo Claude.
    # ==================================================================
    def aplicar(formula, valores):
        """Substitui as variáveis por TRUE/FALSE segundo `valores` (variável -> 0/1) e simplifica a fórmula."""
        substituicao = {}
        for variavel, valor in valores.items():
            substituicao[variavel] = TRUE() if valor == 1 else FALSE()
        return formula.substitute(substituicao).simplify()

    def mudou_exatamente(s, p, celulas, quantas):
        """Fórmula «exatamente `quantas` células normais têm valor diferente em s e p»."""
        termos = []
        for c in celulas:
            termos.append(Ite(Not(Iff(p[c], s[c])), Int(1), Int(0)))
        return Equals(Plus(termos), Int(quantas))

    class TestesEstadoETransicoes(unittest.TestCase):
        # --- Estado inicial ---
        def test_estado_inicial(self):
            """Só as células normais com i, j <= 3 estão vivas no início (e init só admite esse estado)."""
            for n in (5, 17):
                with self.subTest(n=n):
                    fronteira = construir_fronteira(n)
                    s = declarar_estado(0, n)
                    with Solver(name="z3") as solver:
                        solver.add_assertion(init(s, fronteira, n))
                        self.assertTrue(solver.solve(), "init é impossível")
                        for (i, j), variavel in s.items():
                            esperado = i <= 3 and j <= 3
                            self.assertEqual(solver.get_py_value(variavel), esperado, f"({i}, {j}) errada")
                    # o estado inicial é único: não há outro estado que satisfaça init
                    exato = []
                    for (i, j), variavel in s.items():
                        exato.append(variavel if (i <= 3 and j <= 3) else Not(variavel))
                    with Solver(name="z3") as solver:
                        solver.add_assertion(And(init(s, fronteira, n), Not(And(exato))))
                        self.assertFalse(solver.solve(), "init admite mais do que um estado")

        def test_sorteio_reproduzivel(self):
            """A mesma semente dá a mesma moldura; os valores são 0/1 e as finais estão a 0."""
            for n in (2, 17):
                with self.subTest(n=n):
                    a = sortear_iniciais(n, 0)
                    b = sortear_iniciais(n, 0)
                    self.assertEqual(a, b)
                    self.assertEqual(set(a), set(celulas_iniciais(n)))
                    for valor in a.values():
                        self.assertIn(valor, (0, 1))
                    fronteira = construir_fronteira(n, 0)
                    self.assertEqual(set(fronteira), set(celulas_iniciais(n)) | set(celulas_finais(n)))
                    for celula in celulas_finais(n):
                        self.assertEqual(fronteira[celula], 0, f"{celula} final não está morta")
            # com N = 17 há 35 células iniciais: sementes diferentes dão molduras diferentes
            self.assertNotEqual(sortear_iniciais(17, 0), sortear_iniciais(17, 1))

        # --- Regra ---
        def _valor_seguinte(self, viva, vivos):
            """Valor (True/False) da célula (5, 5) com `vivos` vizinhos vivos, segundo proximo_valor."""
            n = 17
            fronteira = construir_fronteira(n)
            s = declarar_estado(0, n)
            vs = vizinhos(5, 5, n)  # (5, 5) é interior: os 8 vizinhos são normais
            valores = {}
            for c in celulas_normais(n):
                valores[s[c]] = 0
            for c in vs[:vivos]:
                valores[s[c]] = 1
            valores[s[(5, 5)]] = 1 if viva else 0
            resultado = aplicar(proximo_valor(s, (5, 5), fronteira, n), valores)
            self.assertTrue(resultado.is_constant(), "a fórmula não ficou constante")
            return resultado.is_true()

        def test_regra_nascimento(self):
            """B3: célula morta nasce só com exatamente 3 vizinhos vivos."""
            for vivos in range(9):
                with self.subTest(vivos=vivos):
                    self.assertEqual(self._valor_seguinte(False, vivos), vivos == 3)

        def test_regra_sobrevivencia_e_morte(self):
            """S23: célula viva sobrevive com 2 ou 3 vizinhos vivos e morre nos outros casos."""
            for vivos in range(9):
                with self.subTest(vivos=vivos):
                    self.assertEqual(self._valor_seguinte(True, vivos), vivos in (2, 3))

        def test_regra_com_vizinhos_da_moldura(self):
            """Na célula (1, 1) as vizinhas iniciais vivas entram na contagem."""
            n = 17
            fronteira = construir_fronteira(n)
            s = declarar_estado(0, n)
            vivos_moldura = 0
            for v in vizinhos(1, 1, n):
                if v in fronteira:
                    vivos_moldura += fronteira[v]
            valores = {}
            for c in celulas_normais(n):
                valores[s[c]] = 0  # todas as normais mortas: só contam as da moldura
            resultado = aplicar(proximo_valor(s, (1, 1), fronteira, n), valores)
            self.assertEqual(resultado.is_true(), vivos_moldura == 3)

        # --- Transições ---
        def test_fronteira_constante(self):
            """Iniciais e finais não são variáveis do estado: valem sempre a constante da moldura."""
            n = 17
            fronteira = construir_fronteira(n)
            for k in (0, 1, 5):
                s = declarar_estado(k, n)
                self.assertEqual(set(s), set(celulas_normais(n)))
                for celula, valor in fronteira.items():
                    termo = valor_celula(s, celula, fronteira)
                    self.assertTrue(termo.is_constant())
                    self.assertEqual(termo.is_true(), valor == 1, f"{celula} com valor errado")

        def test_assincrona_muda_uma_celula(self):
            """Uma transição assíncrona altera exatamente uma célula normal; nenhuma se o estado for estável."""
            n = 17
            fronteira = construir_fronteira(n)
            normais = celulas_normais(n)
            s = declarar_estado(0, n)
            p = declarar_estado(1, n)
            # a partir do estado inicial (há células que podem mudar): há transição e muda exatamente uma
            with Solver(name="z3") as solver:
                solver.add_assertion(And(init(s, fronteira, n), trans_assincrona(s, p, fronteira, n)))
                self.assertTrue(solver.solve(), "o estado inicial não tem sucessor")
            with Solver(name="z3") as solver:
                solver.add_assertion(And(init(s, fronteira, n), trans_assincrona(s, p, fronteira, n),
                                         Not(mudou_exatamente(s, p, normais, 1))))
                self.assertFalse(solver.solve(), "há transições que não mudam exatamente uma célula")
            # num estado estável (nenhuma célula pode mudar) a única transição é o lacete
            estavel = []
            for c in normais:
                estavel.append(Iff(proximo_valor(s, c, fronteira, n), s[c]))
            with Solver(name="z3") as solver:
                solver.add_assertion(And(And(estavel), trans_assincrona(s, p, fronteira, n)))
                self.assertTrue(solver.solve(), "um estado estável não tem sucessor (falta o lacete)")
            with Solver(name="z3") as solver:
                solver.add_assertion(And(And(estavel), trans_assincrona(s, p, fronteira, n),
                                         Not(mudou_exatamente(s, p, normais, 0))))
                self.assertFalse(solver.solve(), "um estado estável muda")

        def test_parametro_seleciona_transicao(self):
            """trans usa a relação indicada por `modo` e recusa modos inválidos."""
            n = 17
            fronteira = construir_fronteira(n)
            s = declarar_estado(0, n)
            p = declarar_estado(1, n)
            self.assertEqual(trans(s, p, fronteira, "sincrona", n), trans_sincrona(s, p, fronteira, n))
            self.assertEqual(trans(s, p, fronteira, "assincrona", n), trans_assincrona(s, p, fronteira, n))
            with self.assertRaises(ValueError):
                trans(s, p, fronteira, "outro", n)

    # ==================================================================
    # FIM DO CÓDIGO GERADO POR LLM (Claude)
    # ==================================================================

    class TestesPorImplementar(unittest.TestCase):
        # --- Transições ---
        def test_sincrona_coincide_com_simulador(self):
            """Modelo simbólico e simulador concreto concordam num passo síncrono."""
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

    saida = io.StringIO()
    suite = unittest.TestSuite()
    for classe in (TestesGeometria, TestesEstadoETransicoes, TestesPorImplementar):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(classe))
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
