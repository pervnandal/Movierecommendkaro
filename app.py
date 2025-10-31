import streamlit as st
import pickle as pkl
import pandas as pd
import requests
import time
import ast # Import abstract syntax tree for safely evaluating string-lists
import html # Import for escaping HTML strings

# Page Configuration
st.set_page_config(
    page_title="MovieRecommender",
    page_icon="🎬",
    layout="wide"
)

# CSS 
st.markdown("""
<style>
    .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
    }

    /* Style the main title */
    h1 {
        color: #ff4b4b; 
        text-align: center;
        font-family: 'Arial Black', sans-serif;
        font-size: 3rem;
    }

    /* Style selectbox labels */
    .stSelectbox label {
        color: #e0e0e0;
        font-weight: bold;
    }

    .stSelectbox div[role="combobox"] {
        background-color: #333333;
        color: #ffffff;
        border-radius: 8px;
    }

    .stButton>button {
        background-color: #ff4b4b;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        font-weight: bold;
        transition: background-color 0.3s ease;
        /* Center the button */
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 200px; 
    }

    .stButton>button:hover {
        background-color: #e04040;
    }

    /* --- New Card Styles for Hover Effect --- */
    
    /* Remove default column padding and add margin */
    .stColumn {
        padding: 0px 5px !important;
    }

    .movie-card {
        background-color: #2b2b2b;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.2s ease;
        position: relative; /* Needed for the overlay */
        overflow: hidden; /* Hide overflowing overlay */
        height: 100%; /* Make cards in a row equal height */
    }

    .movie-card:hover {
        transform: scale(1.05);
        z-index: 10; /* Bring card to front on hover */
    }

    .movie-poster {
        border-radius: 8px;
        width: 100%;
    }

    .movie-title {
        color: #e0e0e0;
        font-weight: bold;
        font-size: 1.1em;
        text-align: center;
        /* Fixed height to align titles */
        height: 3em; 
        margin-top: 10px;
        /* Handle long titles */
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; /* number of lines to show */
        -webkit-box-orient: vertical;
    }

    .movie-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.9);
        color: #ffffff;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease;
        padding: 15px;
        overflow-y: auto; /* Allow scrolling if content is too long */
        text-align: left;
        font-size: 0.9em;
        border-radius: 12px; /* Match card radius */
    }

    .movie-card:hover .movie-overlay {
        opacity: 1;
        visibility: visible;
    }

    .movie-overlay h4 {
        color: #ff4b4b;
        font-size: 1.1em;
        margin-bottom: 5px;
        /* Handle long titles in overlay */
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .movie-overlay p {
        margin-bottom: 10px;
    }
    
    .movie-overlay p strong {
        color: #e0e0e0;
    }

</style>
""", unsafe_allow_html=True)

# --- Data Helper Functions ---

def safe_literal_eval(val):
    """
    Safely evaluate string representations of lists.
    Handles NaNs and actual lists.
    """
    if isinstance(val, list):
        return val
    if pd.isna(val):
        return []
    
    try:
        return ast.literal_eval(val)
    except (ValueError, SyntaxError):
        return []

# --- Main App Functions ---

@st.cache_data
def load_data():
    """
    Loads movie data, similarity matrix, and extracts unique directors and actors.
    """
    try:
        with open('movies_dict.pkl', 'rb') as f:
            movies_dict = pkl.load(f)
        movies = pd.DataFrame(movies_dict)
        
        with open('similarity.pkl', 'rb') as f:
            similarity = pkl.load(f)
            
    except FileNotFoundError:
        st.error("Error: 'movies_dict.pkl' or 'similarity.pkl' not found.")
        st.stop()
    except Exception as e:
        st.error(f"An error occurred loading data: {e}")
        st.stop()

    # Convert string-lists to actual lists
    for col in ['cast', 'crew']:
        if col in movies.columns:
            movies[col] = movies[col].apply(safe_literal_eval)
        else:
            st.error(f"Error: '{col}' column not found in movies_dict.pkl.")
            movies[col] = pd.Series([[]] * len(movies))
            
    # Ensure 'overview' exists
    if 'overview' not in movies.columns:
        st.error("Error: 'overview' column not found in movies_dict.pkl.")
        movies['overview'] = "" # Add empty overview column as fallback
    else:
        # Fill NaN overviews with an empty string
        movies['overview'] = movies['overview'].fillna("")


    all_directors = set()
    movies['crew'].apply(
        lambda crew_list: all_directors.update(crew_list) if isinstance(crew_list, list) else None
    )
    unique_directors = sorted(list(all_directors))
    
    all_actors = set()
    movies['cast'].apply(
        lambda cast_list: all_actors.update(cast_list) if isinstance(cast_list, list) else None
    )
    unique_actors = sorted(list(all_actors))
    
    return movies, similarity, unique_directors, unique_actors

