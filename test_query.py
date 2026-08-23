import sys
import os
from app import _run_query
class MockSlot:
    def empty(self): pass
    def markdown(self, *args, **kwargs): print('UI:', args[0])
print(_run_query('Can a government contractor lose their earnest money if the government suffered no actual loss?', MockSlot(), 'Deep Thinking'))
