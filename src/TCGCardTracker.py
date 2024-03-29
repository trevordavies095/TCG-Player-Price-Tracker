import csv
import locale
import os.path
import sys
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from dblayer import dblayer
from graphutil import graphutil
from prettytable import PrettyTable

def main():
    """
    This function handles any logic that has to do with command arguments.
    It is the driver of the application.

    Parameters:
        None
        
    Returns:
        None
    """

    # Local constants

    # Local variables
    args = sys.argv
    db = dblayer()
    g = graphutil()

    #****** start main() ******#
    
    # Check to see if too many args, or need help
    if len(args) < 2 or args[1] == "help":
        usage()

    # User chose add command
    if args[1] == "add":
        if len(args) < 3: usage()
        res = db.insert_card(parse(args[2].split("?")[0]))

        if res is not None:
            print("\n" + res + "\n")

    # User chose delete command
    elif args[1] == "delete":
        if len(args) < 3: usage()
        res = db.delete_card(args[2].split("?")[0])

        if res is not None:
            print("\n" + res + "\n")

    # User chose update command 
    elif args[1] == "update":
        print()
        print("\tGetting URLs...")
        urls = db.get_urls()

        print("\tUpdating prices...")
        for url in urls:
            db.insert_price_data(parse(url[0]))

        print("\tDone.\n")

    # User chose top25 command
    elif args[1] == "top25":
        t = PrettyTable(['Pokemon', 'Set', 'Normal Price', 'Foil Price', 'Price Date'])	
        res = db.top25()
        for r in res:
            t.add_row([r[0], r[1], r[2], '$' + str(r[3]), r[4]])

        print(t)

    # User chose export command
    elif args[1] == "export":
        urls = db.get_urls()
        filename = 'export' + datetime.now().strftime("%Y%m%d%H%M") + '.txt'

        with open(filename, 'w') as f:
            for url in urls:
                f.write(url[0] + "\n")

    # User chose export_collection command 
    elif args[1] == "export_collection":
        filename = 'collection_export' + datetime.now().strftime("%Y%m%d%H%M") + '.csv'
        with open(filename, 'w', newline = '') as csvfile:
            headers = ['Pokemon', 'Set', 'Normal Price ($)', 'Foil Price ($)', 'Price Date']
            w = csv.writer(csvfile, delimiter=',')
            w.writerow(headers)

            res = db.export()
            
            for r in res:
                r = list(r)
                if r[2] == None: r[2] = ''
                if r[3] == None: r[3] = ''
                w.writerow([r[0], r[1], str(r[2]), str(r[3]), r[4]])

    # User chose import command
    elif args[1] == "import":
        if len(args) < 3: usage()
        f = open(args[2], "r")

        for l in f:
            db.insert_card(parse(l.strip().split("?")[0]))

    # User chose worth command
    elif args[1] == "worth":
        prices = db.worth()

        locale.setlocale(locale.LC_ALL, '')
        print()
        print("\tNormal: " + locale.currency(prices[0], grouping=True))
        print("\tFoil  : " + locale.currency(prices[1], grouping=True))
        print("\tTotal : " + locale.currency(prices[0]+prices[1], grouping=True))
        print()

    # User chose graph command
    elif args[1] == "graph":
        if len(args) < 3: usage()
        url = args[2].split("?")[0]
        price_data = db.get_card_price_data(url)
        card_details = db.get_card_details(url)
        g.graph_card_worth(price_data, card_details)
    
    # User chose graph_worth command
    elif args[1] == "graph_worth":
        if len(args) < 2: usage()
        price_data = db.graph_worth()
        g.graph_collection_worth(price_data)

    # User chose ticker command
    elif args[1] == "ticker":
        if len(args) > 2: days_back = str(args[2])
        else: days_back = str(7)

        ret = db.ticker(days_back)

        locale.setlocale(locale.LC_ALL, '')   
        data = []

        for key, value in ret.items():
            data.append([key, value[0], value[1], value[2], value[3], value[4]])
        
        data.sort(key=lambda x: float(x[5]))

        t = PrettyTable(['Pokemon Card', 'Start Price (' + datetime.strftime(datetime.today() - timedelta(days=int(days_back)), "%Y-%m-%d") + ")", 'Current Price (' + data[0][3] + ")", "Change (+/-)"])

        for x in reversed(data):
            if float(x[2]) > float(x[4]): x[5] = "-"
            else: x[5] = "+"
            x[5] += str(round(abs(float(x[2]) - float(x[4])), 2))
            t.add_row([x[0], locale.currency(x[2], grouping=True), locale.currency(x[4], grouping=True), x[5]])

        print(t)


def parse(url):
    """
    This function will scrape the pricing information off of a provided TCG Player URL.

    Parameters:
        url (string): TCG Player URL of the card to be web scraped.
    
    Returns:
        card_data (Dictionary): Keys are the following
            url
            card_name
            set_name
            Foil
            Normal
    """

    # Local constants

    # Local variables
    data = requests.get(url).text
    soup = BeautifulSoup(data, "html.parser")
    divs = soup.find("div", "price-point price-point--market")
    labels = divs.find_all("th", "price-point__name")
    prices = divs.find_all("td", "price-point__data")
    card_name = soup.find("h1", {"class": "product-details__name"}).text
    set_name = soup.find("a", attrs={"data-aid": "setNameSearch"}).text
    card_data = {
        "url": url,
        "card_name": card_name.replace("\'", ""),
        "set_name": set_name.replace("\'", "")
    }

    #****** start parse() ******#

    for i, val in enumerate(prices):
        # Verifying what's in prices is actual a number of sorts
        if not is_number(prices[i].text[1:]): card_data[labels[i].text] = None
        else: card_data[labels[i].text] = float(prices[i].text[1:])

    return card_data


def is_number(str):
    """ 
    This function takes in a string and determines if it is a real number.

    Parameters:
        str (string): String value we want to determine if it is a number.

    Returns:
        Boolean: True if it is number, false otherwise.

    """

    # Local constants

    # Local variabes

    #****** start is_number() ******#

    try:
        float(str)
        return True
    except ValueError:
        return False


def usage():
    """ 
    This function will output how to use the application.

    Parameters:
        None

    Returns:
        None
    """

    # Local constants

    # Local variables

    #****** start usage() ******#
    print()
    print(" Usage: python TCGCardTracker.py <arguement below> <optional-argument-1>")
    print("\tadd (Optional): Add a card to your collection. Requires TCGPlayer URL.")
    print("\tdelete (Optional): Delete a card from your collection. Requires TCGPlayer URL.")
    print("\tupdate (Optional): Updates pricing data for every card in your collection.")
    print("\ttop25 (Optional): Outputs the 25 most valuable cards from your collection.")
    print("\texport (Optional): Exports a list of TCGPlayer URLs to a text file.")
    print("\texport_collection (Optional): Exports your collection to a .csv including most recent price data.")
    print("\timport (Optional): Imports a text file of TCGPlayer URLs to bulk import cards into your collection. Requires text file.")
    print("\tworth (Optional): Ouputs how much your collection is worth using latest price data.")
    print("\tgraph (Optional): Outputs historical pricing data for a given card. Requires TCGPlayer URL.")
    print("\tgraph (Optional): Outputs historical pricing data for a given card. Requires TCGPlayer URL.")
    print("\tticker (Optional): Displays a ticker grid of the change in value over a given time. If run without the days back parameter it will default to 7 days.")
    sys.exit()
    

if __name__ == '__main__':
    main()