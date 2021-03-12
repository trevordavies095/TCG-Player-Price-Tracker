import csv
import locale
import os.path
import sys
import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dblayer import dblayer
from prettytable import PrettyTable

def main():
    # Local constants

    # Local variables
    args = sys.argv
    db = dblayer()

    #****** start main() ******#
    
    if len(args) < 2:
        usage()
        sys.exit()

    # Moved to DBLayer.py
    if args[1] == "add":
        db.insert_card(parse(args[2].split("?")[0]))

    # Moved to DBLayer.py
    elif args[1] == "delete":
        db.delete_card(args[2].split("?")[0])

    # Moved to DBLayer.py
    elif args[1] == "update":
        db.update_prices()

    # Moved to DBLayer.py
    elif args[1] == "top25":
        t = PrettyTable(['Pokemon', 'Set', 'Normal Price', 'Foil Price', 'Price Date'])	
        res = db.top25()
        for r in res:
            t.add_row([r[0], r[1], r[2], '$' + str(r[3]), r[4]])

        print(t)

    # Moved to DBLayer.py
    elif args[1] == "export":
        filename = 'price_export' + datetime.now().strftime("%Y%m%d%H%M") + '.csv'
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

    elif args[1] == "import":
        f = open(args[2], "r")

        for l in f:
            insert_card(parse(l.strip().split("?")[0]))

    elif args[1] == "worth":
        prices = db.worth()

        locale.setlocale(locale.LC_ALL, '')
        print()
        print("\tNormal: " + locale.currency(prices[0], grouping=True))
        print("\tFoil  : " + locale.currency(prices[1], grouping=True))
        print("\tTotal : " + locale.currency(prices[0]+prices[1], grouping=True))
        print()


def parse(url):
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
    # Local constants

    # Local variabes

    #****** start is_number() ******#

    try:
        float(str)
        return True
    except ValueError:
        return False


def usage():
    # Local constants

    # Local variables

    #****** start usage() ******#

    pass


if __name__ == '__main__':
    main()