# :coding: utf-8

from __future__ import print_function

import os
import sys
import re
import argparse
import logging
import codecs
import unicodedata

import requests
import numpy as np

# Silence invalid floating-point operation error as it is taken into account
# in the algorithm
np.seterr(invalid="ignore")


# Setup the logging format
logging.basicConfig(
    stream=sys.stderr, level=logging.INFO,
    format="[%(name)s] %(levelname)s: %(message)s"
)

# Command line logger
logger = logging.getLogger("jound")


def construct_parser():
    """Return argument parser."""
    parser = argparse.ArgumentParser(
        prog="jound",
        description="A word generator using statistics from a book",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-v", "--verbose", dest="verbose_count",
        action="count", default=0,
        help="increases log verbosity for each occurrence."
    )

    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Additional subcommands.",
        dest="subcommand"
    )

    # Assemble sub-parser

    assemble_subparser = subparsers.add_parser(
        "assemble", help="Assemble all world contained in a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    assemble_subparser.add_argument(
        "target", help="Path to the targeted file to analyse."
    )

    assemble_subparser.add_argument(
        "-o", "--output",
        help="Path to the generated file.",
        default=os.path.join(os.getcwd(), "words.txt")
    )

    assemble_subparser.add_argument(
        "-s", "--start", type=int,
        help="Cut off the targeted content before this index value.",
    )

    assemble_subparser.add_argument(
        "-e", "--end", type=int,
        help="Cut off the targeted content after this index value.",
    )

    # Analyze sub-parser

    analyze_subparser = subparsers.add_parser(
        "analyze", help=(
            "Process a list of words to generate statistic matrix on letters "
            "transitions."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    analyze_subparser.add_argument(
        "target", help="Path to the list of words to process."
    )

    analyze_subparser.add_argument(
        "-o", "--output",
        help="Path to the generated file.",
        default=os.path.join(os.getcwd(), "stats.bin")
    )

    # Generate sub-parser

    generate_subparser = subparsers.add_parser(
        "generate", help="Generate words from a probability matrix.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    generate_subparser.add_argument(
        "number", help="Number of words to generate.",
        type=int, default=1
    )

    generate_subparser.add_argument(
        "-s", "--statistical-file",
        help="Path to the statistical file generated with 'jound analyze'.",
        required=True
    )

    return parser


def main(arguments=None):
    """Jound command line interface."""
    if arguments is None:
        arguments = []

    # Process arguments.
    parser = construct_parser()
    namespace = parser.parse_args(arguments)

    logger.setLevel(max(2 - namespace.verbose_count, 0) * 10)

    if namespace.subcommand == "assemble":
        logger.info("Assemble words from target: {0}".format(namespace.target))

        try:
            output = validate_output(namespace.output)
            content = fetch_target_content(
                namespace.target,
                start=namespace.start,
                end=namespace.end
            )

            words = set()
            for word in yield_words_from_content(content):
                words.add(word)

            logger.info("Writing {0} words to {1}".format(len(words), output))

            with codecs.open(output, "w", encoding="utf8") as f:
                f.write("\n".join(sorted(words)))

        except Exception as err:
            logger.error(
                "[{0}] {1}".format(err.__class__.__name__, str(err))
            )

    elif namespace.subcommand == "analyze":
        logger.info(
            "Generate statistics from target: {0}".format(namespace.target)
        )

        try:
            output = validate_output(namespace.output)
            content = fetch_target_content(namespace.target)
            matrix = generate_statistics_from_words(content.split("\n"))

            logger.info("Writing statistics to {0}".format(output))

            matrix.tofile(output)

        except Exception as err:
            logger.error(
                "[{0}] {1}".format(err.__class__.__name__, str(err))
            )

    elif namespace.subcommand == "generate":
        logger.info("Generate a new word")

        matrix = np.fromfile(
            namespace.statistical_file, dtype="int32"
        ).reshape(256, 256, 256)

        for index in range(namespace.number):
            word = generate_word(matrix)
            print(word, end="")


def validate_output(path):
    """Return validated output *path*.

    Raise :exc:`IOError` if the output directory is inaccessible.

    """
    output = os.path.abspath(path)
    output_directory = os.path.dirname(output)
    if not os.access(output_directory, os.W_OK):
        raise IOError(
            "The output directory is inaccessible: {0}".format(
                output_directory
            )
        )

    return output


def fetch_target_content(target, start=None, end=None):
    """Return content from *target*.

    *target* can be a file or a url.

    *start* and *end* indices can be set to return a particular slice of the
    content.

    Example::

        >>> fetch_target_content(
        ...     "https://www.gutenberg.org/files/2701/old/moby10b.txt",
        ...     start=35044, end=35302
        ... )
        CHAPTER 1\\r\\n\\r\\nLoomings.\\r\\n\\r\\n\\r\\nCall me Ishmael.
        Some years ago--never mind how long\\r\\nprecisely--having little or no
        money in my purse, and nothing\\r\\nparticular to interest me on shore,
        I thought I would sail about a\\r\\nlittle and see the watery part of
        the world.

    """
    if re.match("^https?://", target):
        r = requests.get(target)
        if r.status_code is not 200:
            raise IOError(
                "The targeted url is inaccessible: {0}".format(target)
            )

        r.encoding = "ISO-8859-1"
        return r.text[start:end]

    target_file = os.path.abspath(target)
    if not os.path.isfile(target_file) and os.access(target_file, os.R_OK):
        raise IOError(
            "The targeted file is not readable: {0}".format(target_file)
        )

    with codecs.open(target_file, "r", encoding="ISO-8859-1") as f:
        return f.read()[start:end]


def yield_words_from_content(content):
    """Yield each word found in *content*.

    Filter out whitespaces, numbers and punctuation.

    Example::

        >>> content = (
        ...     "Call me Ishmael.  Some years ago--never mind how long "
        ...     "precisely--having little or no money in my purse, and nothing"
        ... )
        >>> list(yield_words_from_content(content))
        [
            "Call", "me", "Ishmael", "Some", "years", "ago", "never", "mind",
            "how", "long", "precisely", "having", "little", "or", "no", "money",
            "in", "my", "purse", "and"
        ]

    """
    word = ""

    for letter in content:
        if unicodedata.category(letter).startswith("L"):
            word += letter
        elif len(word) > 0:
            yield word
            word = ""


def generate_statistics_from_words(words):
    """Return statistical matrix generated from list of *words*.

    Analyze each word to generate a three dimensional matrix which indicate
    the number of occurrences for each letter:

        - at the first position of a word,
        - at the second position of a word after a specific letter,
        - following a specific combination of two letters,
        - at the last position of a word.

    Example::

        >>> stats = generate_statistics_from_words([
        ...     "Call", "me", "Ishmael", "Some", "years", "ago", "never",
        ...     "mind", "how", "long", "precisely", "having", "little", "or",
        ...     "no", "money", "in", "my", "purse", "and"
        ... ])

        # 4 words start with a 'm'
        >>> stats[0, 0, ord(u"m")]

        # The letter 'a' never follows the group of letters 'iu'
        >>> stats[ord(u"i"), ord(u"u"), ord(u"a")]
        0

        # The letter 'r' follows once the group of letters 'ea'
        >>> stats[ord(u"e"), ord(u"a"), ord(u"r")]
        1

        # 2 words finish by the group of letters 'nd'
        >>> stats[ord(u"n"), ord(u"d"), ord(u"\\n")]
        2

    """
    stats = np.zeros((256, 256, 256), dtype="int32")

    for word in words:
        analyze_word = True

        indices = []
        for letter in word:
            if not unicodedata.category(letter).startswith("L"):
                analyze_word = False
                break

            index = ord(letter)

            # This algorithm only take the first 256 unicode characters
            # into account. Letters such as 'œ' or 'Ω' are currently not
            # recognized.
            if index > 256:
                analyze_word = False
                break

            indices.append(index)

        if not analyze_word:
            continue

        # Append '\n' symbol to process statistics for end of words
        indices.append(10)

        letter_n1 = 0
        letter_n2 = 0

        for index in indices:
            stats[letter_n2, letter_n1, index] += 1
            letter_n2 = letter_n1
            letter_n1 = index

    return stats


def generate_word(stats):
    """Return a word generated by using the *stats* matrix.

    Build a :term:`Markov chain` from the three dimensional statistical matrix,
    which would usually have been generated by
    :func:`generate_statistics_from_words`.

    Return a word created by respecting the probability of occurrence of each
    letters.

    Example:

        >>> stats = generate_statistics_from_words([
        ...     "Call", "me", "Ishmael", "Some", "years", "ago", "never",
        ...     "mind", "how", "long", "precisely", "having", "little", "or",
        ...     "no", "money", "in", "my", "purse", "and"
        ... ])
        >>> generate_word(stats)
        mong

    """
    s = stats.sum(axis=2)
    st = np.tile(s.T, (256, 1, 1)).T
    p = stats.astype("float") / st
    p[np.isnan(p)] = 0

    word = u""

    letter_n1 = 0
    letter_n2 = 0

    while not letter_n1 == 10:
        index = np.random.choice(
            range(256), 1, p=p[letter_n2, letter_n1, :]
        )[0]

        word = word + unichr(index)
        letter_n2 = letter_n1
        letter_n1 = index

    return word
