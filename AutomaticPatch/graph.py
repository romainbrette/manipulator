import matplotlib.pyplot as plt

with open('resistance2', 'rt') as f:
    resistance = [i for i in f]

graph = plt.plot(resistance)
plt.ylabel('Resistance in Ohm')
plt.xlabel('Time by tick')
plt.show(graph)
