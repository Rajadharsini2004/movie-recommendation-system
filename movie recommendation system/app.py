from flask import Flask, render_template, request, jsonify
import pandas as pd
import re
import requests

app = Flask(__name__)

OMDB_API_KEY = "6fb96158"  # Replace with your OMDb key

# ===== Load dataset =====
df = pd.read_csv('data/final_data.csv')  # Must have 'title' and 'type' columns

# ===== FlixHub class =====
class FlixHub:
    def __init__(self, df):
        self.df = df

    def recommendation(self, title, total_result=5):
        idx = self.find_id(title)
        if idx == -1:
            return [], []

        base_title = self.df.at[idx, 'title'].lower()
        self.df['similarity'] = self.df['title'].apply(
            lambda x: self.sim_score(base_title, x.lower())
        )

        sort_df = self.df.sort_values(by='similarity', ascending=False)[1:total_result+1]

        movies = sort_df[sort_df['type'] == 'Movie']['title']
        tv_shows = sort_df[sort_df['type'] == 'TV Show']['title']

        return list(movies), list(tv_shows)

    def find_id(self, name):
        for index, string in enumerate(self.df['title']):
            if re.search(name, string, re.IGNORECASE):
                return index
        return -1

    def sim_score(self, base, compare):
        base_words = set(base.split())
        compare_words = set(compare.split())
        return len(base_words & compare_words)

# ===== Poster cache =====
poster_cache = {}

# ===== Fetch poster from OMDb with caching =====
def fetch_movie_poster(title):
    if title in poster_cache:
        return poster_cache[title]

    clean_title = re.sub(r"\(.*?\)", "", title).strip()
    try:
        url = f"http://www.omdbapi.com/?t={clean_title}&apikey={OMDB_API_KEY}"
        response = requests.get(url, timeout=5).json()
        poster_url = response.get("Poster") if response.get("Poster") != "N/A" else None
        if poster_url and poster_url.startswith("http://"):
            poster_url = poster_url.replace("http://", "https://")  # force HTTPS
    except:
        poster_url = None

    if not poster_url:
        poster_url = "https://via.placeholder.com/150?text=No+Image"

    poster_cache[title] = poster_url
    return poster_url


flix_hub = FlixHub(df)

# ===== Routes =====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json
    title = data.get('title', '')
    movies, tv_shows = flix_hub.recommendation(title, total_result=10)

    movie_data = [{"title": m, "poster": fetch_movie_poster(m)} for m in movies]
    tv_data = [{"title": t, "poster": fetch_movie_poster(t)} for t in tv_shows]

    return jsonify({'movies': movie_data, 'tv_shows': tv_data})
  # check what URLs are being returned


if __name__ == "__main__":
    app.run(debug=True)




