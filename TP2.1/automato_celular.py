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

__generated_with = "0.16.5"
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
    SOLVER = "z3"  # solver SMT usado pelo pySMT


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
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

def vizinhos(i, j, n=N):
    """Células vizinhas de (i, j) segundo max(|i0-i1|, |j0-j1|) = 1 
    (incluindo iniciais e finais)."""
    if not (1 <= i <= n and 1 <= j <= n):
        raise ValueError(f"({i}, {j}) não é uma célula normal")
    lista = []
    for i1 in range(i - 1, i + 2):
        for j1 in range(j - 1, j + 2):
            if max(abs(i - i1), abs(j - j1)) == 1:
                lista.append((i1, j1))
    return lista


@app.function
def sortear_iniciais(n=N, semente=SEMENTE):
    """Dicionário célula inicial -> 0/1, sorteado com probabilidade 1/2 e semente fixa."""
    raise NotImplementedError("TODO")


@app.function
def construir_fronteira(n=N, semente=SEMENTE):
    """Dicionário com o valor fixo de todas as células da moldura: iniciais sorteadas e finais a 0."""
    raise NotImplementedError("TODO")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.function
def declarar_estado(k, n=N):
    """Cria as variáveis do estado número k do traço; devolve um dicionário célula -> variável."""
    raise NotImplementedError("TODO")


@app.function
def valor_celula(s, celula, fronteira):
    """Termo/valor de uma célula no estado s: variável se for normal, constante se for inicial ou final."""
    raise NotImplementedError("TODO")


@app.function
def init(s, fronteira, n=N):
    """Fórmula que caracteriza o estado inicial."""
    raise NotImplementedError("TODO")


@app.function
def proximo_valor(s, celula, fronteira, n=N):
    """Fórmula do valor seguinte de uma célula normal segundo a regra B3/S23."""
    raise NotImplementedError("TODO")


@app.function
def trans_sincrona(s, p, fronteira, n=N):
    """Relação de transição em que todas as células normais transitam em simultâneo."""
    raise NotImplementedError("TODO")


@app.function
def trans_assincrona(s, p, fronteira, n=N):
    """Relação de transição em que uma e só uma célula normal transita de estado (lacete se nenhuma puder mudar)."""
    raise NotImplementedError("TODO")


@app.function
def trans(s, p, fronteira, modo=MODO_TRANSICAO, n=N):
    """Escolhe a relação de transição de acordo com o parâmetro `modo`."""
    raise NotImplementedError("TODO")


@app.function
def erro(s, n=N):
    """Fórmula do estado de erro: todas as células normais mortas."""
    raise NotImplementedError("TODO")


@app.function
def fabricar_fsm(fronteira, modo=MODO_TRANSICAO, n=N):
    """Devolve (declare, init, trans) só com estados como argumentos, prontos para o BMC genérico."""
    raise NotImplementedError("TODO")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 5. Simulação concreta (validação do modelo)

    Simulador em Python puro, independente do solver, com dois papéis:

    - mostrar a evolução da grelha a partir do estado inicial, em qualquer dos
      modos, para se perceber o comportamento antes de usar o BMC;
    - confirmar que cada traço ou contra-exemplo devolvido pelo solver é uma
      execução válida da FSM: o primeiro estado é o inicial, e cada par de
      estados consecutivos respeita a regra no modo escolhido. Isto valida o
      modelo simbólico de forma independente.
    """
    )
    return


@app.function
def estado_inicial_concreto(n=N):
    """Grelha inicial concreta (dicionário célula normal -> 0/1)."""
    raise NotImplementedError("TODO")


@app.function
def passo_concreto(grelha, fronteira, modo=MODO_TRANSICAO, rng=None, n=N):
    """Aplica uma transição concreta à grelha (no modo assíncrono, a célula que muda é escolhida por rng)."""
    raise NotImplementedError("TODO")


@app.function
def traco_e_valido(traco, fronteira, modo=MODO_TRANSICAO, n=N):
    """Verifica se uma sequência de grelhas é uma execução válida da FSM; devolve a lista de erros."""
    raise NotImplementedError("TODO")


@app.function
def apresentar_grelha(grelha, fronteira=None, n=N):
    """Tabela (pandas) da grelha para mostrar no Marimo, com ou sem a moldura de células iniciais/finais."""
    raise NotImplementedError("TODO")


@app.cell
def _(mo):
    # TODO: controlo interativo para percorrer a simulação (ex.: mo.ui.slider com o número de passos
    # e mo.ui.dropdown com o modo de transição) e mostrar a grelha correspondente.
    mo.md("_Simulação por implementar._")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.function
def extrair_traco(modelo, estados):
    """Converte o modelo do solver numa lista de dicionários (variável -> valor Python), um por estado."""
    raise NotImplementedError("TODO")


@app.function
def bmc_always(declare, init, trans, inv, K):
    """BMC genérico de um invariante G inv: devolve resultado, k, traço (contra-exemplo mínimo, se houver) e tempo."""
    raise NotImplementedError("TODO")


@app.function
def bmc_eventually(declare, init, trans, prop, K):
    """BMC genérico de F prop: procura um lacete onde prop nunca é verdade; devolve resultado, k, traço, início do lacete e tempo."""
    raise NotImplementedError("TODO")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.function
def verificar_nunca_erro(fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N):
    """Aplica bmc_always a G ¬erro com a FSM de fabricar_fsm; devolve o dicionário de resultado do BMC."""
    raise NotImplementedError("TODO")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
    return


@app.function
def verificar_permanencia(celula, valor, fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N):
    """Aplica bmc_eventually a F(célula ≠ valor) (0 = morta, 1 = viva); devolve o dicionário de resultado do BMC."""
    raise NotImplementedError("TODO")


@app.function
def verificar_todas_celulas(fronteira, modo=MODO_TRANSICAO, k_max=K_MAX, n=N):
    """Aplica verificar_permanencia a todas as células normais e devolve uma tabela-resumo."""
    raise NotImplementedError("TODO")


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 9. Resultados

    Execução das duas propriedades nos dois modos de transição, com a mesma
    moldura (`SEMENTE`). Cada contra-exemplo é confirmado pelo simulador antes
    de ser apresentado.
    """
    )
    return


@app.cell
def _(mo):
    # TODO: para cada modo em MODOS:
    #   - construir a fronteira com SEMENTE;
    #   - correr verificar_nunca_erro e verificar_todas_celulas;
    #   - medir os tempos;
    #   - validar os contra-exemplos com traco_e_valido;
    #   - juntar tudo numa tabela (modo, propriedade, resultado, profundidade, tempo).
    # Mostrar os contra-exemplos com apresentar_grelha.
    mo.md("_Resultados por implementar._")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## 10. Conclusão

    _TODO: resumir os resultados de cada propriedade em cada modo, comparar as
    duas relações de transição, e discutir limites (tamanho da grelha,
    profundidade, tempos). Este texto deve ser gerado a partir dos resultados
    da secção 9._

    Os testes automáticos estão no notebook `test_automato_celular.py`.
    """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
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
    """
    )
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
