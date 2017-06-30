from FakeAmplifier import *


class TemplateAmplifier(FakeAmplifier):
    """
    Template for making your own class to control your amplifier.
    Subclass of the FakeAmplifier so you can choose which methods to (re)define without worrying about others methods.
    Do not forget to update the __init__.py of the 'amp_devices' for further import.
    """
    def __init__(self):
        FakeAmplifier.__init__(self)
    pass

    # Here make your own methods
