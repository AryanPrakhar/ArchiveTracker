# Archive Tracker

## Overview
Tool to study historical change in trackers usage by websites

## Dependencies
- `requests`: For making HTTP requests to fetch website content.
- `beautifulsoup4`: For parsing HTML and searching through the content.
- `waybackpy`: For interfacing with the Wayback Machine's CDX Server API.

# Versioning

## Version 1.0.0
**Libraries**: requests, BeautifulSoup, urlparse, datetime, WaybackMachineCDXServerAPI.

**Known Trackers**: A list of domains associated with tracking services.

**Functions**:
is_external: Determines if a URL is external relative to a base URL.
fetch_site_content: Fetches the HTML content of a website.
search_for_trackers: Parses HTML to find known trackers and external URLs.
fetch_archives: Retrieves archives from the Wayback Machine.
process_archived_website: Processes each archived website for trackers.

**Main Script**: Processes a predefined list of websites for a specific timeframe.

## Version 1.1.0
⚡️**New Feature**: Tracker database loaded from a CSV file and analysis results written to a csv

**CSV Functionality**:
load_tracker_database: Loads the tracker database from a CSV file.
write_to_csv: Writes the results of the tracker search to a CSV file.

**Enhanced Tracker Search**: Uses the tracker database for a more detailed and dynamic tracker search.

**User Agent**: Updated user agent string for Wayback Machine requests.


## Version 1.2.0
⚡️**New Feature**: 
-Added dyanamic delays to fix api request rate limit issue
-Improvised error handling
-Upto 2 times faster than v1.1.0.

**HTTP Session Management:**
init_requests_session: Initializes a requests session with retry logic for robustness.
Uses the session in fetch_site_content for improved error handling and efficiency.

**Delay Between Requests**: Introduces delays (time.sleep) to manage request rate and avoid potential blocking.

**Error Handling**: Enhanced error handling in fetch_site_content.

