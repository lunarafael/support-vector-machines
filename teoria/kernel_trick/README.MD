# Kernel Trick e SVMs Não Lineares

## Introdução
A ideia inicial das SVMs é encontrar um hiperplano linear que separe os dados em duas classes. No entanto, nem todos os conjuntos de dados podem ser divididos de maneira linear, um exemplo disso seriam os cenários onde os dados estão contidos em outros, como um círculo concêntrico

<img src="images/circulos_concentricos.jpg" alt="Exemplo de Círculos Concêntricos"/>

Para resolver esses casos, é implementado um método, conhecido por Kernel Trick, que transforma os dados para um espaço de dimensão mais alta, onde eles se tornam linearmente separáveis.

<img src="images/kernel_trick.png" alt="Exemplo de aplicação de kernel">

## Conceito de Kernel
Um kernel é uma função que calcula a similaridade entre duas entradas (vetores de características), mas o faz em um espaço dimensional mais alto sem precisar calcular explicitamente as coordenadas nesse novo espaço. Com isso, é possível operar de maneira eficiente, mesmo em dimensões muito elevadas.

Nesse contexto, o kernel funciona como um "atalho" matemático que permite calcular produtos escalares no espaço transformado, mas mantendo as operações no espaço original. Assim, garantindo os benefícios de transformar os dados para um espaço de maior dimensão, sem o custo computacional elevado de realizar a transformação direta.

Dessa forma, supondo que exista um conjunto de dados em 2D que não é linearmente separável. Com a aplicação do kernel, pode-se transformar para um espaço 3D onde há uma divisão linear (um plano) separando claramente as classes.

Ou seja, para um dado conjunto de pontos x e y, o kernel é equivalente à

<div align="center">K(x, y) = ϕ(x) ⋅ ϕ(y)</div>

onde:

- `ϕ` é a transformação dos dados para um espaço de dimensão superior.

- `⋅` representa o produto interno no espaço de características.

Mas, em vez de calcular diretamente ϕ(x), o Kernel Trick permite obter o mesmo resultado apenas utilizando a fórmula do kernel K. Economizando tempo e memória computacional, especialmente para grandes dimensões.

## Tipos de Kernels

Há vários tipos de funções de kernel, cada uma com diferentes características e adequadas para tipos distintos de dados. Dentre eles os que estão presentes na biblioteca SkLearn são:
- Linear:
    - K(x,y) = x ⋅ y , onde ...
- Polynomial: 
    - K(x,y) = (x ⋅ y + c)<sup>d</sup>
, where 
 is specified by parameter degree, 
 by coef0.

- RBF:
    - K(x,y) = exp(-(||x+y||<sup>2</sup>)) where 
 is specified by parameter gamma, must be greater than 0.

- sigmoid 
, where 
 is specified by coef0.

Kernel Linear:


https://towardsdatascience.com/the-kernel-trick-c98cdbcaeb3f

https://scikit-learn.org/stable/modules/svm.html#kernel-functions