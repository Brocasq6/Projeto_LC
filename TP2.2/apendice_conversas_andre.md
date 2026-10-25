# Apêndice — registos de orientação do projeto

Este ficheiro guarda as transcrições de apoio usadas durante a elaboração. A documentação técnica e os resultados finais estão em `cvp_reticulados.py`.

## Declaração de uso de LLMs

Ferramenta usada: **Claude**. Os registos abaixo vêm da conversa de apoio ao trabalho.


## Registo 1

### Registo de apoio — estrutura inicial

    **Prompt (Claude):**

    > (enunciado do Exercício 2)
    >
    > gera me uma estrutura de trabalho e uma ordem de funcoes, sem solucoes!

    **Resposta do LLM:**

    ---

    **Estrutura do notebook**

    0. Descrição do problema (markdown): reescrever o enunciado pelas nossas palavras (reticulado, CVP, distância euclidiana, $g_{i,j}\in[0,1]$, $0\le z_i\le\ell$, $t=G^\top u$).

    1. Imports e configuração: bibliotecas, semente aleatória e verificação dos solvers instalados (`cvxpy.installed_solvers()`).

    2. Geração da instância:
    - `gerar_base(k, m, seed)`: devolve a matriz $G$ com entradas em $[0,1]$.
    - `verificar_base(G)`: devolve True/False conforme os $k$ vetores sejam linearmente independentes.
    - `gerar_target(G, ell, seed)`: gera $u$ e devolve $t$.
    - `gerar_instancia(k, ell, seed)`: junta as três anteriores e repete a geração se a base falhar.

    3. Modelação matemática (markdown), sem código: variáveis de decisão e domínio; função objetivo; restrições; porque é que o problema é cónico e que cone aparece; o que muda quando se relaxa a integralidade.

    4. Construção do modelo: `construir_modelo(G, t, ell, inteiro, limites=None)` devolve o problema cvxpy e as variáveis; `limites` serve para o branch-and-bound.

    5. Resolução (uma das vias):
    - Via Mosek (com inteiros): `resolver_mosek(G, t, ell)` devolve $z$, a distância, o tempo e o estado.
    - Via Clarabel (sem inteiros): `resolver_relaxacao(G, t, ell, limites)`, `e_inteira(z, tol)`, `escolher_variavel(z)`, `branch_and_bound(G, t, ell)` (devolve a melhor solução, a distância, o número de nós e o tempo).

    6. Verificação da solução: `verificar_solucao(z, G, t, ell)` confirma a integralidade, os limites $[0,\ell]$ e recalcula a distância «à mão»; (opcional) `solucao_arredondada(G, t, ell)` como baseline.

    7. Experiências: `correr_experiencia(k, ell, seed)` e `correr_todas()`, que percorre $k\in\{30,40,50\}$, $m=2k$, $\ell\in\{1,5\}$ e devolve uma tabela (DataFrame).

    8. Análise e conclusões (markdown): tempos, distâncias, número de nós e gap face ao arredondamento; como o problema escala com $k$ e $\ell$.

    **Ordem de chamada**

    ```text
    gerar_instancia
      ├─ gerar_base
      ├─ verificar_base
      └─ gerar_target
    construir_modelo
    resolver_mosek  |  branch_and_bound
                         ├─ resolver_relaxacao
                         ├─ e_inteira
                         └─ escolher_variavel
    verificar_solucao
    correr_experiencia  →  correr_todas  →  análise
    ```

    Sugestão de ordem de trabalho: começar pelas secções 2 e 3 e testar com um $k$ pequeno (por exemplo 5); só depois passar para o solver e as experiências.


## Registo 2

