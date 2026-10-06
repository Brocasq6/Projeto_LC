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
 
with app.setup:
    import csv
    import warnings
    from collections import Counter
    from pathlib import Path
    from time import perf_counter
 
    import pandas as pd
    from ortools.sat.python import cp_model

    pd.set_option("display.max_rows", 200)  # mostrar os horários completos, também na exportação para PDF
 
    DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex"]
    PERIODOS = range(1, 6)
 
 
@app.cell
def _():
    import marimo as mo
    return (mo,)
 
 
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    # 1. Descrição do problema e abordagem
 
    > **Objetivo** — construir um gerador de horários semanais a partir dos
    > ficheiros CSV, respeitando as regras das turmas, disciplinas, professores
    > e salas.
 
    ## Regras principais
 
    - Cada disciplina tem uma carga semanal e um professor associado.
    - Algumas disciplinas precisam de uma sala especial ou de blocos de dois
      períodos consecutivos.
    - Uma turma, um professor ou uma sala não podem ter aulas sobrepostas.
    - As indisponibilidades dos professores e a capacidade das salas têm de ser
      respeitadas.
 
    ## Estratégia de resolução
 
    Usaremos programação por restrições com **CP-SAT**, do OR-Tools. Cada
    colocação possível de uma aula será representada por uma decisão booleana.
    O solver procurará primeiro uma solução que cumpra todas as regras
    obrigatórias e, depois, minimizará os tempos livres entre aulas de cada
    professor no mesmo dia (os «buracos»).
 
    Os dados serão sempre lidos dos CSV, pelo que o modelo poderá ser usado com
    outros conjuntos de turmas, disciplinas, salas e indisponibilidades no mesmo
    formato. No final, o notebook compara uma resolução independente com uma
    atualização baseada em H0. O uso do ChatGPT está identificado na secção
    «Uso de ferramentas LLM», no fim do notebook.
    """
    )
    return
 
 
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Modelo e validação
 
    Os CSV são lidos com a biblioteca `csv` e preparados antes da modelação. O
    CP-SAT cria uma variável booleana para cada possível início de aula. Blocos
    duplos só podem começar nos períodos 1 a 4 e ocupam também o período seguinte.
 
    O modelo aplica R1–R7: conflitos de turma, carga semanal, limite diário por
    disciplina, blocos duplos, conflitos e disponibilidade dos professores e
    capacidade de salas. R8 é garantida pela leitura dos quatro CSV. A função
    `validar_horario` verifica de forma independente as regras no horário extraído.
 
    A atualização incremental dá ao solver H0 como pistas e maximiza as
    colocações de aula preservadas. Depois, um segundo modelo CP-SAT atribui as
    salas normais e maximiza quantas aulas mantêm a sala antiga, respeitando as
    sobreposições e as salas temporariamente indisponíveis. As alterações de
    horário e sala são contadas em conjunto por aula.

    ## Justificação das escolhas

    **CP-SAT (OR-Tools).** O problema é combinatório: cada decisão é booleana
    (a aula começa ou não num dado dia e período) e todas as regras R1–R7 se
    escrevem como somas dessas decisões limitadas por uma constante (carga
    exata, no máximo uma aula por período, capacidade de salas). O CP-SAT
    trata diretamente este tipo de restrições lineares sobre booleanos e, no
    mesmo modelo, otimiza um objetivo (os buracos de O1). Além disso:

    - devolve o estado da resolução (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`),
      o que permite distinguir «não há horário» de «não houve tempo»;
    - aceita um limite de tempo, como o enunciado admite para O1;
    - aceita pistas (`add_hint`), que usamos para reaproveitar H0 em R9.

    Para os resultados serem reproduzíveis, o solver corre com um só
    processo e semente fixa (`random_seed = 0`): os mesmos CSV produzem
    sempre o mesmo H0 e os mesmos H1. Só os tempos medidos variam.

    Um solver SAT puro ou SMT obrigaria a codificar à mão as cardinalidades e
    o objetivo. Por isso seguimos a sugestão da disciplina.

    **Biblioteca `csv` para a leitura.** Os ficheiros são pequenos e cada
    linha é validada individualmente antes da modelação (colunas
    obrigatórias, tipos, valores `sim`/`nao`, dias e períodos válidos, salas
    existentes). Com `csv.DictReader` cada linha chega como um dicionário de
    texto, que convertemos e verificamos explicitamente, com mensagens de erro
    claras. O modelo não usa operações tabulares (junções, agrupamentos), por
    isso o pandas não traria vantagem na leitura e acrescentaria conversões
    automáticas de tipos (por exemplo, `sala_especial` vazia passaria a
    `NaN`). Usamos o pandas apenas para apresentar o horário em tabela.
 
    Para registar uma sala temporariamente indisponível, pode acrescentar-se a
    coluna opcional `sala` a `disponibilidade_excecoes.csv`; cada linha indica a
    sala, o dia e o período. Os CSV antigos sem essa coluna continuam válidos.
    """
    )
    return
 
 
# ---------------------------------------------------------------- dados
 
 
@app.function
def ler_csv(caminho, colunas):
    """Lê um CSV, confirma as colunas obrigatórias e devolve as linhas como dicionários."""
    with open(caminho, newline="", encoding="utf-8-sig") as ficheiro:
        leitor = csv.DictReader(ficheiro)
        em_falta = set(colunas) - set(leitor.fieldnames or [])
        if em_falta:
            raise ValueError(f"{caminho}: faltam as colunas {em_falta}")
        return list(leitor)
 
 
