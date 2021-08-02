  
"""
Author: Nandita Bhaskhar
Notion to Twitter helper functions
"""

import os
import sys
sys.path.append('../')

import time
import arrow


class NotionTweetRow():
    ''' A class denoting a row in the Notion twitter database '''

    def __init__(self, row, notion):
        '''
        Args:
            row: (notion row)
            notion: (notion Client) Notion client object
        '''

        self.pageID = row['id']
        self.created = arrow.get(row['created_time']).to('US/Pacific')
        self.lastEdited = arrow.get(row['last_edited_time']).to('US/Pacific')
        self.pageURL = row['url']
        
        self.title = row['properties']['Tweet']['title'][0]['text']['content'] if row['properties']['Tweet']['title'] else None

        try:
            self.postDate = arrow.get(row['properties']['Post Date']['date']['start'])
        except KeyError:
            self.postDate = None

        self.tweeted = row['properties']['Tweeted?']['checkbox']

        self.imagePathPrefix = row['properties']['Image Path Prefix']['formula']['string']

        self.rawContent = notion.blocks.children.list(self.pageID)
        self.threadCount = len(self.rawContent['results'])

    def getTweetThread(self):
        '''
        Returns:
            tweetThread: (list of dict)
                                each dict has keys: 'text', 'images'
                                'text': (str)
                                'images': (list of str) list of image names
        '''
        tweetThread = []
        for item in self.rawContent['results']:
            try:
                para = ''.join([e['plain_text'] for e in item['paragraph']['text']])
            except:
                pass
            text = para.split('<img>')[0]
            try:
                tmp = para.split('<img>')[1:]
                images = [os.path.join(self.imagePathPrefix, item) for item in tmp]
            except:
                images = None
            tweet = {'text': text, 'images': images}

            tweetThread.append(tweet)

        return tweetThread


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
    arrowTime = arrow.get(datetime)

    filteredRows = [item for item in allRows if 'Post Date' in item['properties'] and arrow.get(item['properties']['Post Date']['date']['start']).date() == arrowTime.date()]
    
    return filteredRows


def postRowToTwitter(row, api, notion):
    '''
    Post notion row to twitter + prints staus
    Args:
        row: (NotionTweetRow)
        api: (TwitterAPI) instance of twitter api 
        notion: (notion Client) Notion client object
    '''    
    # verify if the row is not already tweeted
    if ~row.tweeted:

        # defaults
        replyToID, mediaID, tweetText = None, None, None
        errorText = ''
        tweeted, firstTweet = True, True

        # get thread from notion
        thread = row.getTweetThread()

        for tweet in thread:
            
            # tweet text
            tweetText = tweet['text']

            # media images
            if tweet['images']:
                # loop through images, upload them, get their media ids
                mediaID =''
                for img in tweet['images']:
                    file = open(img, 'rb')
                    data = file.read()
                    w = api.request('media/upload', None, {'media': data})
                    print('UPLOAD MEDIA SUCCESS' if w.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + w.text)
                    if w.status_code == 200:
                        mediaID = mediaID + str(w.json()['media_id']) + ','
            else:
                mediaID = None

            # post tweet with a reference to uploaded image as a reply to the replyToID
            try:
                r = api.request('statuses/update', {'status': tweetText, 'in_reply_to_status_id': replyToID, 'media_ids': mediaID})
                # update error text
                errorText = errorText + '\n' + 'UPDATE STATUS SUCCESS' if r.status_code == 200 else 'UPDATE STATUS FAILURE: ' + r.text
                # update reply to ID
                replyToID = str(r.json()['id'])
                # thread tweet ID
                if firstTweet:
                    tweetID = replyToID
                    firstTweet = False

            except:
                tweeted = False
                pass
   
        # update Notion
        updates = {}
        updates['Tweeted?'] = {"checkbox": tweeted}
        updates['Error Message'] = {"rich_text": [{"text": { "content": errorText }}]}
        updates['Start Tweet ID'] =  {"rich_text": [{"text": { "content": tweetID }}]}   
        notion.pages.update(row.pageID, properties = updates)
        print('Updated Notion')
        
    else:
        print('Already tweeted')