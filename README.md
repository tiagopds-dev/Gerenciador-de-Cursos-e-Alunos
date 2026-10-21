# Sistema Gerenciador de Cursos e Alunos

## Descrição

Este projeto é um sistema de gerenciamento acadêmico desenvolvido para aplicar e consolidar os conceitos de Programação Orientada a Objetos (POO) em Python. 

A aplicação foi projetada para administrar o fluxo de uma instituição de ensino, controlando desde as graduações e o catálogo de disciplinas até a abertura de turmas, efetivação de matrículas, acompanhamento de notas e frequência, além da geração de relatórios de desempenho e configuração de regras de negócio.

O projeto destaca-se pela forte tipagem estática (Type Hinting), arquitetura orientada a objetos (POO) limpa, uso rigoroso de encapsulamento, blindagem avançada contra erros em tempo de execução (tratamento de exceções nativo) e proteção contra dependências circulares de arquitetura (*Forward References* com `TYPE_CHECKING`).

## Objetivo

O escopo principal deste projeto visa facilitar a administração de entidades acadêmicas, garantindo regras de negócio consistentes. Suas principais funcionalidades incluem:

- Cadastro e manutenção de graduações, disciplinas e alunos com formatação inteligente de textos.
- Abertura e fechamento de turmas vinculadas às disciplinas.
- Controle rigoroso de matrículas, evitando choque de horário e verificando limites de vagas e pré-requisitos.
- Registro de acompanhamento acadêmico, englobando notas, frequências e cálculo automático de aprovação com suporte a alunos desistentes (assunção de notas zeros).
- Trancamento de disciplinas respeitando prazos pré-estabelecidos e atualizando os limites de turma.
- Leitura de parâmetros operacionais (*semestre_vigente*, prazos, médias mínimas) centralizados por injeção de dependência via arquivo de configuração.
- Geração de relatórios estatísticos sobre o desempenho das turmas e alunos.
- Persistência do estado do sistema (salvamento e carregamento de dados em formato JSON).

## Diagrama UML

Abaixo apresentamos a modelagem da arquitetura do sistema, detalhando as classes, seus atributos, métodos e as relações de herança e associação que conectam cada parte do domínio.

```mermaid
classDiagram
    %% Definição das Classes Base e Herdeiras
    class Pessoa {
        +string nome
        +string cpf
        +string telefone
        +string email
    }

    class Aluno {
        +string matricula
        +graduacao Graduacao
        +list historico
        +calcular_cr() float
    }

    class Oferta {
        +string periodo
        +dict dias_horarios
        +int vagas
        +string local
    }

    class Turma {
        +string id_turma
        +string status
        +list matriculas_ativas
        +curso Curso
        +abrir_turma(configuracao)
        +fechar_turma()
        +verificar_choque_horario(outra_turma) bool
    }

    %% Classes de Domínio Acadêmico
    class Graduacao {
        +string codigo_mec
        +string nome
        +int quantidade_semestres
        +list grade_curricular
        +adicionar_disciplina(disciplina)
        +calcular_carga_horaria_total() int
        +verificar_elegibilidade_formatura(historico_aluno) bool
    }

    class Curso {
        +string codigo
        +string nome
        +int carga_horaria
        +list pre_requisitos
        +string ementa
        +verificar_ciclo_dependencia(novo_pre_requisito)
        +vincular_turma(turma)
    }

    class Matricula {
        +dict notas
        +float frequencia
        +string status
        +lancar_nota(nome_nota, nota)
        +lancar_frequencia(horas)
        +atualizar_situacao(regras)
        +trancar_matricula(regras)
    }

    %% Classes de Controle e Gerenciamento
    class Configuracao {
        +string semestre_vigente
        +float nota_minima_aprovacao
        +float frequencia_minima_aprovacao
        +date data_limite_trancamento
        +int max_turmas_por_aluno
        +int top_n_alunos
    }

    class Sistema {
        +list graduacoes_ofertadas
        +list cursos_disponiveis
        +list turmas_abertas
        +list alunos_matriculados
        +cadastrar_graduacao()
        +cadastrar_curso()
        +cadastrar_aluno()
        +abrir_turma()
        +realizar_matricula(matricula_aluno, id_turma)
        +salvar_estado()
        +carregar_estado()
        +gerar_relatorio_alunos_turma(id_turma)
        +gerar_relatorio_taxa_aprovacao()
        +gerar_relatorio_distribuicao_notas(id_turma)
        +gerar_relatorio_alunos_risco()
        +gerar_relatorio_top_n(periodo)
    }

    %% 1. Relações de Herança (Sem texto para despoluir o diagrama)
    Pessoa <|-- Aluno
    Oferta <|-- Turma

    %% 2. Relações do Sistema (Força o Sistema a ficar no topo)
    Sistema "1" --> "1" Configuracao : Lê regras
    Sistema "1" --> "*" Graduacao : Gerencia
    Sistema "1" --> "*" Curso : Gerencia
    Sistema "1" --> "*" Turma : Gerencia
    Sistema "1" --> "*" Aluno : Gerencia

    %% 3. Relações Associativas Acadêmicas
    Graduacao "1" --> "*" Curso : Agrupa
    Aluno "*" --> "1" Graduacao : Vinculado a
    Turma "*" --> "1" Curso : Referencia
    Matricula "*" --> "1" Aluno : Vincula
    Matricula "*" --> "1" Turma : Pertence a
```