### Registo de apoio — estrutura igual à do trabalho anterior

    **Prompt (Claude):**

    > (anexos: `horario_escolar_enunciado.py`, `horario_escolar.py`, `apendice_conversas.md`, `test_horario_escolar.py`, `relatorio.pdf`)
    >
    > tens aqui a estrutura do anterior.

    **Resposta do LLM:**

    ---

    Fica tudo igual ao Exercício 1: notebook Marimo, as funções como `@app.function` com docstring e comentário `# LLM`, um validador independente do solver, uma comparação de métodos, uma conclusão gerada a partir dos resultados, a secção sobre o uso de LLM e um notebook de testes à parte.

    **Ficheiros:** `cvp_reticulados.py` (notebook principal), `test_cvp_reticulados.py` (testes), `apendice_conversas.md` (registos das conversas), o PDF do relatório e o repositório Git.

    **`app.setup`:** imports (numpy, cvxpy, pandas, perf_counter) e as constantes `VALORES_K = [30, 40, 50]`, `VALORES_ELL = [1, 5]`, `FATOR_M = 2`, `SEMENTE`, `LIMITE_SEGUNDOS`, `TOLERANCIA`.

    **Markdown «1. Descrição do problema e abordagem»:** objetivo; regras ao estilo R1–R8 (C1: base linearmente independente; C2: $z_i$ inteiro; C3: $0\le z_i\le\ell$; C4: $g_{i,j}\in[0,1]$; C5: $t=G^\top u$; O1: minimizar a distância euclidiana); estratégia de resolução.

    **Markdown «Modelo e validação / Justificação das escolhas»:** cvxpy; Mosek ou Clarabel com branch-and-bound; verificação da independência linear; semente fixa.

    **Funções, pela ordem do notebook:**

    | # | Função | O que faz | Equivalente no Ex. 1 |
    | --- | --- | --- | --- |
    | 1 | `gerar_base(k, m, rng)` | Gera $G$ com entradas em $[0,1]$ | `ler_csv` |
    | 2 | `verificar_base(G)` | Verifica C1 e devolve um booleano | validações de `preparar_dados` |
    | 3 | `gerar_target(G, ell, rng)` | Gera $u$ e devolve $t$ | — |
    | 4 | `gerar_instancia(k, ell, semente)` | Junta 1–3, repete se a base falhar e valida as dimensões | `carregar_dados` + `preparar_dados` |
    | 5 | `criar_modelo(instancia, inteiro)` | Cria as variáveis cvxpy | `criar_modelo` |
    | 6 | `adicionar_restricoes(variaveis, instancia, limites=None)` | Restrições de C3 (e limites do B&B) | `adicionar_restricoes` |
    | 7 | `adicionar_objetivo(variaveis, instancia)` | Objetivo O1 em forma cónica | `adicionar_objetivo_buracos` |
    | 8 | `resolver(problema, solver, limite_segundos)` | Corre o solver, devolve estado e tempo | `resolver_com_salas` |
    | 8a | `branch_and_bound(instancia, ...)` | Só com Clarabel: melhor solução e nº de nós | — |
    | 8b | `escolher_variavel(z)` / `e_inteira(z, tol)` | Só com Clarabel: auxiliares do B&B | — |
    | 9 | `construir_solucao(z, instancia)` | Dicionário com $z$, $x$ e a distância | `construir_horario` |
    | 10 | `distancia(x, t)` | Distância «à mão», sem solver | `contar_buracos_horario` |
    | 11 | `validar_solucao(solucao, instancia)` | Verifica C1–C5, devolve a lista de erros | `validar_horario` |
    | 12 | `solucao_arredondada(instancia)` | Baseline: relaxação arredondada | resolução «do zero» |
    | 13 | `comparar_metodos(instancia)` | Ótimo inteiro vs baseline: estado, tempo, distância, gap, nós, erros | `comparar_metodos` |
    | 14 | `apresentar_solucao(solucao)` | Tabela pandas | `apresentar_horario` |
    | 15 | `tabela_markdown(linhas)` | Formata a comparação | `tabela_markdown` |
    | 16 | `correr_experiencias()` | Percorre a grelha $k\times\ell$ | célula da comparação |

    **Células de execução (no fim):** instância de demonstração com $k$ pequeno (equivalente ao H0); grelha de experiências (equivalente a H0 → H1); conclusão gerada com os valores da execução; uso de ferramentas LLM; apêndice.

    **Ordem de chamada**

    ```text
    gerar_instancia ─┬─ gerar_base
                     ├─ verificar_base
                     └─ gerar_target
    criar_modelo → adicionar_restricoes → adicionar_objetivo
    resolver  (ou branch_and_bound → resolver por nó)
    construir_solucao → distancia → validar_solucao
    solucao_arredondada
    comparar_metodos → tabela_markdown
    correr_experiencias → conclusão
    ```

    **Testes (`test_cvp_reticulados.py`), só os nomes:** `test_base_valida_e_independente`, `test_base_dependente_e_rejeitada`, `test_target_dimensao_e_positivo`, `test_reprodutibilidade_com_semente`, `test_c2_validador_deteta_nao_inteiro`, `test_c3_validador_deteta_fora_dos_limites`, `test_distancia_caso_conhecido`, `test_otimo_nao_pior_que_arredondado`, `test_caso_pequeno_contra_forca_bruta` (com $k$ muito pequeno, enumera todos os $z$ possíveis e compara com o solver).


