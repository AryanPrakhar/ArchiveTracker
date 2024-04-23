import pandas as pd

df = pd.read_csv('Educational Labeled Data.csv')
website_list = ['"{}"'.format(w) for w in df['Website']]
comma_separated_websites = ', '.join(website_list)
print(comma_separated_websites)
