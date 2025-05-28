import cv2
import numpy as np
import os
from is_wire.core import Channel, Subscription
from is_msgs.image_pb2 import Image

def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return np.array([], dtype=np.uint8)

# Carrega as imagens mapa_1.png até mapa_15.png
base_path = "/minha_pasta/Imagem/"
imagens = []
for i in range(1, 16):
    filename = f"mapa_{i}.png"
    full_path = os.path.join(base_path, filename)
    img = cv2.imread(full_path)
    if img is not None:
        imagens.append(img)
    else:
        print(f"[ERRO] Não foi possível carregar: {filename}")

# Inicializa detector ArUco
parameters = cv2.aruco.DetectorParameters()
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
arucoDetector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Conexão com broker
camera_id = 1
broker_uri = "amqp://rabbitmq:30000"
channel = Channel(broker_uri)
subscription = Subscription(channel=channel)
subscription.subscribe(topic=f'CameraGateway.{camera_id}.Frame')

# Criar janela uma única vez
cv2.namedWindow("Quebra-Cabeça", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Quebra-Cabeça", 3500, 2500)

while True:
    msg = channel.consume()
    if type(msg) != bool:
        img = msg.unpack(Image)
        frame = to_np(img)

        markerCorners, markerIds, _ = arucoDetector.detectMarkers(frame)

        if markerIds is not None:
            for corners, marker_id in zip(markerCorners, markerIds.flatten()):
                if 1 <= marker_id <= 15:
                    imagem_overlay = imagens[marker_id - 1]
                    h, w = imagem_overlay.shape[:2]

                    # Pontos da imagem original e destino (cantos do ArUco)
                    src_pts = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], dtype=np.float32)
                    dst_pts = corners[0].astype(np.float32)

                    # Perspectiva
                    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                    warped = cv2.warpPerspective(imagem_overlay, matrix, (frame.shape[1], frame.shape[0]))

                    # Máscara para combinar
                    mask = np.zeros((frame.shape[0], frame.shape[1]), dtype=np.uint8)
                    cv2.fillConvexPoly(mask, dst_pts.astype(np.int32), 255)
                    mask_3ch = cv2.merge([mask, mask, mask])

                    # Combina imagem warpada com o frame original
                    frame = cv2.bitwise_and(frame, cv2.bitwise_not(mask_3ch))
                    frame = cv2.add(frame, cv2.bitwise_and(warped, mask_3ch))

            # Desenha os marcadores detectados (uma vez só!)
            frame = cv2.aruco.drawDetectedMarkers(frame, None)

        # Redimensiona e mostra na mesma janela
        frame_resized = cv2.resize(frame, None, fx=3, fy=3)
        cv2.imshow("Quebra-Cabeça", frame_resized)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
