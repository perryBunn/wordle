""" Worlde.py """
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

import argparse
import logging
import math

from tqdm import tqdm

import yaml


iters = {
    0: "first",
    1: "second",
    2: "third",
    3: "fourth",
    4: "fifth",
    5: "sixth"
}

SCALE = 10


def get_logger(alg_info: dict) -> logging.Logger:
    """ Generates logger object """
    logger = logging.getLogger(alg_info["NAME"])
    level = logging.getLevelName(alg_info["LEVEL"])
    logger.setLevel(level)

    now = datetime.now()
    log_dir = Path(alg_info["LOG_DIR"])
    log_dir.mkdir(exist_ok=True)
    rotate_file = RotatingFileHandler(log_dir / f"wordle_{now.strftime('%Y%m%d')}.log")

    fmtstr = "'%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(fmtstr)
    rotate_file.setFormatter(formatter)

    logger.addHandler(rotate_file)
    return logger


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

    output = ""
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

    for row in range(SCALE, -1, -1):
        for column in matrix:
            output = f"{output}{column[row]}"
        output = f"{output}\n"

    return output, alpha


def get_nchars(contains: list[str], previous: list[str], logger) -> list[str]:
    neg_chars = []
    # Get list of chars that are not in the word from previous guesses.
    for word in previous:
        for char in word:
            if char not in contains and char not in neg_chars:
                neg_chars.append(char)
    logger.debug(f"negative chars: {neg_chars}")
    return neg_chars


def get_neg_words(available: list[str], neg_chars: list[str], logger) -> list[str]:
    # for available words, if word contains a negative char, remove from available list
    neg_words = []
    for word in tqdm(available, desc="Preprocessor"):
        logger.debug(f"{word}")
        for nchar in neg_chars:
            if word not in available:
                continue
            if nchar in word:
                neg_words.append(word)
                continue
            logger.debug(f"\t{word} does not contain {nchar}")

    logger.debug(f"negative words: {neg_words}")
    logger.debug(f"num negative words: {len(neg_words)}")
    return neg_words


def get_neg_positions(cchars: list, available: list[str], previous: list[str], logger) -> list[str]:
    neg_positions = []
    for char in tqdm(cchars, desc="Postprocessor"):
        logger.debug(f"{char}")
        if isinstance(char, tuple):
            continue
        for word in available:
            if char in word:
                for pword in previous:
                    if char not in pword:
                        continue
                    pindex = pword.index(char)
                    if word[pindex] == char:
                        neg_positions.append(word)

    return neg_positions


def get_guess(available: list[str], distribution: dict, logger) -> str:
    size = len(available)
    guesses = []
    for word in tqdm(available, desc="Getting guesses"):
        den = []
        density = 1
        for char in word:
            den.append(distribution[char]/size)
        for i in den:
            density *= i
        guesses.append((word, density))
    guesses = sorted(guesses, key = lambda x: x[1], reverse=True)
    logger.debug(guesses)
    return guesses[:5], guesses[-5:]


def get_possible(cchars: list, available: list[str], previous: list[str], logger) -> list:
    """ Returns a list of possible strings """
    _available = available.copy()
    logger.debug(f"Available: {_available}")
    contains = []
    for chars in cchars:
        if isinstance(chars, tuple):
            contains.append(chars[0])
        else:
            contains.append(chars)

    neg_chars = get_nchars(contains, previous, logger)

    neg_words = get_neg_words(_available, neg_chars, logger)

    preproc = list(set(_available) - set(neg_words))
    logger.debug(f"preprocessed: {preproc}")

    pre_temp = []
    # For words left in preproc, if the correct chars are not in the correct
    # positions or contained in the word remove them from the list.
    for word in tqdm(preproc, desc="Processer"):
        logger.debug(f"{word}")
        for char in cchars:
            logger.debug(f"\t{char}, {type(char)}")
            if isinstance(char, tuple):
                logger.debug(f"\t{word}, {word[char[1]]}, {char}")
                if word[char[1]] != char[0]:
                    logger.debug(f"\t{word[char[1]]} != {char[0]}")
                    pre_temp.append(word)
                    break
                logger.debug(f"\t{word} has a valid position for {char[0]}")
            else:
                if char not in word:
                    pre_temp.append(word)
                    break
                logger.debug(f"\t{word} is valid for {char}")

    postproc = list(set(preproc) - set(pre_temp))
    logger.debug(f"postprocessed: {postproc}")
    post_temp = get_neg_positions(cchars, postproc, previous, logger)
    output = list(set(postproc) - set(post_temp))
    logger.debug(f"output: {output}")
    return output


