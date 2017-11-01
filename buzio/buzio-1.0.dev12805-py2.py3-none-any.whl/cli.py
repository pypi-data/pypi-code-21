# -*- coding: utf-8 -*-
"""[summary]

[description]
"""
from __future__ import print_function
import os
import sys
import datetime
import subprocess
from colorama import Fore, Style
from unidecode import unidecode


def get_terminal_size():
    try:
        from shutil import get_terminal_size
        return get_terminal_size(fallback=(80, 24))
    except ImportError:
        cols = int(subprocess.check_output(
            'tput cols',
            shell=True,
            stderr=subprocess.STDOUT
        ))
        lines = int(subprocess.check_output(
            'tput lines',
            shell=True,
            stderr=subprocess.STDOUT
        ))
        return (cols, lines)


class Console():
    """
    """

    DEFAULT_THEMES = {
        'box': Fore.CYAN,
        'choose': Fore.BLUE,
        'confirm': Fore.MAGENTA,
        'error': Fore.RED,
        'info': Fore.CYAN,
        'section': Fore.BLUE,
        'success': Fore.GREEN,
        'warning': Fore.YELLOW,
        'dark': Fore.LIGHTWHITE_EX
    }

    def __init__(self, format_only=False, theme_dict=DEFAULT_THEMES):
        """
        Function: __init__
        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (format_only) default=False: InsertHere
            @param (theme_dict) default=DEFAULT_THEMES: InsertHere
        Returns: InsertHere
        """
        self.format_only = format_only
        self.theme_dict = theme_dict

    def _get_style(self):
        if not isinstance(self.theme_dict, dict):
            raise ValueError("Themes List must be a dictionary.")

        return self.theme_dict.get(self.theme, "")

    def _humanize(self, obj):
        if obj is None:
            ret = "--"
        elif isinstance(obj, str):
            ret = obj
        elif isinstance(obj, bool):
            ret = "Sim" if obj else "Não"
        elif isinstance(obj,
                        (datetime.datetime, datetime.date, datetime.time)):
            ret = obj.isoformat()
        elif isinstance(obj, list) or isinstance(obj, tuple):
            ret = ", ".join([
                self._humanize(data)
                for data in obj
            ])
        elif isinstance(obj, dict):
            ret = "\n".join([
                "({}) {}: {}".format(i + 1, key, self._humanize(obj[key]))
                for i, key in enumerate(obj)
            ])
        else:
            ret = str(obj)

        return ret

    def _print(self, linebreak=True):

        if self.prefix:
            self.text = "{}: {}".format(self.prefix, self.text)

        if self.transform:
            if 'title' in self.transform:
                self.text = self.text.title()
            if 'upper' in self.transform:
                self.text = self.text.upper()
            if 'small' in self.transform:
                self.text = self.text.lower()

        if self.theme:
            self.text = [
                "{}{}{}{}".format(
                    Style.BRIGHT
                    if self.transform and 'bold' in self.transform else "",
                    self._get_style(),
                    line,
                    Style.RESET_ALL
                )
                for line in self.text.split("\n")
            ]

        if not self.format_only:
            print("\n".join(self.text), end="\n" if linebreak else "")

        return self.text

    def success(
            self,
            obj,
            theme="success",
            transform=None,
            use_prefix=True,
            prefix="Success",
            humanize=True):
        """
        """
        self.text = self._humanize(obj) if humanize else obj
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        self.transform = transform
        return self._print()

    def info(
            self,
            obj,
            theme="info",
            transform=None,
            use_prefix=True,
            prefix="Info",
            humanize=True):
        """
        """
        self.text = self._humanize(obj) if humanize else obj
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        self.transform = transform
        return self._print()

    def warning(
            self,
            obj,
            theme="warning",
            transform=None,
            use_prefix=True,
            prefix="Warning",
            humanize=True):
        """
        """
        self.text = self._humanize(obj) if humanize else obj
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        self.transform = transform
        return self._print()

    def error(
            self,
            obj,
            theme="error",
            transform=None,
            use_prefix=True,
            prefix="Error",
            humanize=True):
        """
        """
        self.text = self._humanize(obj) if humanize else obj
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        self.transform = transform
        return self._print()

    def section(
            self,
            obj,
            theme="section",
            transform=None,
            use_prefix=False,
            prefix="Section",
            full_width=False,
            humanize=True):
        """
        """
        self.text = self._humanize(obj) if humanize else obj
        if transform and 'center' in transform:
            format_text = "> {:^{num}} <"
            extra_chars = 4
        elif transform and 'right' in transform:
            format_text = "{:>{num}} <<"
            extra_chars = 3
        else:
            format_text = ">> {:<{num}}"
            extra_chars = 3
        if full_width:
            longest_line = get_terminal_size()[0]
        else:
            line_sizes = [
                len(line) + extra_chars
                for line in self.text.split("\n")
            ]
            longest_line = sorted(line_sizes, reverse=True)[0]
        main_lines = [
            format_text.format(line, num=longest_line - 4)
            for line in self.text.split("\n")
        ]
        bottom_line = "{:-^{num}}".format('', num=longest_line)
        self.text = "\n{}\n{}\n".format(
            "\n".join(main_lines),
            bottom_line
        )
        self.prefix = prefix if use_prefix else ""
        self.theme = theme
        self.transform = transform
        return self._print()

    def box(self, obj, theme="box", transform=None, humanize=True):
        """
        Function: box
        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (obj):InsertHere
            @param (theme) default="box": InsertHere
            @param (transform) default=None: InsertHere
            @param (humanize) default=True: InsertHere
        Returns: InsertHere
        """
        self.text = self._humanize(obj) if humanize else obj
        line_sizes = [
            len(line)
            for line in self.text.split("\n")
        ]
        longest_line = sorted(line_sizes, reverse=True)[0]

        horizontal_line = "{:*^{num}}".format('', num=longest_line + 6)
        vertical_line = "*{:^{num}}*".format('', num=longest_line + 4)

        main_texts = [
            "*{:^{num}}*".format(
                text_line, num=longest_line + 4
            )
            for text_line in self.text.split("\n")
        ]
        self.text = "{}\n{}\n{}\n{}\n{}".format(
            horizontal_line,
            vertical_line,
            "\n".join(main_texts),
            vertical_line,
            horizontal_line
        )
        self.theme = theme
        self.transform = transform
        self.prefix = None
        return self._print()

    def confirm(
            self,
            obj=None,
            theme="confirm",
            transform=None,
            humanize=True,
            default=None):
        """
        """
        if default is not None and not isinstance(default, bool):
            raise ValueError("Default must be a boolean")

        if obj:
            self.text = self._humanize(obj) if humanize else obj
        else:
            self.text = "Por favor confirme"
        answered = False
        self.text = "{} (s/n){} ".format(
            self.text,
            "[{}]".format(self._humanize(default)[0])
            if default is not None else "")
        self.transform = transform
        self.prefix = None
        self.theme = theme
        self._print(linebreak=False)
        if self.format_only:
            return self.text
        while not answered:
            ret = input("? ")
            if not ret and default is not None:
                ret = default
                answered = True
            elif ret and ret[0].upper() in ["S", "N"]:
                answered = True
        return ret if isinstance(ret, bool) else ret[0].upper() == "S"

    def choose(
            self,
            choices,
            question=None,
            theme="choose",
            transform=None,
            humanize=True,
            default=None):
        """
        """
        if not isinstance(choices, list):
            raise ValueError("Choices must be a list")
        if default:
            found = [
                num
                for num, def_choice in enumerate(choices)
                if def_choice == default
            ]
            if found:
                default_index = found[0] + 1
            else:
                raise ValueError("Default object not found in choices")
        else:
            default_index = None

        i = 1
        self.text = ""
        for choice in choices:
            self.text += "{}. {}\n".format(
                i,
                self._humanize(choice) if humanize else choice
            )
            i += 1
        answered = False
        self.theme = theme
        self.transform = transform
        self.prefix = False
        self._print()
        if self.format_only:
            return self.text
        if not question:
            question = "Selecione"
        while not answered:
            try:
                ret = input(
                    "{} (1-{}){}: ".format(
                        question,
                        i - 1,
                        "[{}] ".format(default_index) if default_index else ""
                    )
                )
                if not ret and default_index:
                    ret = default_index
                    answered = True
                elif ret and int(ret) in range(1, i):
                    answered = True
            except ValueError:
                pass
        return choices[int(ret) - 1]

    def unitext(self, obj, theme=None, transform=None, humanize=True):
        """
        Function: unitext
        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (obj):InsertHere
            @param (theme) default=None: InsertHere
            @param (transform) default=None: InsertHere
            @param (humanize) default=True: InsertHere
        Returns: InsertHere
        """
        self.text = self._humanize(obj) if humanize else obj
        self.text = unidecode(self.text)
        return self._print()

    def slugify(self, obj, humanize=True):
        self.text = self._humanize(obj) if humanize else obj
        self.text = unidecode(self.text)
        self.text = self.text.strip().replace(" ", "_")
        self.text = self.text.lower()
        return self.text

    def progress(self, count, total, prefix='Lendo', theme=None,
                 suffix='Completo', barLength=50):
        """
        """
        formatStr = "{0:.2f}"
        percents = formatStr.format(100 * (count / float(total)))
        filledLength = int(round(barLength * count / float(total)))
        bar = '█' * filledLength + '-' * (barLength - filledLength)
        self.text = '\r{} |{}| {}% {} '.format(prefix, bar, percents, suffix)

        if not self.format_only:
            sys.stdout.write(self.text)
            sys.stdout.flush()

        return self.text

    def load_theme(self, theme):
        """
        Function: load_theme
        Summary: InsertHere
        Examples: InsertHere
        Attributes:
            @param (self):InsertHere
            @param (theme):InsertHere
        Returns: InsertHere
        """
        if not isinstance(theme, dict):
            raise ValueError("Theme must be a dict")
        for key in theme:
            self.theme_dict[key] = theme[key]

    def ask(
            self,
            obj,
            theme="warning",
            transform=None,
            humanize=True,
            validator=None,
            default=None,
            required=False):
        self.text = self._humanize(obj) if humanize else obj
        self.theme = theme
        self.transform = transform
        self.prefix = None
        self.text = "{}{}".format(
            self.text,
            " [{}]: ".format(default) if default else " "
        )
        self._print(linebreak=False)

        if self.format_only:
            return self.text
        else:
            answered = False
            while not answered:
                data = input("? ")
                if required and not data and not default:
                    text = self.text
                    self.error("Valor obrigatório")
                    self.text = text
                else:
                    if validator and data:
                        if not callable(validator):
                            raise ValueError(
                                "Validator must be a function")
                        text = self.text
                        answered = validator(data)
                        self.text = text
                    else:
                        answered = True
            return data if data else default

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def select(self,
               obj,
               theme="choose",
               humanize=True,
               question=None,
               default=None):
        if not isinstance(obj, list):
            raise ValueError("select data must be a list")
        if default is not None:
            try:
                obj[default]
            except (ValueError, IndexError):
                raise ValueError("Select default not valid")
        options = [
            self._humanize(item) if humanize else item
            for item in obj
        ]
        phrases = []
        letters = []
        for opt in options:
            letter, phrase = self._get_letter(
                text=opt,
                optlist=letters
            )
            phrases.append(phrase)
            letters.append(letter)

        answered = False
        self.theme = theme
        self.transform = None
        self.prefix = False
        self.text = "{}: {}{}".format(
            question if question else "Selecione",
            ", ".join([text for text in phrases]),
            " [{}]".format(obj[default]) if default is not None else ""
        )
        self._print(linebreak=False)
        if self.format_only:
            return self.text
        while not answered:
            ret = input("? ")
            if not ret and default is not None:
                return default
            elif ret and ret.upper() in letters:
                answered = True
        return [
            index
            for index, data in enumerate(letters)
            if ret.upper() == data
        ][0]

    def _get_letter(self, text, index=0, optlist=[]):
        try:
            test_letter = text[index].upper()
        except IndexError:
            raise ValueError("Can not found letter for {} option".format(text))
        if test_letter in optlist:
            index += 1
            test_letter, new_text = self._get_letter(text, index, optlist)
        else:
            new_text = "{}({}){}".format(
                text[:index] if index > 0 else "",
                test_letter,
                text[index + 1:]
            )
        return test_letter, new_text
