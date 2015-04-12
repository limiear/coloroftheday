from goslate import Goslate
from colordb import colors
import wordspliter


colors_dict = dict(colors)
translator = Goslate()

def rank_diff(color1, color2):
    diff = lambda c1, c2: abs(int(c1, 16) - int(c2, 16))
    return sum(map(lambda i: diff(color1[i: i+2], color2[i: i+2]),
                                  [0, 2, 4]))

def describe(color):
    to_sp = lambda name: translator.translate(name.lower(), "es", "en")
    if color in colors_dict.keys():
        name = to_sp(colors_dict[color])
    else:
        diffs = map(lambda c: rank_diff(c[0], color), colors)
        name = colors[diffs.index(min(diffs))][1]
        if not name.find(' '):
            name = wordspliter.infer_spaces(name)
        name = 'cercano al %s' % to_sp(name.lower())
    return name
