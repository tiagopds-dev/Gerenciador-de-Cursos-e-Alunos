# Sistema Gerenciador de Cursos e Alunos

## Descrição

Este projeto é um sistema de gerenciamento acadêmico desenvolvido para aplicar e consolidar os conceitos de Programação Orientada a Objetos (POO). 

A aplicação foi desenhada para administrar o fluxo de uma instituição de ensino, controlando desde o catálogo de disciplinas até a abertura de turmas, efetivação de matrículas, acompanhamento de notas e frequência, além da geração de relatórios de desempenho e configuração de regras de negócio.

## Objetivo

O escopo principal deste projeto é facilitar a administração de entidades acadêmicas, garantindo regras de negócio consistentes. Suas principais funcionalidades incluem:

- Cadastro e manutenção de cursos e alunos.
- Abertura e fechamento de turmas vinculadas aos cursos.
- Controle rigoroso de matrículas, evitando choques de horário e verificando limites de vagas e pré-requisitos.
- Registro de acompanhamento acadêmico, englobando notas, frequências e status de aprovação.
- Trancamento de disciplinas respeitando prazos estabelecidos.
- Leitura de regras de aprovação e configurações a partir de arquivos externos.
- Geração de relatórios estatísticos sobre o desempenho das turmas e alunos.
- Persistência do estado do sistema (salvamento e carregamento de dados em formato JSON).

## Diagrama UML

Abaixo apresentamos a modelagem da arquitetura do sistema, detalhando as classes, seus atributos, métodos e as relações de herança e associação que conectam cada parte do domínio.

```mermaid
classDiagram
    %% Definição das Classes Base e Herdeiras
    class Pessoa {
        +String nome
        +String cpf
        +String telefone
        +String email
    }

    class Aluno {
        +String matricula
        +List historico
        +calcular_cr() float
    }

    class Oferta {
        +String periodo
        +Dict dias_horarios
        +int vagas
        +String local
    }

    class Turma {
        +String id_turma
        +String status
        +List matriculas_ativas
        +abrir_turma()
        +fechar_turma()
        +verificar_choque_horario(outra_turma) bool
    }

    %% Classes de Domínio Acadêmico
    class Curso {
        +String codigo
        +String nome
        +int carga_horaria
        +List pre_requisitos
        +String ementa
        +verificar_ciclo_dependencia(novo_pre_requisito) bool
    }

    class Matricula {
        +List notas
        +float frequencia
        +String status
        +lancar_nota(nota)
        +lancar_frequencia(frequencia)
        +atualizar_situacao(regras)
        +trancar_matricula(data_atual, data_limite) bool
    }

    %% Classes de Controle e Gerenciamento
    class Configuracao {
        +String caminho_arquivo
        +float nota_minima_aprovacao
        +Date data_limite_trancamento
        +int max_turmas_por_aluno
        +int top_n_alunos
        +carregar_configuracoes()
        +get_instancia() Configuracao
    }

    class Sistema {
        +List cursos_disponiveis
        +List turmas_abertas
        +List alunos_matriculados
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

    %% Relações de Herança
    Pessoa <|-- Aluno : Herda de
    Oferta <|-- Turma : Herda de

    %% Relações de Associação
    Turma "*" --> "1" Curso : Referencia
    Matricula "*" --> "1" Aluno : Vincula
    Matricula "*" --> "1" Turma : Pertence a
    Sistema "1" --> "1" Configuracao : Utiliza regras de
    Sistema "1" --> "*" Curso : Gerencia
    Sistema "1" --> "*" Turma : Gerencia
    Sistema "1" --> "*" Aluno : Gerencia