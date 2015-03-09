from translate import Translator
from colordb import colors
import wordspliter


colors_dict = dict(colors)
translator = Translator(from_lang="en", to_lang="es")


def describe(color):
    if color in colors_dict.keys():
        name = colors_dict[color]
    else:
        diff = lambda c1, c2: abs(int(c1, 16) - int(c2, 16))
        rank = lambda c1, c2: sum(map(lambda i: diff(c1[i: i+2], c2[i: i+2]),
                                      [0, 2, 4]))
        diffs = map(lambda c: rank(c[0], color), colors)
        color = colors[diffs.index(min(diffs))][1]
        color = wordspliter.infer_spaces(color)
        name = 'Closest to %s' % color
    return translator.translate(name.lower()).capitalize()
