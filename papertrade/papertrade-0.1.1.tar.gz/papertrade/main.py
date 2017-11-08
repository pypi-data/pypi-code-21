#!/usr/bin/python3

#    This file is part of 'papertrade'.
#
#    papertrade is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    papertrade is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with papertrade.  If not, see <http://www.gnu.org/licenses/>.


'''Main file for papertrade.'''

from yahoo_finance import Share
import time

import ui
import papertrade.database as db
import papertrade.calculations as cal

DBFILE = "papertrade.dat"
PROVISION = 5.0
TAX = 0.3   # as a percent factor

def show_overview():
    capital = db.get_capital(DBFILE)
    profit = db.get_profit(DBFILE)
    loss = db.get_loss(DBFILE)

    info = ui.underline("Current overview")

    due_tax = round((db.get_profit(DBFILE) + db.get_loss(DBFILE))*TAX, 2)
    if due_tax < 0:
        due_tax = 0

    trades_value = get_trades_value()
    total_value = capital + trades_value
    #total_profit = profit - loss - due_tax
    total_profit = cal.difference(profit, [loss, due_tax])

    lines = (
        "Capital:\t$ {0}\n"
        "Profit:\t\t$ {1}\n"
        "Loss:\t\t$ {2}\n"
        "Total value:\t$ {3}\n"
        "Due tax:\t$ {4}\n"
        "Total profit:\t$ {5}\n"
    ).format(
        capital,
        profit,
        loss,
        total_value,
        due_tax,
        total_profit
    )

    info += lines

    ui.show(info)

def get_trades_value():
    data = db.read_table(DBFILE, "trades")

    total_value = 0
    for trade in data:
        ticker = Share(trade[1])
        value = trade[2]*float(ticker.get_price()) - PROVISION
        total_value += value

    return round(total_value, 2)

def active_trades():
    def lambda_maker(i, table):     # using lambdas directly doesn't work
        return lambda: trade_menu(table[i])

    trade_table = db.read_table(DBFILE, "trades")
    heading = ui.underline("Active trades")
    menuoptions = []

    length = len(trade_table)
    if length == 1:
        menuoptions.append(
            {
                "key":str(1),
                "text":trade_table[0][1],
                "function":lambda: trade_menu(trade_table[0])
            }
        )
    elif length > 1:
        func_list = []
        for i in range(length):
            func_list.append(lambda_maker(i, trade_table))
        for i in range(length):
            menuoptions.append(
                {
                    "key":str(i+1),
                    "text":trade_table[i][1],
                    "function":func_list[i]
                }
            )
    menuoptions.append(
        {
            "key":"n",
            "text":"New trade",
            "function":new_trade
        }
    )
    ui.menu(menuoptions, heading)

def trade_menu(trade):
    share_info = Share(trade[1])
    current_price = float(share_info.get_price())
    growth = cal.growth(trade[3], current_price)
    buy = trade[3]
    quote = trade[2]
    provision = trade[5]*2.0

    current_quote_cash = current_price*quote
    # profit = current_quote_cash - provision - buy*quote
    profit = cal.difference(current_quote_cash, [provision, buy*quote])
    sale = (profit, current_quote_cash - provision/2, current_price)

    heading = ui.underline(trade[1] + " | " + share_info.get_name())
    info = (
        "Bought price:  $ {0}\n"
        "Current sell:  $ {1}\n"
        "Growth: {2}%\n"
        "Prov:  $ {3}\n"
        "Quote: {4}\n"
        "Profit if sold:  $ {5}"
    ).format(
        buy,
        round(float(current_price), 2),
        growth[0],
        trade[5],
        trade[2],
        round(profit, 2)
    )
    info = heading + "\n" + info + "\n"

    menuitems = [   # Should contain options about what to do with the trade.
        {
            "key":"s",
            "text":"Sell",
            "function":lambda: sell(trade, sale)
        }
    ]

    if ui.menu(menuitems, info):
        return 1 # Get out!

def sell(trade, sale):
    if not ui.yn_prompt("Are you sure you wish to sell?"):
        return

    trade_id = trade[0]
    trade = list(trade)
    trade[0] = int(time.time())
    provision = trade[5]
    profit = sale[0]
    cash = sale[1]

    trade[4] = sale[2]

    db.enter_record(DBFILE, "history", trade)
    db.delete_trade(DBFILE, "trades", trade_id)

    new_capital = round(db.get_capital(DBFILE) + cash, 2)
    db.update_total_record(DBFILE, "Capital", new_capital)

    if profit > 0:
        new_profit = round(db.get_profit(DBFILE) + profit, 2)
        db.update_total_record(DBFILE, "Profit", new_profit)
    elif profit < 0:
        new_loss = round(db.get_loss(DBFILE) + profit, 2)
        db.update_total_record(DBFILE, "Loss", new_loss)

    return 1 # Get out!

def new_trade():
    ticker = input("\nEnter ticker: ").strip().upper()
    share_info = Share(ticker)
    price = float(share_info.get_price())
    capital = db.get_capital(DBFILE)

    heading = ui.underline("New trade")
    info = (
        "{0} | {1} \n"
        "Price:  $ {2}\n"
        "Capital:  $ {3}\n"
    ).format(
        ticker,
        share_info.get_name(),
        round(price, 2),
        capital
    )

    print("\n"*3 + heading+info)

    while True:
        quote = int(input("Enter quote: "))
        if price*quote > capital:
            if ui.yn_prompt("You can't afford this quote. Abort?"):
                print("Trade cancelled.")
                break
            else:
                continue

        cost = round(price*quote + PROVISION, 2)

        prev_info = info
        info = (
            "Quote: {0}\n"
            "Total cost:  $ {1}\n"
        ).format(
            quote,
            cost
        )

        info = "\n" + prev_info + info
        print(info)

        if ui.yn_prompt("Complete trade?"):
            trade = [
                int(time.time()),
                ticker,
                quote,
                price,
                0.0,
                PROVISION
            ]

            db.enter_record(DBFILE, "trades", trade)

            new_capital = round(capital - price*quote - PROVISION, 2)
            db.update_total_record(DBFILE, "Capital", new_capital)
            print("Trade completed.")
            return 1
        else:
            print("Trade cancelled.")
            break

def trade_history():
    table = db.read_table(DBFILE, "history")
    display_table = []
    for row in table:
        display_table.append(row)
    display_table = sorted(display_table)

    info = ui.underline("Trade history")
    for row in display_table:
        timestruct = time.localtime(row[0])
        #profit = round(row[2]*row[4] - row[2]*row[3] - row[5]*2, 2)
        profit = cal.difference(row[2]*row[4], [row[2]*row[3], row[5]*2])

        new_row = (
            "{0}-{1}-{2} {3}:{4} |"       # Datestamp and time
            "  {5}\t| Profit:  $ {6}\n"   # Ticker, and profit in dollars
        ).format(
            timestruct[0],  # year
            timestruct[1],  # month
            timestruct[2],  # day
            timestruct[3],  # hour
            timestruct[4],  # minute
            row[1],         # ticker
            profit
        )

        info += new_row

    ui.show(info)

def main_menu():
    menulist = [
        {"key":"o", "text":"Overview", "function":show_overview},
        {"key":"t", "text":"Active trades", "function":active_trades},
        {"key":"h", "text":"Trade history", "function":trade_history},
    ]

    heading = ui.underline("Papertrade - Main menu")

    ui.menu(menulist, heading)
