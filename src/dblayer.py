import sqlite3
from datetime import datetime


class dblayer:
    """
    This is a class for all database interactions for TCGCardTracker.py.

    Attributes:
        None
    """

    def worth(self):
        """
        This function calculates how much your collection is currently worth.

        Parameters:
            None
        
        Returns:
            List: A list of where index 0 contains the normal price worth, index 1 contains the foil price worth.
        """

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


    def graph_worth(self):
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        date_q = "SELECT DISTINCT price_date FROM price_data;"
        n_price_query = """
            SELECT SUM(y.normal_price) FROM (
                SELECT card_id, MAX(price_date) AS MaxDate
                FROM price_data 
                GROUP BY card_id
            )  x
            INNER JOIN price_data y 
                ON y.card_id = x.card_id
            INNER JOIN card c
                ON c.id = x.card_id
            WHERE c.foil = 0
            AND y.price_date = ?
        """

        f_price_query = """
            SELECT SUM(y.foil_price) FROM (
                SELECT card_id, MAX(price_date) AS MaxDate
                FROM price_data 
                GROUP BY card_id
            )  x
            INNER JOIN price_data y 
                ON y.card_id = x.card_id
            INNER JOIN card c
                ON c.id = x.card_id
            WHERE c.foil = 1
            AND y.price_date = ?
        """

        # key: date, value: list, index 0 - normal, index 1 - foil, index 2 - total
        prices = {}
        x = []

        #****** start graph_worth() ******#

        # Grab list of distinct price_dates
        dates = c.execute(date_q).fetchall()

        # For date in price_dates
        for date in dates:
            date = date[0]

            # Calculate worth for that day
            n_worth = float(c.execute(n_price_query, [date]).fetchone()[0])
            f_worth = float(c.execute(f_price_query, [date]).fetchone()[0])

            t_worth = n_worth + f_worth

            # Append to some list
            prices[date] = [n_worth, f_worth, t_worth]

        return prices
        

    def export(self):
        """
        This function queries the database and returns your collection.

        Parameters:
            None
        
        Returns:
            Tuple of tuples.
                Index 0 - Card name
                Index 1 - Set name
                Index 2 - Normal price
                Index 3 - Foil price
                Index 4 - Price date
        """

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


    def top25(self):
        """
        This function grabs the 25 most valuable cards in your collection.

        Parameters:
            None

        Returns:
            Tuple of tuples.
                Index 0 - Card name
                Index 1 - Set name
                Index 2 - Normal price
                Index 3 - Foil price
                Index 4 - Price date
        """

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

    
    def get_urls(self):
        """
        This function grabs the TCG Player URL for all cards in the collection.

        Parameters:
            None

        Returns:
            Tuple of tuples.
                Index 0 - TCG Player URL
        """

        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        get_urls = "SELECT DISTINCT url FROM card;"

        #****** start get_urls() ******#

        return c.execute(get_urls).fetchall()


    def delete_card(self, url):
        """
        This function takes in a URL and either 1) decreases the quantity of the card in the collection or 2) deletes the card
        from the collection if the quantity is 1.

        Parameters:
            url (string): TCG Player URL of the card to be deleted.

        Returns: 
            string: Either the quantity decreased or the card was deleted from the collection.
        """
         
        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        card_id = "SELECT id, quantity FROM card WHERE url = ?;"
        card_delete = "DELETE FROM card WHERE id = ?;"
        price_delete = "DELETE FROM price_data WHERE card_id = ?;"
        decrease_quan = "UPDATE CARD SET quantity = ? WHERE id = ?;"

        #****** start delete_card() ******#
        
        res = conn.execute(card_id, [url]).fetchall()

        if res[0][1] > 1:
            card_id = res[0][0]
            quan = int(res[0][1]) - 1
            c.execute(decrease_quan, [quan, card_id])
            conn.commit()

            return "Quanity decreased."

        else: 
            card_id = res[0][0]
            c.execute(card_delete, [card_id])
            conn.commit()
            c.execute(price_delete, [card_id])
            conn.commit()

            return "Card deleted from collection"


    def insert_price_data(self, card_data):
        """
        This function will insert the most recent price data that was scraped from TCG Player.

        Parameters:
            card_data (Dictionary): Keys are the following 
                url
                card_name
                set_name
                Foil
                Normal

        Returns:
            None
        """

        # Local constants

        # Local variables
        card_id = "SELECT id FROM card WHERE url = ?;"
        price_insert = "INSERT INTO price_data (card_id, price_date, normal_price, foil_price) VALUES (?, ?, ?, ?)"
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        #****** start insert_price_data() ******# 

        if "Normal" not in card_data.keys(): card_data["Normal"] = None
        if "Foil" not in card_data.keys(): card_data["Foil"] = None

        card_id = conn.execute(card_id, [card_data["url"]]).fetchall()[0][0]
        c.execute(price_insert, [card_id, datetime.now().strftime("%Y-%m-%d"), card_data["Normal"], card_data["Foil"]])
        conn.commit()


    def insert_card(self, card_data):
        """
        This function adds a card into the database's card table.

        Parameters:
            card_data (Dictionary): Keys are the following
                url
                card_name
                set_name
                Foil
                Normal

        Returns:   
            string: Card who's quantity was increased if it was already in the database.
        """

        # Local constants

        # Local variables
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        card_id = "SELECT id, quantity FROM card WHERE url = ?"
        card_insert = "INSERT INTO card (card_name, set_name, url, foil) VALUES (?, ?, ?, ?)"
        update_quantity = "UPDATE CARD SET quantity = ? WHERE id = ?"
        foil = None


        #****** start insert_card() ******#

        # Check to see if the card is already in the db
        res = conn.execute(card_id, [card_data["url"]]).fetchall()

        # Card already exists in the database
        if len(res) > 0:
            card_id = res[0][0]
            quantity = int(res[0][1]) + 1

            c.execute(update_quantity, [quantity, card_id])
            conn.commit()

            return card_data["card_name"] + " - " + card_data["set_name"] + ": " + str(quantity) + " cards in collection."

        # Else the card is not already in the database
        else:
            if "Normal" not in card_data.keys(): card_data["Normal"] = None
            if "Foil" not in card_data.keys(): card_data["Foil"] = None

            if card_data["Normal"] and card_data["Foil"]:
                foil = input("Foil? (Y/N) > ").lower()

            if foil == "y": c.execute(card_insert, [card_data["card_name"], card_data["set_name"], card_data["url"], 1])
            else: c.execute(card_insert, [card_data["card_name"], card_data["set_name"], card_data["url"], 0])
            conn.commit()

            self.insert_price_data(card_data)


    def get_card_price_data(self, url):
        """
        This function will query the database for all pricing data for a given card.

        Parameters:
            url (string): TCG Player URL for a given card.

        Returns:
            Tuple of tuples.
                Index 0 - Price date
                Index 1 - Price data
        """

        # Local constants

        # Local variables
        card_id = "SELECT id FROM card WHERE url = ?;"
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()
        price_data_q = """
            SELECT MAX(p.price_date),
	            CASE 
		            WHEN c.foil = 1 THEN MAX(p.foil_price)
		            ELSE MAX(p.normal_price)
	            END AS 'price'
            FROM price_data p
            INNER JOIN card c
                ON c.id = p.card_id
            AND c.id = ?
            GROUP BY p.price_date, 'price'
            ORDER BY p.price_date ASC
        """

        #****** start get_price_data() ******#

        card_id = conn.execute(card_id, [url]).fetchall()[0][0]
        price_data = conn.execute(price_data_q, [card_id]).fetchall()

        return price_data


    def get_card_details(self, url):
        """
        This function will query the database for the card name, set name and whether a card is a foil for
        a given card.

        Parameters:
            url (string): TCG Player URL for a given card.

        Returns:
            Tuple of tuples.
                Index 0 - Card name
                Index 1 - Set name
                Index 2 - Foil flag
        """

        # Local constants

        # Local variables
        card_details_q = "SELECT card_name, set_name, foil FROM card WHERE url = ?"
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        #****** start get_card_details() ******#

        card_details = c.execute(card_details_q, [url]).fetchall()

        return card_details

    
    def ticker(self, way_back):
        """
        This function will calculate the change in the collections card price for a given timeframe.

        Parameters:
            way_back (int): Default is 7 days, otherwise it is user specified.

        Returns:
            data (Dictionary): This provides pricing data for cards which are used as the key in the dictionary. List of pricing data is the value.
                Index 0 - Start date
                Index 1 - Start price
                Index 2 - Current date
                Index 3 - Current price
                Index 4 - Change in price
        """

        # Local constants

        # Local variables
        ids_q = "SELECT DISTINCT id FROM card;"
        current_q = """
            SELECT c.card_name || ' (' || c.set_name || ')', MAX(p.price_date),
	           CASE 
		            WHEN c.foil = 1 THEN p.foil_price
		            ELSE p.normal_price
	            END
            FROM price_data p
            INNER JOIN card c
                ON c.id = p.card_id
            AND c.id = ?
        """

        where_clause = "WHERE DATE(p.price_date) > DATE('now', '-" + way_back + " days')"

        start_q = """
            SELECT c.card_name || ' (' || c.set_name || ')', p.price_date,
	           CASE 
		            WHEN c.foil = 1 THEN p.foil_price
		            ELSE p.normal_price
	            END
            FROM price_data p
            INNER JOIN card c
                ON c.id = p.card_id AND c.id = ?
            """ + where_clause + """
			ORDER BY p.price_date ASC
			LIMIT 1
        """
        data = {}
        conn = sqlite3.connect("tcgcardtracker.db")
        c = conn.cursor()

        #****** start ticker() ******#

        # Grab week worth of price_data for all cards
        ids = c.execute(ids_q).fetchall()

        for id in ids:
            id = id[0]
            start_data = conn.execute(start_q, [id]).fetchall()
            current_data = c.execute(current_q, [id]).fetchall()

            d = [start_data[0][1], start_data[0][2], current_data[0][1], current_data[0][2], float(current_data[0][2]) - float(start_data[0][2])]
            data[start_data[0][0]] = d
        return data        

