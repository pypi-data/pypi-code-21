import datetime
import subprocess
import os
import configparser
from collections import namedtuple

import pygsheets
from trello import TrelloClient
from pick import pick

def main():
  # Config and Setup
  config = configparser.ConfigParser()
  home = os.path.expanduser("~")
  config_path = os.path.join(home, ".trkr/config.ini")
  config.read(config_path)

  trello_config = config["trello"]
  sheet_config = config["sheets"]
  email = config["default"]["email"]

  # Authorize API endpoints
  trello_client = TrelloClient(
    api_key=trello_config.get("api_key"),
    api_secret=trello_config.get("api_secret"),
    token=trello_config.get("token"),
  )

  keyfile = os.path.join(home, ".trkr/keyfile.json")
  ps = pygsheets.authorize(service_file=keyfile)
  wks = ps.open_by_url(sheet_config.get("url")).worksheet_by_title(sheet_config.get("wks_name"))

  # Get current datetime
  now = datetime.datetime.now()
  timestamp = now.strftime("%m/%d/%Y %H:%M:%S")

  # Start requesting user input
  description = input("* Description of work: ")
  if not description:
    print("No description provided, using last commit message instead!")
    description = subprocess.check_output([
      "git",
      "log",
      "-1",
      "--pretty=%B"
    ]).strip().decode('ascii')

  hours = validate_hours()

  # Options for trello card selection
  trello = input("[trello] Input/Search/Pick/None [i/s/p/n]: ")
  if trello == "i":
    card_name = input("[trello] Card URL: ")
  elif trello == "s":
    card_name = search_trello(trello_client, trello_config)
  elif trello == "p":
    card_name = filter_trello(trello_client, trello_config)
  else:
    card_name = ""

  date = validate_date() or now.strftime("%m/%d/%Y")

  wks.insert_rows(wks.rows - 1, 1, [
    timestamp,
    date,
    description,
    hours,
    card_name,
    email
  ], True)

  # Also write to trkr journal
  journal = open(os.path.join(home, ".trkr/journal.csv"), "a+")
  journal.write(f"\"{timestamp},{date},{description},{hours},{card_name},{email}\"\n")
  journal.close()

########## Conveniance methods
def search_trello(client, config):
  query = input("[trello] Search term(s): ")
  if not query: return

  cards = client.search(
    query,
    True,
    ["cards"],
    [config["board_id"]]
  )
  return pick_card(cards)

def filter_trello(client, config):
  board = client.get_board(config["board_id"])
  cards = board.get_cards(
    None,
    "visible"
  )
  cards = filter(lambda x: config["user_id"] in x.member_ids, cards)
  return pick_card(list(cards), "Select from your cards")

def pick_card(cards, title="Select card"):
  title = "[trello] " + title
  options = list(map((lambda c: c.name), cards))
  option, index = pick(options, title)
  return cards[index].short_url

def validate_hours():
  while True:
    try:
      return float(input("* Hours spent: "))
    except ValueError:
      print("Format Error: Must be a number")

def validate_date():
  while True:
    try:
      date_text = input("Date (MM/DD/YYYY): ")
      if date_text:
        datetime.datetime.strptime(date_text, "%m/%d/%Y")
        return date_text
    except ValueError:
      print("Format Error: Must be formatted as MM/DD/YYYY")
##########
