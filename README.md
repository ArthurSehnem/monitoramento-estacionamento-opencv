# Sistema de Detecção de Vagas em Estacionamentos

Este é um projeto simples de sistema de detecção de vagas em estacionamentos utilizando a linguagem Python e a biblioteca OpenCV. O objetivo principal é monitorar a ocupação de vagas em um vídeo, identificar veículos, contar vagas disponíveis e até mesmo estimar a cor dos veículos.

## Funcionalidades

* **Exibição de Vídeo:** Carrega e exibe um vídeo de um estacionamento.
* **Marcação de Vagas:** Desenha polígonos sobre as vagas predefinidas no vídeo, indicando a área de cada espaço.
* **Detecção de Ocupação:** Utiliza técnicas de processamento de imagem para determinar se uma vaga está ocupada por um veículo ou está livre.
* **Contagem de Vagas:** Exibe em tempo real a quantidade de vagas disponíveis no estacionamento.
* **Identificação de Cor:** Estima e exibe a cor predominante de cada veículo detectado em uma vaga ocupada.

## Tecnologias Utilizadas

* **Python:** Linguagem de programação principal.
* **OpenCV (Open Source Computer Vision Library):** Biblioteca essencial para processamento de imagem e visão computacional.
* **NumPy:** Biblioteca para operações numéricas e array, fundamental para manipulação de imagens.

## Como a Detecção de Vagas Funciona

A detecção de vagas é realizada através de um pipeline de processamento de imagem que inclui:

1.  **Pré-processamento:** Conversão para escala de cinza e aplicação de filtro Gaussiano para redução de ruído.
2.  **Detecção de Bordas:** Utilização do algoritmo Canny para identificar as bordas dos objetos (veículos) no frame.
3.  **Operações Morfológicas:** Aplicação de operações de fechamento e dilatação para refinar as bordas e conectar segmentos, formando contornos mais completos.
4.  **Máscara de Região de Interesse (ROI):** As bordas são filtradas para considerar apenas as que estão dentro das áreas predefinidas de cada vaga.
5.  **Análise de Contornos:** Contornos são detectados e analisados por sua área. Se a área total e/ou a quantidade de contornos significativos dentro de uma vaga excederem certos limiares, a vaga é considerada ocupada.
6.  **Suavização Temporal:** Um histórico das detecções de cada vaga é mantido para suavizar o resultado e evitar oscilações rápidas ("flickering"), tornando a detecção mais estável.

A identificação da cor do veículo é feita analisando a região da vaga em seu espaço de cor HSV (Matiz, Saturação, Valor), que é menos suscetível a variações de iluminação, e classificando a cor predominante com base nos valores de Matiz, Saturação e Brilho.

## Como Rodar o Projeto

1.  **Pré-requisitos:**
    * Python 3.x instalado.
    * Instalar as bibliotecas necessárias:
        ```bash
        pip install opencv-python numpy
        ```

2.  **Preparação do Vídeo:**
    * Coloque um arquivo de vídeo de um estacionamento (ex: `video.mp4`) no mesmo diretório do script `main.py`. **Certifique-se de ajustar o nome do arquivo na variável `VIDEO_SOURCE` dentro do código, se necessário.**

3.  **Configuração das Vagas:**
    * As coordenadas das vagas (`VAGAS_COORDENADAS`) no script são exemplos. Você precisará ajustá-las manualmente para corresponder às vagas do seu vídeo. Execute o script, observe o vídeo e edite essas coordenadas para que os polígonos desenhados correspondam precisamente às vagas.
    * Pode ser necessário ajustar também os parâmetros de configuração dentro da classe `DetectorVagas` (`min_contour_area`, `threshold_area_total`, `canny_min`, `canny_max`, etc.) para otimizar a detecção de acordo com a iluminação e características do seu vídeo.

4.  **Execução:**
    * Navegue até o diretório do projeto no seu terminal e execute:
        ```bash
        python seu_script_principal.py
        ```
        (Substitua `seu_script_principal.py` pelo nome do seu arquivo `.py` onde o código está).

5.  **Interação:**
    * A janela do vídeo será exibida com as vagas marcadas, a contagem de vagas livres e o status de cada vaga.
    * Pressione a tecla `ESC` para fechar o programa a qualquer momento.

## Contribuição (Opcional)

Sinta-se à vontade para explorar, modificar e melhorar este código. Sugestões de melhorias incluem:

* Implementar um método interativo para definir as coordenadas das vagas.
* Integrar técnicas mais avançadas de detecção de objetos (ex: Haar Cascades ou modelos de Deep Learning como YOLO) para reconhecimento de veículos.
* Aprimorar o algoritmo de detecção de cor para maior precisão.
* Adicionar persistência (salvar/carregar) das configurações das vagas.

---
