#pip install opencv-python PyQt5


#Captura de Vídeo com OpenCV
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

#Transmissão de Vídeo com Sockets
import socket
import cv2
import pickle
import struct

# Configuração do socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 8080))
server_socket.listen(5)

client_socket, addr = server_socket.accept()

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    data = pickle.dumps(frame)
    message_size = struct.pack("L", len(data))
    client_socket.sendall(message_size + data)

cap.release()
client_socket.close()
server_socket.close()

#No lado do cliente, você precisará receber os frames e exibi-los.
import socket
import cv2
import pickle
import struct

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('IP_DO_SERVIDOR', 8080))

data = b""
payload_size = struct.calcsize("L")

while True:
    while len(data) < payload_size:
        data += client_socket.recv(4096)
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    msg_size = struct.unpack("L", packed_msg_size)[0]

    while len(data) < msg_size:
        data += client_socket.recv(4096)
    frame_data = data[:msg_size]
    data = data[msg_size:]

    frame = pickle.loads(frame_data)
    cv2.imshow('Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

client_socket.close()
cv2.destroyAllWindows()

#5. Interface Gráfica com PyQt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
import sys

class VideoChatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Video Chat App')
        self.setGeometry(100, 100, 800, 600)
        self.label = QLabel('Video Chat', self)
        self.label.setGeometry(50, 50, 700, 500)

app = QApplication(sys.argv)
window = VideoChatApp()
window.show()
sys.exit(app.exec_())

