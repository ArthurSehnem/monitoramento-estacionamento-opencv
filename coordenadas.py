import cv2
import numpy as np

vagas_mapeadas = []
pontos_atuais = []
ARQUIVO_IMAGEM = 'estacionamento_frame.jpg'

def clique_do_mouse(event, x, y, flags, params):
    """
    Função de callback que é chamada a cada clique do mouse na janela.
    """
    global pontos_atuais, img_copia

    if event == cv2.EVENT_LBUTTONDOWN:
        pontos_atuais.append((x, y))
        print(f'Ponto adicionado: ({x}, {y})')

        cv2.circle(img_copia, (x, y), 5, (0, 0, 255), -1)
        if len(pontos_atuais) == 4:
            print(f'Vaga definida com 4 pontos: {tuple(pontos_atuais)}')
            vagas_mapeadas.append(tuple(pontos_atuais))
            
            pts_array = np.array(pontos_atuais, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img_copia, [pts_array], isClosed=True, color=(0, 255, 0), thickness=2)
            
            pontos_atuais = []

try:
    img = cv2.imread(ARQUIVO_IMAGEM)
    if img is None:
        raise FileNotFoundError
    img_copia = img.copy()
except FileNotFoundError:
    print(f"Erro: Arquivo de referência '{ARQUIVO_IMAGEM}' não encontrado.")
    print("Execute o seu script principal de estacionamento e aperte a tecla 's' para salvar um frame primeiro.")
    exit()

cv2.namedWindow('Mapeador de Vagas com 4 Pontos')
cv2.setMouseCallback('Mapeador de Vagas com 4 Pontos', clique_do_mouse)

print("--- Mapeador de Vagas com 4 Pontos ---")
print("Instruções:")
print("- Clique nos 4 cantos de cada vaga, EM ORDEM (ex: sentido horário).")
print("- Pressione 'r' para resetar todos os pontos e recomeçar.")
print("- Pressione 'Esc' para finalizar e imprimir a lista de coordenadas.")

while True:
    cv2.imshow('Mapeador de Vagas com 4 Pontos', img_copia)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        break
    elif key == ord('r'):
        img_copia = img.copy()
        vagas_mapeadas = []
        pontos_atuais = []
        print("\n--- PONTOS RESETADOS ---\n")

cv2.destroyAllWindows()

print("\n--- Mapeamento Concluído! ---")
print("Copie a linha abaixo e cole no seu script principal (na variável 'VAGAS_COORDENADAS'):\n")
print(f'VAGAS_COORDENADAS = {vagas_mapeadas}')