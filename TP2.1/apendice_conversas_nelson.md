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


## Registo 15

### Registo de apoio — guia para o BMC genérico (secção 6)

    **Prompt (Claude):**

    > Certo, guia me agora para as funções da secção 6

    **Resposta do LLM:**

    ---

    *(O LLM deu um guia passo a passo, sem código:)*

    - **Princípio:** as funções da secção 6 são genéricas. Recebem só `declare`, `init`, `trans`, a propriedade e `K`, sem nada específico do Game of Life, para poderem ser testadas primeiro com o programa da ficha 7. As duas devolvem um dicionário com as mesmas chaves: `resultado`, `k`, `traço`, `lacete` e `tempo`.
    - **`extrair_traco`:** para cada estado, um dicionário com as mesmas chaves e o valor Python de cada variável no modelo. Não converter `True` para 1, para servir também a variáveis inteiras. Chamar com o solver ainda aberto.
    - **`bmc_always`:**
      - para $k = 1..K$, procurar um traço de $k$ estados que começa num estado inicial, respeita `trans` e cujo último estado viola `inv`;
      - versão incremental, com um único solver: `init` e as transições ficam como restrições permanentes, e a negação de `inv` fica entre `push` e `pop`;
      - otimização opcional: depois de um $k$ insatisfazível, juntar `inv` desse estado como restrição permanente.
    - **`bmc_eventually`:**
      - um contra-exemplo de $F\,\mathit{prop}$ é um lacete em que `prop` nunca acontece;
      - `not prop` fica permanente em cada estado do traço;
      - o lacete fecha-se com um estado extra, uma única transição até ele e a disjunção «o estado extra é igual a algum estado anterior», escrita com `EqualsOrIff` (que tem de ser acrescentado aos imports);
      - o estado extra e o fecho ficam entre `push` e `pop`;
      - o início do lacete descobre-se comparando o estado extra com os anteriores no traço extraído.
    - **Interpretação:** o BMC refuta mas não prova. «Sem contra-exemplo até K» só vale até esse limite, e no modo síncrono a prova vem da simulação com deteção de ciclo.
    - **Testes com a ficha 7:**
      - $G\,(x \ge 0)$ sem contra-exemplo;
      - $G\,(x \ne 1)$ com contra-exemplo;
      - $F\,(pc = 2)$ sem contra-exemplo;
      - $F\,(x < 0)$ com lacete;
      - confirmar à mão os traços e verificar que o $k$ é mínimo;
      - só depois aplicar ao autómato, começando com K pequeno.

    **Prompt (Claude):**

    > (import de `EqualsOrIff` acrescentado ao `app.setup` e código de `extrair_traco` e `bmc_always`)
    >
    > explica me melhor bmc_eventually

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e explicou com mais detalhe a lógica de `bmc_eventually`, sem código:)*

    - **Revisão:**
      - o import e `extrair_traco` estão corretos;
      - `bmc_always` segue a versão incremental: `init` e as transições são permanentes, a negação de `inv` fica entre `push` e `pop`, a otimização está justificada no comentário e o resultado tem as mesmas chaves que `bmc_eventually` vai usar.
    - **Porquê um lacete:** um traço finito nunca refuta $F\,\mathit{prop}$, porque `prop` pode acontecer mais tarde. Como o espaço de estados é finito, uma execução infinita repete um estado, e o contra-exemplo é um traço $s_0, \dots, s_{k-1}$ que volta a um $s_l$ anterior, com `prop` falsa em todos os estados.
    - **Diferenças em relação a `bmc_always`:** `not prop` é permanente em cada estado do traço, e não só no último. O que fica entre `push` e `pop` é o fecho do lacete.
    - **Fecho do lacete:** um estado extra $s_k$, uma única transição `trans(s_{k-1}, s_k)` e a disjunção, para cada $l$, de «$s_k = s_l$» escrita chave a chave com `EqualsOrIff`. É muito menor do que uma disjunção de $k$ transições, e não é preciso impor `not prop` no estado extra.
    - **Índices:** o estado extra usa o índice $k$, que na iteração seguinte passa a ser um estado normal do traço. Não há problema, porque o `pop` retira as restrições sobre ele.
    - **Resultado:** o início do lacete é o primeiro $l$ cujo estado no traço extraído coincide com o estado extra. Devolve-se o traço sem o estado extra e o índice `lacete`. Para o validar, quem chama acrescenta uma cópia de `traço[lacete]` e usa `traco_e_valido`.

    **Prompt (Claude):**

    > (código de `bmc_eventually`)

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código:)*

    - **Lógica:** está correta e segue o guia. `not prop` é permanente, há um estado extra e o fecho do lacete fica entre `push` e `pop`. A deteção de $l$ por comparação de dicionários também está certa.
    - **Erro de escrita:** `solver.addec_assertion(...)` tem de ser `solver.add_assertion(...)`. Como está, a função lança `AttributeError` na primeira iteração.
    - **`next(...)` sem valor por omissão:** se nenhum estado coincidir com o extra, `next` lança `StopIteration`, uma exceção pouco clara. Deve usar-se `None` como valor por omissão e, nesse caso, lançar um erro explícito a dizer que o lacete não foi encontrado no traço.
    - **A seguir:** depois de corrigir, correr os dois testes da ficha 7 com `bmc_eventually` antes de avançar.