## Estrutura de Classes

A arquitetura do projeto foi dividida em grupos lógicos para facilitar o entendimento de cada responsabilidade.

### Pessoas e Alunos

Estas classes modelam os indivíduos que interagem ou fazem parte da instituição.

- `Pessoa`: É a classe base que concentra os dados de identificação comuns a qualquer pessoa, como nome, CPF, telefone e e-mail. Implementa as lógicas e cálculos de validação de dados base.
- `Aluno`: Especializa a classe Pessoa, adicionando uma matrícula única, o vínculo com o seu curso de graduação e um histórico acadêmico. Também possibilita o cálculo do próprio Coeficiente de Rendimento (CR) baseado nas disciplinas já cursadas. Implementa métodos nativos de comparação matemática para a geração de rankings.

### Catálogo e Oferta Acadêmica

Responsáveis por estruturar o que a instituição ensina e como isso é oferecido aos alunos em cada semestre.

- `Graduacao`: Representa o curso superior do mundo real. Atua como um agrupador lógico, guardando a grade curricular de disciplinas exigidas. Possui capacidade de calcular a carga horária total e verificar se o aluno cumpriu os requisitos para formatura através de análises de interseção em conjuntos (*Sets*).
- `Curso`: Representa a disciplina em sua essência. Guarda a ementa, carga horária e, principalmente, a lista de pré-requisitos a ser cursada (implementando proteções contra ciclos lógicos e interdependências paradoxais).
- `Oferta`: É a classe base responsável por dar vida a uma disciplina em um momento específico no tempo. Nela são centralizados os dados logísticos de qualquer turma que será aberta, como o período letivo, os dias da semana, a sala e o limite de vagas disponíveis.
- `Turma`: Herda de Oferta e concretiza a oferta de um Curso específico. Ela controla a sua própria condição (aberta ou fechada), gerencia as matrículas ativas nela e possui a lógica booleana e de cruzamento de dicionários para impedir choques de horário com outras turmas.

### Vínculo Acadêmico

- `Matricula`: Atua como uma classe associativa, sendo a ponte que liga um Aluno a uma Turma. Guarda as notas e a frequência do aluno e atualiza a situação de aprovação ou reprovação com base nas regras do sistema (assumindo automaticamente a desistência de alunos com médias nulas). Gerencia de forma dinâmica a lógica de trancamento dentro do prazo estipulado, atualizando as listas de alunos ativos em tempo real para controle de vagas.

### Controle, Gerenciamento e Relatórios

Classes responsáveis pelo funcionamento do sistema na totalidade e pela persistência de informações.

- `Configuracao`: Responsável por isolar as regras de negócio parametrizáveis. Ela pode ler dados de um arquivo e garante que o sistema inteiro obedeça às mesmas definições de notas mínimas, prazos e métricas de limite. Injeta parâmetros dinâmicos nas entidades para orientar aprovações e aberturas de semestre.
- `Sistema`: É a classe principal de orquestração. Ela garante todo o funcionamento do programa, armazenando as instâncias de graduações, alunos, turmas e disciplinas em memória. É responsável pelas rotinas de criação, pela lógica de efetivar uma matrícula (checando o encadeamento de todas as validações unitárias) e por percorrer os dados armazenados para gerar relatórios, além de salvar e carregar o estado do programa em JSON.

## Principais Relacionamentos e Padrões

A modelagem reflete os princípios profundos de Orientação a Objetos e Clean Code:

- Herança: `Aluno` estende as características de `Pessoa`, enquanto `Turma` estende as características de espaço e tempo da base `Oferta`.
- Associação e Encapsulamento: O sistema possui referências diretas em vez de apenas guardar códigos. O estado interno de estruturas sensíveis (como dicionários de notas e turmas ofertadas) é protegido e modificado exclusivamente através de métodos de interface (como `vincular_turma`). Uma `Matricula`, por sua vez, conecta diretamente a instância de um `Aluno` com a instância de uma `Turma`.
- Forward Referencing: Dependências cruzadas entre classes de mesma hierarquia arquitetural são mitigadas através da manipulação do momento de avaliação das tipagens (`TYPE_CHECKING`).