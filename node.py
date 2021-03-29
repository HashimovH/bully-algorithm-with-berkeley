import socket
import argparse

class Node:
	HOST = '127.0.0.1'

	def __init__(self, id_, label, time, port):
		self.id_ = id_
		self.label = label
		self.time = time
		self.port = port


	def processMessages(self, message):
		if message == "here?":
			return "yes"

	def join(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
			_socket.bind((Node.HOST, self.port))
			_socket.listen()
			print(f'Node {self.id_} has been created on PORT {self.port}')
			while True:
				con, _ = _socket.accept()
				with con:
					message = con.recv(2048).decode('utf-8').rstrip('\n')

					if message == 'bye':
						print(f'Node {self.id_}: I am going out..')
						break

					response = self.processMessages(message)

					con.send(response.encode('utf-8'))


if __name__ == '__main__':
	print("Node file is running")
	parser = argparse.ArgumentParser(description="Create a new node")
	parser.add_argument('--id', type=int, help='Id of the node')
	parser.add_argument('--port', type=int, help='Port of the node')
	parser.add_argument('--time', type=str, help='The time on port')
	parser.add_argument('--label', type=str, help='The label of the port')
	args = parser.parse_args()
	node = Node(args.id, args.label, args.time, args.port)
	node.join()

