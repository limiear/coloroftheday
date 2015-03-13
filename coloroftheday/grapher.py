from datetime import datetime
import png
import numpy as np
from math import sqrt


def circle(x, y, r):
    return int(sqrt(x ** 2 + y ** 2) / r)


def layer(m, r):
    a, b = map(lambda d: d / 2, list(m.shape))
    fx = lambda ((x, y), v): v + circle(x - a, y - b, r) if v else v
    return np.array(map(fx, np.ndenumerate(m))).reshape(m.shape)


def draw(history, filename):
    color = history.get([datetime.today().date()])[0][1]
    to = lambda c: int(c, 16)
    to_rgb = lambda c: (to(c[0:2]), to(c[2:4]), to(c[4:6]))
    w = 1
    with open(filename, 'wb') as f:
        m = np.zeros((100,200))
        m[:w, :] = 1
        m[-w:, :] = 1
        m[:, :w] = 1
        m[:, -w:] = 1
        palette = [to_rgb(color), (0x00, 0x00, 0x00)]
        w = png.Writer(len(m[0]), len(m), palette=palette,
                       bitdepth=1)
        w.write(f, m)
    return [filename]
