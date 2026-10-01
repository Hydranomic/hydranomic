from machinelearning import iniciar_ml
from data_chart import gerar_dados_grafico

estado_atual = 0

match estado_atual:

    case 1:

        iniciar_ml()

    case 2:
        
        gerar_dados_grafico()