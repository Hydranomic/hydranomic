from machinelearning import iniciar_ml
from data_chart import gerar_dados_grafico

estado_atual = 1

match estado_atual:

    case 1:

        print(iniciar_ml())

        estado_atual = 0

    case 2:

        gerar_dados_grafico()

        estado_atual = 0