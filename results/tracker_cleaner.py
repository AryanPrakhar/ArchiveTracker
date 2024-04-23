import pandas as pd
import re

# Function to extract domains
def extract_domains(url_string):
    if pd.isna(url_string):
        return ""  # Handle NaN values to return an empty string
    # Split the string by semicolon in case there are multiple URLs
    urls = url_string.split('; ')
    # Extract the domain from each URL using regex
    domains = [re.findall(r'https?://([^/]+)', url)[0] for url in urls if re.findall(r'https?://([^/]+)', url)]
    return '; '.join(domains)

# Read the CSV file
df = pd.read_csv('tracker_analysis_results.csv')

# Apply the extract_domains function to both 'External URLs' and 'Trackers' columns
df['External URLs'] = df['External URLs'].apply(extract_domains)
df['Trackers'] = df['Trackers'].apply(extract_domains)

# Write the modified dataframe back to a CSV file with proper CSV formatting
df.to_csv('cleaned_trackers.csv', index=False, escapechar='\\')

print("CSV file has been processed and saved as 'cleaned_trackers.csv'.")
