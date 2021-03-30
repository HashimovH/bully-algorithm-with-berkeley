import sys
from random import randint
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
		for node in nodes:
			# add each node to the network with Node class
			# by default, change K to 0
			node_label = node[1].split("_")[0]
			# Create Node obj to store in the node_list
			node_obj = Node(node[0], node_label+"_0", node[2], self.current_port)
			create(node_obj.id_, node_obj.label, node_obj.time, node_obj.port)
			time.sleep(1)
			reply = send_message("here?", node_obj.port)
			if reply == "yes":
				# self.node_list.append((node[0], node_label+"_0", node[2], self.current_port))
				self.node_list.append(node_obj)
				print(f"Node {node_obj.label} has been created on PORT {self.current_port}")
			
			self.current_port += 1
		time.sleep(1)



	def get_command(self, command):
		message = ""
		if command.strip() == ('list'):
			# Let's check our each node to know it is there or not
			for node in self.node_list:
				# if send_message("here?", node.port) == "yes":
				is_coordinator = send_message("is_coordinator", node.port)
				if is_coordinator == "yes":
					message += f"{node.id_}, {node.label} (Coordinator)\n"
				else:
					message += f"{node.id_}, {node.label}\n" # This should be changed. We should collect node objects not tuples.
		elif command.strip() == "clock":
			for node in self.node_list:
				message += f"{node.label}, {node.time}\n" # This should be changed. We should collect node objects not tuples.

		elif command.startswith('kill'): # Has problem
			id_ = command.split(' ')[1]
			for node in self.node_list:
				if node.id_ == id_:
					send_message("kill", node.port)
					print(f"Process {node.id_} is going to leave")
					if node.is_coordinator:
						pass # New election
					
					self.node_list.remove(node)
					break

		print(message)


	def default_election(self):
		pass # First time election

	def apply_bully(self):
		pass

	def sync_clocks(self):
		pass

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
