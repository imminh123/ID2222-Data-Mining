import pandas as pd

# Load the original CSV file
df = pd.read_csv('data/netflix_titles.csv')

# Extract only the 'title' column
titles_df = df[['title']]

# Save the 'title' column to a new CSV file
titles_df.to_csv('movie_titles.csv', index=False)