@app.function
def carregar_dados(pasta):
    """Lê os quatro CSV da pasta e devolve turmas, disciplinas, salas e exceções."""
    # LLM (ChatGPT) — Registo 1 (passo 1): sugeriu reunir a leitura dos quatro CSV numa função.
    pasta = Path(pasta)
    turmas = ler_csv(pasta / "turmas.csv", ["turma"])
    disciplinas = ler_csv(
        pasta / "disciplinas.csv",
        ["disciplina", "professor", "carga_semanal", "duplo_periodo", "sala_especial"],
    )
    salas = ler_csv(pasta / "salas.csv", ["sala", "tipo", "quantidade"])
    excecoes = ler_csv(pasta / "disponibilidade_excecoes.csv", ["professor", "dia", "periodo"])
    for excecao in excecoes:  # coluna opcional `sala`: sala temporariamente indisponível
        excecao.setdefault("sala", "")
    return turmas, disciplinas, salas, excecoes
 
 
@app.function
def preparar_dados(dados):
    """Limpa e valida os dados lidos dos CSV, convertendo números e valores de duplo período."""
    # LLM (ChatGPT) — Registos 1 (passo 2) e 2: descreveu as conversões de tipos e as validações a fazer.
    linhas_turmas, linhas_disciplinas, linhas_salas, linhas_excecoes = dados
 
    turmas = [linha["turma"].strip() for linha in linhas_turmas]
    if not turmas or not all(turmas):
        raise ValueError("Há turmas sem nome")
    if len(turmas) != len(set(turmas)):
        raise ValueError("Há turmas repetidas")
 
    salas = []
    for linha in linhas_salas:
        sala = {
            "sala": linha["sala"].strip(),
            "tipo": linha["tipo"].strip().lower(),
            "quantidade": int(linha["quantidade"]),
        }
        if sala["tipo"] not in ("normal", "especial"):
            raise ValueError(f"Tipo de sala inválido: {sala['tipo']}")
        if sala["quantidade"] < 1:
            raise ValueError(f"Quantidade inválida para a sala {sala['sala']}")
        if not sala["sala"]:
            raise ValueError("Há salas sem nome")
        if any(sala["sala"] == outra["sala"] for outra in salas):
            raise ValueError(f"Sala repetida: {sala['sala']}")
        salas.append(sala)
    salas_por_nome = {sala["sala"]: sala for sala in salas}
 
    disciplinas = []
    for linha in linhas_disciplinas:
        nome = linha["disciplina"].strip()
        professor = linha["professor"].strip()
        duplo = linha["duplo_periodo"].strip().lower()
        carga = int(linha["carga_semanal"])
        sala_especial = linha["sala_especial"].strip()
 
        if not nome:
            raise ValueError("Há disciplinas sem nome")
        if any(nome == d["disciplina"] for d in disciplinas):
            raise ValueError(f"Disciplina repetida: {nome}")
        if not professor:
            raise ValueError(f"Falta o professor da disciplina {nome}")
        if duplo not in ("sim", "nao"):
            raise ValueError(f"Valor inválido em duplo_periodo: {linha['duplo_periodo']}")
        if carga < 1 or (duplo == "sim" and carga % 2 != 0):
            raise ValueError(f"Carga semanal inválida para {nome}")
        if sala_especial and salas_por_nome.get(sala_especial, {}).get("tipo") != "especial":
            raise ValueError(f"Sala especial inexistente: {sala_especial}")
 
        disciplinas.append({
            "disciplina": nome,
            "professor": professor,
            "carga_semanal": carga,
            "duplo_periodo": duplo == "sim",
            "sala_especial": sala_especial or None,
        })
 
    professores = {d["professor"] for d in disciplinas}
    excecoes = []
    for linha in linhas_excecoes:
        dia = linha["dia"].strip()
        periodo = int(linha["periodo"])
        if dia not in DIAS or periodo not in PERIODOS:
            raise ValueError(f"Dia ou período inválido: {dia}, {periodo}")
 
        sala = linha.get("sala", "").strip()
        if sala:
            if sala not in salas_por_nome:
                raise ValueError(f"Sala desconhecida na exceção: {sala}")
            excecoes.append({"sala": sala, "dia": dia, "periodo": periodo})
            continue
 
        professor = linha["professor"].strip()
        if professor not in professores:  # pode ser uma exceção antiga de um professor substituído
            warnings.warn(
                f"Exceção ignorada para professor desconhecido ou substituído: {professor}",
                UserWarning,
                stacklevel=2,
            )
            continue
        excecoes.append({"professor": professor, "dia": dia, "periodo": periodo})
 
    bloqueadas = Counter((e["sala"], e["dia"], e["periodo"]) for e in excecoes if "sala" in e)
    for (nome, dia, periodo), quantidade in bloqueadas.items():
        if quantidade > salas_por_nome[nome]["quantidade"]:
            raise ValueError(f"Demasiadas salas {nome} indisponíveis em {dia}, período {periodo}")
 
    return turmas, disciplinas, salas, excecoes
 
 
@app.function
def duracao(disciplina):
    """Número de períodos que cada aula da disciplina ocupa (2 se for bloco duplo)."""
    return 2 if disciplina["duplo_periodo"] else 1
 
 
