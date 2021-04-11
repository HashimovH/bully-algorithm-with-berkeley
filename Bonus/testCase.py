import threading
test = "s1"
stillOngoing = True

def omegaPrinter():
	print("30 seconds huh")

def omegaPrinter2():
	print("second time is done")

threadList = []
t1 = threading.Timer(5.0, omegaPrinter)
threadList.append(t1)
#t1.start()
t2 = threading.Timer(5.0, omegaPrinter2)
threadList.append(t2)

"""
while(stillOngoing):
	if(len(threadList) == 1):
		stillOngoing = False

	if(threadList[0].is_alive() == False):
		threadList.pop(0)
		threadList[0].start()

print(threadList)
"""

list_ = "[P1, P2, P3, P4, P5]"
print(list_[1:-1].split(", ")[1])