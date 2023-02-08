import socket
import random

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 5000  # Port to listen on (non-privileged ports are > 1023)

class Server:
	def __init__(self):
		
		h = "127.0.0.1"
		h = h.split(":")
		self.host = h[0]
		self.port = random.randint(5000,8080)
		
		self.run()
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.host, self.port))
		s.listen()
		print(f"Server Started at {self.host} port: {self.port}")
		conn, addr = s.accept()
		with conn:
			print(f"Connected by {addr}")
			while True:
				data = conn.recv(1024)
				if data:
					print(data.decode())
					x = input()
					if x == "sk":
						pass
					else:
						conn.sendall(x.encode())

Server()