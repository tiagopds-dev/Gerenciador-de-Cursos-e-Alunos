class Curso:
    """
    Representa a disciplina na sua essência. Guarda a ementa, carga horária 
    e a lista de pré-requisitos necessários para ser cursada.
    """
    def verificar_ciclo_dependencia(self, novo_pre_requisito: str) -> bool:
        """Impede dependências cruzadas (ex: A exige B e B exige A simultaneamente)."""
        pass