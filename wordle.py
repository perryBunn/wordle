""" Worlde.py """
from pathlib import Path
from typing import Union

import argparse
import logging
import re
import yaml
import sys


iters = {
    0: "first",
    1: "second",
    2: "third",
    3: "fourth",
    4: "fifth",
    5: "sixth"
}


def get_logger():
    """ Generates logger object """


def get_possible(cchars: list, available: list[str], previous: list[str]) -> list:
    """ Returns a list of possible strings """
    _available = available.copy()
    print("Available:", _available)
    contains = []
    for chars in cchars:
        if isinstance(chars, tuple):
            contains.append(chars[0])
        else:
            contains.append(chars)

    neg_chars = []
    # Get list of chars that are not in the word from previous guesses.
    for word in previous:
        for char in word:
            if char not in contains and char not in neg_chars:
                neg_chars.append(char)
    print("negative chars:", neg_chars)
    neg_words = []
    # for available words, if word contains a negative char, remove from available list
    for word in _available:
        print(word)
        for nchar in neg_chars:
            # print("\t", nchar)
            if word not in _available:
                continue
            if nchar in word:
            #     print(f"\tAbout to remove {word}, index: {_available.index(word)}")
            #     print(_available[_available.index(word)])
            #     nword = _available.pop(_available.index(word))
                neg_words.append(word)
                continue
            print(f"\t{word} does not contain {nchar}")

    print("negative words:", neg_words)
    print("num negative words:", len(neg_words))

    preproc = list(set(_available) - set(neg_words))
    print("preprocessed:", preproc)
    temp = []
    for word in preproc:
        print(word)
        for char in cchars:
            print("\t", char, type(char))
            if isinstance(char, tuple):
                print("\t", word, word[char[1]], char)
                if word[char[1]] != char[0]:
                    print("\t", word[char[1]], "!=", char[0])
                    try:
                        # print(f"\tAbout to remove {word}, index: {preproc.index(word)}")
                        # print("word from index:", preproc[preproc.index(word)])
                        # preproc.pop(preproc.index(word))
                        temp.append(word)
                        break
                    except ValueError:
                        print(f"\tError thrown trying to pop {word}")
                else:
                    print(f"\t{word} has a valid position for {char[0]}")
            else:
                if char not in word:
                    try:
                        # print(f"\tAbout to remove {word}, index: {preproc.index(word)}")
                        # print("word from index:", preproc[preproc.index(word)])
                        # preproc.pop(preproc.index(word))
                        temp.append(word)
                        break
                    except ValueError:
                        print(f"\tError thrown trying to pop {word}")
                else:
                    print(f"\t{word} is valid for {char}")

    output = list(set(preproc) - set(temp))
    return output


def game(alg_spec: dict, logger: logging.Logger):
    """ Game loop """
    available = []
    with open(alg_spec["WORD_FILE"], encoding="utf-8") as file:
        for line in file:
            available.append(line.strip())

    guesses = []
    correct_chars = []
    for i in range(6):
        correct, known = '', ''
        guess = input(f"What word is your {iters[i]} guess? ")
        guesses.append(guess)
        res = input("Are any of the letters green or yellow? (g|y|n)" \
                    "  If there are both green and yellow letters respond " \
                    "with both g and y. ")
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

        print("Correct:", correct)
        print("Known", known)

        for char in correct:
            place = (char, guess.index(char))
            correct_chars.append(place)
        for char in known:
            correct_chars.append(char)
        print("Correct characters:", correct_chars)
        possible_words = get_possible(correct_chars, available, guesses)
        # if len(possible_words) <= 10:
        print("Remaining possible words:")
        available = possible_words.copy()
        while possible_words:
            try:
                output = possible_words.pop()
                for i in range(14):
                    output = f"{output}, {possible_words.pop()}"
                print(output)
            except Exception:
                pass
        print(output, f"\nTotal remaining: {len(available)}")
        if len(available) == 1:
            break


def main(conf_path: str):
    """ Driver """
    config = Path(conf_path)
    with open(config.as_posix(), encoding="utf-8") as file:
        alg_info = yaml.safe_load(file.read())
    print(alg_info)
    logger = logging.getLogger()
    game(alg_info["spec"], logger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Because machines are smarter than you.')
    parser.add_argument('config', nargs="?", help="application.yaml file")
    args = parser.parse_args()
    if not args.config:
        conf_path = Path("./application.yaml")
    else:
        conf_path = Path(args.config)
    main(conf_path)
