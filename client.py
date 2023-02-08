import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 5000  # The port used by the server

class Client:
	def __init__(self,*argv):
		self.host = argv[0]
		self.port  = argv[1]
		self.run()
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((self.host, self.port))
		while True:
			x = input()
			
			s.sendall(x.encode())
			data = s.recv(1024)
			if data:
				data = data.decode()
				print(f"{data!r}")

Client('127.0.0.1',6874)