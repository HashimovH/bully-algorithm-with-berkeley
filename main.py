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
	
	def __init__(self, nodes):
		for node in nodes:
			# add each node to the network with Node class
			# by default, change K to 0
			node_label = node[1].split("_")[0]
			create(node[0], node_label+"_0", node[2],self.current_port)
			time.sleep(1)
			reply = send_message("here?", self.current_port)
			if reply == "yes":
				print(f"Node {node[0]} has been created on PORT {self.current_port}")
			
			self.current_port += 1

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
		
	# Create the network
	net = Network(nodes)
	print("Network has been created")

	# Select coordinator

	# get commands and process
