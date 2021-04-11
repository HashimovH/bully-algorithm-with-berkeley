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
#change this to a class maybe? I dunno
#but this is the critical section, it doesn't do anything other than signify when the thread is done
def CS(process_id, node_):
	print(f"P{process_id} is done with critical section")
	send_message("done", node_.port)


class Network:
	current_port = randint(10000, 60000)
	#all the nodes
	node_list = []
	#the queue of nodes wanting CS
	queue_list = []
	#hashmap showing which node belongs to what thread
	threadToNode = {}
	#don't like this, but this shows if there is a proccess running
	running = False

	#create port and timestamp, simple
	def __init__(self, nodes):
		for node in nodes:
			process = Node(node[1], self.current_port)
			self.current_port += 1
			self.node_list.append(process)
	

	#queue priority
	#create a thread for 10 seconds (should be 30, but testing)
	#and we have to see when we should run the thread
	def prioritize(self, node):
		head = send_message("id", node.port)
		t = threading.Timer(10, CS, args = (head, node,))
		#if nothing is in the queue, put it at the start and run, simple
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
				#empty response means that it is using CS or timeStamp is lower, meaning higher priority
				if(response == ""):
					continue
				#this means that the timeStamp is higher, so the node has priority
				elif(response == "OK"):
					#track the best position for our node
					id_ = min(id_, self.queue_list.index(node_))
			#add it in the queue
			self.queue_list.insert(id_)
			#mark the thread
			self.threadToNode[node] = t
			#send the message that it is wanted
			send_message("wanted", node.port)
	#this is a constant function that runs ALWAYS, so be careful
	def cycle(self):
		#to make sure the thread always runs
		while(True):
			#to make sure this part only runs when there is something in the queue
			while(self.running):
				#test
				print("got here")
				#if only one element in the queue, that means it's the last one
				# and we can stop this inner while cycle and reset the lists
				if(len(self.queue_list) == 1):
					self.running = False
					self.queue_list = []
					self.threadToNode = {}
				#check to see if the first process in the queue list is running
				#if it is not, time to pop it and run the second one
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
