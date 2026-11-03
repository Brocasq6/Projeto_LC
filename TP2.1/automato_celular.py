# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo>=0.16.5",
#     "pandas",
#     "pysmt",
# ]
# ///
# Solver SMT: Z3, instalado com `pysmt-install --z3` (como na ficha 1).

import marimo

__generated_with = "0.25.1"
app = marimo.App(width="full")

with app.setup:
    import random
    from itertools import product
    from pathlib import Path
    from time import perf_counter

    import pandas as pd
    from pysmt.shortcuts import (
        FALSE, TRUE, And, Equals, Iff, Int, Ite, Not, Or, Plus, Solver, Symbol,
    )
    from pysmt.typing import BOOL

    # ------------------------------------------------------------------
    # Parâmetros do problema
    # ------------------------------------------------------------------
    N = 17  # dimensão da grelha de células normais (o enunciado exige N > 16)

    # Relação de transição usada pela FSM (exigido pelo enunciado):
    #   "assincrona" -> em cada transição só uma célula normal muda de estado
    #   "sincrona"   -> em cada transição todas as células normais mudam em simultâneo
    MODO_TRANSICAO = "sincrona"
    MODOS = ("assincrona", "sincrona")

    SEMENTE = 0  # semente para sortear as células iniciais (resultados reproduzíveis)
    K_MAX = 10  # número máximo de estados dos traços explorados pelo BMC
    SOLVER = "z3"


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Exercício 1 — Game of Life como máquina de estados finita

    ## 1. Descrição do problema e abordagem

    > **Objetivo** — modelar uma variante finita do *Game of Life* (grelha
    > $N \times N$, $N > 16$, regra B3/S23) como uma FSM com duas relações de
    > transição (síncrona e assíncrona) e verificar duas propriedades:
    > 1. nunca se alcança o estado de erro (todas as células normais mortas);
    > 2. nenhuma célula normal fica permanentemente morta ou viva.

    **Estratégia.** O autómato é um FOTS (`declare`, `init`, `trans`), como na
    ficha 7, e as propriedades são verificadas com BMC através de duas funções
    genéricas, `bmc_always` ($G\,\phi$) e `bmc_eventually` ($F\,\phi$).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Escolhas

    - **Ferramenta:** pySMT com Z3, a ferramenta da cadeira para BMC.
    - **Estado:** uma variável booleana por célula normal ($N^2$). As células
      iniciais e finais são constantes e só entram na contagem de vizinhos.
    - **Células iniciais:** sorteadas uma vez com `SEMENTE` e fixas; os
      resultados valem para essa moldura.
    - **Síncrona:** todas as células tomam o valor da regra ao mesmo tempo.
    - **Assíncrona:** o solver escolhe uma célula que possa mudar; se nenhuma
      puder, o estado transita para si próprio.
    - **Propriedade 1:** invariante $G\,\neg\mathit{erro}$, com `bmc_always`.
    - **Propriedade 2:** por célula, $F\,(c=1)$ e $F\,(c=0)$, com
      `bmc_eventually`; o contra-exemplo é um traço com lacete.
    - **Limite:** sem contra-exemplo até `K_MAX`, o resultado só vale para
      traços desse tamanho.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Geometria da grelha

    A grelha completa tem índices em $\{0..N+1\}^2$: as $N^2$ células normais e
    uma moldura de $(N+2)^2 - N^2 = 4N+4$ células.

    **Decisão sobre a moldura.** O enunciado pede $2N+1$ células iniciais
    («um dos índices é zero») e $2N+3$ células finais («não são iniciais e um
    dos índices é $N+1$»). As duas contagens só batem certo se os índices das
    células iniciais estiverem em $\{0..N\}$:

    - **iniciais:** $\{(i,j) \in \{0..N\}^2 : i = 0 \lor j = 0\}$, ou seja,
      $(0,0)$, $(0,1..N)$ e $(1..N, 0)$: $1 + N + N = 2N+1$ células;
    - **finais:** as restantes células da moldura, todas com um índice igual a
      $N+1$: $(N+1, 0..N+1)$ e $(0..N, N+1)$: $(N+2) + (N+1) = 2N+3$ células.

    Os cantos $(0, N+1)$ e $(N+1, 0)$ têm um índice igual a $0$, mas contam
    como **finais**, porque o outro índice está fora de $\{0..N\}$. Só assim se
    obtém $(2N+1) + (2N+3) = 4N+4$, a moldura completa. A escolha tem efeito:
    estes cantos são vizinhos das células normais $(1, N)$ e $(N, 1)$, que
    passam a ver ali uma célula sempre morta, em vez de uma sorteada.
    """)
    return


@app.function
def celulas_normais(n=N):
    """Lista das N×N células normais (i, j), com i, j em 1..n."""
    celulas = []
    for i in range(1, n + 1):  # range exclui o fim, por isso vai até n + 1
        for j in range(1, n + 1):
            celulas.append((i, j))
    return celulas


@app.function
def celulas_iniciais(n=N):
    """Lista das 2n+1 células iniciais: (i, j) em {0..n}² com i = 0 ou j = 0."""
    celulas = []
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            if i == 0 or j == 0:  # o "ou" conta (0, 0) uma só vez
                celulas.append((i, j))
    return celulas


@app.function
def celulas_finais(n=N):
    """Lista das 2n+3 células finais: as restantes da moldura,
      incluindo os cantos (0, n+1) e (n+1, 0)."""
    iniciais = celulas_iniciais(n)
    celulas = []
    for i in range(0, n + 2):
        for j in range(0, n + 2):
            if (i == n + 1 or j == n + 1) and (i, j) not in iniciais:
                celulas.append((i, j))
    return celulas


@app.function
def vizinhos(i, j, n=N):
    """Lista dos 8 vizinhos da célula normal (i, j): as células (a, b) com
    max(|i - a|, |j - b|) = 1. Só aceita células normais, porque só estas mudam
    de estado; assim os vizinhos caem sempre dentro da moldura {0..n+1}²."""
    if not (1 <= i <= n and 1 <= j <= n):
        raise ValueError(f"({i}, {j}) não é uma célula normal para n = {n}")
    resultado = []
    for a, b in product(range(i - 1, i + 2), range(j - 1, j + 2)):
        if max(abs(i - a), abs(j - b)) == 1:  # a própria célula dá 0 e fica de fora
            resultado.append((a, b))
    return resultado


@app.function
def sortear_iniciais(n=N, semente=SEMENTE):
    """Dicionário célula inicial -> 0/1, sorteado com probabilidade 1/2 e semente fixa."""
    rng = random.Random(semente)  # gerador local: não depende do random global
    valores = {}
    for celula in celulas_iniciais(n):  # lista com ordem fixa -> resultado reproduzível
        valores[celula] = int(rng.random() < 0.5)  # probabilidade 1/2; int em vez de bool
    return valores


@app.function
def construir_fronteira(n=N, semente=SEMENTE):
    """Dicionário com o valor fixo de todas as células da moldura: iniciais sorteadas e finais a 0."""
    fronteira = dict(sortear_iniciais(n, semente))  # cópia: dicionário novo
    for celula in celulas_finais(n):
        fronteira[celula] = 0  # as células finais estão sempre mortas
    return fronteira


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Estados e relações de transição

    `declarar_estado(k)` cria a $k$-ésima
    cópia das variáveis (uma por célula normal). `init` impõe o estado inicial:
    viva se e só se $i, j \le 3$. `proximo_valor` dá, como fórmula, o valor de
    uma célula depois de aplicar B3/S23. A partir dela escrevem-se
    `trans_sincrona` e `trans_assincrona`, e `trans` escolhe uma delas pelo
    `modo`. `erro` é a conjunção de todas as células normais mortas.

    Como o BMC é genérico, recebe `declare(i)`, `init(s)` e `trans(s, p)` só
    com os estados como argumentos. `fabricar_fsm` fixa a moldura, o modo e
    $N$ e devolve essas três funções prontas a passar ao BMC.
    """)
    return


