  
"""
Author: Nandita Bhaskhar
Notion to Twitter helper functions
"""

import os
import sys
sys.path.append('../')

import time
import arrow
import json

from tqdm import tqdm   

def getAllUntweetedRowsFromNotionDatabase(notion, notionDB_id):
    '''
    Gets all rows (pages) that are untweeted from a notion database using a notion client
    Args:
        notion: (notion Client) Notion client object
        notionDB_id: (str) string code id for the relevant database
    Returns:
        allNotionRows: (list of notion rows)

    '''
    start = time.time()
    hasMore = True
    allNotionRows = []
    i = 0

    while hasMore:
        if i == 0:
            try:
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "filter": {"property": "Tweeted?", "checkbox": {"equals": False}},
                                }
                            )
            except:
                print('Sleeping to avoid rate limit')
                time.sleep(30)
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "filter": {"property": "Tweeted?", "checkbox": {"equals": False}},
                                }
                            )
                
        else:
            try:
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "start_cursor": nextCursor,
                                    "filter": {"property": "Tweeted?", "checkbox": {"equals": False}},
                                }
                            )
            except:
                print('Sleeping to avoid rate limit')
                time.sleep(30)
                query = notion.databases.query(
                                **{
                                    "database_id": notionDB_id,
                                    "start_cursor": nextCursor,
                                    "filter": {"property": "Tweeted?", "checkbox": {"equals": False}},
                                }
                            )
            
        allNotionRows = allNotionRows + query['results']
        nextCursor = query['next_cursor']
        hasMore = query['has_more']
        i+=1

    end = time.time()
    print('Number of rows in notion currently: ' + str(len(allNotionRows)))
    print('Total time taken: ' + str(end-start))

    return allNotionRows


