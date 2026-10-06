# Apêndice — registos de orientação do projeto

Este ficheiro guarda as transcrições de apoio usadas durante a elaboração. A documentação técnica e os resultados finais estão em `horario_escolar.py`.


## Registo 1

## Declaração de uso de LLMs

    **Prompt (ChatGPT):**

    > Explica-me os passos que precisamos para chegar ao produto final, e explica o que cada função que vai ser desenvolvida tem de fazer.

    **Resposta do LLM:**

    ---

    ### 1. Carregar os dados

    Já têm `ler_csv`. Essa função abre um CSV, verifica se contém as colunas necessárias e devolve as linhas como uma lista de dicionários.

    A seguir, uma função de carregamento pode reunir os quatro ficheiros:

    ```python
    def carregar_dados(pasta):
        ...
    ```

    Deve ler `turmas.csv`, `disciplinas.csv`, `salas.csv` e `disponibilidade_excecoes.csv` da pasta indicada e devolver os dados agrupados. Assim, a mesma função pode carregar tanto `dados/` como `dados_v2/`.

    ### 2. Limpar e validar os dados

    Os valores lidos de um CSV são texto. Por isso, será preciso preparar os dados para os cálculos e detetar erros antes de tentar gerar um horário.

    ```python
    def preparar_dados(dados):
        ...
    ```

    Esta função pode converter `carga_semanal`, `quantidade` e `periodo` em números; converter `sim`/`nao` em valores booleanos; e verificar, por exemplo, se os dias e períodos são válidos e se as salas especiais pedidas existem.

    ### 3. Definir os tempos possíveis

    O trabalho usa cinco dias e cinco períodos por dia. Uma pequena função pode representar cada tempo como um par `(dia, período)`:

    ```python
    def criar_tempos():
        ...
    ```

    A função devolve todas as combinações possíveis, por exemplo, `("Seg", 1)`, `("Seg", 2)` … até `("Sex", 5)`. Ter essa lista facilita criar as opções de horário para cada aula.

    ### 4. Criar o modelo do horário

    Com os dados preparados, o programa precisa de criar uma variável de decisão para cada combinação relevante de turma, disciplina e tempo. Essa variável representa uma pergunta: «Esta aula fica neste período?»

    ```python
    def criar_modelo(dados):
        ...
    ```

    Esta função cria o modelo CP-SAT, as variáveis de decisão e as restrições obrigatórias. A separação exata depende da forma como decidirem representar as aulas. O importante é que o modelo consiga expressar as regras do enunciado.

    ### 5. Acrescentar as restrições

    Para manter o código compreensível, podem criar funções que acrescentam grupos de regras ao modelo:

    ```python
    def adicionar_restricoes_turmas(modelo, x, dados):
        ...
    ```

    Impede que uma turma tenha duas aulas ao mesmo tempo e garante que cada disciplina cumpre a sua carga semanal.

    ```python
    def adicionar_restricoes_professores(modelo, x, dados):
        ...
    ```

    Impede conflitos entre aulas do mesmo professor e bloqueia os períodos em que esse professor está indisponível.

    ```python
    def adicionar_restricoes_salas(modelo, x, dados):
        ...
    ```

    Garante que cada aula usa uma sala compatível e que não são usadas mais salas do mesmo tipo do que as disponíveis.

    ```python
    def adicionar_restricoes_diarias(modelo, x, dados):
        ...
    ```

    Limita a uma ocorrência diária cada disciplina por turma e trata as disciplinas de duplo período como blocos de dois tempos consecutivos no mesmo dia.

    Estas funções devem traduzir os requisitos do enunciado para o modelo. A forma concreta dependerá das variáveis que escolherem; por exemplo, representar cada aula individualmente ou representar blocos duplos como uma opção própria.

    ### 6. Otimizar e resolver

    Depois das restrições, acrescentam o objetivo de reduzir os «buracos» dos professores — tempos livres entre a primeira e a última aula num dia.

    ```python
    def adicionar_objetivo_buracos(modelo, x, dados, tempos):
        ...
    ```

    Depois, uma função executa o solver:

    ```python
    def resolver_modelo(modelo, limite_segundos=None):
        ...
    ```

    Deve correr o CP-SAT, respeitar um eventual limite de tempo e devolver o estado da resolução e os valores das variáveis. O estado é importante: pode haver solução ótima, solução válida ainda não provada ótima, ou nenhuma solução encontrada.

    ### 7. Transformar a solução num horário legível

    Os valores das variáveis do solver não são ainda uma apresentação amigável. Uma função pode convertê-los numa lista organizada de aulas:

    ```python
    def extrair_horario(solver, x, dados):
        ...
    ```

    Cada aula deve indicar pelo menos a turma, disciplina, professor, dia, período e sala. Depois, outra função pode mostrar o resultado numa tabela:

    ```python
    def apresentar_horario(horario):
        ...
    ```

    No Marimo, podem apresentar uma tabela por turma ou organizar os dias e períodos em grelhas.

    ### 8. Verificar o horário

    Mesmo que o solver use as restrições, o trabalho pede verificações automáticas para confirmar que o horário final respeita as regras.

    ```python
    def validar_horario(horario, dados):
        ...
    ```

    Deve percorrer o horário produzido e verificar cargas semanais, conflitos de turma e professor, disponibilidade, salas e blocos duplos. Pode devolver uma lista de erros; se estiver tudo correto, a lista fica vazia.

    ### 9. Atualizar o horário quando os dados mudam

    Para a parte incremental, será precisa uma função que compare dois horários:

    ```python
    def contar_alteracoes(horario_antigo, horario_novo):
        ...
    ```

    Deve contar quantas aulas mudaram de período ou sala entre H0 e H1. Para comparar corretamente, cada ocorrência de aula precisa de ter uma identificação estável — por exemplo, turma, disciplina e número da ocorrência naquela semana.

    A função de atualização incremental pode receber o horário anterior e os novos dados:

    ```python
    def atualizar_horario(horario_antigo, dados_novos):
        ...
    ```

    Deve gerar um novo horário que respeite os dados novos e, ao mesmo tempo, tente preservar as aulas que ainda podem ficar nos mesmos tempos e salas. Depois, comparem o resultado com uma resolução dos mesmos dados começada do zero. Registem o tempo e o número de alterações para apresentar a evidência pedida no enunciado.


