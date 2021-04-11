import subprocess
import os


# os.environ["PYTHONUNBUFFERED"] = "1"


def create(time, port):
    python_run_command = 'py Node.py --port {} --time {}'.format(port, time)
    subprocess.Popen(python_run_command, shell=True, stdout=subprocess.PIPE)
    # print(python_run_command)