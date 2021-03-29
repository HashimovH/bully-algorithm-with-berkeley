import subprocess
import os


# os.environ["PYTHONUNBUFFERED"] = "1"


def create(id_, label, time, port):
    python_run_command = 'py node.py --id {} --port {} --time {} --label {}'.format(id_, port, time, label)
    subprocess.Popen(python_run_command, shell=True, stdout=subprocess.PIPE)
    # print(python_run_command)