## Registo 2

### Registo de apoio — `preparar_dados`

    **Prompt**

    > Vamos prosseguir. Dá-me as bases para a construção da função `preparar_dados`.

    **Resposta**

    A função `preparar_dados` será a etapa entre **ler os CSV** e **construir o
    modelo do horário**. `ler_csv` devolve valores como texto;
    `preparar_dados` converte-os para os tipos adequados e deteta dados
    inválidos. Ainda não cria o horário.

    Como `carregar_dados` devolve quatro valores, a nova função pode recebê-los assim:
    ```python
    def preparar_dados(turmas, disciplinas, salas, excecoes):
        ...
    ```


## Registo 3

### Registo de apoio — `criar_tempos`

    **Prompt**

    > Muito bem. Vamos prosseguir para a próxima função do plano elaborado para
    > resolver este TP1.1.

    **Resposta**

    A próxima função do plano é `criar_tempos()`. Ela prepara a lista de todos
    os tempos possíveis da semana, que depois o modelo usará para decidir onde
    colocar cada aula.
    O trabalho define **cinco dias e cinco períodos por dia**. A função deve
    devolver 25 pares `(dia, período)`, desde `("Seg", 1)` até `("Sex", 5)`.

    Para construir a lista, percorremos os dias por uma ordem fixa e, para cada
    dia, percorremos os períodos de 1 a 5. Assim, os tempos ficam sempre
    organizados da mesma forma.


## Registo 4

### Registo de apoio — `criar_modelo`

    **Prompt**

    > Ok, vamos então à próxima.

    **Resposta**

    A próxima função do plano é `criar_modelo`. Antes de a escrevermos,
    precisamos de decidir o que representa uma variável de decisão no modelo
    CP-SAT.

    Uma opção que trata naturalmente as aulas duplas é criar uma variável booleana para cada **possível colocação de uma aula**:

    - `False` significa que a aula não começa nesse dia e período.
    - `True` significa que começa aí.
    - Para uma aula simples, qualquer período pode ser início.
    - Para uma aula dupla, só os períodos 1 a 4 podem ser início, porque tem de haver um período seguinte.

    Por exemplo, uma variável para Matemática da turma 7.º A, à terça-feira no
    período 2, representa essa colocação. Pode chamar-se
    `x_7A_Matematica_Ter_2`.

    A função terá este papel:
    ```python
    def criar_modelo(dados, tempos):
    ...
    return modelo, x
    ```

    Deve criar o modelo CP-SAT e as variáveis de decisão. As regras — como
    impedir conflitos de professores e cumprir as cargas semanais — ficam para
    as funções de restrições.

    **Aulas duplas:** uma variável ocupa dois períodos, apesar de representar
    uma única colocação. As restrições terão de considerar o período de início
    e o período seguinte.


## Registo 5

