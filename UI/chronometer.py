# -*- coding: utf-8 -*-
import timeit

class Chronometer(object):
    
    def __init__(self):
        self.start_time = timeit.default_timer()
    
    def end(self, msg):
        self.total = timeit.default_timer() - self.start_time
        print '{} in {:0.3f} seconds'.format(msg, self.total)
        
