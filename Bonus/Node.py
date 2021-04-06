import socket
import argparse

class Node:
	HOST = '127.0.0.1'
	holding = False
	wanted = False
	doNotWant = True

	def __init__(self, timeStamp, port):
		self.timeStamp = timeStamp
		self.port = port

	def __eq__(self, other):
		if(isinstance(other, Node)):
			return self.timeStamp == other.timeStamp

	def __gt__(self, other):
		if(isinstance(other, Node)):
			return int(self.timeStamp) > int(other.timeStamp)

	def __lt__(self, other):
		return int(self.timeStamp) < int(other.timeStamp)

	def __str__(self):
		return f"P:{self.timeStamp}"

	def __hash__(self):
		return hash(self.timeStamp)

	def putWanting(self):
		self.wanted = True
		self.wanted = False
		self.doNotWant = False

	def holding(self):
		self.holding = True
		self.wanted = False
		self.doNotWant = False

	def doNotWant(self):
		self.doNotWant = True
		self.holding = False
		self.wanted = False

	def processMessages(self, message):
		if message == "kill":
			exit()
			return ""
		elif message.startswith("acceess"):
			helper = message.split(" ")
			other_stamp = helper[1]
			if(self.wanted):
				if(other_stamp < self.timeStamp):
					return "OK"
				else:
					return ""
			elif(self.doNotWant):
				return "OK"
			elif(self.holding):
				return ""
		elif message == "id":
			return self.timeStamp
		elif message == "work":
			self.holding()
		elif message == "done":
			self.doNotWant()
		elif message == "wanted":
			self.wanted()
		elif message == "list":
			return self.__str__()
	def join(self):
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
			_socket.bind((Node.HOST, self.port))
			_socket.listen()
			print(f'Node {self.timeStamp} has been created on PORT {self.port}')
			while True:
				con, _ = _socket.accept()
				with con:
					message = con.recv(2048).decode('utf-8').rstrip('\n')

					if message == 'bye':
						print(f'Node {self.timeStamp}: I am going out..')
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

	