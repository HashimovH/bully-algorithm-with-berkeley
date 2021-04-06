import sys
import os
from random import randint
from random import choice
from create_process import create
from Node import Node
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

def CS(process_id, node_):
	print(f"P{process_id} is done with critical section")
	send_message("done", node_.port)


class Network:
	current_port = randint(10000, 60000)
	node_list = []
	queue_list = []
	threadToNode = {}
	#don't like this
	running = False
	def __init__(self, nodes):
		for node in nodes:
			process = Node(node[1], self.current_port)
			self.current_port += 1
			self.node_list.append(process)
	#change this to a class maybe? I dunno


	def prioritize(self, node):
		head = send_message("id", node.port)
		t = threading.Timer(10, CS, args = (head, node,))
		if(len(self.queue_list) == 0):
			#don't like this either
			self.queue_list.append(node)
			self.threadToNode[node] = t
			self.running = True
			t.start()
		else:
			#by default, it goes to the end of the lists
			id_ = len(self.queue_list) - 1
			for node_ in self.node_list:
				response = send_message("access", node_.port)
				if(response == ""):
					continue
				elif(response == "OK"):
					if(node_ in queue_list):
						id_ = min(id_, self.queue_list.index(node_))
			self.queue_list.insert(id_)
			self.threadToNode[node] = t
			send_message("wanted", node.port)

	def cycle(self):
		while(True):
			while(self.running):
				print("got here")
				if(len(self.queue_list) == 1):
					self.running = False
					self.queue_list = []
					self.threadToNode = {}

				elif(self.threadToNode[self.queue_list[0]].is_alive() == False):
					toRemove = queue_list.pop(0)
					self.threadToNode.pop(toRemove)
					self.threadToNode[self.queue_list[0]].start()
					send_message("work", self.queue_list[0].port)
			




	def get_command(self, command):
		message = ""
		if command.strip() == ('list'):
			# Let's check our each node to know it is there or not
			for node in self.node_list:
				#message += send_message("list", node.port) + '\n'
				print(node)
		elif command == 'exit':
			os._exit(0)
		elif command.startswith("access"):
			head = command.split(" ")[1]
			for node in self.node_list:
				if(node.timeStamp == head):
					send_message("work", node.port)
					self.prioritize(node)

		print(message)


if __name__ == '__main__':
	if len(sys.argv) < 2:
		print("Please enter input filename...")
		exit()

	filename = sys.argv[1]
	file_content = open(filename, "r")
	line = file_content.readline()
	nodes = line[1:-1].split(", ")
		
	net = Network(nodes)
	print("Network has been created")
	t1 = threading.Thread(target=lambda: net.cycle())
	t1.start()
	while True:
		print('Enter your command: ', end='$ ')
		cmd = input()
		net.get_command(cmd)
