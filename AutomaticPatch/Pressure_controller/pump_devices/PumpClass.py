__all__ = ['PumpClass']


class PumpClass(object):
    """
    Base class to build a new Pump subclass and ensure full compatibility with the other scripts.
    Do not forget to update the __init__.py file in pump devices directory to import your subclass.
    """

    def __init__(self):
        pass

    def measure(self):
        """
        Measure pressure once
        :return: 
        """
        pass

    def set_pressure(self, pressure):
        """
        Set pressure at desired value in mBar
        :param pressure: Pressure in mBar
        :return: 
        """
        pass
