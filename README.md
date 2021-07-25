<div align="center">    
 
# NotionToTwitter  
 
</div>
 
## Description   
This project allows you to post newly added threads written in your Notion database (along with the image name) directly on to your twitter account via the APIs provided by the two. Update the `Post Date` column in your Notion database to schedule your tweets well. You can run the script `scripts/runNotionToTwitter.sh` peridocially at a reasonable frequency via a `crontab` job. 

## Directory Structure

```
.
+-- globalStore/
|   +-- constants.py
+-- lib/
|   +-- port_utils.py
+-- notebooks/
|   +-- trial.py
|   +-- test port_utils.py
+-- scripts/
|   +-- runNotionToTwitter.sh
+-- src/
|   +-- notionToTwitter.py
+-- .gitignore
+-- juyptext.toml
+-- LICENSE
+-- README.md
+-- requirements.txt
+-- STDOUTlog_examples.txt
```

Additional directory to store images. Make sure to sync it to a cloud service of your choice ( I use Google Drive). You should also add this path to the Notion DB in the `Image Path Prefix` column
```
GoogleDrive/images/
```

## Usage
1. Register an app on Twitters's developer portal (follow instructions online)
2. Obtain its `APIConsumerKey`, `APIConsumerSecret`, `Bearer Token`, `AccessToken` and `AccessTokenSecret` and add it to `secrets/secrets_twitter.json` in the following format:
```
{
    "APIConsumerKey": "your key here",
    "APIConsumerSecret": "your secret here",
    "BearerToken": "your token here",
    "AccessToken": "your token here",
    "AccessTokenSecret": "your access token here"
}
```
3. Register a private integration on your Notion workspace (follow instructions online)
4. Obtain its `notionToken`
5. Create a database on Notion to contain all the entries you need to post on Twitter. Make sure it has the following properties. If you want to add more properties or remove, modify the functions and class in `lib/port_utils.py`.
```
Title property: Tweet
Formula properties: Image Path Prefix
Bool properties: Tweeted?
Date properties: Post Date
```
**Note**: The formula for the `Image Path Prefix` property should be `format("path-to-your-local-images-folder")`
6. Get its `databaseID` and add it to `secrets/secrets_notion.json` in the following format:
```
{
    "notionToken": "your notion token",
    "databaseID": "your notion database ID"
}
```
7. Run the python script `src/notionToTwitter.py` (no command line args)
8. You can periodically run this file again as a script `scripts/runMendToNotion.sh` using a crontab job to get periodic updates (I recommend every day)

## Sources

- [Twitter API Python SDK](https://github.com/geduldig/TwitterAPI)
- [Notion API Python SDK](https://github.com/ramnes/notion-sdk-py)

## If you use it in your work and want to adapt this code, please consider starring this repo or forking from it! 
 

