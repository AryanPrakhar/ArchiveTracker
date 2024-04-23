import requests
import csv
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
from waybackpy import WaybackMachineCDXServerAPI
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0'

delay=10
def init_requests_session():
    print('Initializing requests session...')
    session = requests.Session()
    retries = Retry(total=5, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))
    session.mount('https://', HTTPAdapter(max_retries=retries))
    print('Session initialized with retries configured.')
    return session

def load_tracker_database(csv_file):
    tracker_database = set()
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            _, domain, _ = row
            tracker_database.add(domain)
    return tracker_database

def get_domain(url):
    domain = urlparse(url).netloc
    return domain

def is_external(url, base_domain):
    external = get_domain(url) != base_domain and get_domain(url) != ''
    return external

def fetch_site_content(url, session, max_attempts=3):
    attempts = 0
    while attempts < max_attempts:
        time.sleep(delay)  # Respectful delay between requests
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            return response.text
        except requests.ConnectionError as e:
            attempts += 1
            if attempts == max_attempts:
                return None
        except requests.RequestException as e:
            return None

def clean_up_url(url):
    
    prefix = 'https://web.archive.org/web/'
    if prefix in url:
        cleaned_url = url.split('/http', 1)[-1]
        if cleaned_url.startswith('s://'):
            cleaned_url = 'https://' + cleaned_url[4:]
        elif cleaned_url.startswith('://'):
            cleaned_url = 'http://' + cleaned_url[3:]
        
        return cleaned_url
    
    return url

def archive_check(url):
    is_archive = 'archive.org' in url
    return is_archive

def search_for_trackers(html, base_url, website_url, tracker_database):
    base_domain = get_domain(website_url)
    soup = BeautifulSoup(html, 'html.parser')
    trackers_found = set()
    external_urls = set()

    for tag in soup.find_all(['script', 'img', 'iframe'], src=True):
        raw_url = tag.get('src')
        if raw_url:
            url = clean_up_url(raw_url)
            if url and is_external(url, base_domain) and not archive_check(url) and website_url not in url:
                external_urls.add(url)
                if any(domain in url for domain in tracker_database):
                    trackers_found.add(url)
    return list(trackers_found), list(external_urls)

def write_to_csv(archive_data, csv_filename):
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for data in archive_data:
            writer.writerow(data)

def fetch_archives(url, start_date, end_date, interval):
    print(f'Fetching archives for URL: {url} from {start_date} to {end_date} at intervals of {interval}')
    archives = []
    
    start_timestamp = start_date.strftime('%Y%m%d%H%M%S')
    end_timestamp = end_date.strftime('%Y%m%d%H%M%S')

    cdx = WaybackMachineCDXServerAPI(url, user_agent, start_timestamp=start_timestamp, end_timestamp=end_timestamp)
    
    for snapshot in cdx.snapshots():
        snapshot_date = datetime.datetime.strptime(snapshot.timestamp, '%Y%m%d%H%M%S')
        if start_date <= snapshot_date <= end_date:
            archives.append((snapshot_date, snapshot.archive_url))
            start_date += interval
            time.sleep(delay)  # Adding delay after each snapshot fetch
    return archives

def process_archived_website(url, start_date, end_date, interval, tracker_database, csv_filename, session):
    archives = fetch_archives(url, start_date, end_date, interval)
    archive_data = []

    for date, archive_url in archives:
        print(f'Processing archive: {archive_url} for date: {date}')
        html = fetch_site_content(archive_url, session)
        if html:
            trackers_found, external_urls = search_for_trackers(html, archive_url, url, tracker_database)
            archive_data.append([url, date.strftime('%Y-%m-%d %H:%M:%S'), "; ".join(external_urls), "; ".join(trackers_found)])
    write_to_csv(archive_data, csv_filename)

csv_filename = 'tracker_analysis_results.csv'
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Website', 'Timestamp', 'External URLs', 'Trackers'])

tracker_database = load_tracker_database('./merged_file-Copy.csv')

start_date = datetime.datetime(2022, 1, 1)
end_date = datetime.datetime(2023, 1, 1)
interval = datetime.timedelta(days=365)

# Add the websites here 
websites = []
session = init_requests_session()

for website in websites:
    process_archived_website(website, start_date, end_date, interval, tracker_database, csv_filename, session)
