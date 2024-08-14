import deflib1
import numpy as np
import matplotlib.pyplot as plt

# suggest test data array of 1024 pixels with a few cosmic peaks
a = np.zeros(1024)
# add a cosmic peak at random pixels to a
a[100] = 30
a[200] = 40
a[270:272] = 31
a[300:302] = 50
a[310:320] = 25
a[400:402] = 30

b = 3
c = 20

plt.plot(a)
# call the cosmic removal function
data = deflib1.remove_cosmics(a, b, c)

plt.plot(data)
plt.legend(['Original', 'Cosmic Removed'])
plt.show()