### Registo de apoio — restrições das turmas

    **Prompt**

    > Agora que finalizámos estas funções, vamos começar a tratar das
    > restrições, começando pelas restrições das turmas.

    **Resposta**

    As restrições das turmas cobrem duas regras do enunciado:

    - **R1:** uma turma não pode ter duas aulas ao mesmo tempo.
    - **R2:** cada disciplina tem de cumprir a carga semanal daquela turma.

    A regra **R3** (no máximo uma ocorrência diária da mesma disciplina por
    turma) fica na função `adicionar_restricoes_diarias`.

    ## Representação das aulas

    Cada variável booleana representa uma possível colocação de uma aula. Ela
    fica organizada em quatro níveis:

    ```text
    x[turma][disciplina][dia][período_de_início]
    ```

    Por exemplo, `x["7ºA"]["Matemática"]["Ter"][2]` representa a opção de
    Matemática do 7.º A começar à terça-feira no período 2. `True` quer dizer
    que essa colocação foi escolhida; `False`, que não foi escolhida. Uma aula
    dupla ocupa o período de início e o seguinte.

    A função para acrescentar estas regras ao modelo será:

    ```python
    def adicionar_restricoes_turmas(modelo, x, dados):
        ...
    ```

    ## Começar por R2: carga semanal

    Para cada turma e disciplina, somamos as variáveis de todas as colocações
    possíveis. Uma aula simples conta como 1 período; uma dupla conta como 2.
    Essa soma tem de ser igual à `carga_semanal`.

    ```text
    soma(colocações escolhidas × duração da aula) = carga semanal
    ```

    Por exemplo, Matemática com carga semanal 4 precisa de quatro aulas
    simples; Educação Física com carga 2 e duplo período precisa de um bloco
    duplo.


## Registo 6

### Registo de apoio — restantes restrições

    **Prompt (16:10)**

    > Ok, guia-me agora no resto das funções de restrições.

    **Resposta do ChatGPT**

    Vamos organizar as restrições por recurso. Usaremos esta convenção para `x`:

    ```text
    x[turma][disciplina][dia][período_de_início]
    ```

    Cada entrada é uma decisão do solver: a aula começa nesse período ou não.
    Para uma aula dupla, só criamos opções de início nos períodos 1 a 4; se
    começar no período 3, ocupa os períodos 3 e 4. Isso faz parte da forma de
    construir `x` e já ajuda a cumprir R4.

    Cada função de restrições recebe o mesmo modelo, `x` e os dados preparados.
    Dentro dela, `modelo.Add(...)` acrescenta condições que o horário tem de
    respeitar.

    #### Restrições das turmas

    A função `adicionar_restricoes_turmas(modelo, x, dados)` trata três regras:

    - **R2 — carga semanal:** para cada turma e disciplina, somar as aulas
      escolhidas. Aulas simples contam 1 período e duplas contam 2. A soma tem
      de ser igual à carga semanal.
    - **R3 — no máximo uma ocorrência diária:** para cada turma, disciplina e
      dia, a soma das opções escolhidas nesse dia tem de ser no máximo 1.
    - **R1 — sem conflitos na turma:** para cada turma, dia e período, somar as
      aulas que ocupam esse período. O resultado tem de ser no máximo 1. Para
      uma aula dupla, conta tanto no início como no período seguinte.

    **R4** fica garantida se `x` só tiver opções de início válidas para aulas
    duplas e essas aulas ocuparem sempre dois períodos consecutivos.

    #### Restrições dos professores

    A função `adicionar_restricoes_professores(modelo, x, dados)` trata:

    - **R5 — sem conflitos:** em cada dia e período, somar as aulas que ocupam
      esse período e pertencem ao mesmo professor. O total tem de ser no máximo
      1.
    - **R6 — disponibilidade:** se uma aula calhar num período em que o
      professor não está disponível, essa opção de `x` tem de ser proibida.
      Para uma aula dupla, verifica-se também o período seguinte.

    #### Restrições das salas

    A função `adicionar_restricoes_salas(modelo, x, dados)` trata a capacidade
    e a compatibilidade das salas:

    - Em cada dia e período, conta as aulas que precisam de cada recurso.
    - O total não pode ultrapassar a quantidade disponível em `salas.csv`.
    - Aulas sem sala especial usam a capacidade normal; aulas com uma sala
      especial só contam para essa sala, como Laboratório ou Ginásio.

    Se quiserem apresentar o nome exato da sala em cada aula, terão de decidir
    como atribuí-lo depois. Se as salas de um tipo forem equivalentes, podem
    primeiro garantir a capacidade com estas contagens.

    **R8** não é uma restrição do solver: cumpre-se carregando os dados dos
    CSV, como já fizeram.

    A ordem de implementação pode ser: carga semanal (R2), limite diário (R3),
    conflitos das turmas (R1), conflitos e disponibilidade dos professores
    (R5–R6), e capacidade das salas (R7). Antes de programarmos a primeira
    função, precisamos de ter `x` construído com essa convenção.


## Registo 7

