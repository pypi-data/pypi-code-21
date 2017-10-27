# -*- coding: utf-8 -*-
"""[summary]

[description]
"""
from __future__ import print_function
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
        'warning': Fore.YELLOW
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

    def _print(self):

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
            print("\n".join(self.text))

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
            humanize=True):
        """
        """
        if obj:
            self.text = self._humanize(obj) if humanize else obj
        else:
            self.text = "Por favor confirme"
        answered = False
        self.text = "\n{} (s/n) ".format(self.text)
        self.transform = transform
        self._print()
        if self.format_only:
            return self.text
        while not answered:
            ret = input(self.text)
            if ret and ret[0].upper() in ["S", "N"]:
                answered = True
        return ret[0].upper() == "S"

    def choose(
            self,
            choices,
            question=None,
            theme="choose",
            transform=None,
            humanize=True):
        """
        """
        if not isinstance(choices, list):
            raise ValueError("Choices must be a list")
        self.text = "\n"
        i = 1
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
                    "{} (1-{}): ".format(question, i - 1))
                if ret and int(ret) in range(1, i):
                    answered = True
            except ValueError:
                pass
        return choices[ret]

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

    def add_theme(self, theme):
        """
        Function: add_theme
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
