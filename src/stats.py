import math


SCALE = 10


def char_distribution(words: list[str], contains: list[str], logger) -> str:
    """ Returns a graph of char distribution

    Similar to the blow
             X
             X  X
        X    XXXX  XX   X
     X  XX  XXXXX  XXXX XX  X
    XXXXXXXXXXXXXXXXXXXXXXXXXX
    abcdefghijklmnopqrstuvwxyz
    """
    alpha = {
        'a': 0,
        'b': 0,
        'c': 0,
        'd': 0,
        'e': 0,
        'f': 0,
        'g': 0,
        'h': 0,
        'i': 0,
        'j': 0,
        'k': 0,
        'l': 0,
        'm': 0,
        'n': 0,
        'o': 0,
        'p': 0,
        'q': 0,
        'r': 0,
        's': 0,
        't': 0,
        'u': 0,
        'v': 0,
        'w': 0,
        'x': 0,
        'y': 0,
        'z': 0
    }
    _contains = []
    for char in contains:
        if isinstance(char, tuple):
            _contains.append(char[0])
        else:
            _contains.append(char)
    logger.debug(f"contains: {_contains}")
    logger.debug("populating alphadict")
    logger.debug(f"{words}")
    for word in words:
        logger.debug(f"{word}")
        for char in word:
            logger.debug(f"{char}")
            alpha[char] = alpha[char] + 1
    logger.debug(f"alpha: {alpha}")

    max_count = 0
    for char, value in alpha.items():
        if char not in _contains:
            max_count = max(value, max_count)

    matrix = []
    for char, value in alpha.items():
        if char not in _contains:
            temp = [char]
            logger.debug(f"max: {max_count}")
            val = math.floor((value/max_count)*SCALE)
            logger.debug(f"{char}, {value}, {val}")
            for _ in range(val):
                temp.append('X')

            for _ in range(SCALE-val):
                temp.append(' ')

            matrix.append(temp)

    logger.debug(f"{matrix}")
    output = ""

    for row in range(SCALE, -1, -1):
        for column in matrix:
            output = f"{output}{column[row]}"
        output = f"{output}\n"

    return output, alpha