### Registo de apoio — objetivo dos buracos

    A função deve pedir ao solver para minimizar os tempos livres **entre** a
    primeira e a última aula de cada professor em cada dia. Os períodos livres
    antes da primeira aula ou depois da última não contam como buracos.

    A lógica é:

    1. Para cada professor, dia e período, determinar se há uma aula nesse
       período. Uma aula dupla ocupa o seu período de início e o seguinte.
    2. Considerar como possível buraco cada período interior — períodos 2, 3 e
       4.
    3. Um período é buraco se o professor tiver pelo menos uma aula antes, pelo
       menos uma aula depois e estiver livre nesse período.
    4. Minimizar a soma desses buracos para todos os professores e dias.

    A função terá uma forma semelhante a:

    ```python
    def adicionar_objetivo_buracos(modelo, x, dados, tempos):
        ...
    ```

    Para representar «há aula antes», «há aula depois» e «este período é um
    buraco», provavelmente vais precisar de algumas variáveis auxiliares
    booleanas. Elas não representam aulas novas; servem apenas para o solver
    calcular o objetivo a partir de `x`.

    Depois desta função, a sequência será: executar o solver
    (`resolver_modelo`), extrair as aulas escolhidas (`extrair_horario`),
    apresentar o horário, validá-lo e, por fim, implementar a atualização
    incremental e comparar `H0` com `H1`.

    *Registo da conversa: 16:38.*


## Registo 8

### Registo de apoio — funções finais

    **Prompt (16:41)**

    > Prossegue e guia-me no resto das funções.

    **Resposta do ChatGPT**

    Claro. Depois de `adicionar_objetivo_buracos`, o trabalho passa das regras
    do modelo para **resolver, ler e avaliar a solução**. Vamos fazer uma
    função de cada vez, para poderes implementar e perceber cada etapa.

    #### 1. `resolver_modelo(modelo)`

    Cria o solver CP-SAT, pede-lhe para resolver o modelo e devolve o resultado.
    O resultado inclui um estado:

    - `OPTIMAL`: encontrou a melhor solução segundo o objetivo;
    - `FEASIBLE`: encontrou uma solução válida, mas não provou que seja a melhor;
    - `INFEASIBLE`: as restrições não permitem nenhum horário;
    - `UNKNOWN`: não conseguiu determinar uma solução.

    Só passamos à extração do horário se houver uma solução válida
    (`OPTIMAL` ou `FEASIBLE`).

    #### 2. `extrair_horario(solver, x, dados)`

    Percorre a estrutura `x`. Para cada decisão escolhida pelo solver, cria uma
    entrada legível com a turma, disciplina, professor, dia e período.

    Para uma aula dupla, a entrada tem de representar que ocupa o período inicial
    **e o seguinte**. Também será preciso decidir como atribuir o nome concreto
    da sala, caso o modelo só controle a capacidade por tipo de sala.

    #### 3. `apresentar_horario(horario)`

    Recebe a lista criada por `extrair_horario` e mostra-a de forma clara no
    Marimo. Por exemplo, uma tabela ordenada por turma, dia e período.

    #### 4. `validar_horario(horario, dados)`

    Verifica o horário gerado independentemente do solver: cargas semanais,
    conflitos, indisponibilidades, aulas duplas e salas. Idealmente, devolve
    uma lista de erros; se estiver vazia, o horário passou nas verificações
    implementadas.

    #### 5. `contar_alteracoes(horario_antigo, horario_novo)`

    Compara `H0` e `H1` e conta as aulas que mudaram de período ou sala. Para
    fazer uma comparação coerente, é preciso emparelhar ocorrências da mesma
    turma e disciplina, incluindo disciplinas com várias aulas por semana.

    #### 6. `atualizar_horario(horario_antigo, dados_novos)`

    Constrói e resolve um horário com os dados alterados, tentando manter as
    aulas de `H0` que continuam válidas. Depois, comparamos o tempo de resolução
    e as aulas alteradas com um `H1` gerado do zero.

    O próximo passo concreto é escrever `resolver_modelo`. Para orientar a
    assinatura pelo teu código, envia-me a função que cria o modelo e acrescenta
    o objetivo, ou pelo menos diz-me que valores ela devolve.

    *Registo: a resposta foi indicada como tendo demorado 53 segundos.*


## Registo 9

**Prompt (ChatGPT):**

    > Ok. Agora que está tudo feito, quais são os próximos passos para fechar o projeto?

    **Resposta do LLM:**

    Se as funções já estão implementadas, falta **integrá-las, demonstrar que cumprem o enunciado e preparar a entrega**. Sugiro esta ordem:

    1. **Montar o fluxo completo no notebook**
       - Carregar e preparar `dados/`.
       - Gerar e apresentar `H0`.
       - Carregar e preparar `dados_v2/`.
       - Gerar e apresentar `H1` aproveitando `H0`.

## Link da conversa: https://chatgpt.com/s/cx_6ac29be418648191b9d999922da25f31