## Registo 16

### Registo de apoio — guia para a propriedade 1

    **Prompt (Claude):**

    > Explica me agora como devo fazer o codigo da propriedade 1

    **Resposta do LLM:**

    ---

    *(O LLM deu um guia passo a passo, sem código:)*

    - **`verificar_nunca_erro`:**
      - obter `(declare, init, trans)` com `fabricar_fsm` e definir o invariante «não `erro(s, n)`», passando o `n`;
      - chamar `bmc_always`;
      - se houver contra-exemplo, validá-lo numa chave `"validação"`: `traco_e_valido` sem erros, o último estado todo morto e nenhum estado de erro antes do fim (o que confirma que é mínimo).
    - **Modo síncrono, prova pela simulação:** o sistema é determinista e tem um único estado inicial, por isso há uma só execução, que acaba por repetir um estado. Os estados alcançáveis são os da simulação até à primeira repetição. Se nenhum for de erro, a propriedade está provada sem limite de profundidade. Se algum for, o BMC tem de encontrar esse mesmo prefixo, o que serve de validação cruzada.
    - **`simular_ate_ciclo`:**
      - função auxiliar nova, que também serve à propriedade 2;
      - guarda num dicionário cada estado já visto, convertido em `frozenset` das células vivas, com o índice onde apareceu;
      - devolve o traço, o início do ciclo e o período;
      - tem um número máximo de passos, por segurança;
      - procurar o estado de erro em todo o traço, porque a moldura pode fazer renascer células.
    - **Modo assíncrono, o BMC é a ferramenta principal:**
      - com 9 células vivas e uma mudança por passo, um contra-exemplo precisa de pelo menos 10 estados, por isso `K_MAX = 10` está no limite;
      - correr com `k_max` crescente, registar os tempos e escrever no relatório o $K$ usado e este argumento;
      - sem contra-exemplo, o resultado é inconclusivo. A k-indução teria pouca hipótese de funcionar, porque «pelo menos uma célula viva» não se preserva em geral.
    - **Organização:** `simular_ate_ciclo` na secção 5 ou 7, `verificar_nunca_erro` e o argumento da prova na secção 7, e as execuções e a tabela de resultados na secção 9.
    - **Testes:**
      - `test_contra_exemplos_sao_tracos_validos`;
      - `test_resultados_reproduziveis`, sem comparar os traços no modo assíncrono;
      - `test_outro_tamanho_de_grelha`, com $n = 18$.


## Registo 17

