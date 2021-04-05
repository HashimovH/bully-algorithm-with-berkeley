import sys
import os
from random import randint
from random import choice
from create_process import create
from node import Node
import socket
import time
import threading

def send_message(message, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sc:
        sc.settimeout(1)
        try:
            sc.connect(('127.0.0.1', port))
        except:
            return ''

        sc.send(message.encode('utf-8'))
        r_msg = sc.recv(2048).decode('utf-8')
        return r_msg


class Network:
	current_port = randint(10000, 60000)
	node_list = []
	suspended_list = []
	coordinator = None
	def __init__(self, nodes):
		for node in nodes:
			self.handleCreation(node[0], node[1], node[2][:-2])
			
			self.current_port += 1
		self.coordinator = self.startElection(default = True)
		send_message("make coordinator", self.coordinator.port)
		self.sync_clocks()
		time.sleep(1)


	def handleCreation(self, id_, label, time_):
		# add each node to the network with Node class
		# by default, change K to 0
		node_label = label.split("_")[0]
		# Create Node obj to store in the node_list
		node_obj = Node(id_, node_label+"_0", time_, self.current_port)
		create(node_obj.id_, node_obj.label, node_obj.time, node_obj.port)
		
		reply = send_message("here?", node_obj.port)
		if reply == "yes":
			# self.node_list.append((node[0], node_label+"_0", node[2], self.current_port))
			self.node_list.append(node_obj)
			print(f"Node {node_obj.label} has been created on PORT {self.current_port}")

	def get_command(self, command):
		message = ""
		if command.strip() == ('list'):
			# Let's check our each node to know it is there or not
			for node in self.node_list:
				message += send_message("list", node.port) + '\n'

		elif command.strip() == "clock":
			for node in self.node_list:
				message += send_message("clock", node.port) + '\n'

		elif command.startswith('kill'): #Solved?
			try:
				id_ = command.split(' ')[1]
			except:
				print("Please specify the process id")
				return
			for node in self.node_list:
				if node.id_ == id_:
					send_message("kill", node.port)
					print(f"Process {node.id_} is going to leave")
					self.node_list.remove(node)
					if node.is_coordinator:
						self.startElection()
					break

		elif command.startswith('freeze'):
			id_=0
			try:
				id_ = int(command.split(' ')[1])
			except:
				print("Please specify the process id")
				return
			print(f"Freezing id {id_}")
			for i in self.node_list:
				if int(i.id_)==id_:
					reply = send_message("freeze", i.port)
					if  reply == "freezed":
						print(f"Freezing Node with ID {i.id_} on PORT:{i.port}")
						self.suspended_list.append(i)
						self.node_list.remove(i)
					if i.is_coordinator:
						self.startElection()
						self.sync_clocks()
					break

		elif command.startswith('unfreeze'):
			id_=0
			try:
				id_ = int(command.split(' ')[1])
			except:
				print("Please specify the process id")
				return
			for i in self.suspended_list:
				if int(i.id_)==id_:
					reply = send_message("unfreeze", i.port)
					if  reply == "unfreezed":
						print(f"Unfreezing Node with ID {i.id_} on PORT:{i.port}")
						self.suspended_list.remove(i)
						self.node_list.append(i)
					self.startElection()
					self.sync_clocks()
					break
		
		# elif command.startswith('set-time'):
		# 	try:
		# 		id_ = command.split(' ')[1]
		# 		time = command.split(' ')[2]
		# 	except:
		# 		print("Please enter set-time command in a right way. (set-time <id> <time>)")
		# 		return

		# 	self.setTime(id_, time)
		# 	self.sync_clocks(self.coordinator, self.node_list)
		# 	print("Time has been updated and synced")

		elif command.startswith("reload"):
			file = None
			try:
				file = command.split(' ')[1]
			except:
				print("Please specify the input file name...")
				return
			self.reload(file)

		elif command.startswith("set"):
			try:
				helper = command.split(" ")
				node_ = helper[1]
				newTime = helper[2].strip()[:-2]
				self.setTime(int(node_), newTime)
			except IndexError as error:
				print("Not enough arguments, the use case is: set n hh:mm(am/pm)")

		elif command == 'exit':
			os._exit(0)

		print(message)
	#drift
	def testOmega(self):
		while True:
			time.sleep(60)
			send_message("update", self.coordinator.port)
			self.sync_clocks()


	def startElection(self, default = False):
		for node in self.node_list:
			send_message("reset", node.port)
		#didn't specify who starts it
		randomProcess = choice(self.node_list)
		#sorts by id_ (yes it does sort, i hope)
		sortedList = sorted(self.node_list)
		print(f"Process {randomProcess.id_} starts the election")
		ind = sortedList.index(randomProcess)
		while (ind != len(sortedList)):
			randomProcess = sortedList[ind]
			for node in sortedList[ind:]:
				if(send_message("here?", node.port) != "yes"):
					sortedList.pop(node)
			ind+=1

		randomProcess.make_coordinator()
		self.coordinator = randomProcess
		send_message("make coordinator", self.coordinator.port)
		print(f"Process {randomProcess.id_} is the new coordinator")
		if(default):
			for node in self.node_list:
				node.time = randomProcess.time
		else:
			self.sync_clocks(True)
		return randomProcess


	def setTime(self, process_id, time):
		for i in range(len(self.node_list)):
			if(int(self.node_list[i].id_) == int(process_id)):
				if(send_message(f"set {time}", self.node_list[i].port) == "Wrong format"):
					print("Input correct time format (hh:mm(am/pm)")
					break
				if(self.node_list[i] == self.coordinator):
					self.sync_clocks(True)
				#if the process was not the coordinator, sync must happen automatically
				print(f"Set time for process {process_id}")
				break


	def sync_clocks(self, newProcess = False):
		s = send_message("time", self.coordinator.port)
		for node in self.node_list:
			send_message(f"set {s}", node.port)
			if(newProcess):
				send_message("label", node.port)

	def reload(self, filename):
		file_content = open(filename, "r")
		helper = {}

		# Get the file contenct
		for line in file_content:
			helper[int(line.split(",")[0])] = [line.split(",")[1], line.split(",")[2].strip()]
		
		# Remove current nodes from the helper dictionary
		for i in self.node_list:
			if(int(i.id_ )in list(helper.keys())):
				helper.pop(int(i.id_))

		# Remove suspended nodes from the helper dictionary
		for s in self.suspended_list:
			if(int(s.id_) in list(helper.keys())):
				helper.pop(int(s.id_))

		if len(list(helper.keys()))==0:
			print("No need to reload")
			return

		for h in helper:
			label = helper[h][0]
			time_l = helper[h][1]
			node_label = label.split("_")[0]
			# Create Node obj to store in the node_list
			self.handleCreation(h, label, time_l[:-2])
			self.current_port += 1

		self.coordinator = self.startElection(default = True)
		send_message("make coordinator", self.coordinator.port)
		self.sync_clocks()
		time.sleep(1)






if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Please enter input filename...")
		exit()

	filename = sys.argv[1]
	file_content = open(filename, "r")
	nodes = []
	for line in file_content.readlines():
		line_splitted = line.split(', ')
		id_ = line_splitted[0].strip()
		label = line_splitted[1].strip()
		clock = line_splitted[2].strip()
		nodes.append((id_, label, clock))
		
	net = Network(nodes)
	print("Network has been created")
	print("""
	Command List:
	- list - Lists all the nodes
	- clock - Lists all the clocks of nodes
	- kill <process_id: int> - Kills the process with corresponding ID
	- set <process-id:int> <time:str>- Updates the time of specified node
	- freeze <process-id:int> - Freezes the specified process
	- unfreeze <process-id:int> - Unfreezes the specified process
	- reload <input-file:str> - Reloads the processes from the specified file 
		""")
	# Select coordinator
	# get commands and process
	t1 = threading.Thread(target=lambda: net.testOmega())
	t1.start()
	try:
		while True:
			print('Enter your command: ', end='$ ')
			cmd = input()
			net.get_command(cmd)
	except:
		os._exit(0)
