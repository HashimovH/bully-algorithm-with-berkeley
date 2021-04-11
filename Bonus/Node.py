import socket
import argparse

class Node:
	HOST = '127.0.0.1'
	#is using CS
	HOLD = False
	#wants to use it, but has to wait
	want = False
	#doesn't care
	DNW = True

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
		if(self.HOLD):
			return f"P:{self.timeStamp} (Holding)"
		elif(self.want):
			return f"P:{self.timeStamp} (Wanting)"
		elif(self.DNW):
			return f"P:{self.timeStamp} (Do Not Want)"

	def __hash__(self):
		return hash(self.timeStamp)

	def putWanting(self):
		self.HOLD = False
		self.want = True
		self.DNW = False

	def holding(self):
		self.HOLD = True
		self.want = False
		self.DNW = False

	def doNotWant(self):
		self.DNW = True
		self.HOLD = False
		self.want = False

	def showHolding(self):
		if(self.HOLD):
			return "Yes"
		else:
			return "No"

	def processMessages(self, message):
		if message == "kill":
			exit()
			return ""
		elif message.startswith("access"):
			helper = message.split(" ")
			other_stamp = helper[1]
			if(self.want):
				if(int(other_stamp) < int(self.timeStamp)):
					return "OK"
				else:
					return ""
			elif(self.DNW):
				return "OK"
			elif(self.HOLD):
				return ""
		elif message == "id":
			return self.timeStamp
		elif message == "work":
			self.holding()
			return ""
		elif message == "done":
			self.doNotWant()
			return ""
		elif message == "wanted":
			self.putWanting()
			return ""
		elif message == "list":
			return self.__str__()
		elif message == "show":
			return self.showHolding()
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
	# parser.add_argument('--id', type=int, help='Id of the node')
	parser.add_argument('--port', type=int, help='Port of the node')
	parser.add_argument('--time', type=str, help='The time on port')
	# parser.add_argument('--label', type=str, help='The label of the port')
	args = parser.parse_args()
	node = Node(args.time, args.port)
	node.join()

	