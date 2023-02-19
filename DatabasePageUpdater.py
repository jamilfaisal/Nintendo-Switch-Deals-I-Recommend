import json
import requests
import os

from Logger import Logger


class DatabasePageUpdater:

    def __init__(self, logger: Logger):
        self.logger = logger
        filename = os.path.join('secrets.json')
        try:
            with open(filename, mode='r') as f:
                self.secrets = json.loads(f.read())
        except FileNotFoundError:
            self.secrets = {}

        self.url = "https://api.notion.com/v1/pages/{}"
        self.headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization": self.secrets["AUTH"]
        }

    def update_property(self, page_id, payload):
        response = requests.patch(self.url.format(page_id), json=payload, headers=self.headers)
        if response.status_code != 200:
            self.logger.write_to_logfile("Failed to update sale status with status code: {}, Text :{}".format(response.status_code, response.text))
            return False
        return True

    def update_sale_status(self, page_id, status):
        payload = {"properties": {
            "Sale Status": {
                "status": {
                    "name": status
                }
            }}}
        return self.update_property(page_id, payload)

    def update_price(self, page_id, price):
        payload = {"properties": {"Price": {
            "number": price
        }}}
        return self.update_property(page_id, payload)

    def update_sale_ends(self, page_id, sale_ends):
        payload = {"properties": {"Sale Ends": {
            "date": {
                "start": sale_ends  # Must be YYYY-MM-DD
            }
        }}}
        return self.update_property(page_id, payload)

    def clear_sale_ends(self, page_id):
        payload = {"properties": {"Sale Ends": {
            "date": None  # Must be YYYY-MM-DD
        }}}
        return self.update_property(page_id, payload)

    def update_ATL_price(self, page_id, price):
        payload = {"properties": {"ATL Price": {
            "number": price
        }}}
        return self.update_property(page_id, payload)
