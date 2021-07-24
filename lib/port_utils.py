  
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


def filterRowsToBePostedBasedOnDate(allRows, datetime):
    '''
    Filters rows (notion pages) from a list of rows whose 'Post Date' matches the given datetime
    Args:
        allRows: (list of notion rows)  each row should contain a date property named Post Date  
        datetime: (arrow/str/datetime) representation of datetime
    Returns:
        filteredRows: (list of notion rows)    
    '''
    arrowTime = arrow.get(datetime).to('US/Pacific')
    filteredRows = [item for item in allRows if arrow.get(item['properties']['Post Date']['date']['start']).date() == arrowTime.date()]
    
    return filteredRows


def getStarterRows(allRows):
    '''
    Filters rows (notion pages) from a list of rows whose 'Children Tweets' column is not empty
    Args:
        allRows: (list of notion rows)  each row should contain a relation property named Children Tweets  
    Returns:
        starterRows: (list of notion rows)    
    '''
    starterRows = [item for item in allRows if len(item['properties']['Children Tweets']['relation']) > 0 ]
    
    return starterRows


def sortRowsByOrder(subsetRows):
    '''
    Sort rows (notion pages) from a list of rows based on their 'Order' property
    Args:
        subsetRows: (list of notion rows)  each row should contain a property named Order
    Returns:
        sortedRows: (list of notion rows) sorted by their order property   
    '''
    sortedRows = sorted(subsetRows, key = lambda i: i['properties']['Order']['number'])
    
    return sortedRows


def getChildrenRows(row, allRows):
    '''
    Get children rows (notion pages) of the given row from a list of rows based on their relational property 'Parent Tweet'
    Args:
        row: (notion row) row should contain a key named id
        allRows: (list of notion rows) should contain property named Parent Tweet
    Returns:
        childrenRows: (list of notion rows) rows from allRows whose parent is row
    '''    
    parentId = row['id']
    childrenRows = [item for item in allRows if item['properties']['Parent Tweet']['relation'][0]['id'] == parentId]

    return childrenRows


def postRowToTwitter(row, api, notion):
    '''
    Post notion row to twitter + prints staus
    Args:
        row: (notion row) 
        api: (TwitterAPI) instance of twitter api 
        notion: (notion Client) Notion client object
    '''    
    # verify if the row is not already tweeted
    if ~row['properties']['Tweeted?']['checkbox']:
        
        rowID = row['id']
        parentID = row['properties']['Parent Tweet']['relation'][0]['id']
        imPrefix = row['properties']['Image Path Prefix']['rich_text'][0]['text']['content']
        try: 
            imName = row['properties']['Image File Name']['rich_text'][0]['text']['content']
        except:
            imName = None
        imfile = None if imName is None else os.path.join(imPrefix, imName)
        tweetStatus = row['properties']['Tweet']['title'][0]['text']['content']
        
        # parent
        if rowID == parentID:

            # if no image: direct post
            if imfile is None:
                print('Parent: start direct post')
                # STEP 1 - post tweet 
                w = api.request('statuses/update', {'status': tweetStatus})
                print('SUCCESS' if w.status_code == 200 else 'PROBLEM: ' + w.text)
                # STEP 2 - update Notion
                tweetID = str(w.json()['id'])
                updates = {}
                updates['Tweet ID'] = {"rich_text": [{"text": { "content": tweetID}}]}
                updates['Tweeted?'] = {"checkbox": True}
                notion.pages.update(rowID, properties = updates)
                print('updated Notion')

            # else image + post
            else:
                print('Parent: start image upload + direct post')
                # STEP 1 - upload image
                file = open(imfile, 'rb')
                data = file.read()
                w = api.request('media/upload', None, {'media': data})
                print('UPLOAD MEDIA SUCCESS' if w.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + w.text)
                # STEP 2 - post tweet with a reference to uploaded image
                if w.status_code == 200:
                    mediaID = w.json()['media_id']
                    ww = api.request('statuses/update', {'status': tweetStatus, 'media_ids': mediaID})
                    print('UPDATE STATUS SUCCESS' if ww.status_code == 200 else 'UPDATE STATUS FAILURE: ' + ww.text)
                # STEP 3 - update Notion
                tweetID = str(ww.json()['id'])
                updates = {}
                updates['Tweet ID'] = {"rich_text": [{"text": { "content": tweetID}}]}
                updates['Tweeted?'] = {"checkbox": True}
                notion.pages.update(rowID, properties = updates)
                print('updated Notion')

        # child
        else:
            # get original post Tweet ID
            parentTweetID = int(row['properties']['Parent Tweet ID']['rollup']['array'][0]['text'])

            # if no image: direct reply
            if imfile is None:
                print('Child: start direct reply')
                # STEP 1 - post tweet 
                w = api.request('statuses/update', {'status': tweetStatus, 'in_reply_to_status_id': parentTweetID})
                print('SUCCESS' if w.status_code == 200 else 'PROBLEM: ' + w.text)
                # STEP 2 - update Notion
                tweetID = str(w.json()['id'])
                updates = {}
                updates['Tweet ID'] = {"rich_text": [{"text": { "content": tweetID}}]}
                updates['Tweeted?'] = {"checkbox": True}
                notion.pages.update(rowID, properties = updates)
                print('updated Notion')

            # else image + reply
            else:
                print('Child: start image upload + direct reply')
                # STEP 1 - upload image
                file = open(imfile, 'rb')
                data = file.read()
                w = api.request('media/upload', None, {'media': data})
                print('UPLOAD MEDIA SUCCESS' if w.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + w.text)
                # STEP 2 - post tweet reply with a reference to uploaded image
                if w.status_code == 200:
                    mediaID = w.json()['media_id']
                    ww = api.request('statuses/update', {'status': tweetStatus, 'in_reply_to_status_id': parentTweetID, 'media_ids': mediaID})
                    print('UPDATE STATUS SUCCESS' if ww.status_code == 200 else 'UPDATE STATUS FAILURE: ' + ww.text)
                # STEP 3 - update Notion
                tweetID = str(ww.json()['id'])
                updates = {}
                updates['Tweet ID'] = {"rich_text": [{"text": { "content": tweetID}}]}
                updates['Tweeted?'] = {"checkbox": True}
                notion.pages.update(rowID, properties = updates)
                print('updated Notion')

    else:
        raise AssertionError