import math

def calcular_media_ponderada(jogos, campo):
    """
    Calcula a média ponderada temporal de um campo específico nos últimos 10 jogos.
    Pesos:
    - 3 jogos mais recentes: Peso 3
    - 4 jogos intermediários: Peso 2
    - 3 jogos mais antigos: Peso 1

    Espera-se que 'jogos' seja uma lista onde o índice 0 é o jogo mais recente.
    """
    if not jogos or len(jogos) == 0:
        return 0.0

    soma_ponderada = 0
    soma_pesos = 0

    for i, jogo in enumerate(jogos):
        valor = jogo.get(campo, 0)

        # O fotmob scraper pode não colocar na ordem certa, mas vamos assumir que
        # a lista reflete do mais recente ao mais antigo, ou seja:
        # i=0,1,2 (recente) -> peso 3
        # i=3,4,5,6 (intermediario) -> peso 2
        # i=7,8,9 (antigo) -> peso 1

        if i < 3:
            peso = 3
        elif i < 7:
            peso = 2
        else:
            peso = 1

        soma_ponderada += valor * peso
        soma_pesos += peso

    return soma_ponderada / soma_pesos if soma_pesos > 0 else 0.0

def calcular_poisson(lambda_val, x):
    """
    Calcula a probabilidade de x ocorrências dado a média (lambda_val)
    usando a Distribuição de Poisson.
    P(x; μ) = (e^(-μ) * μ^x) / x!
    """
    return (math.exp(-lambda_val) * (lambda_val ** x)) / math.factorial(x)

def probabilidade_over_gols(media_gols_marcados_a, media_gols_sofridos_b, over_limit=1.5):
    """
    Calcula a probabilidade de um jogo ter mais de 'over_limit' gols usando Poisson.
    A expectativa de gols de um time é uma simplificação da média entre
    o que ele marca e o que o oponente sofre.
    """
    expectativa_gols = (media_gols_marcados_a + media_gols_sofridos_b) / 2.0

    # Calcular probabilidades de 0 e 1 gol
    prob_0 = calcular_poisson(expectativa_gols, 0)
    prob_1 = calcular_poisson(expectativa_gols, 1)

    prob_under_1_5 = prob_0 + prob_1
    prob_over_1_5 = 1 - prob_under_1_5

    # Adicionar 2 se for over 2.5
    if over_limit == 2.5:
        prob_2 = calcular_poisson(expectativa_gols, 2)
        prob_over_2_5 = 1 - (prob_under_1_5 + prob_2)
        return prob_over_2_5 * 100

    return prob_over_1_5 * 100