@app.function
def declarar_estado(k, n=N):
    """Cria as variáveis do estado número k do traço; devolve um dicionário célula -> variável."""
    estado = {}
    for (i, j) in celulas_normais(n):
        # separadores no nome evitam colisões, ex.: (1, 11) e (11, 1) no mesmo estado
        estado[(i, j)] = Symbol(f"c_{i}_{j}_{k}", BOOL)
    return estado


@app.function
def valor_celula(s, celula, fronteira):
    """Termo/valor de uma célula no estado s: variável se for normal, constante se for inicial ou final."""
    if celula in s:  # célula normal: o valor é decidido pelo solver
        return s[celula]
    if celula in fronteira:  # célula da moldura: constante booleana
        return TRUE() if fronteira[celula] == 1 else FALSE()
    raise ValueError(f"{celula} não pertence à grelha")


@app.function
def init(s, fronteira, n=N):
    """Fórmula que caracteriza o estado inicial."""
    condicoes = []
    for (i, j) in celulas_normais(n):
        if i <= 3 and j <= 3:  # bloco 3×3 do canto: viva
            condicoes.append(s[(i, j)])
        else:  # todas as outras células normais: morta
            condicoes.append(Not(s[(i, j)]))
    return And(condicoes)


@app.function
def proximo_valor(s, celula, fronteira, n=N):
    """Fórmula do valor seguinte de uma célula normal segundo a regra B3/S23."""
    i, j = celula
    termos = []
    vivos_moldura = 0
    for v in vizinhos(i, j, n):
        if v in s:  # vizinha normal: conta 1 se a variável for verdadeira
            termos.append(Ite(valor_celula(s, v, fronteira), Int(1), Int(0)))
        else:  # vizinha da moldura: valor constante, somado logo em Python
            vivos_moldura += fronteira[v]
    termos.append(Int(vivos_moldura))
    contagem = Plus(termos)
    # B3/S23 na forma compacta: viva sse 3 vizinhos, ou viva e 2 vizinhos
    return Or(Equals(contagem, Int(3)), And(s[celula], Equals(contagem, Int(2))))


@app.function
def trans_sincrona(s, p, fronteira, n=N):
    """Relação de transição em que todas as células normais transitam em simultâneo."""
    # cada célula de p toma o valor da regra calculado só a partir de s
    return And([Iff(p[c], proximo_valor(s, c, fronteira, n)) for c in celulas_normais(n)])


@app.function
def trans_assincrona(s, p, fronteira, n=N):
    """Relação de transição em que uma e só uma célula normal transita de estado (lacete se nenhuma puder mudar)."""
    restricoes = []
    mudancas = []  # termos 1/0 para contar as células que mudaram
    podem = []  # condições «a célula pode mudar»
    for c in celulas_normais(n):
        pode_mudar = Not(Iff(proximo_valor(s, c, fronteira, n), s[c]))
        mudou = Not(Iff(p[c], s[c]))
        restricoes.append(Or(Not(mudou), pode_mudar))  # mudou => pode_mudar
        mudancas.append(Ite(mudou, Int(1), Int(0)))
        podem.append(pode_mudar)
    # muda exatamente uma se alguma puder mudar; nenhuma se o estado for estável
    restricoes.append(Equals(Plus(mudancas), Ite(Or(podem), Int(1), Int(0))))
    return And(restricoes)


@app.function
def trans(s, p, fronteira, modo=MODO_TRANSICAO, n=N):
    """Escolhe a relação de transição de acordo com o parâmetro `modo`."""
    if modo == "sincrona":
        return trans_sincrona(s, p, fronteira, n)
    if modo == "assincrona":
        return trans_assincrona(s, p, fronteira, n)
    raise ValueError(f"modo inválido: {modo!r}; valores aceites: {MODOS}")


@app.function
def erro(s, n=N):
    """Fórmula do estado de erro: todas as células normais mortas.
    Não recebe fronteira: o enunciado define o erro só com as células normais."""
    return And([Not(s[c]) for c in celulas_normais(n)])


