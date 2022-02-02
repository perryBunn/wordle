from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Union

import argparse
import logging
import math

from tqdm import tqdm

import yaml


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


def clean(words, file_name: Union[str, Path], logger):
    seen = []

    for word in words:
        if word not in seen:
            seen.append(word)
            continue
        logger.debug(f"{word} was already in the list")

    if isinstance(file_name, str):
        file_name = Path(file_name)

    with open(file_name, mode='w', encoding="utf-8") as file:
        for word in seen:
            file.write(f"{word}\n")


def main(conf_path):
    config = Path(conf_path)
    with open(config.as_posix(), encoding="utf-8") as file:
        application_conf = yaml.safe_load(file.read())

    logger = get_logger(application_conf["info"])
    logger.debug(application_conf)

    alg_spec = application_conf["spec"]
    available = []
    with open(alg_spec["WORD_FILE"], encoding="utf-8") as file:
            for line in file:
                available.append(line.strip())

    clean(available, f"clean_{alg_spec['WORD_FILE']}", logger)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Because machines are smarter than you.')
    parser.add_argument('config', nargs="?", help="application.yaml file")
    args = parser.parse_args()
    conf = Path("./application.yaml")
    if args.config:
        conf = Path(args.config)
    main(conf)
