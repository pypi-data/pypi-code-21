# -*- coding: utf-8 -*-

import logging_helper
logging = logging_helper.setup_logging(logger_name = __name__)

import webbrowser
from conversionutil.date_and_time_conversions import epoch_to_time
from collections import OrderedDict

from conversionutil.convert import convert_storage_size
from testing_helpers import assert_table_against_unicode
from tableutil import Table, Cell


def test_empty_table_without_title():
    table = Table(headings       = [{u'heading': u'x'}],
                  show_column_headings = True,
                  table_format   = Table.TEXT_TABLE_FORMAT)
    assert_table_against_unicode(table    = table,
                                 expected = u' ------- \n'\
                                            u'| Empty |\n'\
                                            u' ------- ',)

def test_empty_table_with_title():
    table = Table(title                = u'A Title!',
                  headings             = [{u'heading': u'x'}],
                  show_column_headings = True,
                  table_format   = Table.TEXT_TABLE_FORMAT)
    assert_table_against_unicode(table    = table,
                                 expected = u' ---------- \n'\
                                            u'| A Title! |\n'\
                                            u'|----------|\n'\
                                            u'| Empty    |\n'\
                                            u' ---------- ')

def test_empty_table_with_title_and_multiple_columns():
    table = Table(title                = u'A Title!',
                  headings             = [{u'heading': u'x'},
                                          {u'heading': u'y'}],
                  show_column_headings = True)
    assert_table_against_unicode(table    = table,
                                 expected = u'┌──────────┐\n'\
                                            u'| A Title! |\n'\
                                            u'├──────────┤\n'\
                                            u'| Empty    |\n'\
                                            u'└──────────┘')

def test_row_numbers():
    table = Table(title                = u'A Title!',
                  headings             = [{u'heading': u'x'}],
                  show_column_headings = True,
                  table_format   = Table.TEXT_TABLE_FORMAT)
    table.add_rows([{u'x':10},
                {u'x':20}])
    assert_table_against_unicode(table    = table,
                                 expected = u' ---------- \n'\
                                            u'| A Title! |\n'\
                                            u'|----------|\n'\
                                            u'| # | x    |\n'\
                                            u'|---+------|\n'\
                                            u'| 1 | 10   |\n'\
                                            u'| 2 | 20   |\n'\
                                            u' ---------- ')


def test_justification_in_column_data():
    table = Table(title                = u'A Title!',
                  headings             = [{u'heading': u'left',    u'justify':u'<'},
                                          {u'heading': u'centred', u'justify':u'^'},
                                          {u'heading': u'right',   u'justify':u'>'}],
                  show_column_headings = True,
                  table_format         = Table.TEXT_TABLE_FORMAT)
    table.add_rows([{u'left':u'l',    u'centred':u'c',        u'right':u'r'},
                    {u'left':u'le',   u'centred':u'ce' ,      u'right':u'ri'},
                    {u'left':u'lef',  u'centred':u'cen' ,     u'right':u'rig'},
                    {u'left':u'left', u'centred':u'cent' ,    u'right':u'righ'},
                    {u'left':u'left', u'centred':u'centr' ,   u'right':u'right'},
                    {u'left':u'left', u'centred':u'centre',   u'right':u'right'},
                    {u'left':u'left', u'centred':u'centred' , u'right':u'right'},
                    ])
    assert_table_against_unicode(table    = table,
                                 expected = u' ---------------------------- \n'\
                                            u'|          A Title!          |\n'\
                                            u'|----------------------------|\n'\
                                            u'| # | left | centred | right |\n'\
                                            u'|---+------+---------+-------|\n'\
                                            u'| 1 | l    |    c    |     r |\n'\
                                            u'| 2 | le   |   ce    |    ri |\n'\
                                            u'| 3 | lef  |   cen   |   rig |\n'\
                                            u'| 4 | left |  cent   |  righ |\n'\
                                            u'| 5 | left |  centr  | right |\n'\
                                            u'| 6 | left | centre  | right |\n'\
                                            u'| 7 | left | centred | right |\n'\
                                            u' ---------------------------- ')

