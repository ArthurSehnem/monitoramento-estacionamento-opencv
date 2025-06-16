import cv2
import numpy as np

# --- CONFIGURAÇÕES E VARIÁVEIS GLOBAIS ---

# Caminho para o vídeo
VIDEO_SOURCE = 'video.mp4' 

# Coordenadas das vagas (polígonos de 4 pontos)
# !!! ATENÇÃO: ESTAS COORDENADAS SÃO APENAS UM EXEMPLO. !!!
# !!! VOCÊ DEVE USAR O SCRIPT MAPEADOR PARA OBTER AS SUAS COORDENADAS REAIS. !!!
VAGAS_COORDENADAS = [((259, 71), (199, 421), (407, 427), (399, 68)), ((423, 70), (434, 431), (746, 421), (601, 76)), ((640, 123), (840, 443), (842, 94), (694, 97)), ((95, 127), (208, 128), (20, 457), (5, 166))]

# Limiar para considerar uma vaga ocupada.
# Se a quantidade de pixels brancos na vaga for maior que este valor, está ocupada.
# !!! ESTE VALOR PRECISA SER AJUSTADO DE ACORDO COM SEU VÍDEO E RESOLUÇÃO !!!
LIMIAR_VAGA_OCUPADA = 850 


# --- FUNÇÕES AUXILIARES ---

def get_nome_cor(cor_bgr):
    """
    Função simples para classificar uma cor BGR para um nome em português.
    Não é perfeita, mas funciona para cores básicas.
    """
    b, g, r = int(cor_bgr[0]), int(cor_bgr[1]), int(cor_bgr[2])

    # Se for muito escuro, considera Preto
    if (r + g + b) < 150:
        return 'Preto'
    # Se for muito claro, considera Branco
    if (r + g + b) > 600:
        return 'Branco'
    # Se os valores são muito próximos, é Cinza
    if abs(r - g) < 20 and abs(r - b) < 20 and abs(g - b) < 20:
        return 'Cinza'
    
    # Comparações de cores primárias e secundárias
    if r > g and r > b:
        if r > 120: return 'Vermelho'
    if g > r and g > b:
        if g > 110: return 'Verde'
    if b > r and b > g:
        if b > 120: return 'Azul'
    if r > b and g > b: # Amarelo/Laranja
        if (r-b) > 50 and (g-b)>50: return 'Amarelo'

    return 'Outra'


# --- ALGORITMO PRINCIPAL ---

# 1. CARREGAR O VÍDEO
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print(f"Erro ao abrir o arquivo de vídeo: {VIDEO_SOURCE}")
    exit()

total_de_vagas = len(VAGAS_COORDENADAS)

while True:
    # Ler um frame do vídeo
    ret, frame = cap.read()
    if not ret:
        print("Fim do vídeo. Reiniciando...")
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.GaussianBlur(frame_cinza, (5, 5), 1)
    frame_threshold = cv2.adaptiveThreshold(frame_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

    vagas_livres = 0
    
    # Iterar sobre cada vaga definida
    for i, pontos_vaga in enumerate(VAGAS_COORDENADAS):
        
        # Criar uma máscara para a vaga atual
        mask = np.zeros_like(frame_cinza)
        pts_array = np.array(pontos_vaga, np.int32)
        cv2.fillPoly(mask, [pts_array], 255)
        
        # Recortar a região da vaga da imagem de threshold
        vaga_recortada = cv2.bitwise_and(frame_threshold, frame_threshold, mask=mask)
        
        # Contar os pixels brancos (que indicam um objeto)
        pixels_brancos = cv2.countNonZero(vaga_recortada)
        
        cor_vaga = (0, 255, 0) # Verde (Livre) por padrão
        
        # Se a contagem de pixels for maior que o limiar, a vaga está ocupada
        if pixels_brancos > LIMIAR_VAGA_OCUPADA:
            cor_vaga = (0, 0, 255) # Vermelho (Ocupada)
            
            # --- LÓGICA PARA DETECTAR A COR DO VEÍCULO ---
            vaga_colorida = cv2.bitwise_and(frame, frame, mask=mask)
            cor_media_bgr = cv2.mean(vaga_colorida, mask=mask)
            nome_cor = get_nome_cor(cor_media_bgr)
            
            posicao_texto_cor = pontos_vaga[0]
            cv2.putText(frame, nome_cor, (posicao_texto_cor[0], posicao_texto_cor[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            
        else:
            vagas_livres += 1 

        # 2. DESENHAR AS VAGAS NO FRAME
        cv2.polylines(frame, [pts_array], isClosed=True, color=cor_vaga, thickness=2)

    # 3. EXIBIR A CONTAGEM DE VAGAS DISPONÍVEIS
    texto_contador = f"Disponiveis: {vagas_livres} / {total_de_vagas}"
    cv2.rectangle(frame, (10, 5), (320, 40), (0,0,0), -1) 
    cv2.putText(frame, texto_contador, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    # EXIBIR O VÍDEO PROCESSADO
    cv2.imshow("Video Estacionamento", frame)
    
    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()