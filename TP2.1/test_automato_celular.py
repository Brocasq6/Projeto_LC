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
    > (`TestesGeometria`), do estado inicial, da regra e das transições
    > (`TestesEstadoETransicoes`) e do BMC e das propriedades
    > (`TestesBMCEPropriedades`) foram gerados pelo **Claude**. O nosso
    > trabalho foi integrá-los no projeto, executá-los e confirmar que passam.
    > No código, cada bloco gerado está delimitado pelos comentários
    > `INÍCIO DO CÓDIGO GERADO POR LLM` e `FIM DO CÓDIGO GERADO POR LLM`.

    **Prompt usado (transcrito tal como foi escrito):**

    > gera me agora os testes, so para confirmar que o codigo esta correto

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

    ### BMC e propriedades (implementados)

    | Teste | Função | O que verifica |
    | --- | --- | --- |
    | `test_sincrona_coincide_com_simulador` | `trans_sincrona`, `passo_concreto` | Para vários estados (incluindo um aleatório), o sucessor dado pelo solver é o do simulador. |
    | `test_bmc_always_programa_da_ficha7` | `bmc_always` | No programa da ficha 7, $G\,(x \ge 0)$ não tem contra-exemplo e $G\,(x \ne 1)$ tem um mínimo, com 5 estados. |
    | `test_bmc_eventually_programa_da_ficha7` | `bmc_eventually` | No programa da ficha 7, $F\,(pc = 2)$ não tem contra-exemplo e $F\,(x < 0)$ tem um lacete em $pc = 2$. |
    | `test_contra_exemplos_sao_tracos_validos` | `verificar_nunca_erro`, `verificar_permanencia`, `traco_e_valido` | Os contra-exemplos das propriedades 1 e 2 no modo assíncrono são execuções válidas. |
    | `test_resultados_reproduziveis` | todas | A mesma semente e os mesmos parâmetros dão a mesma moldura, a mesma simulação e o mesmo resultado do BMC (no assíncrono o traço pode ser outro, mas também válido). |
    """
    )
    return


@app.cell
def _(mo):
    import io
    import random
    import unittest

    from pysmt.shortcuts import (
        FALSE, GE, GT, LE, LT, TRUE, And, Equals, Iff, Int, Ite, Minus, Not, Or, Plus, Solver, Symbol,
    )
    from pysmt.typing import INT

    from automato_celular import (
        celulas_finais,
        celulas_iniciais,
        bmc_always,
        bmc_eventually,
        celulas_normais,
        construir_fronteira,
        declarar_estado,
        estado_inicial_concreto,
        init,
        passo_concreto,
        proximo_valor,
        simular_ate_ciclo,
        sortear_iniciais,
        traco_e_valido,
        trans,
        trans_assincrona,
        trans_sincrona,
        valor_celula,
        verificar_nunca_erro,
        verificar_permanencia,
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

    # ==================================================================
    # INÍCIO DO CÓDIGO GERADO POR LLM (Claude)
    # Toda a classe TestesBMCEPropriedades foi gerada pelo Claude.
    # ==================================================================
    # Programa da ficha 7:  { x >= 3 }  0: while (x > 0):  1: x = x - 1  2: stop
    def declare_ficha7(i):
        return {"pc": Symbol(f"pc{i}", INT), "x": Symbol(f"x{i}", INT)}

    def init_ficha7(s):
        return And(Equals(s["pc"], Int(0)), GE(s["x"], Int(3)))

    def trans_ficha7(s, p):
        return Or(
            And(Equals(s["pc"], Int(0)), GT(s["x"], Int(0)), Equals(p["pc"], Int(1)), Equals(p["x"], s["x"])),
            And(Equals(s["pc"], Int(0)), LE(s["x"], Int(0)), Equals(p["pc"], Int(2)), Equals(p["x"], s["x"])),
            And(Equals(s["pc"], Int(1)), Equals(p["pc"], Int(0)), Equals(p["x"], Minus(s["x"], Int(1)))),
            And(Equals(s["pc"], Int(2)), Equals(p["pc"], Int(2)), Equals(p["x"], s["x"])),
        )

    class TestesBMCEPropriedades(unittest.TestCase):
        # --- Transições ---
        def test_sincrona_coincide_com_simulador(self):
            """Modelo simbólico e simulador concreto concordam num passo síncrono."""
            n = 17
            fronteira = construir_fronteira(n)
            normais = celulas_normais(n)
            rng = random.Random(1)
            grelhas = [estado_inicial_concreto(n)]
            for _ in range(5):  # alguns estados da execução síncrona
                grelhas.append(passo_concreto(grelhas[-1], fronteira, "sincrona", n=n))
            grelhas.append({c: rng.randint(0, 1) for c in normais})  # e uma grelha aleatória
            s = declarar_estado(0, n)
            p = declarar_estado(1, n)
            for k, grelha in enumerate(grelhas):
                with self.subTest(grelha=k):
                    esperado = passo_concreto(grelha, fronteira, "sincrona", n=n)
                    fixar = And([s[c] if grelha[c] == 1 else Not(s[c]) for c in normais])
                    with Solver(name="z3") as solver:
                        solver.add_assertion(And(fixar, trans_sincrona(s, p, fronteira, n)))
                        self.assertTrue(solver.solve(), "a transição síncrona não tem sucessor")
                        obtido = {c: int(solver.get_py_value(p[c])) for c in normais}
                    self.assertEqual(obtido, esperado)

        # --- BMC genérico ---
        def test_bmc_always_programa_da_ficha7(self):
            """bmc_always: G(x >= 0) sem contra-exemplo; G(x != 1) com contra-exemplo mínimo (programa da ficha 7)."""
            r = bmc_always(declare_ficha7, init_ficha7, trans_ficha7, lambda s: GE(s["x"], Int(0)), 20)
            self.assertEqual(r["resultado"], "sem contra-exemplo até K")
            r = bmc_always(declare_ficha7, init_ficha7, trans_ficha7, lambda s: Not(Equals(s["x"], Int(1))), 20)
            self.assertEqual(r["resultado"], "contra-exemplo")
            # o mais curto: x = 3 -> 2 -> 1, com 5 estados (pc alterna entre 0 e 1)
            self.assertEqual(r["k"], 5)
            self.assertEqual(len(r["traço"]), 5)
            self.assertEqual(r["traço"][0], {"pc": 0, "x": 3})
            self.assertEqual(r["traço"][-1]["x"], 1)

        def test_bmc_eventually_programa_da_ficha7(self):
            """bmc_eventually: F(pc = 2) sem contra-exemplo; F(x < 0) com lacete (programa da ficha 7)."""
            r = bmc_eventually(declare_ficha7, init_ficha7, trans_ficha7, lambda s: Equals(s["pc"], Int(2)), 20)
            self.assertEqual(r["resultado"], "sem contra-exemplo até K")
            r = bmc_eventually(declare_ficha7, init_ficha7, trans_ficha7, lambda s: LT(s["x"], Int(0)), 20)
            self.assertEqual(r["resultado"], "contra-exemplo")
            traco, lacete = r["traço"], r["lacete"]
            self.assertEqual(len(traco), r["k"])
            self.assertIsNotNone(lacete)
            for estado in traco:  # x < 0 nunca acontece
                self.assertGreaterEqual(estado["x"], 0)
            # o lacete fecha: o último estado transita para o estado onde o lacete começa
            ultimo, alvo = traco[-1], traco[lacete]
            self.assertEqual(ultimo["pc"], 2)
            self.assertEqual(alvo, ultimo)

        # --- Propriedades ---
        def test_contra_exemplos_sao_tracos_validos(self):
            """Os contra-exemplos das propriedades 1 e 2 (modo assíncrono) passam em traco_e_valido."""
            n = 17
            fronteira = construir_fronteira(n)
            r1 = verificar_nunca_erro(fronteira, "assincrona", 10, n)
            self.assertEqual(r1["resultado"], "contra-exemplo")
            self.assertEqual(traco_e_valido(r1["traço"], fronteira, "assincrona", n), [])
            self.assertEqual(r1["validação"], [])
            self.assertEqual(sum(int(v) for v in r1["traço"][-1].values()), 0, "o último estado não é o de erro")

            r2 = verificar_permanencia((1, n), 0, fronteira, "assincrona", 6, n)
            self.assertEqual(r2["resultado"], "contra-exemplo")
            traco = r2["traço"] + [r2["traço"][r2["lacete"]]]  # fecha o lacete
            self.assertEqual(traco_e_valido(traco, fronteira, "assincrona", n), [])
            self.assertEqual(r2["validação"], [])
            for g in r2["traço"]:
                self.assertEqual(int(g[(1, n)]), 0, "a célula devia estar sempre morta")

        def test_resultados_reproduziveis(self):
            """Duas execuções com os mesmos parâmetros dão o mesmo resultado."""
            n = 17
            fronteira = construir_fronteira(n, 0)
            self.assertEqual(fronteira, construir_fronteira(n, 0))
            self.assertEqual(simular_ate_ciclo(fronteira, n), simular_ate_ciclo(fronteira, n))
            a = verificar_nunca_erro(fronteira, "sincrona", 10, n)
            b = verificar_nunca_erro(fronteira, "sincrona", 10, n)
            self.assertEqual((a["resultado"], a["k"], a["traço"]), (b["resultado"], b["k"], b["traço"]))
            # no assíncrono o solver pode devolver outro traço igualmente válido:
            # o que tem de se repetir é o resultado, o k e o início do lacete
            a = verificar_permanencia((1, n), 0, fronteira, "assincrona", 6, n)
            b = verificar_permanencia((1, n), 0, fronteira, "assincrona", 6, n)
            for chave in ("resultado", "k", "lacete"):
                self.assertEqual(a[chave], b[chave], f"«{chave}» mudou entre execuções")
            self.assertEqual(a["validação"], [])
            self.assertEqual(b["validação"], [])

    # ==================================================================
    # FIM DO CÓDIGO GERADO POR LLM (Claude)
    # ==================================================================

    saida = io.StringIO()
    suite = unittest.TestSuite()
    for classe in (TestesGeometria, TestesEstadoETransicoes, TestesBMCEPropriedades):
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
