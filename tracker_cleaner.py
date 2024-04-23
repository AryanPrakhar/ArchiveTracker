import pandas as pd
import re

def extract_domains(url_string):
    if pd.isna(url_string):
        return ""  

    urls = url_string.split('; ')
 
    domains = [re.findall(r'https?://([^/]+)', url)[0] for url in urls if re.findall(r'https?://([^/]+)', url)]
    return '; '.join(domains)

df = pd.read_csv('tracker_analysis_results.csv')

df['External URLs'] = df['External URLs'].apply(extract_domains)
df['Trackers'] = df['Trackers'].apply(extract_domains)

df.to_csv('cleaned_trackers.csv', index=False, escapechar='\\')

print("CSV file has been processed and saved as 'cleaned_trackers.csv'.")
