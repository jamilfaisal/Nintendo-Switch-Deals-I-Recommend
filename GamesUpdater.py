from datetime import datetime, timedelta

import requests
from dateutil.parser import parse
from DatabasePageGetter import DatabasePageGetter
from DatabasePageUpdater import DatabasePageUpdater
from Logger import Logger


class GamesUpdater:
    def __init__(self):
        self.logger = Logger()
        self.games = DatabasePageGetter().get_all_rows_on_sale_and_not_on_sale()
        self.logger.write_to_logfile("Retrieved {} games from database".format(len(self.games)))

    def update_games(self):
        for count, game in enumerate(self.games):
            GameUpdater(self.logger, count+1, game).update_game()



class GameUpdater:
    def __init__(self, logger, count, game):
        self.logger = logger
        self.databasePageUpdater = DatabasePageUpdater(self.logger)
        self.count = count
        self.name = game["properties"]["Name"]["title"][0]["text"]["content"]
        self.page_id = game["id"]
        self.deku_link = game["properties"]["Deku Link"]["url"]
        self.old_sale_status = game["properties"]["Sale Status"]["status"]["name"]
        self.old_price = game["properties"]["Price"]["number"]
        self.ATL_price = game["properties"]["ATL Price"]["number"]
        self.MSRP_price = game["properties"]["MSRP Price"]["number"]
        self.old_sale_ends = game["properties"]["Sale Ends"]["date"]
        if self.old_sale_ends is not None:
            self.old_sale_ends = self.old_sale_ends["start"]
        # Get current information about sale status, price, and sale ends
        self.current_sale_status, self.current_price = self.get_sale_status_and_price_of_game()
        self.current_sale_ends = self.get_sale_ends()


    def update_game(self):
        self.logger.write_to_logfile("{}. Checking \"{}\"".format(self.count, self.name))
        updates = []

        # If sale status has changed, then update Sale Status
        if self.old_sale_status != self.current_sale_status:
            if self.databasePageUpdater.update_sale_status(self.page_id, self.current_sale_status):
                change = "Sale status: {} -> {}".format(self.old_sale_status, self.current_sale_status)
                updates.append(change)
                self.logger.write_to_logfile(change)

        # If Price has changed, then update Price
        if self.current_price != -1 and abs(round(self.old_price, 2) - round(self.current_price, 2)) > 0.1:
            if self.databasePageUpdater.update_price(self.page_id, self.current_price):
                change = "Price: {} -> {}".format(self.old_price, self.current_price)
                updates.append(change)
                self.logger.write_to_logfile(change)

        # If "ATL Price" > "Price", then change "ATL Price" to "Price"
        if self.current_price < self.ATL_price:
            if self.databasePageUpdater.update_ATL_price(self.page_id, self.current_price):
                change = "ATL price: {} -> {}".format(self.ATL_price, self.current_price)
                updates.append(change)
                self.logger.write_to_logfile(change)

        if self.current_sale_ends is not None and self.old_sale_ends != self.current_sale_ends:
            # If information is available and is different, update "Sale Ends"
            if DatabasePageUpdater(self.logger).update_sale_ends(self.page_id, self.current_sale_ends):
                change = "Sale Ends: {} -> {}".format(self.old_sale_ends, self.current_sale_ends)
                updates.append(change)
                self.logger.write_to_logfile(change)
        else:
            # If information is not available and game is not on sale and Sale Ends is not clear, clear "Sale Ends"
            if self.current_sale_status == "Not On Sale" and self.old_sale_ends is not None:
                if self.databasePageUpdater.clear_sale_ends(self.page_id):
                    change = "Cleared Sale Ends"
                    updates.append(change)
                    self.logger.write_to_logfile(change)

        if len(updates) == 0:
            self.logger.write_to_logfile("No updates!")
        self.logger.write_to_logfile("\n")

    def get_sale_status_and_price_of_game(self):
        response = requests.get(self.deku_link).text
        top_purchase_button_class = "btn btn-block btn-primary"
        sale_percentage_text_class = "ml-2 badge badge-light"

        # Find sale status by checking if there is a sale percentage off
        if response.find(sale_percentage_text_class) == -1:
            sale_status = "Not On Sale"
        else:
            sale_status = "On Sale"

        # Find current price
        if response.find(top_purchase_button_class) != -1:
            chunk = response[response.find(top_purchase_button_class) + len(top_purchase_button_class) + 3:]
            price_str = chunk[chunk.find("$") + 1:chunk.find("\n")]
            try:
                price = float(price_str)
            except ValueError:
                self.logger.write_to_logfile("Could not convert {} to a floating point number", price_str)
                return sale_status, -1  # Error: Failed to get price
        else:
            self.logger.write_to_logfile("Could not find current price")
            return sale_status, -1  # Error: Failed to get price
        return sale_status, price

    def get_sale_ends(self):
        response = requests.get(self.deku_link).text
        # Narrow down webpage to just the price table
        chunk1 = response[response.find("h4>Current prices"):response.find("h3>Price history")]
        # Check if Sale ends text exists in the table
        if chunk1.find("Sale ends") == -1:
            return None
        # Narrow down to get the date
        sale_ends_class = "text-dark small pb-1"
        if response.find(sale_ends_class) == -1:
            return None
        else:
            chunk1 = response[response.find(sale_ends_class) + len(sale_ends_class):]
            chunk2 = chunk1[chunk1.find("Sale ends ") + len("Sale ends "):chunk1.find("\n</a>")]
            # Change into date
            # 1. Month Day (Ex: February 27). Need to add current year
            if chunk2.find("in") == -1:
                date = parse(chunk2 + ", " + str(datetime.today().year)).strftime("%Y-%m-%d")
            else:
                # 2. in xx hours (Ex: in 28 hours). Need to add hours from now
                hours = int(chunk2.split(" ")[1])
                date = (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%d")
            return date