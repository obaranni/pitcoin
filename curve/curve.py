import matplotlib.pyplot as plt
import numpy as np

a = len("Barannik")
b = len("Oleksandr")
y, x = np.ogrid[-10:10:1000j, -10:10:1000j]
z = pow(y, 2) - pow(x, 3) - x * a - b
plt.contour(x.ravel(), y.ravel(), z, [0])
plt.xlabel("x axis")
plt.ylabel("y axis")
plt.grid()
plt.show()
