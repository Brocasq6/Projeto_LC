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


## Registo 11

### Registo de apoio — guia para `erro` e `fabricar_fsm`

    **Prompt (Claude):**

    > (código de `trans_sincrona`, `trans_assincrona` e `trans`)
    >
    > Guia me agora para as funções erros e fabricar_fsm

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu um guia passo a passo, sem código:)*

    - **Revisão:** as três relações de transição estão corretas. Falta confirmar a assíncrona contando os sucessores com o blinker e o bloco 2×2.

    - **`erro`:**
      - conjunção da negação de todas as variáveis das células normais;
      - não recebe `fronteira`, porque o enunciado define o erro só com as células normais;
      - o estado de erro não é necessariamente final: as células junto à moldura podem renascer por causa das células iniciais vivas, o que é uma observação útil para a conclusão.
    - **Verificar `erro`:** é satisfazível com um único modelo (tudo morto); com `init` é insatisfazível, para não haver «contra-exemplo» com zero passos; um estado com uma célula viva simplifica para `FALSE()`.
    - **`fabricar_fsm`:**
      - devolve `(declare, init, trans)` como clausuras que já fixam `fronteira`, `modo` e `n`, como o BMC da ficha 7 espera;
      - validar o `modo` logo no início, para o erro aparecer à criação da FSM e não a meio do BMC;
      - dar às funções interiores nomes diferentes de `init` e `trans`, para evitar recursão infinita;
      - passar sempre `n` e os restantes parâmetros às funções globais;
      - na secção 9, chamar `fabricar_fsm` dentro do ciclo sobre `MODOS`, em vez de escrever um `lambda` com a variável do ciclo.
    - **Verificar `fabricar_fsm`:** as fórmulas coincidem com as das funções globais nos dois modos; com n = 20 há 400 variáveis; um modo inválido lança `ValueError`; um «BMC de um passo à mão» no modo síncrono dá um único estado 1, a comparar mais tarde com `passo_concreto`.
    - **Fecho da secção 4:** ativar os testes da regra e das transições, acrescentar uma frase sobre o determinismo do modo síncrono e passar ao simulador da secção 5.


## Registo 12

### Registo de apoio — guia para `estado_inicial_concreto` e `passo_concreto`

    **Prompt (Claude):**

    > explica me a melhor forma de fazer estado_inicial_concerto e passo_concreto

    **Resposta do LLM:**

    ---

    *(O LLM deu um guia passo a passo, sem código:)*

    - **Princípio orientador:** o simulador é um oráculo independente. Pode usar a geometria (`celulas_normais`, `vizinhos`, `construir_fronteira`), mas não `valor_celula`, `init`, `proximo_valor` nem `trans_*`, e nada do pySMT. A grelha é um dicionário célula normal → 0/1, com as mesmas chaves que `declarar_estado`.
    - **`estado_inicial_concreto`:** 1 para $i, j \le 3$ e 0 nas restantes, escrito à parte de `init` para o `test_estado_inicial` comparar as duas.
    - **`passo_concreto`:**
      - uma função auxiliar (`aplicar_regra`) que aplica a regra a todas as células, reutilizável em `traco_e_valido` e registada nas «funções acrescentadas»;
      - ler o valor de cada vizinha na grelha ou, se não for normal, na fronteira;
      - escrever a regra na forma da tabela, diferente da forma compacta de `proximo_valor`, para um erro de raciocínio não se repetir nos dois lados;
      - calcular todos os valores a partir da grelha antiga, num dicionário novo;
      - no modo síncrono, devolver o resultado da regra;
      - no modo assíncrono, listar as células instáveis pela ordem de `celulas_normais(n)`, devolver uma cópia se não houver nenhuma (lacete) e, caso contrário, trocar só uma, escolhida com o `rng`;
      - o gerador é criado por quem chama, uma vez por simulação, e nunca se usa o `random` global; sem `rng` no modo assíncrono, lançar `ValueError` em vez de criar um gerador por omissão; no modo síncrono, o `rng` é ignorado;
      - lançar `ValueError` para modos inválidos e nunca alterar a grelha recebida.
    - **Verificações:**
      - padrões no interior da grelha: blinker, bloco 2×2 e célula isolada;
      - o blinker assíncrono com várias sementes tem de dar exatamente os 4 sucessores;
      - reprodutibilidade com a mesma semente;
      - a grelha de entrada não muda;
      - concordância com `trans_sincrona` em grelhas aleatórias e no estado inicial.
    - **A seguir:** simular o modo síncrono até repetir um estado, para saber se o erro é alcançado, o transiente e o período do ciclo (que orientam o `K_MAX`) e que células ficam constantes. Depois, `traco_e_valido` e `apresentar_grelha`.


## Registo 13

