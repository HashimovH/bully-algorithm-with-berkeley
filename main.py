import sys
from random import randint
from random import choice
from create_process import create
from node import Node
import socket
import time

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
	def __init__(self, nodes):
		biggest_node = None
		for node in nodes:
			# add each node to the network with Node class
			# by default, change K to 0
			node_label = node[1].split("_")[0]
			# Create Node obj to store in the node_list
			node_obj = Node(node[0], node_label+"_0", node[2][:-2], self.current_port)
			if(biggest_node == None or biggest_node.id_ < node_obj.id_):
				biggest_node = node_obj
			create(node_obj.id_, node_obj.label, node_obj.time, node_obj.port)
			#is this needed?
			#time.sleep(1)
			reply = send_message("here?", node_obj.port)
			if reply == "yes":
				# self.node_list.append((node[0], node_label+"_0", node[2], self.current_port))
				self.node_list.append(node_obj)
				print(f"Node {node_obj.label} has been created on PORT {self.current_port}")
			
			self.current_port += 1
		self.default_election(biggest_node)
		self.sync_clocks(biggest_node, self.node_list)
		time.sleep(1)



	def get_command(self, command):
		message = ""
		if command.strip() == ('list'):
			# Let's check our each node to know it is there or not
			for node in self.node_list:
				# if send_message("here?", node.port) == "yes":
				is_coordinator = send_message("is_coordinator", node.port)
				#if is_coordinator == "yes":
					#message += f"{node.id_}, {node.label} (Coordinator)\n"
				#else:
					#message += f"{node.id_}, {node.label}\n" # This should be changed. We should collect node objects not tuples.
				message += node.identify() + '\n'
		elif command.strip() == "clock":
			for node in self.node_list:
				#message += f"{node.label}, {node.time}\n" # This should be changed. We should collect node objects not tuples.
				message += node.clockTime() + '\n'

		elif command.startswith('kill'): # Has problem
			id_ = command.split(' ')[1]
			for node in self.node_list:
				if node.id_ == id_:
					send_message("kill", node.port)
					print(f"Process {node.id_} is going to leave")
					self.node_list.remove(node)
					if node.is_coordinator:
						self.startElection()
					break
		elif command.startswith('set-time'):
			id_ = command.split(' ')[1]
			time = command.split(' ')[2]
			self.setTime(id_, time)

		print(message)

	#is this java?
	def default_election(self, node):
		node.make_coordinator()

	def startElection(self):
		for node in self.node_list:
			node.resetTime()
		#didn't specify who starts it
		randomProcess = choice(self.node_list)
		#sorts by id_ (yes it does sort, i hope)
		sortedList = sorted(self.node_list)
		print(f"Process {randomProcess.id_} starts the election")
		ind = sortedList.index(randomProcess)
		while (ind != len(sortedList)):
			randomProcess = sortedList[ind]
			for node in sortedList[ind:]:
				if(node.processMessages("here?") != "yes"):
					sortedList.pop(node)
			ind+=1

		randomProcess.make_coordinator()
		print(f"Process {randomProcess.id_} is the new coordinator")
		self.sync_clocks(randomProcess, self.node_list, True)


	#hmmm
	def apply_bully(self):
		pass

	def setTime(self, process_id, time):
		for i in range(len(self.node_list)):
			if(self.node_list[i].id_ == process_id):
				self.node_list[i].updateTime(time)
				if(self.node_list[i].is_coordinator):
					self.sync_clocks(self.node_list[i], self.node_list, True)
				#if the process was not the coordinator, sync must happen automatically
				break


	def sync_clocks(self, coordinator, nodes, newProcess = False):
		s = coordinator.time
		for node in nodes:
			node.time = s
			if(newProcess):
				node.K+=1
				node.update_label()


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
		
	# Create the network
	net = Network(nodes)
	print("Network has been created")

	# Select coordinator

	# get commands and process
	while True:
		print('Enter your command: ', end='$ ')
		cmd = input()
		net.get_command(cmd)
