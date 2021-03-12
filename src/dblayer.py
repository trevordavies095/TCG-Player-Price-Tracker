import sqlite3
from datetime import datetime

class dblayer:
    def worth(self):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        n_price_query = """
            SELECT SUM(y.normal_price) FROM (
                SELECT card_id, MAX(price_date) AS MaxDate
                FROM price_data 
                GROUP BY card_id
            )  x
            INNER JOIN price_data y 
                ON y.card_id = x.card_id AND y.price_date = MaxDate
            INNER JOIN card c
                ON c.id = x.card_id
            WHERE c.foil = 0
        """

        f_price_query = """
            SELECT SUM(y.foil_price) FROM (
                SELECT card_id, MAX(price_date) AS MaxDate
                FROM price_data 
                GROUP BY card_id
            )  x
            INNER JOIN price_data y 
                ON y.card_id = x.card_id AND y.price_date = MaxDate
            INNER JOIN card c
                ON c.id = x.card_id
            WHERE c.foil = 1
        """

        #****** start worth() ******#

        n_price = conn.execute(n_price_query).fetchone()[0]
        f_price = conn.execute(f_price_query).fetchone()[0]

        return [n_price, f_price]

    '''
    #TODO Need to clean up the query. It uses IS NOT 'None'. Is there a way to pass in the None value into the query instead of hard coding?
    '''
    def export(self):
        # Local constants

        # Local variabes
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        q = """
            SELECT c.card_name, c.set_name, p.normal_price, p.foil_price, MAX(p.price_date) FROM card c 
            INNER JOIN price_data p 
                ON p.card_id = c.id AND p.foil_price IS NOT 'None' 
            GROUP BY c.id ORDER BY p.foil_price
        """

        #****** start export() ******#

        return conn.execute(q)


    '''
    #TODO Need to clean up the query. It uses IS NOT 'None'. Is there a way to pass in the None value into the query instead of hard coding?
    '''
    def top25(self):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        #****** start top25() ******#
        q = """
            SELECT c.card_name, c.set_name, p.normal_price, p.foil_price, MAX(p.price_date) FROM card c 
            INNER JOIN price_data p 
                ON p.card_id = c.id AND p.foil_price IS NOT 'None' 
            GROUP BY c.id 
            ORDER BY p.foil_price 
            DESC LIMIT 25
        """

        return conn.execute(q).fetchall()

    def update_prices(self):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        get_urls = "SELECT DISTINCT url FROM card;"
        urls = c.execute(get_urls).fetchall()

        #****** start update_prices() ****** #

        print("Updating prices...")

        for url in urls:
            card_data = parse(url[0])
            insert_price_data(card_data)

    def delete_card(self, url):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        card_id = "SELECT id FROM card WHERE url = ?;"
        card_delete = "DELETE FROM card WHERE id = ?;"
        price_delete = "DELETE FROM price_data WHERE card_id = ?;"

        #****** start delete_card() ******#
        
        card_id = str(conn.execute(card_id, [url]).fetchall()[0][0])
        c.execute(card_delete, [card_id])
        conn.commit()
        c.execute(price_delete, [card_id])
        conn.commit()


    def insert_price_data(self, card_data):
        # Local constants

        # Local variables
        card_id = "SELECT id FROM card WHERE url = ?;"
        price_insert = "INSERT INTO price_data (card_id, price_date, normal_price, foil_price) VALUES (?, ?, ?, ?)"
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        #****** start insert_price_data() ******# 

        card_id = conn.execute(card_id, [card_data["url"]]).fetchall()[0][0]
        if "Normal" not in card_data.keys(): card_data["Normal"] = None
        if "Foil" not in card_data.keys(): card_data["Foil"] = None

        c.execute(price_insert, [card_id, datetime.now().strftime("%Y%m%d %H:%M:%S"), card_data["Normal"], card_data["Foil"]])
        conn.commit()


    # TODO: If URL is duplicate, increase quanity instead of creating a new row.
    def insert_card(self, card_data):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        card_insert = "INSERT INTO card (card_name, set_name, url) VALUES (?, ?, ?)"

        #****** start insert_card() ******#

        c.execute(card_insert, [card_data["card_name"], card_data["set_name"], card_data["url"]])
        conn.commit()

        self.insert_price_data(card_data)

