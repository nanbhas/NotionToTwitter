# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import json
import random
import string
import time

# %%
import os
import sys
sys.path.append('../')

# %%
from TwitterAPI import TwitterAPI

# %%
from notion_client import Client

# %%
from globalStore import constants

# %%
with open(constants.TWITTER_SECRET_FILE, "r") as f:
    secrets = json.load(f)

# %%
with open("../secrets/secrets_notion.json", "r") as f:
    secrets_notion = json.load(f)

# %%
notion = Client(auth = secrets_notion['notionToken'])

# %%
notionDB_id = secrets_notion['databaseID']

# %%
import arrow

# %%
arrow.now().to('US/Pacific').date()

# %%
arrow.get(allNotionRows[0]['properties']['Post Date']['date']['start']).date()

# %%
start = time.time()
hasMore = True
allNotionRows = []
i = 0

# %%
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

# %%
end = time.time()
print('Number of rows in notion currently: ' + str(len(allNotionRows)))
print('Total time taken: ' + str(end-start))

# %%
filt = [item for item in allNotionRows if len(item['properties']['Children Tweets']['relation']) > 0 ]

# %%
parentID = '9270c738-fda8-4f88-be51-676ac3bfd646'

# %% jupyter={"outputs_hidden": true} tags=[]
[item for item in allNotionRows if item['properties']['Parent Tweet']['relation'][0]['id'] == parentID]

# %% tags=[]
allNotionRows[4]['properties']['Parent Tweet ID']['rollup']['array'][0]['text']

# %%
allNotionRows[4]['properties']['Thread Length']['number']

# %%
len(allNotionRows[2]['properties']['Children Tweets']['relation'])

# %%
idx = 4
allNotionRows[idx]['properties']['Parent Tweet']['relation'][0]['id'] == allNotionRows[idx]['id']

# %%
idx = 4
#allNotionRows[idx]['properties']['Image File Name']['rich_text'][0]['text']['content']
allNotionRows[idx]['properties']['Image File Name']['rich_text']

# %%
len(allNotionRows[2]['properties']['Children Tweets']['relation'])

# %%
filtt = [item for item in allNotionRows if arrow.get(item['last_edited_time']).to('US/Pacific').date() == arrow.now().to('US/Pacific').date()]

# %%
len(filtt)

# %%
allDBprops = list(allNotionRows[-1]['properties'].keys()) + ['Post Date']
len(allDBprops)

# %%
allDBprops

# %%
starterSet = {item['id'] for item in allNotionRows 
                                  if 'Thread Length' in item['properties'].keys() }

# %%
'Thread Length' in allNotionRows[-1]['properties'].keys()

# %%
starterSet

# %%
for idNo in starterSet:
    

# %%

# %%

# %%

# %%
for row in allNotionRows:
    assert ~row['properties']['Tweeted?']['checkbox'], 'Already Tweeted'
    tweetStatus = row['properties']['Tweet']['title'][0]['text']['content']
    if len(row['properties']['Reply To']['relation']) == 0:
        try:
            print('Thread start')
            w = api.request('statuses/update', {'status': tweetStatus})
            print('SUCCESS' if w.status_code == 200 else 'PROBLEM: ' + w.text)
            tweetID = str(w.json()['id'])
            pageID = row['id']  
            updates = {}
            updates['ID'] = {"rich_text": [{"text": { "content": tweetID}}]}
            updates['Tweeted?'] = {"checkbox": True}
            notion.pages.update( pageID, properties = updates)
        except:
            print(w.text)
    else:
        pageID = row['id']
        row = notion.pages.retrieve(page_id = pageID)
        replyTo = row['properties']['Original Tweet ID']['rollup']['array']
        print(replyTo)


# %% jupyter={"outputs_hidden": true} tags=[]
notion.pages.retrieve(page_id= pageID)

# %%
query = notion.databases.query(
                            **{
                                "database_id": notionDB_id,
                                "filter": {"property": "Tweeted?", "checkbox": {"equals": False}},
                            }
                        )


# %%
len(query['results'])

# %%
imrow = query['results'][1]

# %%
imrow['properties']['Image Path Prefix']['rich_text'][0]['text']['content']

# %%
import os

# %%
imrow['properties']

# %%
imfile = os.path.join(imrow['properties']['Image Path Prefix']['rich_text'][0]['text']['content'], 
                          imrow['properties']['Image File Name']['rich_text'][0]['text']['content'])

# %%
imcont = imrow['properties']['Tweet']['title'][0]['text']['content']

# %%
imfile

