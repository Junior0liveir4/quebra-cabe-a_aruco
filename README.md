# 🧩📷 Quebra-Cabeça ArUco – Entretenimento com Visão Computacional

Este projeto é uma aplicação interativa que usa **marcadores ArUco** para montar dinamicamente um **quebra-cabeça com 15 peças**. Cada marcador detectado ativa a sobreposição de uma imagem correspondente em tempo real, criando um jogo visual de montagem baseado em visão computacional.

Desenvolvido no **LabSEA (IFES - Guarapari)**, o projeto consome imagens transmitidas por um dos **gateways de câmera via RabbitMQ**, e roda localmente em Python com OpenCV.

---

## 🧠 O que são marcadores ArUco?

**ArUco markers** são padrões visuais quadrados com borda preta e um ID interno codificado em branco e preto. Eles são comumente usados para:
- Calibração de câmeras
- Estimação de pose 3D
- Realidade aumentada (AR)
- Rastreamento de objetos

O OpenCV possui suporte nativo a esses marcadores, permitindo **detecção rápida e precisa** em vídeos ou imagens.

---

## 🎯 Objetivo da aplicação

- Detectar até 15 marcadores ArUco posicionados em um plano.
- Substituir dinamicamente cada marcador por uma **imagem correspondente (mapa_1.png até mapa_15.png)**.
- Formar visualmente uma imagem composta como se fosse um quebra-cabeça.
- Exibir a montagem em tempo real com sobreposição por transformação de perspectiva.

---

## ⚙️ Requisitos

Instale as dependências com:

```bash
pip install opencv-python numpy is-wire is-msgs
```

> Certifique-se de que o OpenCV instalado tem suporte ao módulo `aruco`, presente em `opencv-contrib-python`.

---

## 📂 Estrutura esperada

```
quebra-cabeça_aruco/
├── quebra-cabeça_aruco.py
├── Imagem/
│   ├── mapa_1.png
│   ├── mapa_2.png
│   └── ...
│   └── mapa_15.png
```

- A pasta `Imagem/` deve conter as 15 imagens (em PNG) a serem sobrepostas nos marcadores.
- As imagens são indexadas de acordo com o ID do marcador ArUco (de 1 a 15).

---

## 📡 Fonte de imagem

A imagem ao vivo é recebida via **RabbitMQ**, usando a estrutura **IS-Wire**:

- Subscrição no tópico:
  ```
  CameraGateway.{camera_id}.Frame
  ```

- O broker utilizado no código padrão:
  ```
  amqp://guest:guest@10.10.2.211:30000
  ```

---

## 🚀 Como executar

1. Verifique se o broker está rodando e a câmera está publicando no tópico esperado.

2. Ajuste o caminho `base_path` no código, se necessário, para localizar as imagens corretamente.

3. Execute o código:

```bash
python3 quebra-cabeça_aruco.py
```

4. A aplicação abrirá uma janela chamada **"Quebra-Cabeça"**. Quando os marcadores ArUco forem detectados, as imagens correspondentes serão desenhadas sobre eles.

5. Pressione `q` para encerrar o programa.

---

## 🧪 O que o código faz

- Recebe uma imagem de uma câmera via broker.
- Detecta marcadores ArUco com `cv2.aruco.ArucoDetector`.
- Para cada marcador (ID de 1 a 15), aplica:
  - Transformação de perspectiva para alinhar a imagem ao marcador.
  - Máscara para mesclar a imagem com o frame original.
- Exibe o resultado com os marcadores sobrepostos e identificados.

---

## 🎥 Visualização

- Uma janela em tela cheia é criada e atualizada em tempo real.
- Cada imagem é desenhada sobre o marcador que representa sua "posição" no quebra-cabeça.
- Quando todos os 15 marcadores estão corretamente posicionados, a imagem completa é formada visualmente.

---

## 🎉 Finalidade

- **Entretenimento interativo** usando visão computacional.
- Demonstração prática de uso de marcadores ArUco com sobreposição visual.
- Atividade divertida para exposições, feiras ou uso educacional.

---

## 📬 Contato

Para dúvidas ou sugestões, entre em contato com o time do LabSEA.
