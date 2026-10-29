# Apêndice — registos de orientação do projeto

Este ficheiro guarda as transcrições de apoio usadas durante a elaboração. A documentação técnica e os resultados finais estão em `automato_celular.py`.

## Declaração de uso de LLMs

Ferramenta usada: **Claude**. Os registos abaixo vêm da conversa de apoio ao trabalho.


## Registo 1

### Registo de apoio — estrutura do projeto

    **Prompt (Claude):**

    > (enunciado do Exercício 1 do Trabalho Prático 2: Game of Life como FSM, com as duas interpretações das transições e as duas propriedades)
    >
    > gera me uma estrutura para este projeto, tendo em conta este meu trabalho pratico desenvolvido no ambito da mesma cadeira, sem solucoes. é para marimo

    **Resposta do LLM:**

    ---

    *(O LLM gerou o ficheiro `game_of_life_fsm.py` com a estrutura do notebook e as funções por implementar. Depois de ajustado, explicou:)*

    Tirei do `game_of_life_fsm.py` tudo o que era BMC feito à mão: o parâmetro `K_MAX`, a função `gerar_traco` (que desenrolava k estados) e as referências a profundidade e critério de paragem. O notebook continua a correr do início ao fim.

    Agora a verificação divide-se assim:

    - `construir_sistema` junta as variáveis de estado, o `init` e a `trans` no formato de sistema de transição que a ferramenta recebe.
    - `verificar` entrega o sistema e a propriedade ao model checker da própria ferramenta e devolve o resultado, o contra-exemplo e o tempo.
    - `verificar_nunca_erro` e `verificar_permanencia` só escrevem cada propriedade e chamam `verificar`.

    Na secção 2 há um ponto novo, Verificação, para justificares que motor da ferramenta usas e o que ele garante. O simulador e o `traco_e_valido` ficaram, para confirmares de forma independente os contra-exemplos que o model checker devolver.

    Que ferramenta vão usar? Assim que me disseres, ajusto as dependências e os nomes ao que ela espera.


## Registo 2