### Registo de apoio — guia para a propriedade 2

    **Prompt (Claude):**

    > Explica me agora como devo fazer o codigo da propriedade 2

    **Resposta do LLM:**

    ---

    *(O LLM deu um guia passo a passo, sem código:)*

    - **Interpretação:** «permanentemente morta» pode ser (a) $G\,(c = 0)$, morta durante toda a execução, ou (b) $F\,G\,(c = 0)$, morta a partir de certo momento. A leitura principal é a (a), que se verifica com $F\,(c = 1)$ e $F\,(c = 0)$ por célula, ou seja, $2N^2 = 578$ fórmulas. A (b) deve ser mencionada no relatório e respondida no modo síncrono com a simulação.
    - **Metade é trivial:** como o estado inicial é único, cada célula já cumpre uma das duas fórmulas no estado 0. Esses 289 casos marcam-se como «provada no estado inicial», sem BMC.
    - **`verificar_permanencia`:**
      - validar a célula e o valor;
      - aplicar o atalho do estado inicial;
      - nos restantes casos, chamar `bmc_eventually` com a propriedade «a célula é diferente de `valor`»;
      - validar o contra-exemplo com `traco_e_valido`, acrescentando `traço[lacete]` ao fim, e confirmar que a célula vale `valor` em todo o traço.
    - **Modo síncrono:**
      - a simulação até ao ciclo dá a resposta exata nas duas leituras. A leitura (a) olha para os valores em todo o traço, e a (b) só para os valores dentro do ciclo;
      - validação cruzada: o BMC numa célula constante, com `k_max` igual ao comprimento do traço, tem de encontrar o lacete no início do ciclo. Com um `k_max` menor não o encontra, o que ilustra o limite do BMC.
    - **Modo assíncrono:**
      - o BMC é necessário;
      - começar por medir os tempos com $K$ crescente numa célula afastada;
      - começar pelas células com mais probabilidade de ficarem constantes, porque basta uma para refutar a propriedade;
      - incluir no relatório uma nota sobre justiça: os contra-exemplos assumem um escalonador arbitrário.
    - **`verificar_todas_celulas`:**
      - uma linha por célula e por valor testado, com a célula, o valor («morta»/«viva»), o resultado, $k$, o lacete, o tempo e se a validação passou, devolvida num `DataFrame`;
      - parâmetros opcionais `celulas` (para correr só uma amostra no modo assíncrono) e «parar no primeiro contra-exemplo»;
      - além da tabela, uma conclusão global: falsa se houver algum contra-exemplo, provada se todas as linhas estiverem provadas no estado inicial, e inconclusiva até K nos restantes casos.
    - **Funções a criar:** só `verificar_permanencia` e `verificar_todas_celulas`. A análise do modo síncrono pela simulação faz-se na secção 9, a partir de `simular_ate_ciclo`.
    - **No Marimo:** pôr as execuções pesadas da secção 9 atrás de um `mo.ui.run_button`.
    - **Texto da secção 8:** a escolha da leitura, o atalho do estado inicial, o argumento do determinismo, a estratégia no modo assíncrono e a nota sobre justiça.


## Registo 18

