import logging, random, operator, datetime
from threading import Thread, Event, Lock

class Task(object):
    def __init__(self, name, start_time, calc_next_time, func):
        """
        Initialize a Task.
        
        Arguments:
        name            - Name of task.
        start_time      - First time for task to run
        calc_next_time  - Function to calculate the time of next run, 
                          gets one argument, the last run time as a datetime.
                          Returns None when task should no longer be run
        func            - A function to run
        """
        self.name = name
        self.start_time = start_time
        self.scheduled_time = start_time
        self.calc_next_time = calc_next_time
        self.func = func
        self.halt_flag = Event()
        
    def run(self):
        logging.debug("Running %s task, scheduled at: %s" % (self.name, self.scheduled_time,))
        if not self.halt_flag.isSet():
            try:
                try:
                    self.func()
                except:
                    raise
            finally:
                self.scheduled_time = self.calc_next_time(self.scheduled_time)
                logging.debug("Scheduled next run of %s for: %s" % (self.name, self.scheduled_time,))
            
    def halt(self):
        self.halt_flag.set()
        
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
            self.tasks[task_receipt].halt()
            del self.tasks[task_receipt]
        except KeyError:
            logging.error('Invalid task receipt: %s' % (task_receipt,))
        self.tasks_lock.release()
        
    def halt(self):
        self.halt_flag.set()
        map(Task.halt, self.tasks.iteritems())
        
    def __find_next_task(self):
        self.tasks_lock.acquire()
        items = self.tasks.items()
        by_time = lambda x: operator.getitem(x, 1).scheduled_time
        items.sort(key=by_time)
        receipt = items[0][0]
        self.tasks_lock.release()
        return receipt
        
    def run(self):
        while 1:
            receipt = self.__find_next_task()
            task_time = self.tasks[receipt].scheduled_time  
            time_to_wait = task_time - datetime.datetime.now()
            secs_to_wait = 0.
            # Check if time to wait is in the future
            if time_to_wait > datetime.timedelta():
                secs_to_wait = time_to_wait.seconds
                
            logging.debug("Next task is %s in %s seconds" % (self.tasks[receipt].name, time_to_wait,))
            self.halt_flag.wait(secs_to_wait)
            try:
                try:
                    self.tasks_lock.acquire()
                    task = self.tasks[receipt]
                    logging.debug("Running %s..." % (task.name,))
                    task.run()
                finally:
                    self.tasks_lock.release()
            except Exception, e:
                logging.exception(e)

def every_x_secs(x):
    """
    Returns a function that will generate a datetime object that is x seconds
    in the future from a given argument.
    """
    return lambda last: last + datetime.timedelta(seconds=x)
    
def every_x_mins(x):
    """
    Returns a function that will generate a datetime object that is x minutes
    in the future from a given argument.
    """
    return lambda last: last + datetime.timedelta(minutes=x)    

def daily_at(time):
    """
    Returns a function that will generate a datetime object that is one day
    in the future from a datetime argument combined with 'time'.
    """
    return lambda last: datetime.datetime.combine(last + datetime.timedelta(days=1), time)
    
class RunUntilSuccess(object):
    """
    Provide control flow for a procedure.
    Run procedure until it throws no exceptions or exhausts
    its number of attempts.
    """
    def __init__(self, func, num_tries=10):
        self.func = func
        self.num_tries = num_tries

    def __call__(self):
        try_count = 0
        is_success = False
        while not is_success and try_count < self.num_tries:
            try_count += 1
            try:
                self.func()
                is_success = True
            except Exception, e:  # Some exception occurred, try again
                logging.exception(e)
                logging.error("Task failed on try #%s" % (try_count,))
                continue

        if is_success:
            logging.info("Task %s was run successfully." % (self.func.__name__,))
        else:
            logging.error("Success was not achieved!")
"""
Examples
``` import scheduler import datetime

Create a task called "foo", that runs a function named "might_fail" for up to five tries.
foo_task = scheduler.Task("foo", datetime.datetime.now(), scheduler.every_x_mins(30), scheduler.RunUntilSuccess(might_fail, num_tries=5))

Create a scheduler
my_scheduler = scheduler.Scheduler()

Add the foo task, a receipt is returned that can be used to drop the task from the scheduler
foo_receipt = my_scheduler.schedule_task(foo_task)

Once started, the scheduler will identify the next task to run and execute it.
my_scheduler.start()

Ok, no more foo
my_scheduler.drop(foo_receipt)

Let's add the bar task, it'll run for the first time at 9:30 AM tomorrow
and at 9:30 AM every day after.
tomorrow = datetime.datetime.now() + datetime.timedelta(days=1) tomorrow_at_930 = datetime.datetime.combine(tomorrow, datetime.time(9, 30)) my_scheduler.schedule(name="bar", start_time=tomorrow_at_930, calc_next_time=daily_at(datetime.time(9, 30)), func=bar_function)

Stop the scheduler
my_scheduler.halt()

Give it a timeout to halt any running tasks and stop gracefully
my_scheduler.join(100) ```
"""
