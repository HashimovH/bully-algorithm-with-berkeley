import socket
import argparse
import datetime
import time

def add_minutes(tm, minutes1):
	fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
	fulldate = fulldate + datetime.timedelta(minutes = minutes1)
	return fulldate.time()

class Node:
	HOST = '127.0.0.1'
	is_coordinator = False
	suspended = False

	def __init__(self, id_, label, time, port):
		self.id_ = id_
		self.label = label
		#12:34
		helper = [int(i) for i in time.split(":")]
		self.time = datetime.time(helper[0], helper[1])
		self.default_time = datetime.time(helper[0], helper[1])
		self.port = port
		self.K = 0

	def make_coordinator(self):
		self.is_coordinator = True

	def update_label(self):
		self.K += 1
		head, _ = self.label.split("_")
		self.label = head + "_" + str(self.K)

	def resetTime(self):
		self.time = self.default_time

	def updateTime(self):
		self.time = add_minutes(self.time, 1)

	def setTime(self, time_):
		helper = [int(i) for i in time_.split(":")]
		self.time = datetime.time(helper[0], helper[1])

	def __eq__(self, other):
		if(isinstance(other, Node)):
			return self.id_ == other.id_

	def __gt__(self, other):
		if(isinstance(other, Node)):
			return int(self.id_) > int(other.id_)

	def __lt__(self, other):
		return int(self.id_) < int(other.id_)

	def __str__(self):
		if(self.is_coordinator):
			return f"{self.id_}, {self.label}, {self.time} (Coordinator)"
		return f"{self.id_}, {self.label}, {self.time}"

	def identify(self):
		if self.suspended == False:
			if(self.is_coordinator):
				return f"{self.id_}, {self.label} (Coordinator)"
			return f"{self.id_}, {self.label}"
		else:
			return ""

	def get_port(self, id_):
		if self.id_==id_:
			return self.port

	def clockTime(self):
		a = self.time.strftime("%H:%M")
		return f"{self.label}, {a}"

	def setTime(self, newTime):
		self.time = newTime

	def processMessages(self, message):
		if message == "here?":
			if self.suspended == False:
				return "yes"
			else:
				return "no"
		elif message == "is_coordinator":
			if self.is_coordinator:
				return "yes"
			else:
				return "no"
		elif message == "kill":
			exit()
			return ""
		elif message == "id":
			return str(self.id_)
		elif message == "update":
			self.updateTime()
			return ""
		elif message == "clock":
			return self.clockTime()
		elif message == "make coordinator":
			self.make_coordinator()
			return ""
		elif message == "list":
			return self.identify()
		elif message.startswith("set"):
			listTime = [int(i) for i in message.split(" ")[1].split(":")]
			newTime = datetime.time(listTime[0], listTime[1])
			self.setTime(newTime)
			return ""
		elif message == "time":
			return self.time.strftime("%H:%M")
		elif message == "label":
			self.update_label()
			return ""
		elif message == "reset":
			self.resetTime()
			return ""
		elif message.strip() == "freeze":
			self.suspended = True
			return "freezed"
		elif message == "unfreeze":
			self.suspended = False
			return "unfreezed"




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

	