@app.function
def fabricar_fsm(fronteira, modo=MODO_TRANSICAO, n=N):
    """Devolve (declare, init, trans) só com estados como argumentos, prontos para o BMC genérico."""
    if modo not in MODOS:  # o erro aparece já aqui, e não a meio do BMC
        raise ValueError(f"modo inválido: {modo!r}; valores aceites: {MODOS}")

    # nomes diferentes de init/trans, para chamarem as funções globais e não a si próprias
    def declare_fsm(k):
        return declarar_estado(k, n)

    def init_fsm(s):
        return init(s, fronteira, n)

    def trans_fsm(s, p):
        return trans(s, p, fronteira, modo, n)

    return declare_fsm, init_fsm, trans_fsm


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 5. Simulação concreta (validação do modelo)

    Simulador em Python puro, independente do solver, com dois papéis:

    - mostrar a evolução da grelha a partir do estado inicial, em qualquer dos
      modos, para se perceber o comportamento antes de usar o BMC;
    - confirmar que cada traço ou contra-exemplo devolvido pelo solver é uma
      execução válida da FSM: o primeiro estado é o inicial, e cada par de
      estados consecutivos respeita a regra no modo escolhido. Isto valida o
      modelo simbólico de forma independente.
    """)
    return


@app.function
def estado_inicial_concreto(n=N):
    """Grelha inicial concreta (dicionário célula normal -> 0/1)."""
    grelha = {}
    for (i, j) in celulas_normais(n):
        grelha[(i, j)] = 1 if i <= 3 and j <= 3 else 0  # bloco 3×3 vivo
    return grelha


@app.function
def aplicar_regra(grelha, fronteira, n=N):
    """Dicionário célula normal -> valor que a regra B3/S23 lhe dá, calculado a partir de grelha."""
    resultado = {}
    for celula in celulas_normais(n):
        vivos = 0
        for v in vizinhos(*celula, n):
            vivos += grelha[v] if v in grelha else fronteira[v]  # normal: grelha; moldura: fronteira
        if grelha[celula] == 1:
            resultado[celula] = 1 if vivos in (2, 3) else 0  # sobrevivência
        else:
            resultado[celula] = 1 if vivos == 3 else 0  # nascimento
    return resultado


@app.function
def passo_concreto(grelha, fronteira, modo=MODO_TRANSICAO, rng=None, n=N):
    """Aplica uma transição concreta à grelha (no modo assíncrono, a célula que muda é escolhida por rng)."""
    if modo not in MODOS:
        raise ValueError(f"modo inválido: {modo!r}; valores aceites: {MODOS}")
    regra = aplicar_regra(grelha, fronteira, n)  # dicionário novo; a grelha não é alterada

    if modo == "sincrona":
        return regra

    if rng is None:
        raise ValueError("o modo assíncrono precisa de um gerador rng, ex.: random.Random(semente)")
    instaveis = [c for c in celulas_normais(n) if regra[c] != grelha[c]]
    nova = dict(grelha)
    if instaveis:  # se nenhuma for instável, o estado repete-se (lacete)
        c = rng.choice(instaveis)
        nova[c] = regra[c]
    return nova


@app.function
def traco_e_valido(traco, fronteira, modo=MODO_TRANSICAO, n=N):
    """Verifica se uma sequência de grelhas é uma execução válida da FSM; devolve a lista de erros
    (lista vazia = traço válido). Aceita valores 0/1 ou True/False.
    Para validar um lacete, quem chama acrescenta ao fim do traço uma cópia do estado onde o
    lacete começa; assim a transição de regresso também é verificada."""
    if modo not in MODOS:
        raise ValueError(f"modo inválido: {modo!r}; valores aceites: {MODOS}")
    if not traco:
        return ["traço vazio: não há execução"]

    erros = []
    normais = celulas_normais(n)

    # Passo 1 — normalizar para 0/1 e verificar o formato de cada grelha
    grelhas = []
    for k, g in enumerate(traco):
        if set(g) != set(normais):
            erros.append(f"estado {k}: as chaves não são as células normais de uma grelha {n}×{n}")
            return erros
        g = {c: int(g[c]) for c in normais}
        maus = [c for c in normais if g[c] not in (0, 1)]
        if maus:
            erros.append(f"estado {k}: valores fora de {{0, 1}} em {maus}")
            return erros
        grelhas.append(g)

    # Passo 2 — o primeiro estado é o inicial
    inicial = estado_inicial_concreto(n)
    diferentes = [c for c in normais if grelhas[0][c] != inicial[c]]
    if diferentes:
        erros.append(f"estado 0: não é o estado inicial; diferem as células {diferentes}")

    # Passo 3 — cada par consecutivo respeita a transição
    for k in range(len(grelhas) - 1):
        a, b = grelhas[k], grelhas[k + 1]
        regra = aplicar_regra(a, fronteira, n)
        if modo == "sincrona":
            for c in normais:
                if b[c] != regra[c]:
                    erros.append(f"passo {k}->{k + 1}: célula {c} devia valer {regra[c]}, vale {b[c]}")
        else:
            instaveis = [c for c in normais if regra[c] != a[c]]
            mudaram = [c for c in normais if b[c] != a[c]]
            if not instaveis and mudaram:
                erros.append(f"passo {k}->{k + 1}: estado estável, mas mudaram {mudaram}")
            elif instaveis and len(mudaram) != 1:
                erros.append(f"passo {k}->{k + 1}: devia mudar exatamente uma célula instável, "
                             f"mudaram {len(mudaram)}: {mudaram}")
            elif instaveis and mudaram[0] not in instaveis:
                erros.append(f"passo {k}->{k + 1}: a célula {mudaram[0]} mudou, mas não era instável")
    return erros


@app.function
def apresentar_grelha(grelha, fronteira=None, n=N):
    """Tabela (pandas) da grelha para mostrar no Marimo, com ou sem a moldura de células iniciais/finais.
    Legenda: ■ viva e · morta nas células normais; ● viva e ○ morta na moldura."""
    indices = range(1, n + 1) if fronteira is None else range(0, n + 2)
    linhas = []
    for i in indices:
        linha = []
        for j in indices:
            if (i, j) in grelha:
                linha.append("■" if int(grelha[(i, j)]) == 1 else "·")
            else:
                linha.append("●" if int(fronteira[(i, j)]) == 1 else "○")
        linhas.append(linha)
    return pd.DataFrame(linhas, index=list(indices), columns=list(indices))


@app.cell
def _(mo):
    PASSOS_SIMULACAO = 200  # máximo do slider; o assíncrono muda uma célula por passo

    modo_sim = mo.ui.dropdown(
        options=list(MODOS), value=MODO_TRANSICAO, label="Modo de transição"
    )
    passo_sim = mo.ui.slider(
        start=0, stop=PASSOS_SIMULACAO, step=1, value=0, label="Passo", show_value=True
    )
    semente_escalonador = mo.ui.number(
        start=0, stop=1_000_000, step=1, value=0,
        label="Semente do escalonador (só assíncrono)",
    )
    mostrar_moldura = mo.ui.checkbox(value=True, label="Mostrar moldura")

    mo.vstack([
        mo.md("### Simulação concreta"),
        mo.hstack([modo_sim, semente_escalonador, mostrar_moldura], justify="start"),
        passo_sim,
    ])
    return (
        PASSOS_SIMULACAO,
        modo_sim,
        mostrar_moldura,
        passo_sim,
        semente_escalonador,
    )


@app.cell
def _(PASSOS_SIMULACAO, modo_sim, semente_escalonador):
    _rng = random.Random(int(semente_escalonador.value or 0))  # um só gerador para o traço todo
    fronteira_sim = construir_fronteira(N, SEMENTE)  # a mesma moldura do resto do trabalho
    traco_sim = [estado_inicial_concreto(N)]
    for _ in range(PASSOS_SIMULACAO):
        traco_sim.append(passo_concreto(traco_sim[-1], fronteira_sim, modo_sim.value, _rng, N))
    erros_sim = traco_e_valido(traco_sim, fronteira_sim, modo_sim.value, N)
    return erros_sim, fronteira_sim, traco_sim


@app.cell
def _(
    PASSOS_SIMULACAO,
    erros_sim,
    fronteira_sim,
    mo,
    modo_sim,
    mostrar_moldura,
    passo_sim,
    traco_sim,
):
    _k = passo_sim.value
    _grelha = traco_sim[_k]
    _vivas = sum(_grelha.values())

    _linhas = [f"**Passo {_k}** de {PASSOS_SIMULACAO} · modo **{modo_sim.value}** · "
               f"células vivas: **{_vivas}**"]
    if _vivas == 0:
        _linhas.append("⚠️ **Estado de erro:** todas as células normais estão mortas.")
    if _k > 0:
        _mudaram = [c for c in _grelha if _grelha[c] != traco_sim[_k - 1][c]]
        if not _mudaram:
            _linhas.append("Estado igual ao anterior (estável).")
        elif modo_sim.value == "assincrona":
            _linhas.append(f"Mudou a célula {_mudaram[0]}.")
        else:
            _linhas.append(f"Mudaram {len(_mudaram)} células.")
    _linhas.append("✅ Traço válido." if not erros_sim
                   else f"❌ Traço inválido: {len(erros_sim)} erros (ex.: {erros_sim[0]})")
    _linhas.append("Legenda: ■ viva, · morta (células normais); ● viva, ○ morta (moldura).")

    _tabela = apresentar_grelha(_grelha, fronteira_sim if mostrar_moldura.value else None, N)
    mo.vstack([mo.md("\n\n".join(_linhas)), mo.Html(_tabela.to_html())])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 6. Bounded model checking genérico

    As duas funções servem para qualquer FOTS: recebem
    `declare`, `init`, `trans`, a propriedade e o limite `K`, e não dependem do
    autómato.

    - `bmc_always` (invariantes $G\,\phi$): para $k = 1..K$, procura um traço
      de $k$ estados que começa num estado inicial, respeita `trans` e cujo
      último estado viola $\phi$. Como $k$ cresce, o primeiro contra-exemplo
      encontrado é mínimo.
    - `bmc_eventually` (animação $F\,\phi$): para $k = 1..K$, procura um traço
      de $k$ estados em que $\phi$ é falsa em todos os estados e o último
      estado transita para um dos anteriores (lacete). Isso é uma execução
      infinita em que $\phi$ nunca acontece. Devolve também o estado onde o
      lacete começa.

    Ambas devolvem um dicionário com o resultado (`"contra-exemplo"` ou
    `"sem contra-exemplo até K"`), o número de estados, o traço (valores das
    variáveis em cada estado) e o tempo.
    """)
    return


