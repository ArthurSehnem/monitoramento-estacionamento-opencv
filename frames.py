import cv2
import numpy as np

# --- CONFIGURAÇÕES ---
VIDEO_SOURCE = 'video.mp4'
VAGAS_COORDENADAS = [
    # Cole aqui as coordenadas geradas pelo mapeador
]
LIMIAR_VAGA_OCUPADA = 900 

# --- FUNÇÕES AUXILIARES ---
def get_nome_cor(cor_bgr):
    b, g, r = int(cor_bgr[0]), int(cor_bgr[1]), int(cor_bgr[2])
    if (r + g + b) < 150: return 'Preto'
    if (r + g + b) > 600: return 'Branco'
    if abs(r - g) < 20 and abs(r - b) < 20: return 'Cinza'
    if b > r and b > g: return 'Azul'
    if g > r and g > b: return 'Verde'
    if r > g and r > b: return 'Vermelho'
    return 'Outra'

# --- ALGORITMO PRINCIPAL ---
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print(f"Erro ao abrir o vídeo: {VIDEO_SOURCE}")
    exit()

total_de_vagas = len(VAGAS_COORDENADAS)

while True:
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        continue

    # <<-- 1. FAÇA UMA CÓPIA LIMPA DO FRAME AQUI -->>
    # Guardamos o frame original antes de qualquer modificação.
    frame_original = frame.copy()

    # Processamento de imagem para detecção
    frame_cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame_blur = cv2.GaussianBlur(frame_cinza, (5, 5), 1)
    frame_threshold = cv2.adaptiveThreshold(frame_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

    vagas_livres = 0
    
    # O resto do código desenha sobre a variável 'frame', deixando 'frame_original' intacta
    for pontos_vaga in VAGAS_COORDENADAS:
        mask = np.zeros_like(frame_cinza)
        pts_array = np.array(pontos_vaga, np.int32)
        cv2.fillPoly(mask, [pts_array], 255)
        
        vaga_recortada = cv2.bitwise_and(frame_threshold, frame_threshold, mask=mask)
        pixels_brancos = cv2.countNonZero(vaga_recortada)
        
        cor_vaga = (0, 255, 0)
        
        if pixels_brancos > LIMIAR_VAGA_OCUPADA:
            cor_vaga = (0, 0, 255)
            vaga_colorida = cv2.bitwise_and(frame, frame, mask=mask)
            cor_media_bgr = cv2.mean(vaga_colorida, mask=mask)
            nome_cor = get_nome_cor(cor_media_bgr)
            cv2.putText(frame, nome_cor, (pontos_vaga[0][0], pontos_vaga[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        else:
            vagas_livres += 1

        cv2.polylines(frame, [pts_array], isClosed=True, color=cor_vaga, thickness=2)

    texto_contador = f"Disponiveis: {vagas_livres} / {total_de_vagas}"
    cv2.rectangle(frame, (10, 5), (320, 40), (0, 0, 0), -1)
    cv2.putText(frame, texto_contador, (15, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

    cv2.imshow("Analisador de Estacionamento", frame)
    
    key = cv2.waitKey(30) & 0xFF
    if key == 27:
        break
    elif key == ord('s'):
        # <<-- 2. SALVE A CÓPIA ORIGINAL, NÃO O FRAME MODIFICADO -->>
        cv2.imwrite('estacionamento_frame.jpg', frame_original)
        print("✅ Frame PURO salvo como 'estacionamento_frame.jpg'")

cap.release()
cv2.destroyAllWindows()