## Registo 3

### Registo de apoio — `gerar_base`

    **Prompt (Claude):**

    > ok. vamos por partes. vamos desenvolver a primeira funcao, guia me, sem solucoes

    **Resposta do LLM:**

    ---

    **Função 1: `gerar_base(k, m, rng)`**

    **O que faz.** Cria a matriz $G$ com os $k$ vetores da base. Cada vetor vive em $\mathbb{R}^m$ e cada entrada é uma «probabilidade» (C4).

    **Entradas e saída**

    | Parâmetro | O que é |
    | --- | --- |
    | `k` | número de vetores (linhas) |
    | `m` | dimensão de cada vetor (colunas) |
    | `rng` | gerador aleatório do NumPy, criado fora da função |
    | devolve | um `np.ndarray` de forma `(k, m)` em que a linha `i` é $g_i$ |

    **Perguntas para pensares antes de escrever**

    1. **Que distribuição usar?** O enunciado diz que as entradas são geradas aleatoriamente em $[0,1]$. Que distribuição dá a mesma probabilidade a qualquer valor desse intervalo?
    2. **Porque é que o `rng` vem de fora?** Pensa na semente fixa e na reprodutibilidade. Lembra-te de que no TP1.1 fixaste `random_seed = 0` no CP-SAT. Se a função criasse o seu próprio gerador, o que acontecia quando `gerar_instancia` a chamasse várias vezes?
    3. **Linhas ou colunas?** Decidimos que cada $g_i$ é uma linha. Confirma que isto bate certo com $t = G^\top u$ e $x = G^\top z$: que forma tem $G^\top u$ se $G$ for $k\times m$ e $u$ tiver $k$ entradas?

    **Pistas**

    - O objeto `rng` (um `numpy.random.Generator`) tem métodos para várias distribuições. Procura na documentação do NumPy o método da distribuição que escolheste na pergunta 1.
    - Esse método aceita os limites do intervalo e um argumento para a forma do resultado. Assim não precisas de ciclos `for`: a função cabe numa linha.
    - Usa só o `rng` que recebes e nunca `np.random.qualquer_coisa` diretamente. Senão os testes de reprodutibilidade falham.

    **Como verificas**

    No fim de uma célula, ou num terminal:

    ```python
    G = gerar_base(3, 6, np.random.default_rng(0))
    G.shape, G.min(), G.max()
    ```

    Deve dar a forma `(3, 6)` e valores entre 0 e 1. Corre também a mesma linha duas vezes com a mesma semente: o resultado tem de ser igual.

    O teste correspondente é `test_gerar_base_dimensoes_e_intervalo`. Mais tarde, `test_reprodutibilidade_com_semente` também vai depender desta função.

    Quando tiveres a tua versão, cola-a aqui e eu revejo-a contigo antes de passarmos à `verificar_base`.


## Link da conversa: https://claude.ai/share/5859e7ce-c1cb-4b69-bcdc-bc465fc54d0d
