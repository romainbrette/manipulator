__all__ = ['FakeOB1']


class FakeOB1(object):

    def __init__(self):
        self.val = 0.
        pass

    def measure(self, port=0):
        return self.val

    def set_pressure(self, port=0):
        pass
