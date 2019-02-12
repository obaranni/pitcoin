import os
import threading
import time
import sys


class myThread1 (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      premine()

class myThread2 (threading.Thread):
   def __init__(self, threadID, name, counter):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
      self.counter = counter
   def run(self):
      run_server()

def premine():
    print("Thread2 sleep 10")
    time.sleep(8)
    print("\n\nThread2 run premine")
    output = os.popen('python3 ./premine.py').read()
    print(output)

def run_server():
    print("Thread1 run server")
    os.system('python3 api/api.py')




# Create new threads
if len(sys.argv) > 1 and sys.argv[1] == '-pre':
    thread1 = myThread1(1, "Thread-1", 1)
thread2 = myThread2(2, "Thread-2", 2)

# Start new Threads
if len(sys.argv) > 1 and sys.argv[1] == '-pre':
    thread1.start()
thread2.start()
if len(sys.argv) > 1 and sys.argv[1] == '-pre':
    thread1.join()
thread2.join()
print ("Exiting Main Thread")