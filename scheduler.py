import logging
import random
import operator
import datetime
import time
from threading import Thread, Event, Lock

logging.basicConfig(filename="test.log",level=logging.DEBUG,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

class Task(object):
	def __init__(self, name, start_time, calc_next_time, func):
		self.name = name
		self.start_time = start_time
		self.scheduled_time = start_time
		self.calc_next_time = calc_next_time
		self.func = func

	def run(self):
		log.info("Running %s task, scheduled at: %s" % (self.name, self.scheduled_time,))
		
		print(".... Run task `%s`" % (self.name))
		try:
			try:
				self.func()
			except:
				raise
		finally:
			self.scheduled_time = self.calc_next_time(self.scheduled_time)
			log.info("Scheduled next run of %s for: %s" % (self.name, self.scheduled_time,))

class Scheduler(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.tasks = {}
		self.tasks_lock = Lock()
		self.halt_flag = Event()

	def schedule(self, name, start_time, calc_next_time, func):
		task = Task(name, start_time, calc_next_time, func)
		receipt = self.schedule_task(task)
		return receipt

	def schedule_task(self, task):
		receipt = random.random()
		self.tasks_lock.acquire()
		self.tasks[receipt] = task
		self.tasks_lock.release()
		
		return receipt

	def drop(self, task_receipt):

		self.tasks_lock.acquire()

		try:
			log.info(self.tasks)
			del self.tasks[task_receipt]
		except KeyError:
			log.info('Invalid task receipt: %s' % (task_receipt,))

		self.tasks_lock.release()

	def halt(self):
		self.halt_flag.set()
		
	def __find_next_task(self):

		self.tasks_lock.acquire()

		items = self.tasks.items()

		by_time = lambda x: operator.getitem(x, 1).scheduled_time
		items = list(items)
		items.sort(key=by_time)
		log.info("items:  %s " % items)

		receipt = items[0][0]

		log.info("receipt: %s" % receipt)

		self.tasks_lock.release()

		return receipt

	def run(self):
		while 1:
			if self.halt_flag.is_set():
				break
			receipt = self.__find_next_task()

			task_time = self.tasks[receipt].scheduled_time
			time_to_wait = task_time - datetime.datetime.now()
			secs_to_wait = 0.
			# Check if time to wait is in the future
			if time_to_wait > datetime.timedelta():
				secs_to_wait = time_to_wait.seconds

			log.info("Next task is %s in %s seconds" % (self.tasks[receipt].name, time_to_wait))

			self.halt_flag.wait(secs_to_wait)
			try:
				try:
					self.tasks_lock.acquire()
					task = self.tasks[receipt]
					log.info("Running %s..." % (task.name,))
					task.run()
				finally:
					self.tasks_lock.release()
			except Exception as e:
				logging.exception(e)


def every_x_secs(x):
	return lambda last: last + datetime.timedelta(seconds=x)

def every_x_mins(x):
	return lambda last: last + datetime.timedelta(minutes=x)

def daily_at(time):
	return lambda last: datetime.datetime.combine(last + datetime.timedelta(days=1), time)

class RunUntilSuccess(object):
	def __init__(self, func, *args, num_tries=10):
		self.func = func
		self.num_tries = num_tries
		self.args = args

	def __call__(self):

		try_count = 0
		is_success = False

		while not is_success and try_count < self.num_tries:
			try_count += 1
			try:
				if self.args:
					self.func(self.args)
				else:
					self.func()

				is_success = True
			except Exception as e: 
				logging.exception(e)
				logging.error("Task failed on try #%s" % (try_count,))
				continue

		if is_success:
			logging.info("Task %s was run successfully." % (self.func.__name__,))
		else:
			logging.error("Success was not achieved!")

#ex functions that wraps your logic/subprocess
def test():
	print("hello")

#ex functions that wraps your logic/subprocess
def sample():
	print("hi")

if __name__ == "__main__":
	task1 = Task(name="test", start_time=datetime.datetime.now(), calc_next_time=every_x_secs(2), func=RunUntilSuccess(test, num_tries=2))
	task2 = Task(name="sample", start_time=datetime.datetime.now(), calc_next_time=every_x_secs(3), func=sample)
	sched = Scheduler()
	a = sched.schedule_task(task1)
	b = sched.schedule_task(task2)
	sched.start()
	time.sleep(5)
	sched.drop(a)
	time.sleep(20)
	sched.halt()
	sched.join(30)