# --------------------------------------------------------------- modelo
 
 
@app.function
def criar_modelo(dados):
    """Cria o modelo CP-SAT com uma variável booleana por início possível de aula, indexada por (turma, disciplina, dia, período)."""
    # LLM (ChatGPT) — Registo 4: propôs uma variável booleana por colocação possível, com blocos duplos só a começar nos períodos 1 a 4.
    turmas, disciplinas, _, _ = dados
    modelo = cp_model.CpModel()
    x = {}
    for turma in turmas:
        for disciplina in disciplinas:
            for dia in DIAS:
                for periodo in PERIODOS:
                    if disciplina["duplo_periodo"] and periodo == 5:
                        continue  # um bloco duplo não pode começar no último período
                    chave = (turma, disciplina["disciplina"], dia, periodo)
                    x[chave] = modelo.new_bool_var(f"x_{len(x)}")
    return modelo, x
 
 
@app.function
def ocupantes(x, turma, disciplina, dia, periodo):
    """Variáveis da disciplina que ocupam um período: o início nele ou, nos blocos duplos, no período anterior."""
    # LLM (ChatGPT) — Registo 6: indicou que uma aula dupla ocupa o período de início e o seguinte.
    inicios = [periodo, periodo - 1] if disciplina["duplo_periodo"] else [periodo]
    chaves = [(turma, disciplina["disciplina"], dia, i) for i in inicios]
    return [x[chave] for chave in chaves if chave in x]
 
 
