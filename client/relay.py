import socket
import threading

HOST = "0.0.0.0"
PORT = 5050

clients = []

def forward(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data:
                break
            dst.sendall(data)
    except:
        pass
    finally:
        src.close()
        dst.close()

def handle_pair(conn1, conn2):
    threading.Thread(target=forward, args=(conn1, conn2), daemon=True).start()
    threading.Thread(target=forward, args=(conn2, conn1), daemon=True).start()

def relay_server():
    print(f"[RELAY] Ожидание 2 подключений на {HOST}:{PORT}...")
    server = socket.socket()
    server.bind((HOST, PORT))
    server.listen(2)

    while True:
        conn, addr = server.accept()
        print(f"[RELAY] Подключение от {addr}")
        clients.append(conn)

        if len(clients) == 2:
            print("[RELAY] Связываю клиентов...")
            c1, c2 = clients.pop(0), clients.pop(0)
            handle_pair(c1, c2)
            print("[RELAY] Готов к новым соединениям.")

if __name__ == "__main__":
    relay_server()