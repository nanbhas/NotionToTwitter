"""
Author: Nandita Bhaskhar
All global constants
"""
import sys
sys.path.append('../')

import globalStore.privateConstants as privateConstants

### All global constants here

TWITTER_SECRETS = {
    'nanbhas': privateConstants.TWITTER_SECRET_FILE_NAB,
    'medai': privateConstants.TWITTER_SECRET_FILE_MEDAI,
    'test': privateConstants.TWITTER_SECRET_FILE_TEST,
}

NOTION_SECRETS = {
    'nanbhas': privateConstants.NOTION_SECRET_FILE_NAB,
    'medai': privateConstants.NOTION_SECRET_FILE_MEDAI,
    'test': privateConstants.NOTION_SECRET_FILE_TEST,
}