### Registo de apoio — escolha da ferramenta

    **Prompt (Claude):**

    > que ferramenta recomendas?

    **Resposta do LLM:**

    ---

    Recomendo o nuXmv. Escreves o modelo em linguagem SMV a partir do Python, no próprio notebook, e corres o nuXmv por `subprocess`.

    Porque é que encaixa neste exercício:

    - É um model checker completo. Defines a máquina de estados e a ferramenta faz a verificação toda, sem BMC feito à mão. Para sistemas finitos tem algoritmos IC3, interpolação e K-liveness, que dão provas completas e não apenas até uma profundidade.
    - As duas relações de transição escrevem-se diretamente em SMV. A síncrona e a assíncrona são ambas naturais, e o parâmetro `MODO_TRANSICAO` só decide qual delas é gerada.
    - Verifica tanto invariantes como propriedades temporais. A propriedade 2 («nenhuma célula permanentemente morta ou viva») não é um simples invariante. Uma ferramenta que só prova invariantes obrigar-te-ia a codificações extra para essa propriedade.
    - Devolve contra-exemplos como traços. Podes confirmá-los com o simulador do esqueleto (`traco_e_valido`).

    Cuidados a ter:

    - Licença. O nuXmv não é open source, mas é gratuito para uso académico e não comercial.
    - Instalação. Tens de descarregar o binário à parte, porque não vem pelo pip. Isso tem de ficar escrito no README, já que o `uvx marimo --sandbox` não o instala.
    - PyNuSMV. É a ligação Python ao NuSMV, mas está parada: a última versão é de 2017, para Python 3.5/3.6. Por isso recomendo gerar o `.smv` e chamar o binário.
    - Tamanho do estado. Com N = 17 tens 289 variáveis de estado. Os motores baseados em BDD podem não aguentar, e é por isso que deves usar os motores IC3/SAT.

    Alternativas:

    - Z3 com o motor Spacer. Instala-se pelo pip (`z3-solver`) e prova invariantes de forma completa. Mas só trata propriedades de segurança, por isso a propriedade 2 dava muito mais trabalho.
    - pySMT. Não tem model checker incorporado, logo obrigava-te precisamente a implementar o BMC à mão.

    Antes de decidires, confirma com o docente se ferramentas externas à cadeira são aceites, porque no TP1.1 havia uma sugestão oficial (o CP-SAT). Se escolheres o nuXmv, adapto o esqueleto: as dependências, o README com a instalação e as funções `construir_sistema` e `verificar` com a assinatura de gerar o `.smv` e ler o resultado, sem as implementar.

    Fontes:

    - [nuXmv — licença](https://nuxmv.fbk.eu/license.html)
    - [nuXmv — funcionalidades](https://nuxmv.fbk.eu/features.html)
    - [nuXmv — download](https://nuxmv.fbk.eu/download.html)
    - [PyNuSMV no PyPI](https://pypi.org/project/pynusmv/1.0rc3/)


## Registo 3

### Registo de apoio — guia para `celulas_normais` e `celulas_iniciais`

    **Prompt (Claude):**

    > guia me agora no desenvolvimento das duas primeiras funcoe, sem solucoes

    **Resposta do LLM:**

    ---

    Definindo o formato das saídas e cuidados.

    As duas primeiras funções são `celulas_normais` e `celulas_iniciais`. São simples, mas tudo o resto (vizinhos, estados, transições, propriedades) é construído a partir delas, por isso vale a pena acertar já três decisões.

    **Decisões comuns às duas**

    - Representação de cada célula. O esqueleto usa o par `(i, j)`. Mantém essa convenção em todo o notebook, porque os estados vão ser dicionários indexados por estes pares.
    - Lista ou conjunto. Um conjunto facilita testes de pertença. Uma lista tem ordem fixa, e a ordem importa. Quando, mais à frente, `sortear_iniciais` percorrer as células e sortear um valor para cada uma, a ordem de percurso decide que valor calha a que célula. Com uma ordem fixa, a mesma `SEMENTE` dá sempre a mesma fronteira, o que precisas para resultados reproduzíveis. Escolhe e justifica numa frase na secção 3.
    - Parâmetro `n`. Usa sempre o `n` recebido e nunca a constante `N` dentro da função. É isso que permite o teste com outro tamanho de grelha.

    **`celulas_normais(n)`**

    O que deve devolver: todas as células com os dois índices entre 1 e `n`, inclusive.

    Pontos de atenção:

    - Os índices do enunciado começam em 1, não em 0. Confirma os limites dos `range` do Python, que excluem o valor final.
    - No `app.setup` tens `itertools.product` importado. Vê se te serve aqui.

    Como verificar:

    - Com `n = 3`, deves obter 9 células, sem nenhuma com índice 0 nem 4.
    - Para um `n` qualquer, o total tem de ser `n²`.

    **`celulas_iniciais(n)`**

    O que deve devolver: as células em que pelo menos um índice é 0.

    Antes de programar, falta decidir até onde vai o outro índice. O enunciado não o diz diretamente, mas dá duas contagens que, juntas, o determinam: $2N+1$ células iniciais e $2N+3$ finais.

    Sugiro este exercício:

    1. Desenha a moldura completa para `n = 2`, com os índices de 0 a 3 nos dois eixos.
    2. Marca as células normais.
    3. Na moldura sobram três cantos ambíguos: `(0, 0)`, `(0, n+1)` e `(n+1, 0)`. Decide a que conjunto pertence cada um, de forma a que as contagens de iniciais e de finais batam certo ao mesmo tempo.
    4. Confirma que nenhuma célula da moldura fica sem conjunto.

    Armadilha: se construíres o resultado juntando a «linha» com `i = 0` e a «coluna» com `j = 0`, há uma célula que aparece nas duas. Comparar o tamanho da lista com o tamanho de `set(lista)` deteta isso.

    Como verificar:

    - A contagem tem de ser `2n + 1` para vários valores de `n`.
    - Não pode haver repetidos.
    - Nenhuma célula inicial pode ser também normal.

    Esta última verificação e a da contagem correspondem ao `test_numero_de_celulas` e ao `test_conjuntos_disjuntos` do notebook de testes. Quando as duas funções estiverem feitas, já podes trocar o `skipTest` dessas partes pelas verificações.

    Como no TP1.1, acrescenta a cada função o comentário `# LLM (Claude) — Registo N: ...` e copia esta conversa para o `apendice_conversas.md`.

    Quando tiveres as duas funções feitas, envia-mas e eu reviso antes de passarmos a `celulas_finais` e `vizinhos`.


## Registo 4

### Registo de apoio — guia para `celulas_finais` e `vizinhos`

    **Prompt (Claude):**

    > otimo. vamos prosseguir com as proximas duas funcoes

    **Resposta do LLM:**

    ---

    Checando a união dos três conjuntos de células

    As duas funções seguintes são `celulas_finais` e `vizinhos`. A primeira fecha a moldura da grelha; a segunda define quem conta para a regra B3/S23 de cada célula.

    **`celulas_finais(n)`**

    O que deve devolver: as células com um índice igual a `n+1` que não sejam iniciais.

    O «não sejam iniciais» do enunciado é a pista principal. A forma mais direta de cumprir essa condição é reaproveitar `celulas_iniciais`, em vez de repetir à mão a decisão sobre os cantos. Assim, se um dia mudares a decisão numa função, a outra acompanha.

    Pontos de atenção:

    - Cantos. A decisão que tomaste sobre `(0, n+1)`, `(n+1, 0)` e `(n+1, n+1)` tem de dar exatamente $2n+3$ células finais.
    - Repetidos. A mesma armadilha da função anterior: a linha `i = n+1` e a coluna `j = n+1` partilham uma célula.
    - Ordem. Usa a mesma convenção de lista ou conjunto que escolheste para as outras duas funções.

    Como verificar: as três funções juntas têm de cobrir a moldura inteira, de 0 a `n+1` nos dois eixos, sem sobreposições. As contagens batem certo, porque $n^2+(2n+1)+(2n+3)=(n+2)^2$. Por isso, confirma:

    - que a união dos três conjuntos é exatamente o quadrado de `(n+2)×(n+2)` posições;
    - que nenhum par de conjuntos se interseta.

    Esta é a melhor prova de que os cantos ficaram bem decididos, e é praticamente o `test_conjuntos_disjuntos`.

    **`vizinhos(i, j, n)`**

    O que deve devolver: as células à distância 1 de `(i, j)` segundo o enunciado, $\max(|i_0-i_1|, |j_0-j_1|)=1$.

    Antes de programar, decide duas coisas:

    1. A célula conta como vizinha de si própria? Aplica a fórmula a `(i, j)` com ela mesma e vê o que dá.
    2. Para que células é chamada a função? Só as células normais mudam de estado, por isso só elas precisam dos vizinhos. Repara que, se `(i, j)` for normal, todos os vizinhos caem dentro da moldura de 0 a `n+1`: nunca saem da grelha. Se a função for chamada para uma célula da moldura, isso já não é verdade. Escolhe entre:
       - aceitar só células normais e lançar `ValueError` para as outras;
       - aceitar qualquer célula e filtrar as posições que não existem.

       Escolhe uma e justifica-a numa frase.

    Implementação: há duas formas razoáveis.

    - Gerar os deslocamentos possíveis à volta de `(i, j)`.
    - Percorrer as posições candidatas e ficar com as que cumprem a condição do enunciado.

    A segunda segue a definição à letra, o que dá jeito para a justificação no relatório. A primeira é mais curta. Qualquer uma serve.

    Eficiência (opcional): `vizinhos` vai ser chamada para cada célula sempre que construíres uma transição. Com N = 17 não faz diferença. Se mais à frente quiseres testar grelhas maiores, podes calcular os vizinhos uma vez e guardá-los num dicionário.

    Como verificar: é o `test_vizinhanca`.

    - Célula interior, por exemplo `(5, 5)`: deve ter o número de vizinhos que esperas, todos normais.
    - Canto `(1, 1)`: deve ter o mesmo número de vizinhos. Alguns serão iniciais; confirma quais.
    - Canto `(1, n)`: é o caso mais revelador, porque os vizinhos misturam células normais, iniciais e finais. Se a decisão sobre `(0, n+1)` estiver errada, é aqui que se nota.
    - Canto `(n, n)`: os vizinhos fora da grelha normal devem ser todos finais.

    Uma nota para mais à frente: `vizinhos` devolve só posições. Saber se cada vizinha está viva (variável do solver nas normais, constante nas iniciais e finais) é trabalho de `valor_celula`. Mantém essa separação: assim, `vizinhos` serve tanto para o modelo pySMT como para o simulador concreto.

    Quando tiveres estas duas funções, podes trocar o `skipTest` de `test_numero_de_celulas`, `test_conjuntos_disjuntos` e `test_vizinhanca` pelas verificações. A seguir vem `sortear_iniciais`, que fecha a secção 3.


## Link da conversa: (colar aqui o link da conversa com o Claude)
