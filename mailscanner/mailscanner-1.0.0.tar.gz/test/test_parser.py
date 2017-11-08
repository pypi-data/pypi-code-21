import unittest
from mailscanner.parser import *
from mailscanner import Parser

class TestParser(unittest.TestCase):
    def setUp(self):
        self.p = Parser()

        self.stripstring = "Lorem ipsum dolor sit amet, consectetur \
adipiscing elit."

        self.strip_message = """Praesent semper vulputate scelerisque.
Phasellus posuere, massa quis facilisis cursus, sem metus
volutpat quam, in ultricies justo sapien id nunc. Praesent in ex
turpis. Pellentesque eu mauris neque. Quisque porttitor, massa
eget tristique lacinia, enim odio gravida risus, tincidunt
sollicitudin nulla nunc non enim."""


        self.target_stripped_string = """Praesent semper vulputate scelerisque.
Phasellus justo sapien id nunc. Praesent in ex
turpis. Pellentesque eu mauris neque. Quisque porttitor, massa
eget tristique lacinia, enim odio gravida risus, tincidunt
sollicitudin nulla nunc non enim."""


        self.bad_word1 = r"posuere"
        self.bad_word2 = r"ultricies"
        self.bad_word3 = r"enim"

        self.date1 = "January 15th"
        self.date2 = "15.01.2017"
        self.date3 = "15th of January"
        self.date4 = "15.1"


    def test_addzero(self):
        self.assertEqual(add_zero("5"), "05")

    def test_is_date_valid(self):
        self.assertEqual(date_is_valid(["05", "05"]), True)
        self.assertEqual(date_is_valid(["45", "05"]), False)
        self.assertEqual(date_is_valid(["09", "15"]), False)

    def test_simple_date(self):
        self.assertEqual(get_simple_date("8.11.2016"), "08.11.")
        self.assertEqual(get_simple_date("02.01."), "02.01.")
        self.assertEqual(get_simple_date("89.01."), "Failed")

    def test_get_month(self):
        self.assertEqual(get_month("August"), "08")
        self.assertEqual(get_month("November"), "11")
        self.assertEqual(get_month("Helmikuu"), "None")

    def test_day_of_month(self):
        self.assertEqual(get_day_of_month("1st"), "01")
        self.assertEqual(get_day_of_month("2nd"), "02")
        self.assertEqual(get_day_of_month("3rd"), "03")
        self.assertEqual(get_day_of_month("25th"), "25")

    def test_strip_string(self):
        self.assertEqual(self.p.strip_string(self.stripstring, "ipsum",
            "amet"), "Lorem  dolor sit , consectetur adipiscing elit.")

    def test_strip_between(self):
        stripped = self.p.strip_between(self.strip_message,
                self.bad_word1, self.bad_word2)
        self.assertEqual(stripped, self.target_stripped_string)

    def test_distance_between(self):
        self.assertEqual(self.p.distance_between(self.strip_message,
            self.bad_word1, self.bad_word3), 3)

    def test_scan_line(self):
        self.assertEqual(self.p.scan_line(self.stripstring, "dolor"), True)
        self.assertEqual(self.p.scan_line(self.stripstring, "santa"), False)

    def test_scan_message(self):
        line = "Phasellus posuere, massa quis facilisis cursus, sem metus"
        self.assertEqual(self.p.scan_message(
            self.strip_message, "massa"), line)
        self.assertEqual(self.p.scan_message(
            self.strip_message, "santa"), "")

    def test_create_line(self):
        self.assertEqual(self.p.create_line(
            3,
            "Company: Position",
            "DL: 15.03."),
            "3: Company: Position - DL: 15.03.\n")

    def test_format_date(self):
        self.assertEqual(self.p.format_date(self.date1), "15.01.")
        self.assertEqual(self.p.format_date(self.date2), "15.01.")
        self.assertEqual(self.p.format_date(self.date3), "15.01.")
        self.assertEqual(self.p.format_date(self.date4), "15.01.")
        self.assertEqual(self.p.format_date("lolnotadate"), "None.None.")
