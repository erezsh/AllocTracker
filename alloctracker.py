"AllocTracker - track allocations/acquires/opens to debug resource leaks"

import time
import logging
import traceback
from weakref import ref
import threading

class AllocTracker(object):
    log = logging.getLogger('AllocTracker')

    def __init__(self):
        self.objs = {}
        self.total = 0

    def logAlloc(self, obj, *args):
        stack = ''.join(traceback.format_stack()[:-1])

        if (ref(obj),args) in self.objs:
            self.log.warn("'alloc' call for an already allocated object")
            return

        # We use a ref to obj so we won't prevent its garbage collection
        # We rely on python's behaviour that calling ref twice on the same object returns the same ref object.
        self.objs[ (ref(obj),args) ] = (stack, time.time(), threading.currentThread())
        self.total += 1

    def logDealloc(self, obj, *args):
        try:
            del self.objs[ (ref(obj),args) ]
        except KeyError:
            self.log.warn("'dealloc' call for an unallocated object", exc_info=True)

    def dump(self, obj, *args):
        try:
            stack = self.objs[ (ref(obj),args) ]
            self.log.info( 'Allocation traceback for obj %s%s:\n%s' % (obj, args, stack ) )
        except KeyError:
            self.log.warn("'dump' call for an unallocated object")

    def dumpAll(self):
        self.log.info( ' --- Dumping all %d open allocations (out of %d) --- ', len(self.objs), self.total )
        for (objRef, args), (stack, acktime, thread) in self.objs.iteritems():
            meta = "%d secs ago at thread %s (%s)" % (acktime-time.time(), thread.name, ('Dead','Alive')[thread.isAlive()])
            obj = objRef()
            if obj:
                self.log.info( 'Allocation traceback for obj %s%s, %s:\n%s' % (obj, args, meta, stack ) )
            else:
                self.log.info( 'DEAD Allocation traceback for collected obj with args %s, %s:\n%s' % (args, meta, stack ) )


allocTracker = AllocTracker()

def _test():
    a = AllocTracker()
    a.logAlloc(a)
    a.logAlloc(a)
    a.logAlloc(a,2)
    a.dump(a)
    a.logDealloc(a)
    a.logDealloc(a)
    a.logAlloc(a,3)
    a.dumpAll()