def test_justification_in_headings():
    table = Table(title                = u'A Title!',
                  headings             = [{u'heading': u'left',    u'justify':u'<'},
                                          {u'heading': u'centred', u'justify':u'^'},
                                          {u'heading': u'right',   u'justify':u'>'}],
                  show_column_headings = True,
                  table_format         = Table.TEXT_TABLE_FORMAT)
    table.add_rows([{u'left':u'left justified', u'centred':u'centre justified', u'right':u'right justified'},
                   ])
    assert_table_against_unicode(table    = table,
                                 expected = u' --------------------------------------------------------- \n'\
                                            u'|                        A Title!                         |\n'\
                                            u'|---------------------------------------------------------|\n'\
                                            u'| # |      left      |     centred      |      right      |\n'\
                                            u'|---+----------------+------------------+-----------------|\n'\
                                            u'| 1 | left justified | centre justified | right justified |\n'\
                                            u' --------------------------------------------------------- ')



def test_embedded_conversion():
    table = Table.init_from_tree(tree         = {u"sz": 1536,
                                                 u"b" :[{u"sz": 1934727,},
                                                        {u"x": 0}]},
                                 conversions  = {u'sz': {u'converter': convert_storage_size}},
                                 table_format = Table.TEXT_TABLE_FORMAT)

    assert_table_against_unicode(table    = table,
                                 expected = u' ------------------------ \n'\
                                            u'| sz | 1.5KB             |\n'\
                                            u'| b  |  ---------------  |\n'\
                                            u'|    | | # |  sz   | x | |\n'\
                                            u'|    | |---+-------+---| |\n'\
                                            u'|    | | 1 | 1.8MB | - | |\n'\
                                            u'|    | | 2 | -     | 0 | |\n'\
                                            u'|    |  ---------------  |\n'\
                                            u' ------------------------ ')


def test_rounded_box_formatting():
    table = Table.init_from_tree(tree = {u"sz": 1536,
                                         u"b" :[{u"sz": 1934727,},
                                                {u"x": 0}]},
                                 conversions = {u'sz': {u'converter': convert_storage_size}},
                                 table_format = Table.ROUNDED_TABLE_FORMAT)

    assert_table_against_unicode(table    = table,
                                 expected =u'╭────┬───────────────────╮\n'\
                                           u'│ sz │ 1.5KB             │\n'\
                                           u'│ b  │ ╭───┬───────┬───╮ │\n'\
                                           u'│    │ │ # │  sz   │ x │ │\n'\
                                           u'│    │ ├───┼───────┼───┤ │\n'\
                                           u'│    │ │ 1 │ 1.8MB │ - │ │\n'\
                                           u'│    │ │ 2 │ -     │ 0 │ │\n'\
                                           u'│    │ ╰───┴───────┴───╯ │\n'\
                                           u'╰────┴───────────────────╯')

def test_light_box_formatting():
    table = Table.init_from_tree(tree         = {u"sz": 1536,
                                                 u"b" :[{u"sz": 1934727,},
                                                        {u"x": 0}]},
                                 conversions  = {u'sz': {u'converter': convert_storage_size}},
                                 table_format = Table.LIGHT_TABLE_FORMAT)

    assert_table_against_unicode(table    = table,
                                 expected =u'┌────┬───────────────────┐\n'\
                                           u'│ sz │ 1.5KB             │\n'\
                                           u'│ b  │ ┌───┬───────┬───┐ │\n'\
                                           u'│    │ │ # │  sz   │ x │ │\n'\
                                           u'│    │ ├───┼───────┼───┤ │\n'\
                                           u'│    │ │ 1 │ 1.8MB │ - │ │\n'\
                                           u'│    │ │ 2 │ -     │ 0 │ │\n'\
                                           u'│    │ └───┴───────┴───┘ │\n'\
                                           u'└────┴───────────────────┘')

def test_double_box_formatting():
    table = Table.init_from_tree(tree         = {u"sz": 1536,
                                                 u"b" :[{u"sz": 1934727,},
                                                        {u"x": 0}]},
                                 conversions  = {u'sz': {u'converter': convert_storage_size}},
                                 table_format = Table.DOUBLE_TABLE_FORMAT)

    assert_table_against_unicode(table    = table,
                                 expected =u'╔════╦═══════════════════╗\n'\
                                           u'║ sz ║ 1.5KB             ║\n'\
                                           u'║ b  ║ ╔═══╦═══════╦═══╗ ║\n'\
                                           u'║    ║ ║ # ║  sz   ║ x ║ ║\n'\
                                           u'║    ║ ╠═══╬═══════╬═══╣ ║\n'\
                                           u'║    ║ ║ 1 ║ 1.8MB ║ - ║ ║\n'\
                                           u'║    ║ ║ 2 ║ -     ║ 0 ║ ║\n'\
                                           u'║    ║ ╚═══╩═══════╩═══╝ ║\n'\
                                           u'╚════╩═══════════════════╝')