### Registo de apoio — revisão do simulador e guia para `traco_e_valido` e `apresentar_grelha`

    **Prompt (Claude):**

    > (código de `estado_inicial_concreto` e `passo_concreto`)
    >
    > explica me agora então como fazer traco_e_valido e apresentar_grelha

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu um guia passo a passo, sem código:)*

    - **Revisão:**
      - `estado_inicial_concreto` está correta;
      - **erro em `passo_concreto`:** no modo síncrono, `nova = grelha` não copia o dicionário. As contagens passam a ler valores já atualizados (o erro clássico do Game of Life) e a grelha recebida é alterada. Correção: ler e escrever em dicionários diferentes;
      - com `rng=None`, criar o gerador dentro da função repete sempre a mesma escolha. Deve lançar-se `ValueError`;
      - sugestão: tirar a regra para uma função própria, `aplicar_regra`, reutilizável em `traco_e_valido` e escrita na forma da tabela.
    - **`traco_e_valido`:**
      - devolve uma lista de mensagens de erro, vazia se o traço for válido, para indicar onde e porquê falha;
      - lança `ValueError` para modos inválidos e trata o traço vazio como erro;
      - normaliza os valores para 0/1, para aceitar traços do solver com `True`/`False`, e verifica as chaves e os valores de cada grelha;
      - o primeiro estado tem de ser `estado_inicial_concreto(n)`;
      - no modo síncrono, cada estado tem de ser igual à regra aplicada ao anterior;
      - no modo assíncrono, sem instáveis não há mudanças (lacete), e com instáveis muda exatamente uma, que é instável;
      - para validar um lacete, quem chama acrescenta ao fim do traço uma cópia do estado onde o lacete começa.
    - **Verificar `traco_e_valido`:** traços simulados válidos nos dois modos; uma célula trocada; troca de modo; estado inicial errado; lacete indevido; valores `True`/`False`.
    - **`apresentar_grelha`:**
      - devolve um `DataFrame` sem usar `mo`, para continuar a ser uma `@app.function`;
      - usa rótulos de 1 a $n$, ou de 0 a $n+1$ com a moldura;
      - lê o valor da grelha ou da fronteira e mostra símbolos em vez de 0/1, distinguindo a moldura;
      - a legenda vai por cima da tabela.
    - **A seguir:** a célula interativa da secção 5 e a simulação síncrona até um estado se repetir, antes do BMC.


## Registo 14

### Registo de apoio — revisão de `traco_e_valido` e `apresentar_grelha` e guia para a célula interativa

    **Prompt (Claude):**

    > (código de `traco_e_valido` e `apresentar_grelha`)

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código:)*

    - **`traco_e_valido`:** está correta, com os três casos do modo assíncrono bem encadeados e mensagens que indicam o passo, a célula e o valor. Há dois pormenores, nenhum deles bloqueante:
      - validar os valores em $\{0, 1\}$ antes de os converter com `int`, para não aceitar em silêncio valores como `0.7`;
      - juntar as células erradas de cada passo síncrono numa só mensagem, para o resultado ficar legível.
    - **`apresentar_grelha`:** está correta. A legenda deve aparecer também por cima da tabela. Se a tabela interativa do Marimo cortar a grelha em páginas, pode usar-se `mo.ui.table` com o tamanho de página igual ao número de linhas, ou `mo.Html`.
    - **Estado da secção 5:** todas as funções estão feitas. Falta testar `traco_e_valido` com o quadro do guia, fazer a célula interativa e simular o modo síncrono até um estado se repetir.

    **Prompt (Claude):**

    > Guia me então na célula interativa

    **Resposta do LLM:**

    ---

    *(O LLM explicou como construir a simulação interativa:)*

    - **`mo.md`:** mostra texto em Markdown como saída da célula. A célula com «_Simulação por implementar._» é só um marcador, e é substituída.
    - **Duas células:** no Marimo, o valor de um controlo só pode ser lido numa célula diferente daquela onde o controlo é criado.
      - **Célula 1:** cria um `mo.ui.slider` com o número de passos (até 200, para chegar ao estado fixo do modo síncrono) e um `mo.ui.dropdown` com `MODOS`, mostrados lado a lado com `mo.hstack`.
      - **Célula 2:** constrói a fronteira e um gerador `random.Random(SEMENTE)`, parte de `estado_inicial_concreto` e aplica `passo_concreto` tantas vezes quanto o valor do slider. Mostra com `mo.vstack` um texto com o passo, o modo, o número de células vivas e a legenda, seguido da tabela de `apresentar_grelha`.
    - **Reatividade:** ao mexer nos controlos, o Marimo volta a correr a célula 2 automaticamente.
    - **Nomes com `_`:** ficam locais à célula e evitam conflitos com nomes definidos noutras células.
    - **Reprodutibilidade:** a simulação recomeça sempre do início com a mesma semente, por isso o mesmo número de passos dá sempre a mesma grelha, também no modo assíncrono.

    **Prompt (Claude):**

    > Podes me dar o código da célula interativa,  não sei como fazer este tipo de funções

    **Resposta do LLM:**

    ---

    *(O LLM escreveu o código da simulação interativa, dividido em três células:)*

    - **Célula A — controlos:** a constante `PASSOS_SIMULACAO = 200` e quatro controlos: um `mo.ui.dropdown` para o modo, um `mo.ui.slider` para o passo, um `mo.ui.number` para a semente do escalonador (só no modo assíncrono) e um `mo.ui.checkbox` para mostrar a moldura.
    - **Célula B — simulação:** lê o modo e a semente, mas não o slider. Constrói a fronteira com `SEMENTE` e cria um único gerador para a simulação toda. Calcula o traço completo com `passo_concreto` e valida-o com `traco_e_valido`.
    - **Célula C — visualização:** lê o slider e mostra o estado escolhido. Por cima da tabela indica o número de células vivas, assinala o estado de erro e o estado estável, mostra a célula que mudou (no modo assíncrono), o resultado da validação e a legenda. A tabela é mostrada com `mo.Html`, para não ficar paginada.
    - **Porque são três células:** o valor de um controlo só pode ser lido numa célula diferente daquela onde é criado. Com a simulação separada da visualização, mover o slider não recalcula o traço.


## Link da conversa: (colar aqui o link da conversa com o Claude)