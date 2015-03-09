

def infer_spaces(s):
    """Uses dynamic programming to infer the location of spaces in a string
    without spaces."""
    out = find_words(s)
    return " ".join(out)


def find_words(instring, prefix='', words=None):
    if not instring:
        return []
    if words is None:
        words = set()
        with open('/usr/share/dict/words') as f:
            for line in f:
                words.add(line.strip())
    if (not prefix) and (instring in words):
        return [instring]
    prefix, suffix = prefix + instring[0], instring[1:]
    solutions = []
    # Case 1: prefix in solution
    if prefix in words:
        try:
            solutions.append([prefix] + find_words(suffix, '', words))
        except ValueError:
            pass
    # Case 2: prefix not in solution
    try:
        solutions.append(find_words(suffix, prefix, words))
    except ValueError:
        pass
    if solutions:
        return sorted(solutions,
                      key=lambda solution: [len(word) for word in solution],
                      reverse=True)[0]
    else:
        raise ValueError('no solution')
