# Apêndice — registos de orientação do projeto (Nelson)

Este ficheiro guarda as transcrições de apoio usadas durante a elaboração. A documentação técnica e os resultados finais estão em `automato_celular.py`.

## Declaração de uso de LLMs

Ferramenta usada: **Claude**. Os registos abaixo vêm da conversa de apoio ao trabalho. A numeração continua a do apêndice do André (Registos 1 a 4).


## Registo 5

### Registo de apoio — objetivo do projeto e ponto de situação

    **Prompt (Claude):**

    > Analisa este enunciado e o código anexado, explica o que é pretendido neste projeto, o ponto de situação em que se encontra e o que devo fazer em seguida
    >
    > (enunciado do Exercício 1 do Trabalho Prático 2, enviado com `automato_celular.py`, `test_automato_celular.py` e os apêndices)

    **Resposta do LLM:**

    ---

    *(O LLM resumiu o objetivo do projeto e o estado do código:)*

    - **Objetivo:** modelar uma variante finita do Game of Life como FSM, com estado formado pelas $N^2$ células normais, moldura constante e duas relações de transição (síncrona e assíncrona) escolhidas por `MODO_TRANSICAO`. Depois, provar ou refutar $G\,\neg\mathit{erro}$ e a não permanência de cada célula, com BMC em pySMT/Z3, como na ficha 7.
    - **Feito:** estrutura do notebook, texto das secções 1 a 8 e as funções `celulas_normais`, `celulas_iniciais` e `celulas_finais`, corretas nas contagens e nos cantos.
    - **Em falta:** a função `vizinhos`, todas as restantes funções, os comentários `# LLM (Claude) — Registo N`, este apêndice e os testes.
    - **Ordem sugerida:** `vizinhos` e a fronteira, depois o simulador, o modelo simbólico, o BMC genérico (testado com a ficha 7) e, por fim, as propriedades e os resultados.


## Registo 6

### Registo de apoio — regras do Game of Life e lógica das funções

    **Prompt (Claude):**

    > Explica bem as  regras do Game of Life e quero que me indiques a logica que devo utilizar nas funções sem me dizeres o codigo, começando pela vizinhos

    **Resposta do LLM:**

    ---

    *(O LLM explicou as regras e a lógica das funções, sem código:)*

    - **Regras:** vizinhança de Moore (8 células, a própria célula não conta) e regra B3/S23. Na forma compacta, uma célula fica viva se tiver 3 vizinhos vivos, ou se estiver viva e tiver 2.
    - **Variante do exercício:** a moldura conta para os vizinhos mas não aplica a regra. No modo síncrono, todas as células leem o mesmo estado antigo. No modo assíncrono, muda uma única célula que possa mudar.
    - **`vizinhos`:** aceitar só células normais (`ValueError` nas outras), combinar os deslocamentos $-1, 0, +1$ com `product` e excluir a própria célula. Valores esperados para os testes em $(5,5)$, $(1,1)$, $(1,n)$ e $(n,n)$.
    - **`sortear_iniciais`:** gerador próprio `random.Random(semente)`, percurso pela ordem de `celulas_iniciais(n)` e um bit equiprovável guardado como inteiro 0/1.


## Registo 7

### Registo de apoio — guia para `sortear_iniciais` e `construir_fronteira`

    **Prompt (Claude):**

    > dá me agora um guia de como fazer as funções sortear_iniciais e construir_fronteira

    **Resposta do LLM:**

    ---

    *(O LLM deu um guia passo a passo, sem código:)*

    - **`sortear_iniciais`:** criar um gerador local com `random.Random(semente)` em vez do `random` global, para o sorteio não depender da ordem de execução das células. Percorrer `celulas_iniciais(n)` pela ordem da lista e nunca um `set`. Sortear cada célula com probabilidade 1/2 e converter o resultado para `int`.
    - **`construir_fronteira`:** partir de `sortear_iniciais(n, semente)`, usando os parâmetros recebidos e não `N` nem `SEMENTE`. Acrescentar cada célula de `celulas_finais(n)` com valor 0, de preferência num dicionário novo.
    - **Verificações:**
      - $2n+1$ chaves no sorteio e $4n+4$ na fronteira;
      - reprodutibilidade com a mesma semente, mesmo depois de usar o `random` global;
      - nenhuma interseção com as células normais;
      - cantos $(0, n+1)$ e $(n+1, 0)$ com valor 0;
      - união com as normais igual à grelha $(n+2)^2$.
    - **A seguir:** ver a moldura sorteada junto ao bloco 3×3, ativar os testes da secção 3 e passar ao simulador (`estado_inicial_concreto` e `passo_concreto`).


## Registo 8

