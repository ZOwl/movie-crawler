# Scrapy settings for moviecrawler project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from os import path

PROJECT_ROOT = path.dirname(path.abspath(__file__))

BOT_NAME = 'moviecrawler'

SPIDER_MODULES = ['moviecrawler.spiders']
NEWSPIDER_MODULE = 'moviecrawler.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'moviecrawler (+http://www.yourdomain.com)'
USER_AGENT = 'Mozilla/5.0 (compatible; iaskspider/1.0; MSIE 9.0)'

DOWNLOADER_MIDDLEWARES = {
    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': 400,
    'scrapy.contrib.downloadermiddleware.cookies.CookiesMiddleware': 700,
}

#DOWNLOAD_DELAY = 0.1
#RANDOMIZE_DOWNLOAD_DELAY = True

# COOKIES_ENABLED = True
# COOKIES_DEBUG = True
ITEM_PIPELINES = {
    'moviecrawler.pipelines.CSVPipeline': 2,
    'moviecrawler.pipelines.PPPipeline': 1
    }

LOG_LEVEL = 'INFO'

# Include localsettings.py
local_settings_path = path.join(PROJECT_ROOT, 'localsettings.py')
if path.exists(local_settings_path):
    # use execfile to allow modifications within this context
    execfile(local_settings_path)
else:
    import sys
    sys.stderr.write("Can't find local settings, using default settings.\n")
