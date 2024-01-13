import requests
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import datetime
from waybackpy import WaybackMachineCDXServerAPI

# Function to load tracker database from CSV file
def load_tracker_database(csv_file):
    tracker_database = {}
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            company, domain, _ = row
            if company in tracker_database:
                tracker_database[company].add(domain)
            else:
                tracker_database[company] = {domain}
    return tracker_database



# Function to determine if a URL is external
def is_external(url, base_url):
    return urlparse(url).netloc and urlparse(url).netloc != urlparse(base_url).netloc

# Function to fetch and parse the website
def fetch_site_content(url):
    try:
        response = requests.get(url)
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Function to search for trackers in the HTML content using the tracker database
def search_for_trackers(html, base_url, website_url, tracker_database):
    soup = BeautifulSoup(html, 'html.parser')
    trackers_found = []
    external_urls = []

    for tag in soup.find_all(['script', 'img', 'iframe'], src=True):
        url = tag.get('src')
        if is_external(url, base_url):
            external_urls.append(url)
            continue
        for company, domains in tracker_database.items():
            if any(domain in url for domain in domains):
                trackers_found.append({
                    'website': website_url,
                    'timestamp': base_url.split('/')[4][:14],  # Extract timestamp from archive URL
                    'company': company,
                    'domain': url
                })
                break

    return trackers_found, external_urls

# Function to write results to CSV
def write_to_csv(trackers, csv_filename):
    with open(csv_filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for tracker in trackers:
            writer.writerow([tracker['website'], tracker['timestamp'], tracker['company'], tracker['domain']])

# Function to fetch archives from Wayback Machine
def fetch_archives(url, start_date, end_date, interval):
    archives = []
    user_agent = "Chrome/89.0.4389.82"  # Replace with your user agent
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
def process_archived_website(url, start_date, end_date, interval, tracker_database, csv_filename):
    archives = fetch_archives(url, start_date, end_date, interval)
    for archive_url in archives:
        print(f"Processing archive: {archive_url}")
        html = fetch_site_content(archive_url)
        if html:
            trackers_found, external_urls = search_for_trackers(html, archive_url, url, tracker_database)
            write_to_csv(trackers_found, csv_filename)

# Define the CSV file name
csv_filename = 'tracker_analysis_results.csv'

# Initialize the CSV file with headers
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Website', 'Timestamp', 'Company', 'Domain'])

#Load tracker database from CSV
tracker_database = load_tracker_database('./tracker_domains.csv')

#Input timeframe and interval
start_date = datetime.datetime(2012, 1, 1)
end_date = datetime.datetime(2023, 1, 1)
interval = datetime.timedelta(days=365)

websites = [ 
    
    "studygroup.com",
    "iletaitunehistoire.com",
    "focusbiomolecules.com",
    "stjo.org",
    "matematiktutkusu.com",
    "insumisos.com",
    "admissionmba.in",
    "conferencealerts.org",
    "decrecimiento.info",
    "hajjajj.com",
    "cfbisd.edu",
    "rfh-koeln.de",
    "jaqm.ro",
    "phytools.org",
    "lasaweb.org",
    "bremertonschools.org",
    "mansd.org",
    "ant-neuro.com",
    "medcalc.org",
    "alvaradoisd.net",
    "objectivismschoolhomepage0schoolhomepage.com",
    "typing.academy",
    "acml-conf.org",
    "doublexscience.org",
    "almhultsbostader.se",
    "blackgoldmovie.com",
    "helleniccomserve.com",
    "norwichcsd.org",
    "boligbloggen.nu",
    "anateklabs.com",
    "mexicanhistory.org",
    "lindeloev.net",
    "slussenspensionat.se",
    "nickchk.com",
    "davidkane.info",
    "col-int.com",
    "biologyboom.com",
    "ircam.ma",
    "sycamorelifesciences.com",
    "reospartners.com",
    "nodictionaries.com",
    "quantumconsciousness.org",
    "schoolarabia.net",
    "jgieseking.org",
    "optimaxsi.com",
    "optimist.org",
    "monroeuniversityhomepageboces.org",
    "sase.org",
    "ucl-ioe-press.com",
    "cn-seminar.com",
    "eksmaoptics.com",
    "e-polis.cz",
    "sysy.com",
    "sonics.com",
    "punkrockor.com",
    "delphoscityschools.org",
    "cigarsense.com"
]


for website in websites:
    process_archived_website(website, start_date, end_date, interval, tracker_database, csv_filename)