### Registo de apoio — revisão da geometria e guia para `declarar_estado` e `valor_celula`

    **Prompt (Claude):**

    > (código de `sortear_iniciais` e `construir_fronteira`)
    >
    > Verifica se está tudo feito que é necessário para a geometria de grelha, se sim avancemos para as funções declarar_estado e valor_celula
    > Indica a logica que devo utilizar

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu um guia passo a passo, sem código:)*

    - **Revisão:** `sortear_iniciais` e `construir_fronteira` estão corretas. O código da geometria está completo. Faltam apenas tarefas que não bloqueiam o resto: ativar os testes da secção 3, os comentários de registo LLM e uma frase sobre o gerador local e sobre `vizinhos`.
    - **Papel das funções:** um traço de $k$ estados usa $k$ cópias das variáveis, uma por instante. `declarar_estado(k)` cria a cópia $k$. `valor_celula` esconde a diferença entre células normais, que são variáveis, e células da moldura, que são constantes.
    - **`declarar_estado`:** uma variável `BOOL` por célula normal, para o domínio ficar correto sem restrições $0 \le c \le 1$. O nome inclui $i$, $j$ e $k$ com separadores, para evitar colisões silenciosas como $(1, 11)$ e $(11, 1)$. Verificar com $n \ge 11$.
    - **`valor_celula`:**
      - devolver a variável se a célula for normal;
      - devolver `TRUE()` ou `FALSE()` se for da moldura;
      - lançar exceção se não for nenhuma das duas;
      - devolver sempre uma fórmula booleana, deixando a conversão para número a `proximo_valor`.
    - **Simulador independente:** o simulador não deve usar `valor_celula`, para que o teste de concordância consiga detetar erros no modelo simbólico.
    - **Verificações:** casos normal, final, inicial viva e morta, e fora da grelha. Teste de integração com `vizinhos` para todas as células normais.
    - **Otimização opcional:** somar as vizinhas da moldura como números Python em `proximo_valor`.
    - **A seguir:** `init` e `proximo_valor`.


## Registo 9

### Registo de apoio — revisão do estado simbólico e guia para `init` e `proximo_valor`

    **Prompt (Claude):**

    > (código de `declarar_estado` e `valor_celula`)
    >
    > Guia me agora para fazer as funções inits e proximo_valor

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu um guia passo a passo, sem código:)*

    - **Revisão:** `declarar_estado` e `valor_celula` estão corretas. Os nomes têm os três índices com separadores e o tipo é `BOOL`. Os três casos estão tratados e o resultado é sempre uma fórmula booleana.
    - **`init`:**
      - o estado inicial é o quadrado $(1..3)\times(1..3)$ vivo, porque «$i, j \le 3$» exige as duas condições;
      - é preciso fixar todas as $n^2$ células normais, com a variável ou a sua negação, e juntar tudo com `And`;
      - se se fixarem só as 9 vivas, `init` descreve $2^{280}$ estados em vez de um;
      - a moldura não precisa de restrições, e o parâmetro `fronteira` fica só para manter as assinaturas uniformes.
    - **Verificar `init`:** a fórmula tem de ser satisfazível e ter uma só solução. Para o confirmar, juntar a condição «alguma célula difere do modelo encontrado», que tem de dar insatisfazível.
    - **`proximo_valor`:**
      - devolve, só com as variáveis de `s`, o valor seguinte da célula; a ligação ao estado seguinte `p` é feita pelas funções de transição;
      - obter as vizinhas com `vizinhos`, que também valida a célula;
      - somar as vizinhas da moldura num inteiro Python (a «base») e converter cada vizinha normal com `Ite(…, Int(1), Int(0))`;
      - a contagem é o `Plus` destes termos com a base;
      - por fim, aplicar a regra B3/S23 a essa contagem.


## Registo 10

### Registo de apoio — revisão de `init` e `proximo_valor` e guia para as relações de transição

    **Prompt (Claude):**

    > (código de `init` e `proximo_valor`)
    >
    > Segue a logica de trans_sincrona, trans_assincrona e trans da forma que tinhas mencionado

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu um guia passo a passo, sem código:)*

    - **Revisão:** `init` fixa todas as células normais e `proximo_valor` separa as vizinhas constantes das variáveis, com a regra na forma compacta. Único reparo: indicar na docstring de `init` que `fronteira` só existe para uniformizar as assinaturas.
    - **Ideia comum:** o valor da regra calcula-se sempre a partir de `s`, nunca de `p`. Sugestão de eficiência: calcular `proximo_valor` uma vez por célula e guardar num dicionário.
    - **`trans_sincrona`:** conjunção, para cada célula, de `Iff(p[c], proximo_valor(s, c))`. É determinista, por isso o modo síncrono tem uma única execução. Verificar com um blinker e com a unicidade do sucessor.
    - **`trans_assincrona`:**
      - para cada célula, definir `pode_mudar` (a regra dá um valor diferente do atual) e `mudou` (`p` difere de `s`), ambas como negação de um `Iff`;
      - impor que uma célula só muda se podia mudar;
      - impor que o número de células que mudam (soma de `Ite`) é 1 se alguma pode mudar e 0 caso contrário. Esta formulação tem tamanho linear, em vez de uma disjunção com $n^4$ equivalências, e o estado estável dá o lacete.
      - a interpretação escolhida evita que a propriedade 2 tenha contra-exemplos triviais por o sistema ficar parado.
      - verificar contando os sucessores com o solver, que devem ser tantos quantas as células que podem mudar, e testar um estado estável.
    - **`trans`:** escolher a função pelo `modo`, passar o `n` recebido e lançar `ValueError` (com `MODOS`) para valores inválidos. Verificar comparando as fórmulas devolvidas.
    - **A seguir:** `erro` e `fabricar_fsm`, e depois o simulador da secção 5.


## Link da conversa: (colar aqui o link da conversa com o Claude)