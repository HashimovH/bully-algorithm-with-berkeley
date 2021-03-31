import socket
import argparse

class Node:
	HOST = '127.0.0.1'
	is_coordinator = False

	def __init__(self, id_, label, time, port):
		self.id_ = id_
		self.label = label
		self.time = time
		self.default_time = time
		self.port = port
		self.K = 0

	def make_coordinator(self):
		self.is_coordinator = True

	def update_label(self):
		head, _ = self.label.split("_")
		self.label = head + "_" + str(self.K)

	def resetTime(self):
		self.time = self.default_time

	def updateTime(self, time):
		self.time = time

	def __eq__(self, other):
		if(isinstance(other, Node)):
			return self.id_ == other.id_

	def __gt__(self, other):
		if(isinstance(other, Node)):
			return self.id_ > other.id_

	def __lt__(self, other):
		return self.id_ < other.id_

	def __str__(self):
		if(self.is_coordinator):
			return f"{self.id_}, {self.label}, {self.time} (Coordinator)"
		return f"{self.id_}, {self.label}, {self.time}"

	def identify(self):
		if(self.is_coordinator):
			return f"{self.id_}, {self.label} (Coordinator)"
		return f"{self.id_}, {self.label}"

	def clockTime(self):
		return f"{self.label}, {self.time}"

	def processMessages(self, message):
		if message == "here?":
			return "yes"
		elif message == "list":
			return "yes"
		elif message == "is_coordinator":
			if self.is_coordinator:
				return "yes"
			else:
				return "no"
		elif message == "kill":
			exit()
		elif message == "id":
			return str(self.id_)

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

	