@app.cell
def _():
    from pysmt.shortcuts import (
        FALSE, TRUE, And, Equals, EqualsOrIff, Iff, Int, Ite, Not, Or, Plus, Solver, Symbol,
    )

    return (
        And,
        Equals,
        EqualsOrIff,
        FALSE,
        Iff,
        Int,
        Ite,
        Not,
        Or,
        Plus,
        Solver,
        Symbol,
        TRUE,
    )


@app.function
def extrair_traco(modelo, estados):
    """Converte o modelo do solver numa lista de dicionários (variável -> valor Python), um por estado."""
    traco = []
    for estado in estados:
        traco.append({chave: modelo.get_py_value(var) for chave, var in estado.items()})
    return traco


@app.function
def bmc_always(declare, init, trans, inv, K):
    """BMC genérico de um invariante G inv: devolve resultado, k, traço (contra-exemplo mínimo, se houver) e tempo."""
    inicio = perf_counter()
    with Solver(name=SOLVER) as solver:
        estados = [declare(0)]
        solver.add_assertion(init(estados[0]))  # permanente
        for k in range(1, K + 1):
            if k > 1:
                estados.append(declare(k - 1))
                solver.add_assertion(trans(estados[-2], estados[-1]))  # permanente
            solver.push()
            solver.add_assertion(Not(inv(estados[-1])))  # só para este k
            if solver.solve():
                traco = extrair_traco(solver.get_model(), estados)
                return {"resultado": "contra-exemplo", "k": k, "traço": traco,
                        "lacete": None, "tempo": perf_counter() - inicio}
            solver.pop()
            # insatisfazível: inv vale no último estado de qualquer traço com k estados,
            # por isso pode ficar como restrição permanente (ajuda o solver nos k seguintes)
            solver.add_assertion(inv(estados[-1]))
    return {"resultado": "sem contra-exemplo até K", "k": K, "traço": None,
            "lacete": None, "tempo": perf_counter() - inicio}


