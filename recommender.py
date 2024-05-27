import requests
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix

API_KEY_TMDB = 'your_tmdb_api_key'
API_KEY_OMDB = 'd743b342'

def fetch_tmdb_data():
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={API_KEY_TMDB}&language=en-US&sort_by=popularity.desc'
    response = requests.get(url)
    data = response.json()
    return data['results']

def load_data():
    tmdb_data = fetch_tmdb_data()
    df = pd.DataFrame(tmdb_data)
    df['title'] = df['title'].str.lower()
    return df

def compute_similarity(df):
    df['rating'] = df['vote_average']
    df = df[['title', 'rating']].dropna()
    df['rating'] = df['rating'].astype(float)
    movie_matrix = df.pivot_table(index='title', values='rating', aggfunc='mean').fillna(0)
    movie_matrix_sparse = csr_matrix(movie_matrix)
    movie_similarity = cosine_similarity(movie_matrix_sparse)
    movie_indices = pd.Series(movie_matrix.index)
    movie_indices.name = 'title'
    return movie_similarity, movie_indices

def get_recommendations_by_title(title, movie_similarity, movie_indices, num_recommendations=10):
    try:
        idx = movie_indices[movie_indices == title].index[0]
    except IndexError:
        return []
    sim_scores = list(enumerate(movie_similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    movie_indices_ = [i[0] for i in sim_scores[1:num_recommendations+1]]
    recommended_titles = movie_indices.iloc[movie_indices_].tolist()
    return recommended_titles
