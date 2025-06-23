import cv2
import numpy as np
import time
from collections import deque

# Caminho do vídeo
VIDEO_SOURCE = 'video.mp4'

# Coordenadas das vagas (ajustar conforme o vídeo)
VAGAS_COORDENADAS = [
    ((244, 99), (399, 85), (406, 388), (223, 387)),
    ((439, 85), (449, 384), (735, 377), (598, 84)),
    ((631, 89), (784, 372), (844, 163), (715, 80)),
    ((134, 121), (218, 116), (156, 390), (1, 214))
]

class DetectorVagas:
    def __init__(self):
        self.historico_vagas = [deque(maxlen=7) for _ in VAGAS_COORDENADAS]
        self.config = {
            'min_contour_area': 400,
            'max_contour_area': 50000,
            'threshold_area_total': 1000,
            'blur_kernel': (5, 5),
            'canny_min': 50,
            'canny_max': 150,
            'morph_kernel_size': (3, 3)
        }

    def detectar_ocupacao(self, frame, pontos_vaga):
        """Detecta se a vaga está ocupada usando contornos"""
        cinza = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(cinza, self.config['blur_kernel'], 0)
        edges = cv2.Canny(blur, self.config['canny_min'], self.config['canny_max'])

        kernel = np.ones(self.config['morph_kernel_size'], np.uint8)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        edges = cv2.dilate(edges, kernel, iterations=1)

        mask = np.zeros_like(cinza)
        pts = np.array(pontos_vaga, np.int32)
        cv2.fillPoly(mask, [pts], 255)
        vaga_edges = cv2.bitwise_and(edges, edges, mask=mask)

        contornos, _ = cv2.findContours(vaga_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        area_total = 0
        contornos_significativos = 0
        for c in contornos:
            area = cv2.contourArea(c)
            if self.config['min_contour_area'] < area < self.config['max_contour_area']:
                area_total += area
                contornos_significativos += 1

        ocupada = contornos_significativos > 0 and area_total > self.config['threshold_area_total']
        return ocupada

    def suavizar_deteccao(self, historico, nova_deteccao):
        """Reduz oscilações nas detecções usando histórico"""
        historico.append(nova_deteccao)
        return sum(historico) > len(historico) // 2

    def extrair_cor(self, frame, pontos_vaga):
        """Detecta a cor predominante do veículo usando HSV e moda do Hue"""
        mask = np.zeros(frame.shape[:2], np.uint8)
        pts = np.array(pontos_vaga, np.int32)
        cv2.fillPoly(mask, [pts], 255)
    
        # Erosão para focar no centro da vaga
        kernel = np.ones((45, 45), np.uint8)
        mask_eroded = cv2.erode(mask, kernel, iterations=1)
    
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_masked = cv2.bitwise_and(hsv, hsv, mask=mask_eroded)
    
        h, s, v = cv2.split(hsv_masked)
    
        # Filtra pixels válidos
        h_values = h[mask_eroded == 255]
        s_values = s[mask_eroded == 255]
        v_values = v[mask_eroded == 255]
    
        if len(h_values) == 0:
            return "Indefinida"
    
        # Calcula a moda (cor predominante real)
        hist = cv2.calcHist([h_values], [0], None, [180], [0, 180])
        hue_dominante = np.argmax(hist)
        s_media = np.mean(s_values)
        v_media = np.mean(v_values)
    
        # Classificação baseada na moda do Hue
        if v_media < 50:
            return "Preto"
        if v_media > 200 and s_media < 50:
            return "Branco"
        if s_media < 50:
            return "Cinza"
    
        if hue_dominante < 10 or hue_dominante > 160:
            return "Vermelho"
        elif 10 < hue_dominante <= 25:
            return "Amarelo"
        elif 25 < hue_dominante <= 85:
            return "Verde"
        elif 85 < hue_dominante <= 135:
            return "Azul"
        else:
            return "Outra"

def main():
    detector = DetectorVagas()
    cap = cv2.VideoCapture(VIDEO_SOURCE)

    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    print("Detector de Vagas iniciado. Pressione ESC para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        vagas_livres = 0
        for i, vaga in enumerate(VAGAS_COORDENADAS):
            ocupada_bruta = detector.detectar_ocupacao(frame, vaga)
            ocupada = detector.suavizar_deteccao(detector.historico_vagas[i], ocupada_bruta)

            pts = np.array(vaga, np.int32)
            cor_borda = (0, 0, 255) if ocupada else (0, 255, 0)
            cv2.polylines(frame, [pts], True, cor_borda, 3)

            x, y = vaga[0]
            status = "OCUPADA" if ocupada else "LIVRE"
            cv2.putText(frame, f"Vaga {i+1}: {status}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor_borda, 2)

            if ocupada:
                cor = detector.extrair_cor(frame, vaga)
                cv2.putText(frame, f"Cor: {cor}", (x, y + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, cor_borda, 1)
            else:
                vagas_livres += 1

        # Caixa de fundo preta + texto verde da contagem
        texto = f"Vagas livres: {vagas_livres} / {len(VAGAS_COORDENADAS)}"
        posicao = (20, 40)
        (tam, _) = cv2.getTextSize(texto, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
        w_texto, h_texto = tam
        cv2.rectangle(frame, (posicao[0] - 10, posicao[1] - h_texto - 10),
                      (posicao[0] + w_texto + 10, posicao[1] + 10),
                      (0, 0, 0), -1)  # fundo preto
        cv2.putText(frame, texto, posicao, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Detector de Vagas", frame)

        if cv2.waitKey(30) & 0xFF == 27:  # ESC para sair
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Programa finalizado.")

if __name__ == "__main__":
    main()
