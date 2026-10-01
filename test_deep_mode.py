from app import _run_query
class DummySlot:
    def empty(self): pass
    def markdown(self, text, **kwargs): pass
result = _run_query('Under what conditions can a seller forfeit earnest money or an advance payment?', DummySlot(), 'Deep Thinking')
print(result)
