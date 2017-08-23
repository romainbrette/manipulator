import matplotlib.pyplot as plt

with open('resistance2', 'rt') as f:
    resistance = [i for i in f]

graph = plt.plot(resistance)
plt.show(graph)
