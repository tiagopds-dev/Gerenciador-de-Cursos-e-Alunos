from pessoas import Pessoa


class Aluno(Pessoa):
    """
    Especializa a classe Pessoa, adicionando uma matrícula única, o vínculo com a sua 
    Graduação e um histórico acadêmico. Responsável por calcular o Coeficiente de Rendimento (CR).
    """
    def calcular_cr(self) -> float:
        """Calcula o coeficiente de rendimento/média ponderada com base nas disciplinas do histórico."""
        pass