def test_log():
    from testfixtures import LogCapture

    table = Table.init_from_tree(tree         = {u"sz": 1536,
                                                 u"b" :[{u"sz": 1934727,},
                                                        {u"x": 0}]},
                                 conversions  = {u'sz': {u'converter': convert_storage_size}},
                                 table_format = Table.TEXT_TABLE_FORMAT)
    expected_message = u'\n ------------------------ \n'\
                         u'| sz | 1.5KB             |\n'\
                         u'| b  |  ---------------  |\n'\
                         u'|    | | # |  sz   | x | |\n'\
                         u'|    | |---+-------+---| |\n'\
                         u'|    | | 1 | 1.8MB | - | |\n'\
                         u'|    | | 2 | -     | 0 | |\n'\
                         u'|    |  ---------------  |\n'\
                         u' ------------------------ '

    with LogCapture() as logs:
        table.log(level = logging_helper.DEBUG)
        table.log(level = logging_helper.INFO)
        table.log(level = logging_helper.WARNING)
        logs.check((u'ITT_General.Utilities.table',
                    u'DEBUG',
                    expected_message),
                   (u'ITT_General.Utilities.table',
                    u'INFO',
                    expected_message),
                   (u'ITT_General.Utilities.table',
                    u'WARNING',
                    expected_message))

if __name__ == u"__main__":
    test_empty_table_without_title()
    test_empty_table_with_title()
    test_empty_table_with_title_and_multiple_columns()
    test_row_numbers()
    test_justification_in_column_data()
    test_justification_in_headings()

    test_embedded_conversion()
    test_log()
    test_light_box_formatting()
    test_rounded_box_formatting()
    test_double_box_formatting()
    logging.info(u'PASSED!')