def game(alg_spec: dict, logger: logging.Logger):
    """ Game loop """
    available = []
    with open(alg_spec["WORD_FILE"], encoding="utf-8") as file:
        for line in file:
            available.append(line.strip())

    guesses = []
    correct_chars = []

    print(f"Possible words: {len(available)}")
    # print("Char Distribution:")
    # graph, _ = char_distribution(available, correct_chars, logger)
    # print(graph)

    for i in range(6):
        correct, known = '', ''
        guess = input(f"What word is your {iters[i]} guess? ")
        guesses.append(guess)
        res = input("Are any of the letters green or yellow? (g|y|n)" \
                    "\nIf there are both green and yellow letters respond " \
                    "with both g and y. ")
        if 'g' not in res and 'y' not in res and 'n' not in res:
            print(f"{res} is not an acceptable response.")
            return
        if 'g' in res:
            correct = input("Which letters are green? ")
            if len(correct) > 1:
                for char in correct:
                    if char not in guess:
                        print(f"At least 1 of those letters is not in {guess}.")
            if correct not in guess:
                print(f"That letter is not in {guess}.")
        if 'y' in res:
            known = input("Which letters are yellow? ")
            if len(known) > 1:
                for char in known:
                    if char not in guess:
                        print(f"At least 1 of those letters is not in {guess}.")
            if known not in guess:
                print(f"That letter is not in {guess}.")

        logger.debug(f"Correct: {correct}")
        logger.debug(f"Known {known}")

        for char in correct:
            position = None
            if guess.count(char) > 1:
                position = int(input(f"There are more than one occurrences of {char}. Enter the position of {char}, where {guess[0]} is 1: ")) - 1
            if char in correct_chars:
                _ = correct_chars.pop(correct_chars.index(char))
            if position:
                place = (char, position)
            else:
                place = (char, guess.index(char))
            correct_chars.append(place)
        for char in known:
            correct_chars.append(char)

        logger.debug(f"Correct characters: {correct_chars}")
        possible_words = get_possible(correct_chars, available, guesses, logger)
        available = possible_words.copy()

        print("Remaining possible words:")
        while possible_words:
            try:
                output = possible_words.pop()
                for _ in range(14):
                    output = f"{output}, {possible_words.pop()}"
                print(output)
            except IndexError:
                pass
        print(output, f"\nTotal remaining: {len(available)}")

        if len(available) == 1:
            break

        print("\nChar Distribution:")
        graph, distribution = char_distribution(available.copy(), correct_chars, logger)
        print(graph)

        top_guesses, _ = get_guess(available.copy(), distribution, logger)
        print("Best Guesses:")
        for best in top_guesses:
            print(f"  - {best[0]}")



    print("Better luck tomorrow")

def main(conf_path: str):
    """ Driver """
    config = Path(conf_path)
    with open(config.as_posix(), encoding="utf-8") as file:
        application_conf = yaml.safe_load(file.read())
    logger = get_logger(application_conf["info"])
    logger.debug(application_conf)
    game(application_conf["spec"], logger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Because machines are smarter than you.')
    parser.add_argument('config', nargs="?", help="application.yaml file")
    args = parser.parse_args()
    conf = Path("./application.yaml")
    if args.config:
        conf = Path(args.config)
    main(conf)