### Registo de apoio — revisão da propriedade 2 e secção 9 (resultados)

    **Prompt (Claude):**

    > Reve
    >
    > (código de `verificar_permanencia` e `verificar_todas_celulas`)
    >
    > e guia me pra secção 9

    **Resposta do LLM:**

    ---

    *(O LLM reviu o código e deu a estrutura da secção 9, sem código:)*

    - **Revisão:**
      - `verificar_permanencia` está correta: valida os argumentos, o atalho do estado inicial usa o mesmo formato e a validação inclui a transição de regresso do lacete;
      - `verificar_todas_celulas` está correta na lógica principal, mas precisa de três ajustes:
        - um contra-exemplo com validação falhada não deve contar como «falsa», porque indica um erro no modelo;
        - tratar à parte a lista de células vazia, que dá `KeyError`;
        - os `attrs` do pandas são experimentais, por isso deve ler-se a conclusão logo a seguir à chamada, ou devolver o par (tabela, conclusão).
    - **Estrutura da secção 9,** em blocos com custos diferentes:
      - **A — moldura e simulação síncrona** (sempre):
        - mostrar a moldura e o estado inicial;
        - indicar o transiente, o período e se é ponto fixo;
        - propriedade 1 no modo síncrono, provada pelo argumento do determinismo;
        - propriedade 2 no modo síncrono, nas leituras (a) e (b), com as contagens e, se possível, uma grelha com a categoria de cada célula.
      - **B — propriedade 1 com BMC** (atrás de um botão): no modo síncrono, com `k_max` igual ao comprimento do traço, como verificação cruzada com a simulação; no modo assíncrono, com a profundidade escolhida, que é o resultado principal.
      - **C — propriedade 2, verificações cruzadas no modo síncrono** (atrás de um botão): duas ou três células constantes, com `k_max` igual ao comprimento do traço. Espera-se $k$ igual a esse comprimento, lacete no início do ciclo e validação vazia. Opcionalmente, uma delas com `k_max` menor, para mostrar o limite do BMC.
      - **D — propriedade 2 no modo assíncrono** (atrás de um botão): decidir pelos tempos medidos entre todas as células, uma amostra representativa ou parar no primeiro contra-exemplo.
      - **E — resumo e contra-exemplos:**
        - uma tabela com propriedade, modo, método, resultado, $k$ ou $K$, tempo e validação;
        - os contra-exemplos mostrados com `apresentar_grelha`, só depois de confirmada a validação.
    - **Botões:** um `mo.ui.run_button` por bloco pesado, com `mo.stop` na primeira linha da célula do cálculo.
    - **Constantes:** no `app.setup`, um $K$ para a propriedade 1 e outro para a propriedade 2 no modo assíncrono, justificados pelos tempos medidos. O ponto «Limite» da secção 2 deve ser atualizado.
    - **Ligação à secção 10:**
      - gerar a conclusão com uma f-string a partir das variáveis do bloco E;
      - deixar em texto fixo a discussão: comparação dos modos, papel da moldura, limites do BMC, justiça e leituras (a) e (b).
    - **Testes:** `test_contra_exemplos_sao_tracos_validos`, `test_resultados_reproduziveis` e `test_outro_tamanho_de_grelha`, com $K$ pequenos.

    **Prompt (Claude):**

    > (pedido do código da secção 9)

    **Resposta do LLM:**

    ---

    *(O LLM escreveu o código da secção 9 e correu-o:)*

    - **Célula 9A:** constrói a fronteira e faz a simulação síncrona até ao ciclo. Mostra a propriedade 1 no modo síncrono (provada) e a propriedade 2 nas leituras (a) e (b), com a tabela por célula.
    - **Célula 9B:** a amostra de células para o modo assíncrono (cantos, centro e junto ao quadrado inicial) e um `mo.ui.run_button`.
    - **Célula 9C,** atrás do botão com `mo.stop`:
      - a propriedade 1 com BMC nos dois modos;
      - a validação cruzada da propriedade 2 no modo síncrono numa célula constante, com `k_max` igual ao comprimento do traço;
      - a propriedade 2 no modo assíncrono na amostra;
      - a tabela-resumo.
    - **Célula 9D:** os contra-exemplos da propriedade 1 (primeiro, meio e último estado) e da propriedade 2 (início do lacete e último estado), com `apresentar_grelha`.
    - **Resultados (N = 17, `SEMENTE = 0`):**
      - propriedade 1: provada no modo síncrono pela simulação (157 estados, ponto fixo no estado 156); falsa no modo assíncrono, com contra-exemplo validado de $k = 10$;
      - propriedade 2: falsa nos dois modos. No modo síncrono, 71 células nunca mudam, e o BMC em $(17,17)$ com $K = 157$ dá lacete em 156. No modo assíncrono, as 8 células da amostra têm contra-exemplo com $k = 6$.


## Link da conversa: https://claude.ai/share/ca8de5ff-c760-4448-a412-7917826374d5
