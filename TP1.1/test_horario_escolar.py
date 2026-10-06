# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.16.5",
#     "pandas",
#     "ortools",
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
    # Testes automáticos do gerador de horários

    > **Código gerado por LLM.** Todos os testes deste notebook (a classe
    > `TestesHorarioEscolar`, com os 22 testes listados abaixo) foram gerados
    > pelo **ChatGPT**. Não foram escritos por nós: o nosso trabalho foi
    > integrá-los no projeto, executá-los e confirmar que passam. No código,
    > o bloco gerado está delimitado pelos comentários
    > `INÍCIO DO CÓDIGO GERADO POR LLM` e `FIM DO CÓDIGO GERADO POR LLM`.
    >
    > Conversa com o ChatGPT:
    > <https://chatgpt.com/s/cx_6ac29be418648191b9d999922da25f31>
    > (ver também a secção «Uso de ferramentas LLM» em `horario_escolar.py`).

    **Prompt usado (transcrito tal como foi escrito):**

    > ok. gera me os testes todos necessarios para confirmar o funcionamento do projeo

    Esta suite executa testes de leitura e preparação dos CSV, validação R1–R8,
    geração dos horários H0 e H1, atualização incremental e dados adicionais.
    É executada ao abrir e correr este notebook Marimo.

    Os tempos de execução são registados no notebook principal; os testes não
    exigem que uma execução seja sempre mais rápida, porque os tempos variam
    entre computadores e execuções.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## O que verifica cada teste

    Todos os testes destas tabelas foram gerados pelo ChatGPT; as descrições
    explicam o que cada um verifica.

    ### Leitura e preparação dos dados

    | Teste | O que verifica |
    | --- | --- |
    | `test_csv_com_bom_e_coluna_em_falta` | Confirma que um CSV com BOM é lido corretamente e que a falta de uma coluna obrigatória gera um erro. |
    | `test_preparacao_rejeita_disciplina_repetida` | Confirma que `preparar_dados` rejeita disciplinas com o mesmo nome. |
    | `test_preparacao_avisa_excecao_de_professor_substituido` | Confirma que uma exceção antiga para um professor desconhecido é ignorada com um aviso. |
    | `test_professor_substituido_gera_horario_com_excecao_antiga` | Confirma que uma substituição de professor continua a permitir gerar e validar o horário, mesmo com uma exceção antiga no CSV. |

    ### Regras R1–R8 e dados de entrada

    | Teste | Regra | O que verifica |
    | --- | --- | --- |
    | `test_h0_gerado_respeita_r1_a_r8` | R1–R8 | Confirma que H0 é gerado e que o validador não encontra erros. |
    | `test_r1_conflito_de_turma` | R1 | Cria uma sobreposição na mesma turma e confirma que o validador a deteta. |
    | `test_r2_carga_semanal` | R2 | Remove uma aula e confirma que o validador deteta uma carga semanal incompleta. |
    | `test_r3_limite_diario` | R3 | Repete uma disciplina no mesmo dia e confirma que o validador deteta a repetição. |
    | `test_r4_bloco_duplo` | R4 | Confirma que as aulas duplas ocupam dois períodos e deteta uma que comece no último período. |
    | `test_r5_conflito_de_professor` | R5 | Coloca o mesmo professor a dar duas aulas ao mesmo tempo e confirma que o conflito é detetado. |
    | `test_r6_indisponibilidade` | R6 | Coloca uma aula num período indisponível para o professor e confirma que a violação é detetada. |
    | `test_r7_capacidade_de_sala_especial` | R7 | Ultrapassa a capacidade de uma sala especial e confirma que o validador deteta o excesso. |
    | `test_r8_dados_lidos_dos_csv` | R8 | Acrescenta uma turma ao CSV e confirma que o programa a lê sem alterar o código. |
    | `test_dados_alternativos_geram_horario_valido` | Dados diferentes | Gera e valida um horário com as turmas adicionais `8A` e `9Z`. |

    ### Atualização, salas e objetivo

    | Teste | O que verifica |
    | --- | --- |
    | `test_fluxo_dados_v2_e_atualizacao_incremental` | Gera H1 com `dados_v2/`, valida-o e confirma também que uma resolução independente do zero produz um horário válido. |
    | `test_incremental_repara_aula_de_h0_afetada` | Escolhe uma aula da Prof. Ana em H0, torna o seu período indisponível e confirma que a atualização move a aula e continua válida. |
    | `test_sala_temporariamente_indisponivel` | Acrescenta uma indisponibilidade de sala normal e confirma que o horário respeita o bloqueio. |
    | `test_bloco_duplo_sem_sala_comum_e_rejeitado_sem_excecao` | Confirma que o solver rejeita um bloco duplo quando não existe uma sala normal disponível durante os dois períodos. |
    | `test_contagem_de_alteracoes_trata_ocorrencias_repetidas` | Verifica que a contagem de alterações trata corretamente várias ocorrências da mesma disciplina. |
    | `test_buracos_calculados_num_caso_conhecido` | Usa aulas feitas à mão, com dois buracos esperados, e confirma o total calculado. |
    | `test_preferencia_de_sala_antiga_quando_disponivel` | Confirma que a atribuição tenta manter a sala usada no horário anterior quando ela continua livre. |
    | `test_capacidade_normal_zero_proibe_aulas_normais` | Confirma que, sem salas normais disponíveis, o solver não gera aulas que precisem delas. |
    """
    )
    return


@app.cell
def _(mo):
    import io
    import unittest
    import warnings
    from pathlib import Path
    from tempfile import TemporaryDirectory

    from horario_escolar import (
        atribuir_salas_normais,
        carregar_dados,
        contar_alteracoes,
        contar_buracos_horario,
        gerar_horario,
        ler_csv,
        preparar_dados,
        atualizar_horario,
        validar_horario,
    )

    pasta_projeto = Path(__file__).resolve().parent
    pasta_dados = pasta_projeto / "dados"

    # ==================================================================
    # INÍCIO DO CÓDIGO GERADO POR LLM (ChatGPT)
    # Toda a classe TestesHorarioEscolar (22 testes) foi gerada pelo
    # ChatGPT a partir do prompt transcrito no início deste notebook.
    # Nós integrámos o código no projeto, executámo-lo e confirmámos que
    # todos os testes passam.
    # ==================================================================
    class TestesHorarioEscolar(unittest.TestCase):
        @classmethod
        def setUpClass(cls):
            cls.dados_csv = carregar_dados(pasta_dados)
            cls.dados = preparar_dados(cls.dados_csv)
            cls.horario, cls.estado, cls.erros_geracao = gerar_horario(cls.dados_csv)

        def horario_copia(self):
            return [aula.copy() for aula in self.horario]

        def test_csv_com_bom_e_coluna_em_falta(self):
            with TemporaryDirectory() as pasta:
                ficheiro = Path(pasta) / "turmas.csv"
                ficheiro.write_text("\ufeffturma\n7A\n", encoding="utf-8")
                self.assertEqual(ler_csv(ficheiro, ["turma"]), [{"turma": "7A"}])
                ficheiro.write_text("nome\n7A\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "faltam as colunas"):
                    ler_csv(ficheiro, ["turma"])

        def test_preparacao_rejeita_disciplina_repetida(self):
            dados = [lista.copy() for lista in self.dados_csv]
            dados[1].append(dados[1][0].copy())
            with self.assertRaisesRegex(ValueError, "Disciplina repetida"):
                preparar_dados(dados)

        def test_preparacao_avisa_excecao_de_professor_substituido(self):
            dados = [lista.copy() for lista in self.dados_csv]
            dados[3].append({"professor": "Professor antigo", "dia": "Seg", "periodo": "1"})
            with warnings.catch_warnings(record=True) as avisos:
                warnings.simplefilter("always")
                preparar_dados(dados)
            self.assertTrue(any("Professor antigo" in str(aviso.message) for aviso in avisos))

        def test_professor_substituido_gera_horario_com_excecao_antiga(self):
            dados_csv = [[linha.copy() for linha in lista] for lista in self.dados_csv]
            for disciplina in dados_csv[1]:
                if disciplina["professor"].strip() == "Prof. Ana":
                    disciplina["professor"] = "Prof. Nova"
            dados_csv[3].append({
                "professor": "Prof. Ana",
                "dia": "Seg",
                "periodo": "1",
                "sala": "",
            })
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                dados = preparar_dados(dados_csv)
                horario, estado, erros = gerar_horario(dados_csv)
            self.assertIn(estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(erros, [])
            self.assertEqual(validar_horario(horario, dados), [])
            self.assertTrue(all(a["professor"] != "Prof. Ana" for a in horario))

        def test_h0_gerado_respeita_r1_a_r8(self):
            self.assertIn(self.estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(self.erros_geracao, [])
            self.assertEqual(validar_horario(self.horario, self.dados), [])

        def test_r1_conflito_de_turma(self):
            horario = self.horario_copia()
            horario.append(horario[0].copy())
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Sobreposição na turma" in erro for erro in erros))

        def test_r2_carga_semanal(self):
            horario = self.horario_copia()
            horario.pop(0)
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Carga semanal incorreta" in erro for erro in erros))

        def test_r3_limite_diario(self):
            horario = self.horario_copia()
            aula = horario[0].copy()
            aula["periodo"] = 1 if aula["periodo"] != 1 else 4
            horario.append(aula)
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Mais de uma ocorrência" in erro for erro in erros))

        def test_r4_bloco_duplo(self):
            disciplinas = {d["disciplina"]: d for d in self.dados[1]}
            duplas = [a for a in self.horario if disciplinas[a["disciplina"]]["duplo_periodo"]]
            self.assertTrue(duplas)
            for aula in duplas:
                self.assertEqual(aula["duracao"], 2)
                self.assertLess(aula["periodo"], 5)
            horario = self.horario_copia()
            aula_invalida = next(a for a in horario if disciplinas[a["disciplina"]]["duplo_periodo"])
            aula_invalida["periodo"] = 5
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Aula dupla começa no último período" in erro for erro in erros))

        def test_r5_conflito_de_professor(self):
            horario = self.horario_copia()
            aula = horario[0]
            outra_turma = next(t for t in self.dados[0] if t != aula["turma"])
            duplicada = aula.copy()
            duplicada["turma"] = outra_turma
            horario.append(duplicada)
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Sobreposição do professor" in erro for erro in erros))

        def test_r6_indisponibilidade(self):
            excecao = self.dados[3][0]
            horario = self.horario_copia()
            aula = next(a for a in horario if a["professor"] == excecao["professor"])
            aula["dia"] = excecao["dia"]
            aula["periodo"] = excecao["periodo"]
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("indisponível em" in erro for erro in erros))

        def test_r7_capacidade_de_sala_especial(self):
            horario = self.horario_copia()
            sala = next(s for s in self.dados[2] if s["tipo"] == "especial" and s["quantidade"] == 1)
            aula = next(a for a in horario if a["sala"] == sala["sala"])
            horario.append(aula.copy())
            erros = validar_horario(horario, self.dados)
            self.assertTrue(any("Capacidade excedida na sala" in erro for erro in erros))

        def test_r8_dados_lidos_dos_csv(self):
            with TemporaryDirectory() as pasta:
                pasta = Path(pasta)
                for nome in ("turmas.csv", "disciplinas.csv", "salas.csv", "disponibilidade_excecoes.csv"):
                    (pasta / nome).write_bytes((pasta_dados / nome).read_bytes())
                with (pasta / "turmas.csv").open("a", encoding="utf-8") as ficheiro:
                    if (pasta / "turmas.csv").stat().st_size and not (pasta / "turmas.csv").read_bytes().endswith(b"\n"):
                        ficheiro.write("\n")
                    ficheiro.write("9Z\n")
                self.assertIn({"turma": "9Z"}, carregar_dados(pasta)[0])

        def test_dados_alternativos_geram_horario_valido(self):
            dados_csv = carregar_dados(pasta_projeto / "dados_teste")
            dados = preparar_dados(dados_csv)
            horario, estado, erros = gerar_horario(dados_csv)
            self.assertIn(estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(erros, [])
            self.assertEqual(validar_horario(horario, dados), [])
            self.assertEqual({a["turma"] for a in horario}, set(dados[0]))
            self.assertIn("8A", dados[0])
            self.assertIn("9Z", dados[0])

        def test_fluxo_dados_v2_e_atualizacao_incremental(self):
            dados_v2_csv = carregar_dados(pasta_projeto / "dados_v2")
            dados_v2 = preparar_dados(dados_v2_csv)
            horario, estado, alteracoes = atualizar_horario(self.horario, dados_v2_csv)
            self.assertIn(estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(validar_horario(horario, dados_v2), [])
            self.assertEqual(alteracoes, contar_alteracoes(self.horario, horario))

            horario_raiz, estado_raiz, erros_raiz = gerar_horario(dados_v2_csv)
            self.assertIn(estado_raiz, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(erros_raiz, [])
            self.assertEqual(validar_horario(horario_raiz, dados_v2), [])

        def test_incremental_repara_aula_de_h0_afetada(self):
            dados_csv = carregar_dados(pasta_projeto / "dados_v2")
            dados_afetados_csv = []
            for grupo in dados_csv:
                copia_grupo = []
                for linha in grupo:
                    copia_grupo.append(linha.copy())
                dados_afetados_csv.append(copia_grupo)

            indisponibilidades_ana = []
            for excecao in dados_csv[3]:
                if excecao.get("professor") == "Prof. Ana":
                    indisponibilidades_ana.append(
                        (excecao["dia"], int(excecao["periodo"]))
                    )

            aula_afetada = None
            periodo_afetado = None
            for aula in self.horario:
                if aula["professor"] != "Prof. Ana":
                    continue
                for periodo in range(
                    aula["periodo"], aula["periodo"] + aula["duracao"]
                ):
                    if (aula["dia"], periodo) not in indisponibilidades_ana:
                        aula_afetada = aula
                        periodo_afetado = periodo
                        break
                if aula_afetada is not None:
                    break
            self.assertIsNotNone(aula_afetada)

            dados_afetados_csv[3].append({
                "professor": "Prof. Ana",
                "dia": aula_afetada["dia"],
                "periodo": str(periodo_afetado),
                "sala": "",
            })
            dados_afetados = preparar_dados(dados_afetados_csv)
            horario_novo, estado, _ = atualizar_horario(
                self.horario, dados_afetados_csv
            )

            self.assertIn(estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(validar_horario(horario_novo, dados_afetados), [])
            for aula in horario_novo:
                if aula["professor"] == "Prof. Ana":
                    for periodo in range(
                        aula["periodo"], aula["periodo"] + aula["duracao"]
                    ):
                        self.assertFalse(
                            aula["dia"] == aula_afetada["dia"]
                            and periodo == periodo_afetado
                        )

        def test_sala_temporariamente_indisponivel(self):
            dados_csv = [lista.copy() for lista in self.dados_csv]
            sala_normal = next(s["sala"] for s in dados_csv[2] if s["tipo"].strip().lower() == "normal")
            dados_csv[3].append({
                "professor": "",
                "dia": "Seg",
                "periodo": "1",
                "sala": sala_normal,
            })
            dados = preparar_dados(dados_csv)
            horario, estado, erros = gerar_horario(dados_csv)
            self.assertIn(estado, {"OPTIMAL", "FEASIBLE"})
            self.assertEqual(erros, [])
            self.assertEqual(validar_horario(horario, dados), [])
            quantidade = next(s["quantidade"] for s in dados[2] if s["sala"] == sala_normal)
            sala_bloqueada = f"{sala_normal} {quantidade}" if quantidade > 1 else sala_normal
            self.assertFalse(any(
                aula["sala"] == sala_bloqueada
                and aula["dia"] == "Seg"
                and aula["periodo"] <= 1 < aula["periodo"] + aula["duracao"]
                for aula in horario
            ))

        def test_bloco_duplo_sem_sala_comum_e_rejeitado_sem_excecao(self):
            dados_csv = (
                [{"turma": "T"}],
                [{
                    "disciplina": "Dupla",
                    "professor": "P",
                    "carga_semanal": "2",
                    "duplo_periodo": "sim",
                    "sala_especial": "",
                }],
                [
                    {"sala": "Sala A", "tipo": "normal", "quantidade": "1"},
                    {"sala": "Sala B", "tipo": "normal", "quantidade": "1"},
                ],
                [
                    {"sala": "Sala A", "dia": "Seg", "periodo": "1"},
                    {"sala": "Sala B", "dia": "Seg", "periodo": "2"},
                ],
            )

            for dia in ("Seg", "Ter", "Qua", "Qui", "Sex"):
                for periodo in range(1, 6):
                    if dia != "Seg" or periodo not in (1, 2):
                        dados_csv[3].append({
                            "professor": "P",
                            "dia": dia,
                            "periodo": str(periodo),
                        })

            horario, estado, erros = gerar_horario(dados_csv)

            self.assertEqual(estado, "INFEASIBLE")
            self.assertEqual(horario, [])
            self.assertTrue(erros)

        def test_contagem_de_alteracoes_trata_ocorrencias_repetidas(self):
            aula = {"turma": "7A", "disciplina": "Matemática", "dia": "Seg", "periodo": 1, "sala": "Sala 1"}
            antigas = [aula.copy(), aula.copy()]
            novas = [aula.copy()]
            self.assertEqual(contar_alteracoes(antigas, novas), 1)
            novas[0]["sala"] = "Sala 2"
            self.assertEqual(contar_alteracoes([aula], novas), 1)

        def test_buracos_calculados_num_caso_conhecido(self):
            horario = [
                {"professor": "P", "dia": "Seg", "periodo": 1, "duracao": 1},
                {"professor": "P", "dia": "Seg", "periodo": 4, "duracao": 1},
            ]
            self.assertEqual(contar_buracos_horario(horario), 2)

        def test_preferencia_de_sala_antiga_quando_disponivel(self):
            sala_antiga = next(s for s in self.dados[2] if s["tipo"] == "normal")
            nome_sala = sala_antiga["sala"] if sala_antiga["quantidade"] == 1 else f"{sala_antiga['sala']} 2"
            aula = {"turma": "7A", "disciplina": "Matemática", "dia": "Seg", "periodo": 1, "duracao": 1, "sala": None}
            antiga = {**aula, "sala": nome_sala}
            resultado = atribuir_salas_normais([aula], self.dados[2], [antiga])
            self.assertEqual(resultado[0]["sala"], nome_sala)

        def test_capacidade_normal_zero_proibe_aulas_normais(self):
            dados_csv = [lista.copy() for lista in self.dados_csv]
            dados_csv[2] = [s for s in dados_csv[2] if s["tipo"].strip().lower() != "normal"]
            horario, estado, _ = gerar_horario(dados_csv)
            self.assertEqual(estado, "INFEASIBLE")
            self.assertEqual(horario, [])

    # ==================================================================
    # FIM DO CÓDIGO GERADO POR LLM (ChatGPT)
    # ==================================================================

    saida = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestesHorarioEscolar)
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
