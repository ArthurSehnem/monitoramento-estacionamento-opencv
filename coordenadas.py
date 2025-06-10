import cv2
import numpy as np

# Lista para armazenar os polígonos (coordenadas das vagas)
vagas_mapeadas = []
pontos_atuais = []
# Nome do arquivo de imagem a ser usado como referência
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

        # Se já tivermos 4 pontos, formamos um polígono (vaga)
        if len(pontos_atuais) == 4:
            print(f'Vaga definida com 4 pontos: {tuple(pontos_atuais)}')
            vagas_mapeadas.append(tuple(pontos_atuais))
            
            # Desenha o polígono na imagem para visualização
            pts_array = np.array(pontos_atuais, np.int32).reshape((-1, 1, 2))
            cv2.polylines(img_copia, [pts_array], isClosed=True, color=(0, 255, 0), thickness=2)
            
            # Limpa a lista de pontos atuais para a próxima vaga
            pontos_atuais = []

# --- SCRIPT PRINCIPAL ---

# Tenta carregar a imagem de referência
try:
    img = cv2.imread(ARQUIVO_IMAGEM)
    if img is None:
        raise FileNotFoundError
    img_copia = img.copy()  # Trabalhamos em uma cópia para não alterar a original
except FileNotFoundError:
    print(f"Erro: Arquivo de referência '{ARQUIVO_IMAGEM}' não encontrado.")
    print("Execute o seu script principal de estacionamento e aperte a tecla 's' para salvar um frame primeiro.")
    exit()

# Cria a janela e associa a função de callback do mouse a ela
cv2.namedWindow('Mapeador de Vagas com 4 Pontos')
cv2.setMouseCallback('Mapeador de Vagas com 4 Pontos', clique_do_mouse)

print("--- Mapeador de Vagas com 4 Pontos ---")
print("Instruções:")
print("- Clique nos 4 cantos de cada vaga, EM ORDEM (ex: sentido horário).")
print("- Pressione 'r' para resetar todos os pontos e recomeçar.")
print("- Pressione 'Esc' para finalizar e imprimir a lista de coordenadas.")

while True:
    # Exibe a imagem na janela
    cv2.imshow('Mapeador de Vagas com 4 Pontos', img_copia)
    key = cv2.waitKey(1) & 0xFF

    # Se 'Esc' for pressionada, sai do loop
    if key == 27:
        break
    # Se 'r' for pressionada, reseta o mapeamento
    elif key == ord('r'):
        img_copia = img.copy()
        vagas_mapeadas = []
        pontos_atuais = []
        print("\n--- PONTOS RESETADOS ---\n")

# Fecha todas as janelas do OpenCV
cv2.destroyAllWindows()

# Imprime a lista final no formato exato para ser copiada
print("\n--- Mapeamento Concluído! ---")
print("Copie a linha abaixo e cole no seu script principal (na variável 'VAGAS_COORDENADAS'):\n")
print(f'VAGAS_COORDENADAS = {vagas_mapeadas}')