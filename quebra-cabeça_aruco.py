import cv2
import numpy as np
import os
import threading
import queue
from is_wire.core import Subscription
from is_msgs.image_pb2 import Image
from streamChannel import StreamChannel

# Conversão de mensagem para imagem NumPy
def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return np.array([], dtype=np.uint8)

# Carregar imagens de sobreposição
base_path = "/minha_pasta/Imagem/"
imagens = [cv2.imread(os.path.join(base_path, f"mapa_{i}.png")) for i in range(1, 16)]

# Detector ArUco com refinamento
parameters = cv2.aruco.DetectorParameters()
parameters.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
arucoDetector = cv2.aruco.ArucoDetector(dictionary, parameters)

# Broker
camera_id = 1
broker_uri = "amqp://rabbitmq:30000"
channel = StreamChannel(broker_uri)
subscription = Subscription(channel=channel)
subscription.subscribe(topic=f'CameraGateway.{camera_id}.Frame')

# Fila para troca entre threads
frame_queue = queue.Queue(maxsize=1)  # mantém só o frame mais recente

# 🧵 THREAD 1: Recebe frames do broker
def receber_frames():
    while True:
        msg = channel.consume()
        if type(msg) != bool:
            img = msg.unpack(Image)
            frame = to_np(img)
            try:
                # Remove frame antigo se a fila estiver cheia
                if frame_queue.full():
                    frame_queue.get_nowait()
                frame_queue.put_nowait(frame)
            except queue.Full:
                pass  # Ignora se não conseguir colocar

# 🧵 THREAD 2: Processa e exibe os frames
def processar_frames():
    cv2.namedWindow("Quebra-Cabeça", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Quebra-Cabeça", 2500, 2000)

    resize_scale = 0.8  # Redução para detecção

    while True:
        try:
            frame_full = frame_queue.get(timeout=1)  # pega o frame mais recente
        except queue.Empty:
            continue

        frame_small = cv2.resize(frame_full, None, fx=resize_scale, fy=resize_scale)
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)

        markerCorners, markerIds, _ = arucoDetector.detectMarkers(gray)

        if markerIds is not None:
            for corners, marker_id in zip(markerCorners, markerIds.flatten()):
                if 1 <= marker_id <= 15:
                    imagem_overlay = imagens[marker_id - 1]
                    if imagem_overlay is None:
                        continue
                    h, w = imagem_overlay.shape[:2]
                    dst_pts = (corners[0] / resize_scale).astype(np.float32)
                    src_pts = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], dtype=np.float32)

                    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                    warped = cv2.warpPerspective(imagem_overlay, matrix, (frame_full.shape[1], frame_full.shape[0]))

                    mask = np.zeros((frame_full.shape[0], frame_full.shape[1]), dtype=np.uint8)
                    cv2.fillConvexPoly(mask, dst_pts.astype(np.int32), 255)
                    mask_3ch = cv2.merge([mask, mask, mask])

                    frame_full = cv2.bitwise_and(frame_full, cv2.bitwise_not(mask_3ch))
                    frame_full = cv2.add(frame_full, cv2.bitwise_and(warped, mask_3ch))

        frame_resized = cv2.resize(frame_full, None, fx=3, fy=3)
        cv2.imshow("Quebra-Cabeça", frame_resized)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

# Inicia as threads
t_receber = threading.Thread(target=receber_frames, daemon=True)
t_processar = threading.Thread(target=processar_frames)

t_receber.start()
t_processar.start()
t_processar.join()  # espera a thread principal encerrar
