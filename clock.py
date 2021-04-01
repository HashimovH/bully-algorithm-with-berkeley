import argparse
import socket
from main import send_message
import time


if __name__ == '__main__':
	print("Clock server is running")
	parser = argparse.ArgumentParser(description="Create a new Clock")
	parser.add_argument('--port', type=int, help='Port of the node')
	parser.add_argument('--start', type=str, help='The time on port')
	args = parser.parse_args()
	port = args.port
	start = args.start

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as _socket:
		_socket.bind(("127.0.0.1", 9997))
		_socket.listen()
		print(f'Clock server is running on PORT 9999')
		while True:
			time.sleep(60)
			hour = int(start.split(":")[0])
			minute = int(start.split(":")[1])
			minute += 1
			if minute > 60:
				minute == 0
				hour += 1
				if hour > 24:
					hour = 0
					minute = 0
			start = f"{str(hour).zfill(2)}:{str(minute).zfill(2)}"
			send_message("Clock-"+start, port)
			print(start)

	