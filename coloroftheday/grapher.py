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
    template = png.Reader('picker_mask.png')
    meta = template.asDirect()
    meta[3]['background'] = to_rgb(color)
    with open(filename, 'wb') as f:
        w = png.Writer(**meta[3])
        w.write(f, meta[2])
    return [filename]
