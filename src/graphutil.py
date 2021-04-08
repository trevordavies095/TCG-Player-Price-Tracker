import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

class graphutil:
    """
    This is the class that handles all graphing aspects for TCG Card Tracker.

    Attributes:
        None
    """

    def graph_card_worth(self, price_data, card_details):
        """
        This function graphs a cards worth over time

        Parameters:
            price_data: Tuple of tuples.
                Index 0 - Price date
                Index 1 - Price data

            card_details: Tuple of tuples.
                Index 0 - Card name
                Index 1 - Set name
                Index 2 - Foil flag
        
        Returns:
            None
        """

        # Local constants

        # Local variables
        price_data = list(map(list, zip(*price_data)))
        x_axis_data = price_data[0]
        y_axis_data = price_data[1]
        card_name = card_details[0][0]
        set_name = card_details[0][1]
        foil = card_details[0][2]

        #****** start graph_card_worth() ******#

        # Plot the actual data
        plt.plot(x_axis_data, y_axis_data, 'o')

        # Calculate the trendline
        z = np.polyfit(mdates.date2num(x_axis_data), y_axis_data, 1)
        p = np.poly1d(z)

        # Plot the trendline
        plt.plot(x_axis_data,p(mdates.date2num(x_axis_data)), "r--")

        # Get the title pretty
        if foil == 1: foil = "Foil"
        else: foil = ""
        title = card_name + " (" + set_name + ") " + foil
        plt.title(title)

        # Change the labels pretty
        plt.xlabel("Date")
        plt.xticks(rotation=-45)
        plt.ylabel("Price ($)")
        
        # Done
        plt.show()


