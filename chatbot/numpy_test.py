import numpy as np
import math
ang = np.arange(180)
xo = np.sin(np.radians(ang))
noise = ((np.random.rand(180)*2)-1.0)/100.0
xn = xo+noise
print("xo = {}".format(xo))
print("xo+noise = {}".format(xn))