def glob():
    #TODO: Move stuff we want from here to discrete functions and call from unit_tests
    t=Table(headings       = [{u'heading': u'x'}],
            show_column_headings = False,
            row_numbers    = False)

    sub_table = Cell(Table.init_from_tree([Cell(tags = {u'img': {u'src':u'blah'}}),
                                           Cell(tags = {u'img': {u'src':u'vlah'}})]))

    t.add_rows([{u'x':u'a'},
                {u'x':u'b'},
                {u'x':sub_table}])

    print t.html()

    print unicode(t)
    print unicode(t).splitlines()
    assert unicode(t).splitlines() == [u' --- ',
                                       u'| a |',
                                       u'| b |',
                                       u' --- ',]
    t = Table.init_from_tree([Cell(value = u'a',
                                   tags={u'a':{u'href':u'blah'}}),
                              Cell(value = u'b',
                                   tags={u'a':{u'href':u'vlah'}})])

    print t.jira_table_notation().splitlines()
    assert t.jira_table_notation() == [u'|  [a|blah]  |',
                                       u'|  [b|vlah]  |']



    c = Cell(value = u'blah',
             tags  = {u'a':{u'href' : u'http://www.google.com',
                            u'title': u'Do the google'}})
    assert c.html() == u"""<a href="http://www.google.com" title="Do the google">blah</a>"""

    c = Cell(value = u'blah',
             href = u'hjtt[',
             tags  = {u'a':{u'href' : u'http://www.google.com',
                            u'title': u'Do the google'}}).get_href() == u'http://www.google.com'

    0/0
    assert Cell(tags  = {u'img':{u'src':u'http://www.google.com/google.jpg',
                                u'alt':u'Do the google'}}).html() \
        == u"""<img src="http://www.google.com/google.jpg" alt="Do the google"/>"""


    c = Cell(tags  = [{u'img':{u'src'  : u'http://www.google.com/google.jpg',
                               u'alt'  : u'Google image'}},
                      {u'a'  :{u'href' : u'http://www.google.com',
                               u'title': u'Do the google!'}},
                      ])

    assert c.html() == u"""<a href="http://www.google.com" title="Do the google!"><img src="http://www.google.com/google.jpg" alt="Google image"/></a>""", c.html()

    try:
        Cell(tags  =  {u'img':{u'src'  : u'http://www.google.com/google.jpg',
                                 u'alt'  : u'Do the google'},
                         u'a'  :{u'href' : u'http://www.google.com',
                                 u'title': u'Do the google'}})
    except ValueError:
        pass

    print c.html()

    0/0
    tree = {u'Name' : u'htx', u'Device_ID': u'34939046'}

    t = Table.init_from_tree(tree = tree)

    print unicode(t)

    0/0

    tree = OrderedDict([(u'Timeslot 1', OrderedDict([(u'Name', u'Timeslot 1'), (u'Description', u'Weekday Preschool (05:55 - 08:55)'), (u'Channel', u'607'), (u'Genre', u'Kids'), (u'Tune For', u'1 min')])), (u'Timeslot 2', OrderedDict([(u'Name', u'Timeslot 2'), (u'Description', u'Weekday Day (08:55 - 14:55)'), (u'Channel', u'145'), (u'Genre', u'Entertainment/Game Shows'), (u'Tune For', u'1 min')])), (u'Timeslot 5', OrderedDict([(u'Name', u'Timeslot 5'), (u'Description', u'Weekday Early Evening (14:55 - 17:55)'), (u'Channel', u'523'), (u'Genre', u'Documentaries/Animals'), (u'Tune For', u'1 min')])), (u'Timeslot 6', OrderedDict([(u'Name', u'Timeslot 6'), (u'Description', u'Evening Weekday (17:55 - 20:55)'), (u'Channel', u'108'), (u'Genre', u'Entertainment'), (u'Tune For', u'1 min')])), (u'Timeslot 8', OrderedDict([(u'Name', u'Timeslot 8'), (u'Description', u'Primetime - Weekday (20:55 - 23:55)'), (u'Channel', u'301'), (u'Genre', u'Movies'), (u'Tune For', u'1 min')])), (u'Timeslot 10', OrderedDict([(u'Name', u'Timeslot 10'), (u'Description', u'Overnight - Weekday (23:55 - 05:55)'), (u'Channel', u'112'), (u'Genre', u'Comedy'), (u'Tune For', u'1 min')])), (u'Timeslot 3', OrderedDict([(u'Name', u'Timeslot 3'), (u'Description', u'Weekend Morning (05:55 - 08:55)'), (u'Channel', u'524'), (u'Genre', u'Documentaries/Motoring'), (u'Tune For', u'1 min')])), (u'Timeslot 4', OrderedDict([(u'Name', u'Timeslot 4'), (u'Description', u'Weekend Daytime/Early Evening (08:55 - 17:55)'), (u'Channel', u'405'), (u'Genre', u'Sport'), (u'Tune For', u'1 min')])), (u'Timeslot 7', OrderedDict([(u'Name', u'Timeslot 7'), (u'Description', u'Evening Weekend (17:55 - 20:55)'), (u'Channel', u'607'), (u'Genre', u'Kids'), (u'Tune For', u'1 min')])), (u'Timeslot 9', OrderedDict([(u'Name', u'Timeslot 9'), (u'Description', u'Primetime Weekend (20:55 - 23:55)'), (u'Channel', u'405'), (u'Genre', u'Sport'), (u'Tune For', u'1 min')])), (u'Timeslot 11', OrderedDict([(u'Name', u'Timeslot 11'), (u'Description', u'Overnight - Weekend (23:55 - 05:55)'), (u'Channel', u'301'), (u'Genre', u'Movies'), (u'Tune For', u'1 min')]))])

    tree = [OrderedDict([(u'Name', u'htx'), (u'Device_ID', u'34939046'), (u'Bouquet', u'4101'), (u'Sub-Bouquet', u'1')]), OrderedDict([(u'Name', u'kd1'), (u'Device_ID', u'34939007'), (u'Bouquet', u'4101'), (u'Sub-Bouquet', u'1')])]

    for key in tree[0]:
        print key

    t = Table.init_from_tree (tree = tree,
                              row_numbers = False)

    print unicode(t)


    0/0
    t = Table.init_from_tree (tree = {u'htx':{u'Name' : u'htx', u'Device_ID': u'34939046'},
                                      u'kd1':{u'Name' : u'kd1', u'Device_ID': u'34939007'}},
                              row_numbers = False)

    print unicode(t)


    0/0


    t = Table.init_from_tree (tree = {u"entitlements" : [ u"SKY+",
                                                          u"GATEWAYENABLER",
                                                          u"SIDELOAD",
                                                          u"SPORTS",
                                                          u"MOVIES",
                                                          u"VIP",
                                                          u"SKY_DRM_MR",
                                                          u"SKY_DRM_CE",
                                                          u"ETHAN_APP_1",
                                                          u"ANALYTICS",
                                                          u"HD",
                                                          u"SKY_IPPV",
                                                          u"PDL" ]})


    print unicode(t)


    0/0

    def swap(a,b):
        return b,a

    def upper(s):
        return s.upper()



    t = Table.init_from_tree (tree = {u'1.2.3.4':{2002:[{u'A': u'x', u'B': u'w'},
                                                        {u'A': u'y', u'B': u'o'}]}},
                              conversions = {u'A':{u'converter' : upper}})

    print unicode(t)

    0/0

    t = Table.init_from_tree (tree = {u'1.2.3.4':{2002:['A','B','C','D']}})
    print unicode(t)




    conversions = {u'A':{u'converter': upper},
                   (u'A',u'B'):{u'converter': swap}}

    t = Table.init_from_tree (tree = {u'A': u'a',
                                      u'B': u'b'},
                              conversions = conversions)

    print unicode(t)



    t = Table.init_from_tree (tree = {u'1.2.3.4':{2002:[{u'A': u'A', u'B': u'B'}],
                                                }
                                     },
                              conversions = conversions)

    print unicode(t)

    conversions = {u'Date':{u'converter': epoch_to_time,
                            u'format'  : u'%Y-%m-%d\n%H:%M'}}

    t = Table.init_from_tree (tree = {u'1.2.3.4':{2002:[{u'Date': 1453329600}],
                                                }
                                     },
                              conversions = conversions)

    print unicode(t)




    t = Table.init_from_pasted_excel(u"""t1	t2	t3
123	654	789
321	456	987
321	465	987
""")

    print(unicode(t))
    t.sort_by_column(u't2')
    print(unicode(t))
    print(t.jira())


    t = Table.init_from_text(u"""
 -------------
|  Title.1    |
|  Title.2    |
|-------------|
| H1.1 | H2.1 |
| H1.2 | H2.2 |
|------+------|
| 2    |   b  |
| 1    |   a  |
 -------------
"""
)
    print unicode(t)
    0/0
    t = Table.init_from_text(u"""
 -------------
|  Title.1    |
|  Title.2    |
|-------------|
| #    | H2.1 |
|      | H2.2 |
|------+------|
| 1    |   b  |
| 2    |   a  |
 -------------
"""
)

    t = Table.init_from_file(u'test_table.txt')
    print(unicode(t))
    0/0
    t.sort_by_column(u'H2.1\nH2.2')
    print(unicode(t))
    0/0
    print t.headings
    t.add_row([u'c'])
    print(unicode(t))

    t = Table.init_from_tree (tree = {u'1.2.3.4':{2002:[{u'Date': u'2015-09-11'}],
                                                }
                                     })

    print unicode(t)
    0/0

    t = Table.init_from_tree(tree = {
u"nodeid": u"C4200_536B79204D6F76696573",
u"nodetype": u"MENU",
u"t": u"Sky Movies",
u"childnodes": [
{
"nodetype": "MENU",
"nodeid": "B24426_526563656E746C79204164646564",
"t": "Recently Added",
"renderhints": "{ \"template\": \"5COL\", \"imagetype\": \"COVER\" }",
"sy": "Movies we've recently added available for you to watch right now on demand. Watch these and over 1000 movies with Sky Movies on demand."
},
{
"nodetype": "MENU",
"nodeid": "B4195_466F7220596F75",
"t": "For You",
"renderhints": "{ \"template\": \"5COL\", \"imagetype\": \"COVER\", \"directive\": \"RECS-FORYOU\" }",
"sy": "Great Sky Movies especially selected for you. Watch these and over 1000 movies with Sky Movies On Demand."
},
{
"nodetype": "MENU",
"nodeid": "B13605_4D6F737420506F70756C6172",
"t": "Most Popular",
"renderhints": "{ \"template\": \"5COL\", \"imagetype\": \"COVER\" }",
"sy": "What are people watching now on demand? Watch these and over 1000 movies with Sky Movies on demand."
},
{
"nodetype": "MENU",
"nodeid": "C16430_4772656174204272697473",
"t": "Great Brits",
"renderhints": "{ \"template\": \"MENUPANEL\" }",
"sy": "Sky Movies presents our most patriotic collection yet as we showcase the best acting talent from Great Britain."
},
{
"nodetype": "MENU",
"nodeid": "C16000_536B792053746F7265",
"t": "Sky Store",
"renderhints": "{ \"template\": \"MENUPANEL\" }",
"sy": "Find more movies in Sky Store available to rent whenever you want. From new releases out on DVD to a library of favourites, the choice is yours. "
},
{
"nodetype": "MENU",
"nodeid": "A21440_416C6C",
"t": "All",
"renderhints": "{ \"template\": \"5COL\", \"imagetype\": \"COVER\" }",
"sy": "A complete A-Z list of all the movies available as part of the Sky Movies subscription."
},
{
"nodetype": "MENU",
"nodeid": "C37209_4469736E6579",
"t": "Disney",
"renderhints": "{ \"template\": \"MENUPANEL\" }",
"sy": "Enjoy Disney magic on demand all day long, with animated classics, Pixar hits and much more."
},
{
"nodetype": "MENU",
"nodeid": "D10276_46616D696C79",
"t": "Family",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "Terrible tykes, animated antics, magic and adventure - all under one bursting roof. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "D4286_436F6D656479",
"t": "Comedy",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "If laughter is the best medicine, this is the world's biggest pharmacy. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "D4314_416374696F6E",
"t": "Action",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "Want top gear, adrenalin-pumping excitement? Then look no further for thrills and spills. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "C6195_506C61796C6973747320",
"t": "Playlists ",
"renderhints": "{ \"template\": \"MENUPANEL\" }",
"sy": "Sky Movies presents a host of movie playlists hand selected by celebrities from the world of film, music and television. What better way to get a movie recommendation?!"
},
{
"nodetype": "MENU",
"nodeid": "D15650_546872696C6C6572",
"t": "Thriller",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "They fought the law, but who won? Take a seat, but you'll only use the edge of it with these nail-biters. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "D4410_5363692D466920262046616E74617379",
"t": "Sci-Fi & Fantasy",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "Buckle up for a cosmic ride beyond the final frontiers and into a world of dazzling imagination. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "D12715_486F72726F72",
"t": "Horror",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "From hardcore gore to supernatural shivers and psychological sweats, welcome to the fear factory. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "C22027_4163746F7273",
"t": "Actors",
"renderhints": "{ \"template\": \"MENUPANEL\" }",
"sy": "Have a look through our extensive actor collection. Who is your silver screen favourite?"
},
{
"nodetype": "MENU",
"nodeid": "D4597_436C617373696373",
"t": "Classics",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "From the golden age of Hollywood to bold 1970s cinema, welcome to the classics collection. "
},
{
"nodetype": "MENU",
"nodeid": "D16898_4472616D61",
"t": "Drama",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "Hankies at the ready for a place where emotions run high and tear ducts run dry. Press 'Select' for our highlights and if you then want more, press the yellow button."
},
{
"nodetype": "MENU",
"nodeid": "D17140_526F6D616E6365",
"t": "Romance",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "Movies not music are the food of love, so feast on these romantic greats."
},
{
"nodetype": "MENU",
"nodeid": "D17373_496E646965",
"t": "Indie",
"renderhints": "{\"template\": \"5COL\", \"imagetype\": \"COVER\", \"structure\": \"EXPAND-CHILDREN\"}",
"sy": "The best in exciting cinema from Hollywood and beyond."
},
{
"nodetype": "MENU",
"nodeid": "B58614_3344",
"t": "3D",
"renderhints": "{ \"template\": \"5COL\", \"imagetype\": \"COVER\" }",
"sy": "If you want the best eye popping 3D blockbuster titles, you have come to the right place. Sit back, put your specs on, and enjoy these movies in glorious 3D."
}
]
})
    import pprint
    pprint.pprint(dir(t.rows[0]))
    print t.rows[0].keys
    print t.rows[0].row
    for cell in t.rows[0].row:
        print t.rows[0].row[cell].value
        print unicode(t.rows[0].row[cell])
    print unicode(t)
    #print t.fixed_width()
    0/0




    pass
    assert Cell([u'first\nsecond', [u'third', u'fourth',[u'fifth']]]).value == [u'first',
                                                                                u'second',
                                                                                u'third',
                                                                                u'fourth',
                                                                                u'fifth'], u"Well that's not right!"
    assert Cell([u'first\nsecond',[u'third', u'fourth',[u'fifth']]]).width() == 6, u"width is wrong"
    assert len( Cell([u'first\nsecond',[u'third', u'fourth',[u'fifth']]]) ) == 5, u"length"






    t=Table(headings       = [{u'heading': u'xxxxx\nyyy\nzzz', u'justify': u'>'},
                              {u'heading': u'y', u'justify': u'^'},
                              {u'heading': u'z'}],
            show_summaries = True,
            title = [u'This is the title\nThis is a second line', u'this is s third line that is really really really long']
            )

    for row in ({u'xxxxx\nyyy\nzzz':u'a',  u'y':1,    u'z':Cell(u'cbbbbbb')},
                {u'xxxxx\nyyy\nzzz':u'eg', u'y':u'f', u'z':Cell(value = u'gbb', href=u'www.google.com')},
                {u'xxxxx\nyyy\nzzz':u'hg', u'y':u'i', u'z':u'jb'},
                {u'xxxxx\nyyy\nzzz':u'kgg',u'y':u'l', u'z':u'm'},
                {u'xxxxx\nyyy\nzzz':u'a',  u'y':u'b', u'z':u'cbbbbbb'},
                {u'xxxxx\nyyy\nzzz':u'eg', u'y':u'f', u'z':u'gbb'},
                {u'xxxxx\nyyy\nzzz':u'hg', u'y':u'i', u'z':u'jb'},
                {u'xxxxx\nyyy\nzzz':u'kgg',u'y':u'l', u'z':u'm'},
                {u'xxxxx\nyyy\nzzz':u'a',  u'y':u'b', u'z':u'cbbbbbb'},
                {u'xxxxx\nyyy\nzzz':u'eg', u'y':u'f', u'z':u'gbb'},
                {u'xxxxx\nyyy\nzzz':u'hg', u'y':u'i', u'z':u'jb'},
                {u'xxxxx\nyyy\nzzz':u'kgg',u'y':u'l', u'z':u'm'},
               ):
        t.add_row(row)
    t.add_row((u'fd',u'rr',u'ggg\nffff'))
    print unicode(t)
    t.row_numbers = False
    print unicode(t)
    t.row_numbers = True
    t.add_summaries({u'y':u'123456sfdsfdsfdsfdsa'})
    t.add_summaries({u'z':[u'zr1',u'z r 2']})
    print unicode(t)
    print t.as_text(solid_borders=False, cross_char='-')

    print t.html()


    #print t.jira_table_notation()


    t1=Table(headings       = [{u'heading': u'h1',},
                               {u'heading': u'h2'}],
             show_summaries = False,
             )



    t2=Table(headings       = [{u'heading': u't2h1',},
                               {u'heading': u't2h2'}],
             show_summaries = False,
             row_numbers    = False
             )

    t3=Table(headings       = [{u'heading': u't3h1',},
                               {u'heading': u't3h2'}],
             show_summaries = False,
             )


    t3.add_row((u'blah\nblah', [u'blah', u'blah']))

    t2.add_row((Cell(value = u'2.1', href=u'www.google.com'), t3))


    t1.add_row((u'A', Cell(value = t2, href = u'www.apple.com')))
    t1.add_row((Cell(value = u'<img src="http://autoskills.aaa.com/documents/11475/29113/Practice_Test.jpg"/>',
                     href  = u"http://autoskills.aaa.com/documents/11475/29113/Practice_Test.jpg"),
               u'2'))

    print unicode(t1)
    #print t1.fixed_width()
    print t1.jira()
    f = itt_html.open(u'temp.html')
    f.write(t1.html())
    f.close()
    webbrowser.open(u'temp.html')
