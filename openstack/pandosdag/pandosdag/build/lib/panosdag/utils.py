import eventlet.semaphore

class RWLock(object):
    def __init__(self):
        self.num_readers = 0
        self.num_writers = 0

        self.m1 = eventlet.semaphore.Semaphore(1)
        self.m2 = eventlet.semaphore.Semaphore(1)
        self.m3 = eventlet.semaphore.Semaphore(1)
        self.w = eventlet.semaphore.Semaphore(1)
        self.r = eventlet.semaphore.Semaphore(1)

    def lock(self):
        self.m2.acquire()

        self.num_writers += 1
        if self.num_writers == 1:
            self.r.acquire()

        self.m2.release()
        self.w.acquire()

    def unlock(self):
        self.w.release()
        self.m2.acquire()

        self.num_writers -= 1
        if self.num_writers == 0:
            self.r.release()

        self.m2.release()

    def rlock(self):
        self.m3.acquire()
        self.r.acquire()
        self.m1.acquire()

        self.num_readers += 1
        if self.num_readers == 1:
            self.w.acquire()

        self.m1.release()
        self.r.release()
        self.m3.release()

    def runlock(self):
        self.m1.acquire()

        self.num_readers -= 1
        if self.num_readers == 0:
            self.w.release()

        self.m1.release()
