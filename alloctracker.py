"AllocTracker - track allocations/acquires/opens to debug resource leaks"

import logging
import traceback
from weakref import ref

logging.basicConfig(level=logging.DEBUG)

class AllocTracker(object):
    log = logging.getLogger('AllocTracker')

    def __init__(self):
        self.objs = {}

    def log_alloc(self, obj, *args):
        stack = ''.join(traceback.format_stack()[:-1])

        if (ref(obj),args) in self.objs:
            self.log.warn("'alloc' call for an already allocated object")
            return

        # We use a ref to obj so we won't prevent its garbage collection
        # We rely on python's behaviour that calling ref twice on the same object returns the same ref object.
        self.objs[ (ref(obj),args) ] = stack

    def log_dealloc(self, obj, *args):
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
        self.log.info( ' --- Dumping all open allocations --- ' )
        for (obj_ref, args), stack in self.objs.iteritems():
            obj = obj_ref()
            if obj:
                self.log.info( 'Allocation traceback for obj %s%s:\n%s' % (obj, args, stack ) )
            else:
                self.log.info( 'DEAD Allocation traceback for collected obj with args %s:\n%s' % (args, stack ) )


def _test():
    a = AllocTracker()
    a.log_alloc(a)
    a.log_alloc(a)
    a.log_alloc(a,2)
    a.dump(a)
    a.log_dealloc(a)
    a.log_dealloc(a)
    a.log_alloc(a,3)
    a.dumpAll()

_test()
