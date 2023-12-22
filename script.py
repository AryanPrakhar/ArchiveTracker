#importing required libraries
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
from waybackpy import WaybackMachineCDXServerAPI

# Function to determine if a URL is external
def is_external(url, base_url):
    return urlparse(url).netloc and urlparse(url).netloc != urlparse(base_url).netloc

# A list of known tracker patterns/domains to look for
known_trackers = [
    # Google services
    'google-analytics.com', 'googletagmanager.com', 'googleadservices.com',
    'doubleclick.net', 'ad.doubleclick.net', 'googleusercontent.com',
    'googlesyndication.com', 'googleapis.com', 'gstatic.com',

    # Facebook
    'facebook.com', 'facebook.net', 'fbcdn.net', 'connect.facebook.net',

    # Twitter
    'twitter.com', 'twimg.com',

    # Amazon Ads
    'amazon-adsystem.com', 'amazonaws.com',

    # Microsoft
    'bing.com', 'msecnd.net',

    # Verizon Media
    'yahoo.com', 'aol.com', 'yimg.com',

    # Adobe Analytics
    'omniture.com', '2o7.net', 'omtrdc.net',

    # Quantcast
    'quantserve.com', 'quantcast.com',

    # Scorecard Research
    'scorecardresearch.com', 'voicefive.com',

    # AppNexus
    'adnxs.com', 'adxnxs.com',

    # Criteo
    'criteo.com', 'criteo.net',

    # Rubicon Project
    'rubiconproject.com',

    # Taboola
    'taboola.com',

    # Outbrain
    'outbrain.com',

    # Disqus
    'disqus.com', 'disquscdn.com',

    # New Relic
    'newrelic.com',

    # Hotjar
    'hotjar.com', 'hotjar.io',

    # Clicky
    'getclicky.com',

    # LinkedIn
    'licdn.com',

    # TikTok
    'tiktok.com',

    # Pinterest
    'pinimg.com',

    # Snapchat
    'snapchat.com',

    # Yandex
    'yandex.ru', 'yandex.net', 'yandex.com',

    # CDN and Ads Services
    'cdn.contextads.live', 'cdn.adsafeprotected.com', 'cloudfront.net',

    # Other common ad/tracking networks
    'pubmatic.com', 'advertising.com', 'media.net', 'adroll.com',
    'bluekai.com', 'exelator.com', 'tapad.com', 'mathtag.com',
    'serving-sys.com', 'openx.net', 'revcontent.com', 'taboola.com',
    'outbrain.com', 'zergnet.com', 'adform.net', 'teads.tv',
    'bidswitch.net', 'adition.com', 'thetradedesk.com', 'adsrvr.org',
    'contextweb.com', 'smartadserver.com', 'adtechus.com', 'moatads.com',
    'sovrn.com', 'lijit.com', 'sharethrough.com', 'spotxchange.com',
    'spotx.tv', 'tremorhub.com', 'fyber.com', '33across.com', 'adblade.com',
    'advertising.com', 'conversantmedia.com', 'coxmt.com', 'criteo.net',
    'districtm.io', 'freewheel.tv', 'innovid.com', 'rhythmone.com',
    'rubiconproject.com', 'sonobi.com', 'yieldmo.com'
]

# Function to fetch and parse the website
def fetch_site_content(url):
    try:
        response = requests.get(url)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to search for trackers in the HTML content
def search_for_trackers(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    trackers = []
    external_urls = []

    # Check all script, img, and iframe tags
    for tag in soup.find_all(['script', 'img', 'iframe'], src=True):
        url = tag.get('src')
        if any(tracker in url for tracker in known_trackers):
            tracker_info = {
                'type': tag.name.capitalize(),
                'url': url,
                'base_url': base_url  # Include the base URL for context
            }
            trackers.append(tracker_info)
        elif is_external(url, base_url):
            external_urls.append(url)

    return trackers, external_urls

# Function to fetch archives from Wayback Machine
def fetch_archives(url, start_date, end_date, interval):
    archives = []
    user_agent = "Your User Agent"  # Replace with your user agent
    start_timestamp = start_date.strftime('%Y%m%d%H%M%S')
    end_timestamp = end_date.strftime('%Y%m%d%H%M%S')

    cdx = WaybackMachineCDXServerAPI(url, user_agent, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    
    for snapshot in cdx.snapshots():
        snapshot_date = datetime.datetime.strptime(snapshot.timestamp, '%Y%m%d%H%M%S')
        if start_date <= snapshot_date <= end_date:
            archives.append(snapshot.archive_url)
            start_date += interval
    
    return archives

# Function to process archived websites
def process_archived_website(url, start_date, end_date, interval):
    archives = fetch_archives(url, start_date, end_date, interval)
    for archive_url in archives:
        print(f"Processing archive: {archive_url}")
        html = fetch_site_content(archive_url)
        if html:
            trackers, external_urls = search_for_trackers(html, archive_url)
            if trackers:
                print(f"Found {len(trackers)} trackers on {archive_url}:")
                for tracker in trackers:
                    split_url = tracker['url'].split('/')
                    if len(split_url) > 8:
                        tracker_id = '/'.join(split_url[7:8])
                        
                        print(f" - {tracker['type']}: {tracker_id}")
                    else:
                        print(f" - {tracker['type']}: URL too short to split")
            else:
                print(f"No specific known trackers found on {archive_url}. Listing all external URLs:")
                for ext_url in external_urls:
                    print(f" - {ext_url}")


# Input timeframe and interval
start_date = datetime.datetime(2018, 1, 1)  
end_date = datetime.datetime(2020, 1, 1)    
interval = datetime.timedelta(days=270)      

# List of websites to check 
websites = [
     'https://indianexpress.com',
     'https://aajtak.com',
     'https://time.com/',
     'https://www.thehindu.com/'
]

# Running the script for each website
for website in websites:
    process_archived_website(website, start_date, end_date, interval)