@app.function
def adicionar_restricoes(modelo, x, dados):
    """Acrescenta ao modelo as regras R1–R7: carga, limite diário, conflitos, disponibilidade e salas."""
    # LLM (ChatGPT) — Registos 5 e 6: descreveu como escrever R1–R7 como somas de variáveis; as quatro funções sugeridas foram juntadas numa só.
    turmas, disciplinas, salas, excecoes = dados
    prof_indisponivel = {(e["professor"], e["dia"], e["periodo"]) for e in excecoes if "professor" in e}
    salas_bloqueadas = Counter((e["sala"], e["dia"], e["periodo"]) for e in excecoes if "sala" in e)
 
    for turma in turmas:
        for d in disciplinas:
            nome = d["disciplina"]
            # R2: carga semanal exata (em blocos, se a disciplina for dupla).
            todas = [x[(turma, nome, dia, p)] for dia in DIAS for p in PERIODOS if (turma, nome, dia, p) in x]
            modelo.add(sum(todas) == d["carga_semanal"] // duracao(d))
            for dia in DIAS:
                # R3: no máximo uma ocorrência da disciplina por dia.
                do_dia = [x[(turma, nome, dia, p)] for p in PERIODOS if (turma, nome, dia, p) in x]
                modelo.add(sum(do_dia) <= 1)
                # R6: nenhum período da aula pode ser de indisponibilidade do professor.
                for p in PERIODOS:
                    if (turma, nome, dia, p) in x and any(
                        (d["professor"], dia, p + i) in prof_indisponivel for i in range(duracao(d))
                    ):
                        modelo.add(x[(turma, nome, dia, p)] == 0)
 
    professores = {d["professor"] for d in disciplinas}
    for dia in DIAS:
        for p in PERIODOS:
            # R1: uma turma só tem uma aula de cada vez.
            for turma in turmas:
                modelo.add(sum(v for d in disciplinas for v in ocupantes(x, turma, d, dia, p)) <= 1)
            # R5: um professor só dá uma aula de cada vez.
            for professor in professores:
                modelo.add(sum(
                    v for turma in turmas for d in disciplinas if d["professor"] == professor
                    for v in ocupantes(x, turma, d, dia, p)
                ) <= 1)
            # R7: as salas normais são uma capacidade partilhada (pode ser zero).
            normais = sum(
                v for turma in turmas for d in disciplinas if not d["sala_especial"]
                for v in ocupantes(x, turma, d, dia, p)
            )
            capacidade = sum(s["quantidade"] - salas_bloqueadas[(s["sala"], dia, p)] for s in salas if s["tipo"] == "normal")
            modelo.add(normais <= max(0, capacidade))
            # R7: cada sala especial tem a sua própria capacidade.
            for s in salas:
                if s["tipo"] == "especial":
                    usos = sum(
                        v for turma in turmas for d in disciplinas if d["sala_especial"] == s["sala"]
                        for v in ocupantes(x, turma, d, dia, p)
                    )
                    modelo.add(usos <= max(0, s["quantidade"] - salas_bloqueadas[(s["sala"], dia, p)]))
 
 
@app.function
def adicionar_objetivo_buracos(modelo, x, dados):
    """Minimiza os buracos: períodos livres entre duas aulas do mesmo professor no mesmo dia."""
    # LLM (ChatGPT) — Registo 7: explicou a lógica do buraco (aula antes, aula depois, período livre) para os períodos 2 a 4.
    turmas, disciplinas, _, _ = dados
    buracos = []
    for professor in sorted({d["professor"] for d in disciplinas}):
        for dia in DIAS:
            # tem[p] vale 1 se o professor dá aula no período p (as regras garantem no máximo 1).
            tem = {
                p: sum(
                    v for turma in turmas for d in disciplinas if d["professor"] == professor
                    for v in ocupantes(x, turma, d, dia, p)
                )
                for p in PERIODOS
            }
            for p in range(2, 5):
                buraco = modelo.new_bool_var(f"buraco_{len(buracos)}")
                buracos.append(buraco)
                # Há buraco em p se houver aula antes e depois mas não em p.
                for antes in range(1, p):
                    for depois in range(p + 1, 6):
                        modelo.add(buraco >= tem[antes] + tem[depois] - tem[p] - 1)
    modelo.minimize(sum(buracos))
 
 
# ---------------------------------------------------------------- salas
 
 
@app.function
def nomes_salas_normais(salas):
    """Nomes individuais das salas normais por tipo, p. ex. {'Sala Normal': ['Sala Normal 1', ...]}."""
    return {
        s["sala"]: [s["sala"]] if s["quantidade"] == 1 else [f"{s['sala']} {n}" for n in range(1, s["quantidade"] + 1)]
        for s in salas
        if s["tipo"] == "normal"
    }
 
 
@app.function
def salas_bloqueadas(salas, excecoes):
    """Mapa (dia, período) -> nomes das salas normais indisponíveis (as últimas N de cada tipo)."""
    por_tipo = nomes_salas_normais(salas)
    contagem = Counter((e["sala"], e["dia"], e["periodo"]) for e in excecoes or [] if "sala" in e)
    bloqueadas = {}
    for (tipo, dia, periodo), n in contagem.items():
        bloqueadas.setdefault((dia, periodo), set()).update(por_tipo.get(tipo, [])[-n:])
    return bloqueadas
 
 
@app.function
def atribuir_salas_normais(horario, salas, horario_antigo=None, excecoes_salas=None, limite_segundos=30):
    """Atribui salas físicas às aulas normais (sem conflitos) e prefere manter as salas do horário anterior."""
    nomes = [n for ns in nomes_salas_normais(salas).values() for n in ns]
    bloqueadas = salas_bloqueadas(salas, excecoes_salas)
    antigas = {(a["turma"], a["disciplina"], a["dia"], a["periodo"]): a["sala"] for a in horario_antigo or []}
    aulas = [(i, a) for i, a in enumerate(horario) if a["sala"] is None]
    if not aulas:
        return horario
 
    modelo = cp_model.CpModel()
    var = {}
    mantidas = []
    for i, a in aulas:
        periodos = range(a["periodo"], a["periodo"] + a["duracao"])
        for sala in nomes:
            if any(sala in bloqueadas.get((a["dia"], p), ()) for p in periodos):
                continue
            var[(i, sala)] = modelo.new_bool_var(f"sala_{len(var)}")
            if antigas.get((a["turma"], a["disciplina"], a["dia"], a["periodo"])) == sala:
                mantidas.append(var[(i, sala)])
        modelo.add(sum(var[(i, s)] for s in nomes if (i, s) in var) == 1)
 
    for sala in nomes:  # uma sala não pode ter duas aulas ao mesmo tempo
        for dia in DIAS:
            for p in PERIODOS:
                modelo.add(sum(
                    var[(i, sala)] for i, a in aulas
                    if a["dia"] == dia and a["periodo"] <= p < a["periodo"] + a["duracao"] and (i, sala) in var
                ) <= 1)
 
    modelo.maximize(sum(mantidas))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 0
    if limite_segundos is not None:
        solver.parameters.max_time_in_seconds = limite_segundos
    estado = solver.solve(modelo)
    if estado == cp_model.INFEASIBLE:
        raise ValueError("Não há salas normais disponíveis para o horário")
    if estado not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        raise TimeoutError("O solver não conseguiu atribuir as salas a tempo")
 
    for (i, sala), variavel in var.items():
        if solver.value(variavel):
            horario[i]["sala"] = sala
    return horario
 
 
# ---------------------------------------------------------- resolução
 
 
@app.function
def construir_horario(solver, x, dados):
    """Transforma as decisões verdadeiras do solver em aulas; as salas normais ficam por atribuir (None)."""
    # LLM (ChatGPT) — Registo 8 (passo 2): corresponde a `extrair_horario`, sugerida pelo ChatGPT.
    por_nome = {d["disciplina"]: d for d in dados[1]}
    ocorrencias = Counter()
    horario = []
    for (turma, nome, dia, inicio), variavel in x.items():
        if solver.value(variavel):
            ocorrencias[(turma, nome)] += 1
            d = por_nome[nome]
            horario.append({
                "id": (turma, nome, ocorrencias[(turma, nome)]),
                "turma": turma,
                "disciplina": nome,
                "professor": d["professor"],
                "dia": dia,
                "periodo": inicio,
                "duracao": duracao(d),
                "sala": d["sala_especial"],
            })
    return horario
 
 
@app.function
def resolver_com_salas(modelo, x, dados, limite_segundos=30, horario_antigo=None):
    """Resolve o horário; se não houver salas físicas para ele, exclui-o do modelo e pede outro."""
    # LLM (ChatGPT) — Registo 8 (passo 1): corresponde a `resolver_modelo`, sugerida pelo ChatGPT; a atribuição de salas foi acrescentada depois.
    fim = None if limite_segundos is None else perf_counter() + limite_segundos
    while True:
        solver = cp_model.CpSolver()
        # Um só processo e semente fixa: a mesma entrada dá sempre o mesmo horário (resultados reproduzíveis).
        solver.parameters.num_search_workers = 1
        solver.parameters.random_seed = 0
        restante = None if fim is None else fim - perf_counter()
        if restante is not None:
            if restante <= 0:
                return [], "UNKNOWN"
            solver.parameters.max_time_in_seconds = restante
        estado = solver.solve(modelo)
        if estado not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return [], solver.status_name(estado)
 
        restante = None if fim is None else fim - perf_counter()
        if restante is not None and restante <= 0:
            return [], "UNKNOWN"
        horario = construir_horario(solver, x, dados)
        try:
            horario = atribuir_salas_normais(horario, dados[2], horario_antigo, dados[3], restante)
            return horario, solver.status_name(estado)
        except TimeoutError:
            return [], "UNKNOWN"
        except ValueError:
            escolhidas = [v for v in x.values() if solver.value(v)]
            modelo.add(sum(escolhidas) <= len(escolhidas) - 1)  # exclui esta solução
 
 
@app.function
def gerar_horario(dados_csv, limite_segundos=30):
    """Gera o horário do zero, otimizando os buracos; devolve o horário, o estado e os erros de validação."""
    # LLM (ChatGPT) — Registo 9: fluxo completo (dados → H0) sugerido pelo ChatGPT.
    dados = preparar_dados(dados_csv)
    modelo, x = criar_modelo(dados)
    adicionar_restricoes(modelo, x, dados)
    adicionar_objetivo_buracos(modelo, x, dados)
    horario, estado = resolver_com_salas(modelo, x, dados, limite_segundos)
    if estado in ("OPTIMAL", "FEASIBLE"):
        return horario, estado, validar_horario(horario, dados)
    return horario, estado, ["O solver não encontrou um horário válido."]
 
 
@app.function
def atualizar_horario(horario_antigo, dados_novos, limite_segundos=30, usar_pistas=True):
    """Gera um novo horário com os dados atualizados, preservando o máximo de aulas e salas de H0."""
    # LLM (ChatGPT) — Registos 1 (passo 9) e 8 (passo 6): sugeriu reaproveitar H0 e preservar as aulas que continuam válidas.
    dados = preparar_dados(dados_novos)
    modelo, x = criar_modelo(dados)
    adicionar_restricoes(modelo, x, dados)
 
    antigas = {(a["turma"], a["disciplina"], a["dia"], a["periodo"]) for a in horario_antigo}
    if usar_pistas:  # H0 como ponto de partida do solver
        for chave, variavel in x.items():
            modelo.add_hint(variavel, int(chave in antigas))
    modelo.maximize(sum(v for chave, v in x.items() if chave in antigas))
 
    horario_novo, estado = resolver_com_salas(modelo, x, dados, limite_segundos, horario_antigo)
    if estado in ("OPTIMAL", "FEASIBLE"):
        erros = validar_horario(horario_novo, dados)
        if erros:
            raise ValueError("O novo horário falhou na validação:\n" + "\n".join(erros))
    return horario_novo, estado, contar_alteracoes(horario_antigo, horario_novo)
 
 
# ------------------------------------------------- validação e medidas
 
 
@app.function
def validar_horario(horario, dados):
    """Verifica R1–R7 de forma independente do solver e devolve a lista de erros (vazia se o horário é válido)."""
    # LLM (ChatGPT) — Registos 1 (passo 8) e 8 (passo 4): sugeriu um validador independente do solver que devolve a lista de erros.
    turmas, disciplinas, salas, excecoes = dados
    por_nome = {d["disciplina"]: d for d in disciplinas}
    nomes_normais = nomes_salas_normais(salas)
    normais = [n for ns in nomes_normais.values() for n in ns]
    bloqueadas = salas_bloqueadas(salas, excecoes)
    prof_indisponivel = {(e["professor"], e["dia"], e["periodo"]) for e in excecoes if "professor" in e}
    salas_indisponiveis = Counter((e["sala"], e["dia"], e["periodo"]) for e in excecoes if "sala" in e)
    capacidade_especial = {s["sala"]: s["quantidade"] for s in salas if s["tipo"] == "especial"}
 
    erros = []
    cargas, por_dia = Counter(), Counter()
    turma_ocupada, prof_ocupado, sala_ocupada, normais_ocupadas = Counter(), Counter(), Counter(), Counter()
 
    for a in horario:
        turma, nome, dia, inicio = a["turma"], a["disciplina"], a["dia"], a["periodo"]
        if turma not in turmas:
            erros.append(f"Turma desconhecida: {turma}")
            continue
        if nome not in por_nome:
            erros.append(f"Disciplina desconhecida: {nome}")
            continue
        d = por_nome[nome]
        if a["duracao"] != duracao(d):
            erros.append(f"Duração incorreta para {turma} - {nome}")
        if dia not in DIAS or inicio not in PERIODOS:
            erros.append(f"Dia ou período inválido para {turma} - {nome}")
            continue
        if d["duplo_periodo"] and inicio == 5:
            erros.append(f"Aula dupla começa no último período: {turma} - {nome}")
            continue
 
        cargas[(turma, nome)] += duracao(d)
        por_dia[(turma, nome, dia)] += 1
        especial = d["sala_especial"]
        if especial and a["sala"] != especial:
            erros.append(f"Sala incompatível para {turma} - {nome}")
        if not especial and a["sala"] not in normais:
            erros.append(f"Sala normal incompatível para {turma} - {nome}")
 
        for p in range(inicio, inicio + duracao(d)):
            turma_ocupada[(turma, dia, p)] += 1
            prof_ocupado[(d["professor"], dia, p)] += 1
            sala_ocupada[(bool(especial), especial or a["sala"], dia, p)] += 1
            if (d["professor"], dia, p) in prof_indisponivel:
                erros.append(f"{d['professor']} indisponível em {dia}, período {p}")
            if not especial:
                normais_ocupadas[(dia, p)] += 1
                if a["sala"] in bloqueadas.get((dia, p), ()):
                    erros.append(f"Sala {a['sala']} indisponível em {dia}, período {p}")
 
    for turma in turmas:
        for d in disciplinas:
            carga = cargas[(turma, d["disciplina"])]
            if carga != d["carga_semanal"]:
                erros.append(
                    f"Carga semanal incorreta para {turma} - {d['disciplina']}: "
                    f"{carga} em vez de {d['carga_semanal']}"
                )
    erros += [f"Mais de uma ocorrência de {n} para {t} à {dia}" for (t, n, dia), q in por_dia.items() if q > 1]
    erros += [f"Sobreposição na turma {t}, {dia}, período {p}" for (t, dia, p), q in turma_ocupada.items() if q > 1]
    erros += [f"Sobreposição do professor {pr}, {dia}, período {p}" for (pr, dia, p), q in prof_ocupado.items() if q > 1]
    for (especial, sala, dia, p), q in sala_ocupada.items():
        capacidade = max(0, capacidade_especial.get(sala, 0) - salas_indisponiveis[(sala, dia, p)]) if especial else 1
        if q > capacidade:
            erros.append(f"Capacidade excedida na sala {sala}, {dia}, período {p}")
    total_normais = sum(s["quantidade"] for s in salas if s["tipo"] == "normal")
    for (dia, p), q in normais_ocupadas.items():
        indisponiveis = sum(salas_indisponiveis[(tipo, dia, p)] for tipo in nomes_normais)
        if q > max(0, total_normais - indisponiveis):
            erros.append(f"Capacidade de salas normais excedida em {dia}, período {p}")
    return erros
 
 
@app.function
def contar_alteracoes(horario_antigo, horario_novo):
    """Conta as aulas que mudaram de dia, período ou sala, incluindo aulas novas ou removidas."""
    # LLM (ChatGPT) — Registos 1 (passo 9) e 8 (passo 5): sugeriu emparelhar as ocorrências da mesma turma e disciplina.
    def agrupar(horario):
        grupos = {}
        for a in horario:
            grupos.setdefault((a["turma"], a["disciplina"]), Counter())[(a["dia"], a["periodo"], a["sala"])] += 1
        return grupos
 
    antigos, novos = agrupar(horario_antigo), agrupar(horario_novo)
    total = 0
    for chave in set(antigos) | set(novos):
        a, n = antigos.get(chave, Counter()), novos.get(chave, Counter())
        total += max(sum(a.values()), sum(n.values())) - sum((a & n).values())
    return total
 
 
@app.function
def contar_buracos_horario(horario):
    """Conta os períodos livres entre a primeira e a última aula de cada professor em cada dia."""
    ocupacao = {}
    for a in horario:
        ocupacao.setdefault((a["professor"], a["dia"]), set()).update(range(a["periodo"], a["periodo"] + a["duracao"]))
    return sum(max(ps) - min(ps) + 1 - len(ps) for ps in ocupacao.values())
 
 
# --------------------------------------------------------- apresentação
 
 
@app.function
def apresentar_horario(horario):
    """Organiza o horário numa tabela ordenada por turma, dia e período para mostrar no Marimo."""
    # LLM (ChatGPT) — Registos 1 (passo 7) e 8 (passo 3): sugeriu uma tabela ordenada por turma, dia e período.
    colunas = ["turma", "dia", "periodo", "duracao", "disciplina", "professor", "sala"]
    if not horario:
        return pd.DataFrame(columns=colunas)
    tabela = pd.DataFrame(horario)
    tabela["ordem_dia"] = tabela["dia"].map(DIAS.index)
    return tabela.sort_values(["turma", "ordem_dia", "periodo"])[colunas].reset_index(drop=True)
 
 
@app.function
def comparar_metodos(horario_h0, dados_csv, limite_segundos=30):
    """Corre a atualização incremental e a resolução do zero e devolve as linhas da tabela e os dois horários."""
    # LLM (ChatGPT) — Registos 1 (passo 9) e 9: sugeriu comparar com uma resolução do zero, medindo o tempo e as aulas alteradas.
    dados = preparar_dados(dados_csv)
    linhas, horarios = [], []
    for metodo in ("Incremental com pistas de H0", "Resolução independente do zero"):
        inicio = perf_counter()
        if metodo.startswith("Incremental"):
            horario, estado, _ = atualizar_horario(horario_h0, dados_csv, limite_segundos)
        else:
            horario, estado, _ = gerar_horario(dados_csv, limite_segundos)
        linhas.append({
            "metodo": metodo,
            "estado": estado,
            "tempo": perf_counter() - inicio,
            "alteracoes": contar_alteracoes(horario_h0, horario),
            "buracos": contar_buracos_horario(horario),
            "erros": len(validar_horario(horario, dados)),
        })
        horarios.append(horario)
    return linhas, horarios
 
 
@app.function
def tabela_markdown(linhas):
    """Formata as linhas de comparação como tabela em markdown."""
    topo = "| Método | Estado | Tempo (s) | Aulas alteradas | Buracos | Erros |\n| --- | --- | ---: | ---: | ---: | ---: |"
    corpo = [
        f"| {l['metodo']} | {l['estado']} | {l['tempo']:.3f} | {l['alteracoes']} | {l['buracos']} | {l['erros']} |"
        for l in linhas
    ]
    return "\n".join([topo] + corpo)
 
 
@app.function
def forcar_reparacao(horario_h0, dados_csv, professor="Prof. Ana"):
    """Copia os dados e bloqueia (só em memória) um período de uma aula do professor em H0; devolve os dados, a aula e o período."""
    ja_indisponivel = {(e["dia"], e["periodo"]) for e in preparar_dados(dados_csv)[3] if e.get("professor") == professor}
    for aula in horario_h0:
        if aula["professor"] != professor:
            continue
        for p in range(aula["periodo"], aula["periodo"] + aula["duracao"]):
            if (aula["dia"], p) not in ja_indisponivel:
                novos = [[linha.copy() for linha in grupo] for grupo in dados_csv]
                novos[3].append({"professor": professor, "dia": aula["dia"], "periodo": str(p), "sala": ""})
                return novos, aula, p
    raise ValueError(f"Não foi encontrada uma aula disponível de {professor} em H0")
 
 
# ------------------------------------------------------------ resultados
 
 
@app.cell
def _(mo):
    dados_csv = carregar_dados(Path(__file__).resolve().parent / "dados")
    horario, estado, erros = gerar_horario(dados_csv)
 
    resultado = mo.vstack([
        mo.md(f"**Estado do solver:** {estado}"),
        mo.md("**Erros de validação:** " + "; ".join(erros) if erros else "**Validação:** sem erros"),
        apresentar_horario(horario),
    ])
 
    resultado
    return (horario,)
 
 
@app.cell
def _(horario, mo):
    dados_v2 = carregar_dados(Path(__file__).resolve().parent / "dados_v2")
    linhas_v2, (h1_incremental, h1_raiz) = comparar_metodos(horario, dados_v2)
 
    dados_forcados, aula_afetada, periodo_afetado = forcar_reparacao(horario, dados_v2)
    linhas_forcadas, (h1_forcado_inc, h1_forcado_raiz) = comparar_metodos(horario, dados_forcados)
    ocupado = any(
        a["professor"] == aula_afetada["professor"]
        and a["dia"] == aula_afetada["dia"]
        and a["periodo"] <= periodo_afetado < a["periodo"] + a["duracao"]
        for a in h1_forcado_inc
    )
    reparacao_confirmada = (
        linhas_forcadas[0]["estado"] in ("OPTIMAL", "FEASIBLE")
        and linhas_forcadas[0]["erros"] == 0
        and not ocupado
    )
 
    comparacao = mo.vstack([
        mo.md(
            "## Comparação: H0 → dados_v2/\n\n"
            "A primeira tabela mostra a alteração fornecida em `dados_v2/`. "
            "Cada método corre uma vez; os tempos variam e os objetivos "
            "são diferentes. A resolução independente minimiza os buracos; "
            "a incremental tenta manter as aulas de H0."
        ),
        mo.md("### Alteração fornecida em dados_v2/"),
        mo.md(tabela_markdown(linhas_v2)),
        mo.md(
            "### Reparação forçada de uma aula de H0\n\n"
            f"Foi escolhida a aula {aula_afetada['disciplina']} da turma "
            f"{aula_afetada['turma']} em {aula_afetada['dia']}, período "
            f"{periodo_afetado}. Esse período foi acrescentado às "
            "indisponibilidades da Prof. Ana apenas nesta execução; não foi "
            "criado outro CSV.\n\n"
            "A atualização incremental libertou o período: "
            f"{'sim' if reparacao_confirmada else 'não foi possível confirmar'}."
        ),
        mo.md(tabela_markdown(linhas_forcadas)),
        mo.md("### H1 incremental com reparação forçada"),
        apresentar_horario(h1_forcado_inc),
        mo.md("### H1 resolvido do zero com reparação forçada"),
        apresentar_horario(h1_forcado_raiz),
        mo.md("### H1 incremental"),
        apresentar_horario(h1_incremental),
        mo.md("### H1 resolvido do zero"),
        apresentar_horario(h1_raiz),
    ])
 
    comparacao
    return linhas_forcadas, linhas_v2


@app.cell(hide_code=True)
def _(horario, linhas_forcadas, linhas_v2, mo):
    def resumo_r9(linhas, cenario):
        """Frase com o tempo e as aulas alteradas de cada método num cenário."""
        inc, raiz = linhas
        if inc["tempo"] < raiz["tempo"]:
            tempo = (
                f"foi {raiz['tempo'] / inc['tempo']:.1f} vezes mais rápida "
                f"({inc['tempo']:.3f} s contra {raiz['tempo']:.3f} s)"
            )
        else:
            tempo = f"não foi mais rápida nesta execução ({inc['tempo']:.3f} s contra {raiz['tempo']:.3f} s)"
        return (
            f"- **{cenario}:** a atualização incremental {tempo} e alterou "
            f"**{inc['alteracoes']}** aula(s), contra **{raiz['alteracoes']}** "
            "na resolução do zero. Os dois horários H1 passaram na validação "
            f"({inc['erros']} e {raiz['erros']} erros)."
        )

    resumo = "\n".join([
        resumo_r9(linhas_v2, "Alteração de `dados_v2/`"),
        resumo_r9(linhas_forcadas, "Reparação forçada de uma aula de H0"),
    ])

    ana_sexta_4_5 = any(
        a["professor"] == "Prof. Ana" and a["dia"] == "Sex" and a["periodo"] + a["duracao"] - 1 >= 4
        for a in horario
    )
    if ana_sexta_4_5:
        verificacao_h0 = (
            "H0 tem aula(s) da Prof. Ana à sexta nos períodos 4 ou 5. "
            "A alteração de `dados_v2/` afeta pelo menos uma aula."
        )
    else:
        verificacao_h0 = (
            "H0 não tem aulas da Prof. Ana à sexta nos períodos 4 ou 5. "
            "A alteração fornecida em `dados_v2/` não afeta este H0; a tabela "
            "de reparação forçada acima acrescenta uma indisponibilidade para "
            "demonstrar uma mudança necessária."
        )
 
    mo.md(
        r"""
    ## Conclusão

    ### Evidência para R9 (valores desta execução)

    """ + resumo + r"""

    A diferença no número de aulas alteradas é a esperada: a resolução do zero
    não conhece H0 e reorganiza quase todo o horário, enquanto a atualização
    incremental maximiza as aulas preservadas e só muda as que a alteração
    obriga a mudar. A diferença de tempo vem de H0 ser dado ao solver como
    pista: a solução inicial já é quase ótima para o objetivo de preservação,
    que é também mais simples de provar ótimo do que o dos buracos. Os tempos
    absolutos variam entre execuções e computadores; o número de aulas
    alteradas é a medida mais estável.

    """ + verificacao_h0 + r"""
 
    O conjunto `dados_teste/` acrescenta as turmas 9Z e 8A; mantém as mesmas seis
    disciplinas.
 
    Os testes automáticos de R1–R8, da atualização H0 → H1 e dos dados adicionais
    estão no notebook `test_horario_escolar.py`.
    """
    )
    return
 
 
@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Uso de ferramentas LLM

    Usámos o **ChatGPT** como apoio ao longo do trabalho. A conversa completa
    está em: <https://chatgpt.com/s/cx_6ac29be418648191b9d999922da25f31>.
    Os registos dessa conversa estão transcritos no apêndice abaixo (e no
    ficheiro `apendice_conversas.md`).

    No código, cada função em que o ChatGPT contribuiu tem um comentário
    `# LLM (ChatGPT) — Registo N: ...` logo a seguir à documentação, que indica
    o registo da conversa e o que foi sugerido. As funções sem esse comentário
    não têm registo na conversa.

    | Função no código | Registo | Contributo do ChatGPT |
    | --- | --- | --- |
    | `carregar_dados` | 1 | Reunir a leitura dos quatro CSV numa função |
    | `preparar_dados` | 1, 2 | Conversões de tipos e validações dos dados |
    | `criar_modelo` | 4 | Uma variável booleana por colocação possível de aula |
    | `ocupantes` | 6 | Uma aula dupla ocupa o período de início e o seguinte |
    | `adicionar_restricoes` | 5, 6 | Formulação de R1–R7 como somas de variáveis |
    | `adicionar_objetivo_buracos` | 7 | Lógica de deteção de buracos nos períodos 2 a 4 |
    | `resolver_com_salas` | 8 | Função de resolução (`resolver_modelo`) |
    | `construir_horario` | 8 | Extração das aulas escolhidas (`extrair_horario`) |
    | `apresentar_horario` | 1, 8 | Tabela ordenada por turma, dia e período |
    | `validar_horario` | 1, 8 | Validador independente do solver |
    | `contar_alteracoes` | 1, 8 | Emparelhar ocorrências da mesma turma e disciplina |
    | `atualizar_horario` | 1, 8 | Reaproveitar H0 e preservar as aulas válidas |
    | `gerar_horario` | 9 | Fluxo completo dados → H0 |
    | `comparar_metodos` | 1, 9 | Comparar com a resolução do zero (tempo e aulas alteradas) |
    | `test_horario_escolar.py` | — | Testes gerados a partir do prompt indicado nesse notebook |

    ### Diferenças entre a conversa e o código final

    - `criar_tempos` (Registo 3) foi substituída pelas constantes `DIAS` e
      `PERIODOS`, definidas no início do notebook.
    - As quatro funções de restrições sugeridas (`adicionar_restricoes_turmas`,
      `_professores`, `_salas` e `_diarias`, Registos 1, 5 e 6) foram juntadas
      em `adicionar_restricoes`.
    - `resolver_modelo` e `extrair_horario` (Registo 8) passaram a chamar-se
      `resolver_com_salas` e `construir_horario`. A atribuição de salas
      concretas (`atribuir_salas_normais`) foi acrescentada depois.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    # Mostra o apêndice com as conversas, retirando a indentação dos blocos para o markdown ser renderizado.
    apendice = (Path(__file__).resolve().parent / "apendice_conversas.md").read_text(encoding="utf-8")
    mo.md("\n".join(linha.removeprefix("    ") for linha in apendice.splitlines()))
    return


if __name__ == "__main__":
    app.run()