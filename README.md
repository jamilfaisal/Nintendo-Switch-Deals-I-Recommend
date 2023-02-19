# Nintendo Switch Deals I Recommend (nSDIR)

This tool updates the Sale Status, prices, and the Sale Ending dates for games in the Switch Game Recommendations Notion page by scraping information from [DekuDeals](dekudeals.com).


## Installation

0. Follow the steps in this [Notion Guide](https://developers.notion.com/docs/create-a-notion-integration) for working with databases
1. Clone the repository
2. Rename "secrets_TEMPLATE.json" to "secrets.json"
3. Fill out the values in secrets.json
    - DB_ID: The database ID containing the nintendo switch games
    - AUTH: The Internal Integration token. For more information, click [here](https://developers.notion.com/docs/authorization)
4. Run main.py
5. (Optional) Check console and logs in the "logs" folder for all changes.