# %%
# STEP 1 - upload image
file = open(imfile, 'rb')
data = file.read()
rr = api.request('media/upload', None, {'media': data})
print('UPLOAD MEDIA SUCCESS' if rr.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + rr.text)

# %%
# STEP 2 - post tweet with a reference to uploaded image
if rr.status_code == 200:
    media_id = rr.json()['media_id']
    rr = api.request('statuses/update', {'status': imcont, 'media_ids': media_id})
    print('UPDATE STATUS SUCCESS' if rr.status_code == 200 else 'UPDATE STATUS FAILURE: ' + rr.text)

# %%

# %%

# %%

# %%
row0['properties'].keys()

# %%
row0['properties']['Tweeted?']['checkbox']

# %%
row0['properties']['ID']

# %%
row0['properties']['Reply To']['relation']

# %%
row1['properties']['Reply To']['relation']

# %%
row0['properties']['Original Tweet ID']['rollup']['array']

# %%
row1['properties']['Original Tweet ID']['rollup']['array'][0]['text']

# %%
pageID = row0['id']

# %%

# %%
api = TwitterAPI(consumer_key = secrets['APIConsumerKey'], 
                    consumer_secret = secrets['APIConsumerSecret'],
                    access_token_key = secrets['AccessToken'],
                    access_token_secret = secrets['AccessTokenSecret']
                )

# %%
api2 = TwitterAPI(consumer_key = secrets['APIConsumerKey'], 
                    consumer_secret = secrets['APIConsumerSecret'],
                    access_token_key = secrets['AccessToken'],
                    access_token_secret = secrets['AccessTokenSecret'],
                    api_version= '2'
                )

# %%
r = api.request('statuses/update', {'status':'Hello World'})
print('SUCCESS' if r.status_code == 200 else 'PROBLEM: ' + r.text)

# %%
r.json()

# %%
originalID = r.json()['id']

# %%

# %%
rk = api.request('statuses/update', {'status':'I will reply to this text', 'in_reply_to_status_id': originalID})
print('SUCCESS' if rk.status_code == 200 else 'PROBLEM: ' + rk.text)

# %%
ri = api.request('statuses/retweet/:%d' % originalID)
print('SUCCESS' if ri.status_code == 200 else 'PROBLEM: ' + ri.text)

# %%

# %%
rp = api.request('statuses/update', {'status':'This is a quote retweet2222', 'attachment_url': 'https://twitter.com/' + 'na_notion/status/' + str(1416257727907602440) })
print('SUCCESS' if rp.status_code == 200 else 'PROBLEM: ' + rp.text)

# %%

# %%

# %%

# %%
# STEP 1 - upload image
file = open('../data_temp/stanford_logo.png', 'rb')
data = file.read()
rr = api.request('media/upload', None, {'media': data})
print('UPLOAD MEDIA SUCCESS' if rr.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + rr.text)

# %%
media_id = str(rr.json()['media_id']) + ','
media_id

# %%
# STEP 2 - post tweet with a reference to uploaded image
zz = api.request('statuses/update', {'status': "33333333 trial media", 'media_ids': media_id})
print('UPDATE STATUS SUCCESS' if zz.status_code == 200 else 'UPDATE STATUS FAILURE: ' + zz.text)

# %%
# STEP 1 - upload image
file = open('../data_temp/oats.jpg', 'rb')
data = file.read()
rrs = api.request('media/upload', None, {'media': data})
print('UPLOAD MEDIA SUCCESS' if rrs.status_code == 200 else 'UPLOAD MEDIA FAILURE: ' + rrs.text)
if rrs.status_code == 200:
    media_id += str(rrs.json()['media_id']) + ','
media_id

# %%
# STEP 2 - post tweet with a reference to uploaded image
if rr.status_code == 200:
    media_id = rr.json()['media_id']
    rr = api.request('statuses/update', {'status': "trial media", 'in_reply_to_status_id': originalID, 'media_ids': media_id})
    print('UPDATE STATUS SUCCESS' if rr.status_code == 200 else 'UPDATE STATUS FAILURE: ' + rr.text)

# %%
originalID = 1416257727907602440
media_id = '1419115595400769538,1419117987492098052,'
text = 'I am a panda bear'

# %%
media_id

# %%
rr = api.request('statuses/update', {'status': text, 'in_reply_to_status_id': originalID, 'media_ids': media_id})
print('UPDATE STATUS SUCCESS' if rr.status_code == 200 else 'UPDATE STATUS FAILURE: ' + rr.text)

# %%

# %%
r2 = api2.request('statuses/update', {'status':'Hello World'})
print('SUCCESS' if r2.status_code == 200 else 'PROBLEM: ' + r2.text)

# %%