@app.cell
def _(EqualsOrIff):
    def bmc_eventually(declare, init, trans, prop, K):
        """BMC genérico de F prop: procura um lacete onde prop nunca é verdade; devolve resultado, k, traço, início do lacete e tempo."""
        inicio = perf_counter()
        with Solver(name=SOLVER) as solver:
            estados = [declare(0)]
            solver.add_assertion(init(estados[0]))
            for k in range(1, K + 1):
                if k > 1:
                    estados.append(declare(k - 1))
                    solver.add_assertion(trans(estados[-2], estados[-1]))
                solver.add_assertion(Not(prop(estados[-1])))  # permanente: vale em todo o lacete
                extra = declare(k)  # estado extra que fecha o lacete
                solver.push()
                solver.add_assertion(trans(estados[-1], extra))
                solver.add_assertion(Or([
                    And([EqualsOrIff(extra[c], anterior[c]) for c in extra]) for anterior in estados
                ]))
                if solver.solve():
                    completo = extrair_traco(solver.get_model(), estados + [extra])
                    traco, fecho = completo[:-1], completo[-1]
                    lacete = next((l for l, estado in enumerate(traco) if estado == fecho), None)
                    if lacete is None:  # não deve acontecer: o solver garantiu que algum estado coincide
                        raise RuntimeError(f"k = {k}: o estado extra não coincide com nenhum estado do traço")
                    return {"resultado": "contra-exemplo", "k": k, "traço": traco,
                            "lacete": lacete, "tempo": perf_counter() - inicio}
                solver.pop()  # o estado extra e o fecho do lacete só valiam para este k
        return {"resultado": "sem contra-exemplo até K", "k": K, "traço": None,
                "lacete": None, "tempo": perf_counter() - inicio}

    return (bmc_eventually,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 7. Propriedade 1 — nunca se alcança o estado de erro

    **Formulação.** $G\,\neg\mathit{erro}$: em todos os estados alcançáveis há
    pelo menos uma célula normal viva.

    **Técnica.** `bmc_always` com `inv = lambda s: Not(erro(s))`, para cada modo
    de transição.

    **Interpretação.**
    - *Contra-exemplo:* um traço mínimo desde o estado inicial até a grelha
      morrer toda. A propriedade é **falsa**, e o traço é confirmado com
      `traco_e_valido` e mostrado com `apresentar_grelha`.
    - *Sem contra-exemplo até `K_MAX`:* a propriedade vale nos primeiros
      `K_MAX` estados, mas isto **não é uma prova** para execuções mais longas.
      Nesse caso o resultado é inconclusivo e indicamos o limite atingido.
    """)
    return


@app.function
def simular_ate_ciclo(fronteira, n=N, passos_max=10_000):
    """Simula o modo síncrono a partir do estado inicial até um estado se repetir.
    Devolve (traço sem repetições, índice onde o ciclo começa, período do ciclo)."""
    grelha = estado_inicial_concreto(n)
    traco = []
    vistos = {}  # frozenset das células vivas -> índice onde o estado apareceu
    while True:
        chave = frozenset(c for c, v in grelha.items() if v == 1)
        if chave in vistos:
            inicio = vistos[chave]
            return traco, inicio, len(traco) - inicio
        if len(traco) >= passos_max:
            raise RuntimeError(f"nenhum estado se repetiu em {passos_max} passos")
        vistos[chave] = len(traco)
        traco.append(grelha)
        grelha = passo_concreto(grelha, fronteira, "sincrona", n=n)


@app.function
def verificar_nunca_erro(fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N):
    """Aplica bmc_always a G ¬erro com a FSM de fabricar_fsm; devolve o dicionário de resultado do BMC."""
    declare, init_fsm, trans_fsm = fabricar_fsm(fronteira, modo, n)
    resultado = bmc_always(declare, init_fsm, trans_fsm, lambda s: Not(erro(s, n)), k_max)
    if resultado["traço"] is not None:  # contra-exemplo: conferido pelo simulador
        traco = resultado["traço"]
        problemas = traco_e_valido(traco, fronteira, modo, n)
        if sum(int(v) for v in traco[-1].values()) != 0:
            problemas.append("o último estado não é o estado de erro")
        anteriores = [k for k, g in enumerate(traco[:-1]) if sum(int(v) for v in g.values()) == 0]
        if anteriores:
            problemas.append(f"contra-exemplo não mínimo: estados de erro antes do fim em {anteriores}")
        resultado["validação"] = problemas
    return resultado


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 8. Propriedade 2 — nenhuma célula normal permanentemente morta ou viva

    **Formulação.** Para cada célula normal $c$:
    - não está permanentemente morta: $F\,(c = 1)$;
    - não está permanentemente viva: $F\,(c = 0)$.

    A propriedade 2 é a conjunção destas $2N^2$ fórmulas.

    **Técnica.** `bmc_eventually` para cada célula e cada valor. Um
    contra-exemplo é um lacete em que a célula nunca muda, ou seja, uma
    execução infinita em que ela fica para sempre morta (ou viva). Basta uma
    célula com contra-exemplo para a propriedade 2 ser **falsa**.

    **Agregação.** `verificar_todas_celulas` junta os resultados numa tabela
    (célula, valor, resultado, $k$, tempo). No modo síncrono, com a moldura
    fixa, o sistema é determinista: há uma única execução, que a simulação
    concreta reproduz. Por isso ela mostra logo que células mudam e quais
    ficam constantes, o que serve para conferir os resultados do BMC e para
    escolher que células verificar primeiro. No modo assíncrono há muitas
    execuções possíveis, e uma simulação não chega para excluir um
    contra-exemplo. Aí só o BMC responde.
    """)
    return


@app.cell
def _(bmc_eventually):
    def verificar_permanencia(celula, valor, fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N):
        """Aplica bmc_eventually a F(célula ≠ valor) (0 = morta, 1 = viva); devolve o dicionário de resultado do BMC."""
        if celula not in set(celulas_normais(n)):
            raise ValueError(f"{celula} não é uma célula normal para n = {n}")
        if valor not in (0, 1):
            raise ValueError(f"valor tem de ser 0 ou 1, recebido {valor!r}")

        # atalho: se a célula já é diferente de valor no estado inicial, F(célula ≠ valor) vale no estado 0
        if estado_inicial_concreto(n)[celula] != valor:
            return {"resultado": "provada no estado inicial", "k": 1, "traço": None,
                    "lacete": None, "tempo": 0.0, "validação": None}

        declare, init_fsm, trans_fsm = fabricar_fsm(fronteira, modo, n)

        def prop(s):  # «a célula é diferente de valor»
            return s[celula] if valor == 0 else Not(s[celula])

        resultado = bmc_eventually(declare, init_fsm, trans_fsm, prop, k_max)
        resultado["validação"] = None
        if resultado["traço"] is not None:  # contra-exemplo: conferido pelo simulador
            traco = resultado["traço"]
            problemas = traco_e_valido(traco + [traco[resultado["lacete"]]], fronteira, modo, n)
            mudou = [k for k, g in enumerate(traco) if int(g[celula]) != valor]
            if mudou:
                problemas.append(f"a célula {celula} não vale {valor} nos estados {mudou}")
            resultado["validação"] = problemas
        return resultado

    return (verificar_permanencia,)