@st.cache_data
def fetch_poster(movie_id):
    """
    Fetches movie poster URL from TMDB API with retries.
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6d90565f372a61b80c2880887efb194c&language=en-US'
    
    for i in range(3):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() 
            data = response.json()
            poster_path = data.get('poster_path')
            if poster_path:
                return "https://image.tmdb.org/t/p/w500" + poster_path
            else:
                return "https://placehold.co/500x750/2b2b2b/e0e0e0?text=No+Poster"
        except requests.exceptions.RequestException as e:
            print(f"API request failed (attempt {i + 1}): {e}")
            time.sleep(1) 

    return "https://placehold.co/500x750/2b2b2b/e0e0e0?text=No+Image"


def recommend(movie_title):
    """
    Recommends 5 similar movies.
    Returns a list of dictionaries, each containing movie details.
    """
    try:
        movie_index = movies[movies['title'] == movie_title].index[0]
    except IndexError:
        st.error("Could not find movie index. Please refresh.")
        return []
        
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommendations = []
    
    with st.spinner('Fetching recommendations...'):
        for p in movie_list:
            if p[0] < len(movies):
                movie_data = movies.iloc[p[0]]
                movie_id = movie_data.movie_id
                
                recommendations.append({
                    'title': movie_data.title,
                    'poster': fetch_poster(movie_id),
                    'cast': movie_data.cast,
                    'crew': movie_data.crew,
                    'overview': movie_data.overview
                })
            else:
                print(f"Skipping index {p[0]} as it's out of bounds for movies (length {len(movies)}).")
            
    return recommendations

# --- Main App ---

# Load all data
movies, similarity, unique_directors, unique_actors = load_data()

st.title('Movie Recommendation System')

# --- Filter Section ---
director_options = ['All'] + unique_directors if unique_directors else ['All']
actor_options = ['All'] + unique_actors if unique_actors else ['All']

col1, col2 = st.columns(2)
with col1:
    selected_director = st.selectbox('Filter by Director', director_options)
with col2:
    selected_actor = st.selectbox('Filter by Actor', actor_options)

# --- Apply filters ---
filtered_movies = movies.copy()

if selected_director != 'All':
    filtered_movies = filtered_movies[
        filtered_movies['crew'].apply(
            lambda crew_list: isinstance(crew_list, list) and selected_director in crew_list
        )
    ]

if selected_actor != 'All':
    filtered_movies = filtered_movies[
        filtered_movies['cast'].apply(
            lambda cast_list: isinstance(cast_list, list) and selected_actor in cast_list
        )
    ]

st.write("") # Spacer

# --- Movie Selection and Recommendation ---
if filtered_movies.empty:
    st.warning("No movies match your filter criteria. Please broaden your search.")
else:
    movie_titles = filtered_movies['title'].values
    if len(movie_titles) > 0:
        selected_movie = st.selectbox('Select a Movie from the Filtered List', movie_titles)
        st.write("")

        if st.button("Recommend"):
            # recommend() now returns a list of dicts
            recommendations = recommend(selected_movie)

            if recommendations:
                st.write("") 
                st.markdown("<h2 style='text-align: center;'>Here are 5 movies you might also like:</h2>", unsafe_allow_html=True)
                st.write("") 

                cols = st.columns(5)
                for i, col in enumerate(cols):
                    if i < len(recommendations):
                        with col:
                            movie = recommendations[i]
                            
                            # Prepare data for HTML, limiting cast and escaping
                            title_safe = html.escape(movie['title'])
                            cast_str = ", ".join(movie['cast'][:5]) if movie['cast'] else "N/A"
                            director_str = ", ".join(movie['crew']) if movie['crew'] else "N/A"
                            overview_str = movie['overview'] if movie['overview'] else "No overview available."
                            
                            # Escape strings for safe HTML rendering
                            cast_safe = html.escape(cast_str)
                            director_safe = html.escape(director_str)
                            overview_safe = html.escape(overview_str)

                            # Build HTML card
                            html_card = f"""
                            <div class="movie-card">
                                <img src="{movie['poster']}" class="movie-poster" alt="{title_safe} poster">
                                <div class="movie-title">{title_safe}</div>
                                <div class="movie-overlay">
                                    <h4>{title_safe}</h4>
                                    <p><strong>Director:</strong> {director_safe}</p>
                                    <p><strong>Cast:</strong> {cast_safe}</p>
                                    <p><strong>Overview:</strong> {overview_safe}</p>
                                </div>
                            </div>
                            """
                            st.markdown(html_card, unsafe_allow_html=True)
    else:
        st.warning("No movie titles found for the filtered criteria.")