# from flask import Flask, request, render_template
import socket
import json
import datetime
HOST = '0.0.0.0'
PORT = 65431



if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                try:
                    json_data = json.loads(data)
                    if json_data is not None:
                        name = json_data.get('name', '').strip().lower()
                        if name == 'bob':
                            print(datetime.datetime.now())
                except json.JSONDecodeError as e:
                    print(f"Error decoding JSON: {e}")