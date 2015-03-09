from datetime import datetime
import png
import numpy as np


def draw(history, filename):
    color = history.get([datetime.today().date()])[0][1]
    to = lambda c: int(c, 16)
    to_rgb = lambda c: (to(c[0:2]), to(c[2:4]), to(c[4:6]))
    with open(filename, 'wb') as f:
        m = np.zeros((200, 300))
        m[:10, :] = 1
        m[-10:, :] = 1
        m[:, :10] = 1
        m[:, -10:] = 1
        palette = [to_rgb(color), (0x00, 0x00, 0x00)]
        w = png.Writer(len(m[0]), len(m), palette=palette, bitdepth=1)
        w.write(f, m)

        pass
    return [filename]
