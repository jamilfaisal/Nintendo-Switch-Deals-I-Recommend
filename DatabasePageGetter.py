import json
import requests
import os


class DatabasePageGetter:

    def __init__(self):
        filename = os.path.join('secrets.json')
        try:
            with open(filename, mode='r') as f:
                self.secrets = json.loads(f.read())
        except FileNotFoundError:
            self.secrets = {}

        self.url = "https://api.notion.com/v1/databases/{}/query".format(self.secrets["DB_ID"])
        self.database_filter = {
            "or": [
                {
                    "property": "Sale Status",
                    "status": {
                        "equals": "Not On Sale"
                    }
                },
                {
                    "property": "Sale Status",
                    "status": {
                        "equals": "On Sale"
                    }
                }
            ]
        }
        self.sorts = [
            {
                "property": "Name",
                "direction": "ascending"
            }
        ]
        self.headers = {
            "accept": "application/json",
            "Notion-Version": "2022-06-28",
            "content-type": "application/json",
            "Authorization": self.secrets["AUTH"]
        }
        self.payload = {
            "filter": self.database_filter,
            "sorts": self.sorts
        }

    def get_all_rows_on_sale_and_not_on_sale(self):
        response = requests.post(self.url, json=self.payload, headers=self.headers)
        if response.status_code != 200:
            raise Exception("First POST call to get database rows failed with status code: {}, Text :{}",
                            response.status_code, response.text)
        response_formatted = json.loads(response.text)
        result = response_formatted["results"]
        # Notion Pagination limits results returned to 100 rows. Need to make further calls to get all rows of the database
        while response_formatted["has_more"]:
            headers = self.headers["start_cursor"] = response_formatted["next_cursor"]
            response = requests.post(self.url, json=self.payload, headers=headers)
            if response.status_code != 200:
                raise Exception("Consequent POST call to get database rows failed with status code: {}, Text :{}",
                                response.status_code, response.text)
            response_formatted = json.loads(response.text)
            result.extends(response_formatted["results"])
        return result