@app.cell
def _(verificar_permanencia):
    def verificar_todas_celulas(fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N,
                                celulas=None, parar_no_primeiro=False):
        """Aplica verificar_permanencia a todas as células normais e devolve uma tabela-resumo.
        A conclusão global fica em tabela.attrs["conclusão"]: falsa, provada ou inconclusiva até K."""
        celulas = celulas_normais(n) if celulas is None else celulas
        linhas = []
        for c in celulas:
            for valor in (0, 1):
                r = verificar_permanencia(c, valor, fronteira, modo, k_max, n)
                linhas.append({
                    "célula": c,
                    "valor testado": "morta" if valor == 0 else "viva",
                    "resultado": r["resultado"],
                    "k": r["k"],
                    "lacete": r["lacete"],
                    "tempo (s)": round(r["tempo"], 2),
                    "validação": "—" if r["validação"] is None else ("ok" if not r["validação"] else "falhou"),
                })
                if parar_no_primeiro and r["resultado"] == "contra-exemplo":
                    break
            if parar_no_primeiro and linhas[-1]["resultado"] == "contra-exemplo":
                break

        tabela = pd.DataFrame(linhas)
        resultados = tabela["resultado"]
        if (resultados == "contra-exemplo").any():
            tabela.attrs["conclusão"] = "falsa"
        elif (resultados == "provada no estado inicial").all():
            tabela.attrs["conclusão"] = "provada"
        else:
            tabela.attrs["conclusão"] = "inconclusiva até K"
        return tabela

    return (verificar_todas_celulas,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 9. Resultados

    Execução das duas propriedades nos dois modos de transição, com a mesma
    moldura (`SEMENTE`). Cada contra-exemplo é confirmado pelo simulador antes
    de ser apresentado.
    """)
    return


app._unparsable_cell(
    r"""
        # Profundidades da secção 9 (ajustar depois de medir os tempos de uma célula)
        K_ERRO_ASSINCRONA = 15        # >= 10: o erro precisa de pelo menos 9 transições
        K_PERMANENCIA_ASSINCRONA = 10
        AMOSTRA_P2_ASSINCRONA = None  # None = todas as células; um número = só as N mais afastadas
        PARAR_P2_ASSINCRONA = True    # parar no primeiro contra-exemplo da propriedade 2
        LIMITE_K_SINCRONA = 60        # teto do K das verificações cruzadas no modo síncrono
    """,
    name="_"
)


@app.function
def estado_validacao(resultado):
    """Resume a chave «validação» de um resultado: «—» sem contra-exemplo, «ok» ou «falhou»."""
    validacao = resultado.get("validação")
    if validacao is None:
        return "—"
    return "ok" if not validacao else "falhou"


@app.cell
def _():
    moldura = construir_fronteira(N, SEMENTE)
    traco_sinc, inicio_ciclo_sinc, periodo_sinc = simular_ate_ciclo(moldura, N)

    # propriedade 1: primeiro estado do traço com todas as células mortas (None se não existir)
    erro_sinc = next((k for k, g in enumerate(traco_sinc) if sum(g.values()) == 0), None)

    # propriedade 2: valores de cada célula no traço inteiro (leitura a) e só no ciclo (leitura b)
    categoria_sinc = {}
    constante_no_ciclo_sinc = []
    for _c in celulas_normais(N):
        _no_traco = {g[_c] for g in traco_sinc}
        _no_ciclo = {g[_c] for g in traco_sinc[inicio_ciclo_sinc:]}
        if _no_traco == {0}:
            categoria_sinc[_c] = "sempre morta"
        elif _no_traco == {1}:
            categoria_sinc[_c] = "sempre viva"
        else:
            categoria_sinc[_c] = "muda"
        if len(_no_ciclo) == 1:
            constante_no_ciclo_sinc.append(_c)
    return (
        categoria_sinc,
        constante_no_ciclo_sinc,
        erro_sinc,
        inicio_ciclo_sinc,
        moldura,
        periodo_sinc,
        traco_sinc,
    )


@app.cell
def _(
    categoria_sinc,
    constante_no_ciclo_sinc,
    erro_sinc,
    inicio_ciclo_sinc,
    mo,
    moldura,
    periodo_sinc,
    traco_sinc,
):
    _contagem = {cat: sum(1 for v in categoria_sinc.values() if v == cat)
                 for cat in ("sempre morta", "sempre viva", "muda")}
    _constantes = _contagem["sempre morta"] + _contagem["sempre viva"]
    _simbolo = {"sempre morta": "·", "sempre viva": "■", "muda": "◆"}
    _mapa = pd.DataFrame(
        [[_simbolo[categoria_sinc[(i, j)]] for j in range(1, N + 1)] for i in range(1, N + 1)],
        index=range(1, N + 1), columns=range(1, N + 1),
    )

    if erro_sinc is None:
        _p1 = (f"**provada.** Nenhum dos {len(traco_sinc)} estados alcançáveis é o estado de erro. "
               "Como o modo síncrono é determinista e tem um único estado inicial, estes são "
               "todos os estados alcançáveis.")
    else:
        _p1 = (f"**falsa.** O estado de erro é alcançado no estado {erro_sinc} "
               f"(traço de {erro_sinc + 1} estados).")

    mo.vstack([
        mo.md(f"""
    ### Moldura e simulação síncrona

    Moldura sorteada com `SEMENTE = {SEMENTE}`, N = {N}. Estado inicial com a moldura
    (■ viva, · morta nas células normais; ● viva, ○ morta na moldura):
    """),
        mo.Html(apresentar_grelha(estado_inicial_concreto(N), moldura, N).to_html()),
        mo.md(f"""
    A execução síncrona tem **{len(traco_sinc)} estados distintos**: transiente de
    {inicio_ciclo_sinc} estados e ciclo de período {periodo_sinc}
    {"(ponto fixo)" if periodo_sinc == 1 else "(oscilador)"}.

    **Propriedade 1 (síncrono):** {_p1}

    **Propriedade 2 (síncrono), leitura (a):** {_contagem["sempre morta"]} células sempre
    mortas, {_contagem["sempre viva"]} sempre vivas e {_contagem["muda"]} que mudam.
    A propriedade é **{"falsa" if _constantes else "provada"}**.

    **Leitura (b):** {len(constante_no_ciclo_sinc)} células ficam constantes dentro do ciclo.

    Mapa das células (· sempre morta, ■ sempre viva, ◆ muda):
    """),
        mo.Html(_mapa.to_html()),
    ])
    return


@app.cell
def _(mo):
    botao_p1 = mo.ui.run_button(label="Propriedade 1 — BMC")
    botao_p2_sinc = mo.ui.run_button(label="Propriedade 2 — verificação cruzada (síncrono)")
    botao_p2_assinc = mo.ui.run_button(label="Propriedade 2 — BMC (assíncrono)")
    mo.hstack([botao_p1, botao_p2_sinc, botao_p2_assinc], justify="start")
    return botao_p1, botao_p2_assinc, botao_p2_sinc


@app.cell
def _(
    K_ERRO_ASSINCRONA,
    LIMITE_K_SINCRONA,
    botao_p1,
    erro_sinc,
    mo,
    moldura,
    traco_sinc,
):
    mo.stop(not botao_p1.value, mo.md("_Carrega em «Propriedade 1 — BMC» para correr esta verificação._"))

    k_p1_sinc = min(len(traco_sinc), LIMITE_K_SINCRONA)
    p1_sinc = verificar_nunca_erro(moldura, "sincrona", k_p1_sinc, N)
    p1_assinc = verificar_nunca_erro(moldura, "assincrona", K_ERRO_ASSINCRONA, N)

    # verificação cruzada no síncrono: o BMC tem de concordar com a simulação
    if erro_sinc is not None and erro_sinc + 1 <= k_p1_sinc:
        _traco_bmc = [{c: int(v) for c, v in g.items()} for g in (p1_sinc["traço"] or [])]
        p1_concorda = p1_sinc["k"] == erro_sinc + 1 and _traco_bmc == traco_sinc[: erro_sinc + 1]
    else:  # sem erro ao alcance de K: o BMC não pode encontrar contra-exemplo
        p1_concorda = p1_sinc["resultado"] != "contra-exemplo"

    mo.md(f"""
    ### Propriedade 1 — BMC

    **Síncrono** (K = {k_p1_sinc}): {p1_sinc["resultado"]}, k = {p1_sinc["k"]},
    {p1_sinc["tempo"]:.2f} s, validação: {estado_validacao(p1_sinc)}.
    Concorda com a simulação: {"sim ✅" if p1_concorda else "não ❌"}.

    **Assíncrono** (K = {K_ERRO_ASSINCRONA}): {p1_assinc["resultado"]}, k = {p1_assinc["k"]},
    {p1_assinc["tempo"]:.2f} s, validação: {estado_validacao(p1_assinc)}.
    """)
    return p1_assinc, p1_concorda, p1_sinc


@app.cell
def _(
    LIMITE_K_SINCRONA,
    botao_p2_sinc,
    categoria_sinc,
    inicio_ciclo_sinc,
    mo,
    moldura,
    traco_sinc,
    verificar_permanencia,
):
    mo.stop(not botao_p2_sinc.value,
            mo.md("_Carrega em «Propriedade 2 — verificação cruzada (síncrono)»._"))

    _L = len(traco_sinc)
    _mortas = [c for c, cat in categoria_sinc.items() if cat == "sempre morta"]
    _vivas = [c for c, cat in categoria_sinc.items() if cat == "sempre viva"]
    # as duas últimas sempre mortas (as mais afastadas do quadrado inicial) e uma sempre viva
    _amostra = [(c, 0) for c in _mortas[-2:]] + [(c, 1) for c in _vivas[:1]]

    _linhas = []
    if _amostra and _L <= LIMITE_K_SINCRONA:
        for _c, _valor in _amostra:
            _r = verificar_permanencia(_c, _valor, moldura, "sincrona", _L, N)
            _linhas.append({
                "célula": str(_c), "valor testado": "morta" if _valor == 0 else "viva", "K": _L,
                "resultado": _r["resultado"], "k": _r["k"], "k esperado": _L,
                "lacete": _r["lacete"], "lacete esperado": inicio_ciclo_sinc,
                "validação": estado_validacao(_r), "tempo (s)": round(_r["tempo"], 2),
                "concorda": _r["k"] == _L and _r["lacete"] == inicio_ciclo_sinc
                            and estado_validacao(_r) == "ok",
            })
        if _L > 1:  # limitação do BMC: com K abaixo do comprimento do traço, o lacete não fecha
            _c, _valor = _amostra[0]
            _r = verificar_permanencia(_c, _valor, moldura, "sincrona", _L - 1, N)
            _linhas.append({
                "célula": str(_c), "valor testado": "morta" if _valor == 0 else "viva", "K": _L - 1,
                "resultado": _r["resultado"], "k": _r["k"], "k esperado": "—",
                "lacete": _r["lacete"], "lacete esperado": "—",
                "validação": estado_validacao(_r), "tempo (s)": round(_r["tempo"], 2),
                "concorda": _r["resultado"] != "contra-exemplo",
            })
    tabela_p2_sinc = pd.DataFrame(_linhas)

    if not _amostra:
        _saida = mo.md("Não há células constantes no modo síncrono: não há contra-exemplos para confirmar.")
    elif _L > LIMITE_K_SINCRONA:
        _saida = mo.md(f"O traço síncrono tem {_L} estados, acima de `LIMITE_K_SINCRONA` = "
                       f"{LIMITE_K_SINCRONA}: a verificação cruzada com BMC não foi feita.")
    else:
        _saida = mo.vstack([
            mo.md(f"""
    ### Propriedade 2 — verificação cruzada (síncrono)

    Para as células constantes, o BMC com K = {_L} tem de encontrar um lacete com k = {_L}
    que começa no estado {inicio_ciclo_sinc}. A última linha usa K = {_L - 1}: aí o lacete
    ainda não fecha e o BMC não encontra o contra-exemplo, embora ele exista.
    """),
            tabela_p2_sinc,
        ])
    _saida
    return (tabela_p2_sinc,)


@app.cell
def _(
    AMOSTRA_P2_ASSINCRONA,
    K_PERMANENCIA_ASSINCRONA,
    PARAR_P2_ASSINCRONA,
    botao_p2_assinc,
    mo,
    moldura,
    verificar_permanencia,
    verificar_todas_celulas,
):
    mo.stop(not botao_p2_assinc.value, mo.md("_Carrega em «Propriedade 2 — BMC (assíncrono)»._"))

    # células mais afastadas do quadrado inicial primeiro: são as que mais provavelmente ficam constantes
    _ordem = sorted(celulas_normais(N), key=lambda c: max(c[0] - 3, c[1] - 3, 0), reverse=True)
    tabela_p2_assinc = verificar_todas_celulas(
        moldura, "assincrona", K_PERMANENCIA_ASSINCRONA, N,
        celulas=_ordem[:AMOSTRA_P2_ASSINCRONA], parar_no_primeiro=PARAR_P2_ASSINCRONA,
    )
    _falhou = (tabela_p2_assinc["validação"] == "falhou").any()
    conclusao_p2_assinc = "erro de validação" if _falhou else tabela_p2_assinc.attrs["conclusão"]

    # repetir o primeiro contra-exemplo para ter o traço (o BMC é determinista: dá o mesmo)
    _cex = tabela_p2_assinc[tabela_p2_assinc["resultado"] == "contra-exemplo"]
    if len(_cex):
        _celula = _cex.iloc[0]["célula"]
        _valor = 0 if _cex.iloc[0]["valor testado"] == "morta" else 1
        p2_assinc_exemplo = (_celula, _valor, verificar_permanencia(
            _celula, _valor, moldura, "assincrona", K_PERMANENCIA_ASSINCRONA, N))
    else:
        p2_assinc_exemplo = None

    _mostrar = tabela_p2_assinc.copy()
    _mostrar["célula"] = _mostrar["célula"].astype(str)
    mo.vstack([
        mo.md(f"""
    ### Propriedade 2 — BMC (assíncrono)

    K = {K_PERMANENCIA_ASSINCRONA}; {len(tabela_p2_assinc)} verificações em
    {tabela_p2_assinc["tempo (s)"].sum():.1f} s. Conclusão: **{conclusao_p2_assinc}**.
    """),
        _mostrar,
    ])
    return conclusao_p2_assinc, p2_assinc_exemplo, tabela_p2_assinc


@app.cell
def _(
    AMOSTRA_P2_ASSINCRONA,
    K_PERMANENCIA_ASSINCRONA,
    categoria_sinc,
    conclusao_p2_assinc,
    erro_sinc,
    mo,
    p1_assinc,
    p1_concorda,
    p1_sinc,
    tabela_p2_assinc,
    tabela_p2_sinc,
    traco_sinc,
):
    def _texto_bmc(r):
        if r["resultado"] == "contra-exemplo":
            return "falsa" if estado_validacao(r) == "ok" else "erro de validação"
        return f"inconclusiva até K = {r['k']}"

    _constantes = sum(1 for v in categoria_sinc.values() if v != "muda")
    _val_p2_sinc = ("—" if tabela_p2_sinc.empty
                    else "ok" if (tabela_p2_sinc["validação"] != "falhou").all() else "falhou")
    _cex_p2 = tabela_p2_assinc[tabela_p2_assinc["resultado"] == "contra-exemplo"]
    _resultado_p2_assinc = {
        "falsa": "falsa",
        "provada": "provada",
        "inconclusiva até K": f"inconclusiva até K = {K_PERMANENCIA_ASSINCRONA}",
    }.get(conclusao_p2_assinc, conclusao_p2_assinc)

    resumo = pd.DataFrame([
        {"propriedade": "1 — nunca erro", "modo": "síncrono",
         "método": "simulação até ao ciclo + BMC (verificação cruzada)",
         "resultado": "provada" if erro_sinc is None else "falsa",
         "k / K": "—" if erro_sinc is None else str(erro_sinc + 1),
         "tempo (s)": round(p1_sinc["tempo"], 2),
         "validação": estado_validacao(p1_sinc) + ("" if p1_concorda else " (BMC discorda!)")},
        {"propriedade": "1 — nunca erro", "modo": "assíncrono", "método": "BMC",
         "resultado": _texto_bmc(p1_assinc), "k / K": str(p1_assinc["k"]),
         "tempo (s)": round(p1_assinc["tempo"], 2), "validação": estado_validacao(p1_assinc)},
        {"propriedade": "2 — nenhuma célula permanente", "modo": "síncrono",
         "método": "simulação até ao ciclo + BMC (amostra)",
         "resultado": "falsa" if _constantes else "provada",
         "k / K": str(len(traco_sinc)) if _constantes else "—",
         "tempo (s)": round(tabela_p2_sinc["tempo (s)"].sum(), 2) if not tabela_p2_sinc.empty else 0.0,
         "validação": _val_p2_sinc},
        {"propriedade": "2 — nenhuma célula permanente", "modo": "assíncrono",
         "método": "BMC" + ("" if AMOSTRA_P2_ASSINCRONA is None else f" (amostra de {AMOSTRA_P2_ASSINCRONA})"),
         "resultado": _resultado_p2_assinc,
         "k / K": str(_cex_p2.iloc[0]["k"]) if len(_cex_p2) else str(K_PERMANENCIA_ASSINCRONA),
         "tempo (s)": round(tabela_p2_assinc["tempo (s)"].sum(), 2),
         "validação": "ok" if conclusao_p2_assinc != "erro de validação" else "falhou"},
    ])
    mo.vstack([mo.md("### Resumo"), resumo])
    return (resumo,)


@app.cell
def _(
    categoria_sinc,
    inicio_ciclo_sinc,
    mo,
    moldura,
    p1_assinc,
    p1_sinc,
    p2_assinc_exemplo,
    periodo_sinc,
    traco_sinc,
):
    _ver = lambda g: mo.Html(apresentar_grelha(g, moldura, N).to_html())
    _blocos = [mo.md("### Contra-exemplos")]

    for _nome, _r in (("síncrono", p1_sinc), ("assíncrono", p1_assinc)):
        if _r["resultado"] == "contra-exemplo" and estado_validacao(_r) == "ok":
            _t = _r["traço"]
            _blocos += [
                mo.md(f"**Propriedade 1, modo {_nome}:** traço de {len(_t)} estados. "
                      "À esquerda o estado inicial, à direita o estado de erro."),
                mo.hstack([_ver(_t[0]), _ver(_t[-1])], justify="start"),
            ]

    _constantes_sinc = [c for c, cat in categoria_sinc.items() if cat != "muda"]
    if _constantes_sinc:
        _c = _constantes_sinc[-1]
        _blocos += [
            mo.md(f"**Propriedade 2, modo síncrono:** a célula {_c} está {categoria_sinc[_c]}. "
                  f"Cabo de {inicio_ciclo_sinc} estados e laço de {periodo_sinc}. "
                  "Estado onde o laço começa:"),
            _ver(traco_sinc[inicio_ciclo_sinc]),
        ]

    if p2_assinc_exemplo is not None:
        _c, _valor, _r = p2_assinc_exemplo
        _blocos += [
            mo.md(f"**Propriedade 2, modo assíncrono:** a célula {_c} fica sempre "
                  f"{'morta' if _valor == 0 else 'viva'}. Traço de {_r['k']} estados: cabo de "
                  f"{_r['lacete']} e laço de {_r['k'] - _r['lacete']}. Estado onde o laço começa:"),
            _ver(_r["traço"][_r["lacete"]]),
        ]

    mo.vstack(_blocos) if len(_blocos) > 1 else mo.md("_Não foram encontrados contra-exemplos._")
    return


@app.cell
def _(mo, resumo):
    _frases = "\n".join(
        f"- **Propriedade {linha['propriedade']}**, modo {linha['modo']}: {linha['resultado']} "
        f"({linha['método']}; k / K = {linha['k / K']}; {linha['tempo (s)']} s)."
        for _, linha in resumo.iterrows()
    )
    mo.md(f"### Resultados obtidos\n\n{_frases}")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 10. Conclusão

    _TODO: resumir os resultados de cada propriedade em cada modo, comparar as
    duas relações de transição, e discutir limites (tamanho da grelha,
    profundidade, tempos). Este texto deve ser gerado a partir dos resultados
    da secção 9._

    Os testes automáticos estão no notebook `test_automato_celular.py`.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Uso de ferramentas LLM

    _TODO: identificar a(s) ferramenta(s) usadas e o link da conversa._

    No código, cada função em que houve contributo de um LLM tem um comentário
    `# LLM (...) — Registo N: ...` logo a seguir à documentação.

    | Função no código | Registo | Contributo |
    | --- | --- | --- |
    | `celulas_normais` | 3 | Guia do LLM; |
    | `celulas_iniciais` | 3 | Guia do LLM; |

    ### Diferenças entre a conversa e o código final

    - **Ferramenta de verificação.** No Registo 2 o LLM recomendou o nuXmv e
      sugeriu não usar BMC. Não seguimos essa recomendação: usamos pySMT com
      Z3 e BMC, como na ficha 7, por serem as ferramentas e a técnica da
      cadeira.
    - **Funções de verificação.** A estrutura do Registo 1 tinha
      `construir_sistema` e `verificar`, pensadas para um model checker
      externo. Foram substituídas por `fabricar_fsm`, que devolve
      `(declare, init, trans)`, e pelas funções genéricas `bmc_always` e
      `bmc_eventually`, com a mesma assinatura da ficha 7.
    - **Funções acrescentadas.** `construir_fronteira` (valores fixos da
      moldura) e `extrair_traco` (leitura do traço a partir do modelo do
      solver), que não existiam na estrutura proposta.
    - **Nomes dos ficheiros.** `game_of_life_fsm.py` passou a
      `automato_celular.py`, e o apêndice foi dividido por elemento do grupo.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    # Mostra os apêndices com as conversas de cada elemento do grupo (se existirem),
    # retirando a indentação dos blocos para o markdown ser renderizado.
    _pasta = Path(__file__).resolve().parent
    _partes = []
    for _nome in ("apendice_conversas_andre.md", "apendice_conversas_nelson.md"):
        _ficheiro = _pasta / _nome
        if _ficheiro.exists() and _ficheiro.read_text(encoding="utf-8").strip():
            _texto = _ficheiro.read_text(encoding="utf-8")
            _partes.append("\n".join(_linha.removeprefix("    ") for _linha in _texto.splitlines()))
    mo.md("\n\n---\n\n".join(_partes) if _partes else "_Apêndice por preencher._")
    return


if __name__ == "__main__":
    app.run()
