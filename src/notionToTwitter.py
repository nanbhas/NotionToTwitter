  
"""
Author: Nandita Bhaskhar
End-to-end script for posting twitter threads from a Notion Database of your choice to your Twitter account
"""

import sys
sys.path.append('../')

import time
import arrow
import json

from TwitterAPI import TwitterAPI
from notion_client import Client

from lib.port_utils import getAllUntweetedRowsFromNotionDatabase, filterRowsToBePostedBasedOnDate, postRowToTwitter
from lib.port_utils import NotionTweetRow

from globalStore import constants

# main script
if __name__ == "__main__":

    print('\n\n==========================================================')
    start = arrow.get(time.time()).to('US/Pacific').format('YYYY-MM-DD HH:mm:ss ZZ')
    print('Starting at ' + str(start) + '\n\n')

    # open secrets 
    with open(constants.TWITTER_SECRET_FILE, "r") as f:
        secrets = json.load(f)
    with open(constants.NOTION_SECRET_FILE, "r") as f:
        secrets_notion = json.load(f)

    # initialize notion client and determine notion DB
    notion = Client(auth = secrets_notion['notionToken'])
    notionDB_id = secrets_notion['databaseID']

    # start a twitter api session
    api = TwitterAPI(consumer_key = secrets['APIConsumerKey'], 
                    consumer_secret = secrets['APIConsumerSecret'],
                    access_token_key = secrets['AccessToken'],
                    access_token_secret = secrets['AccessTokenSecret']
                )

    # get all untweeted notion rows
    allNotionRows = getAllUntweetedRowsFromNotionDatabase(notion, notionDB_id)

    # get today's date
    datetime = arrow.now().to('US/Pacific').date()
    print(datetime)

    # filter based on datetime
    todayNotionRows = filterRowsToBePostedBasedOnDate(allNotionRows, datetime)
    print(str(len(todayNotionRows)) + ' filtered rows for today')

    # loop over row in filtered rows collection
    for row in todayNotionRows: 
        row = NotionTweetRow(row, notion)
        # post the row to twitter
        postRowToTwitter(row, api, notion)

