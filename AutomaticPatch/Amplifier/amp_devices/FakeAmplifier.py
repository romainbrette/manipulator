"""
Fake multiclamp class in case no multiclamp is connected
"""

from AmpliferClass import *

__all__ = ['FakeAmplifier']


class FakeAmplifier(AmplifierClass):
    """
    Fake device representing a MultiClamp amplifer channel (i.e., one amplifier with
    two channels is represented by two devices).
    Does absolutly nothing.

    """

    def __init__(self):
        AmplifierClass.__init__(self)
        pass
