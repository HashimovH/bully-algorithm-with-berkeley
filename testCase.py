import datetime

time_ = datetime.time(1, 20)
print(time_)

a =  time_.strftime("%H:%M")
print(a)

def add_timuntes(tm, minutes1):
	fulldate = datetime.datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
	fulldate = fulldate + datetime.timedelta(minutes = minutes1)
	return fulldate.time()

b = add_timuntes(time_, 1)

print(b)

time = "97:69"
hour,minute = [int(i) for i in time.split(":")]

print(hour)
print(minute)

omega = datetime.time(hour, minute)
