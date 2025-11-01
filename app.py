import streamlit as st
import pickle as pkl
import pandas as pd
import requests
import time
import ast 
import html

# Page Configuration
st.set_page_config(
    page_title="MovieRecommender",
    page_icon="🎬",
    layout="wide"
)

# --- Improved CSS Styling ---
st.markdown("""
<style>
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    /* NEW: Import FontAwesome Icons */
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');

    html, body, .stApp {
        background-color: #1a1a1a;
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    html, body, .stApp {
        /* OLD: background-color: #1a1a1a; */
        background: radial-gradient(ellipse at center, #2c2c2e 0%, #1a1a1a 70%);
        background-attachment: fixed; /* Keeps the gradient in place on scroll */
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }

    /* --- Title --- */
    h1 {
        color: #ff4b4b; 
        text-align: center;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 3rem;
        text-shadow: 0 2px 4px rgba(255, 75, 75, 0.2);
    }
    
    /* --- Recommendation Subheader --- */
    .recommend-header {
        text-align: center;
        color: #e0e0e0;
        font-weight: 600;
        margin-top: 2rem;
        margin-bottom: 1.5rem;
    }

    /* --- Control Container --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        /* OLD: background-color: #222222; */
        background-color: rgba(34, 34, 34, 0.7); /* Semi-transparent */
        backdrop-filter: blur(10px); /* Glassmorphism effect */
        -webkit-backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 25px;
        border: 1px solid #333;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .stSubheader {
        color: #e0e0e0;
        font-weight: 600;
    }

    /* --- Select Box Styling --- */
    .stSelectbox label {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.05em;
    }

    .stSelectbox div[role="combobox"] {
        background-color: #333333;
        color: #ffffff;
        border-radius: 8px;
        border: 1px solid #444;
    }

    /* NEW: Center the button */
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
    }

    /* --- Button Styling --- */
    .stButton>button {
        background-color: #ff4b4b;
        color: #ffffff;
        border-radius: 8px;
        border: none;
        padding: 12px 20px;
        font-weight: 700;
        font-size: 1.1em;
        transition: background-color 0.3s ease, transform 0.2s ease;
        /* OLD: width: 100%; /* Handled by use_container_width=True */
        max-width: 300px; /* Set a max width for a smaller button */
    }

    .stButton>button:hover {
        background-color: #e04040;
        transform: scale(1.02);
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* --- Card Styling --- */
    
    /* Remove default column padding and add margin */
    .stColumn {
        padding: 0px 8px !important; /* Add some horizontal spacing between cards */
    }

    .movie-card {
        background-color: #2b2b2b;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative; 
        overflow: hidden; 
        height: 100%; 
        border: 1px solid #3a3a3a;
        display: flex;
        flex-direction: column;
        min-height: 480px; /* Ensure consistent min height */
    }

    .movie-card:hover {
        transform: scale(1.04);
        box-shadow: 0 8px 16px rgba(0,0,0,0.4);
        z-index: 10; 
    }

    .movie-poster {
        border-radius: 8px;
        width: 100%;
        aspect-ratio: 2 / 3; /* Maintain poster aspect ratio */
        object-fit: cover; /* Cover the area, don't stretch */
        background-color: #333; /* Placeholder bg */
    }

    .movie-title {
        color: #e0e0e0;
        font-weight: 600;
        font-size: 1.1em;
        text-align: center;
        height: 3.3em; /* 2 lines with 1.65em line-height */
        line-height: 1.65em;
        margin-top: 15px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2; 
        -webkit-box-orient: vertical;
        flex-shrink: 0; /* Prevent title from shrinking */
    }

    /* --- Card Overlay Styling --- */
    .movie-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        /* Glassmorphism effect */
        background-color: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
        
        color: #ffffff;
        opacity: 0;
        visibility: hidden;
        transition: opacity 0.3s ease, visibility 0.3s ease;
        padding: 20px;
        overflow-y: auto; 
        text-align: left;
        font-size: 0.9em;
        border-radius: 12px; 
        line-height: 1.5;
    }

    .movie-card:hover .movie-overlay {
        opacity: 1;
        visibility: visible;
    }

    .movie-overlay h4 {
        color: #ff4b4b;
        font-size: 1.2em;
        margin-bottom: 10px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        font-weight: 700;
    }

    /* OLD: .movie-overlay p { ... } */
    /* NEW: Styles for overlay info */
    .movie-overlay .info-label {
        display: flex;
        align-items: flex-start; /* Align icon with first line of text */
        margin-bottom: 10px;
        font-size: 0.95em;
        line-height: 1.5; /* For if value wraps */
    }

    .movie-overlay .info-label strong {
        color: #ffffff; /* Bright white label */
        white-space: nowrap;
        margin-right: 8px;
        font-weight: 600;
        flex-shrink: 0; /* Don't let the label shrink */
        display: flex; /* To align icon and text */
        align-items: center;
    }
    
    .movie-overlay .info-label span {
        color: #d1d1d1; /* Dimmer value text */
    }
    
    .movie-overlay .overview-label {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        font-size: 0.95em;
    }
    
    .movie-overlay .overview-label strong {
        color: #ffffff;
        white-space: nowrap;
        font-weight: 600;
        display: flex;
        align-items: center;
    }
    
    .movie-overlay .overview-text {
        color: #d1d1d1;
        font-size: 0.92em; /* Slightly smaller for overview block */
        line-height: 1.6;
        margin-bottom: 10px;
    }
    
    /* OLD: .movie-overlay p strong { ... } */
    
    /* NEW: Icon styling */
    .overlay-icon {
        color: #ff4b4b;
        margin-right: 8px;
        min-width: 16px; /* Ensure alignment */
    }
    
    /* NEW: Trailer Button Style */
    .trailer-button {
        display: flex; /* Use flex for icon alignment */
        align-items: center;
        justify-content: center;
        width: 100%;
        padding: 8px 10px;
        margin-top: 15px; /* Space above it */
        background-color: #ff4b4b;
        color: #ffffff;
        text-align: center;
        text-decoration: none;
        font-weight: 600;
        border-radius: 6px;
        transition: background-color 0.2s ease;
    }
    .trailer-button:hover {
        background-color: #e04040;
        color: #ffffff; /* Ensure color stays white */
    }
    
    /* Scrollbar for overlay */
    .movie-overlay::-webkit-scrollbar {
        width: 6px;
    }
    .movie-overlay::-webkit-scrollbar-thumb {
        background-color: #ff4b4b;
        border-radius: 6px;
    }
    .movie-overlay::-webkit-scrollbar-track {
        background-color: #333;
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
        st.error("Error: 'movies_dict.pkl' or 'similarity.pkl' not found. Please ensure the files are in the same directory.")
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
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6d90565f372a61b80c2880887efb194c&language=en-US'
    
    for i in range(3): # Retry logic
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status() # checks https error
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


@st.cache_data
def fetch_trailer(movie_id):
    """
    Fetches the YouTube trailer link for a given movie ID.
    Prioritizes official trailers first, then unofficial trailers,
    then official teasers, then unofficial teasers.
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key=6d90565f372a61b80c2880887efb194c&language=en-US'
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        videos = data.get('results', [])
        
        if not videos:
            return None

        # --- New Prioritization Logic ---
        
        # Filter for YouTube videos
        yt_videos = [v for v in videos if v['site'] == 'YouTube']
        
        # 1. Official Trailers
        official_trailers = [v for v in yt_videos if v['type'] == 'Trailer' and v.get('official', False)]
        if official_trailers:
            # Sort by publish date, newest first (most likely main trailer)
            official_trailers.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            return f"https://www.youtube.com/watch?v={official_trailers[0]['key']}"
        
        # 2. Unofficial Trailers (fallback)
        all_trailers = [v for v in yt_videos if v['type'] == 'Trailer']
        if all_trailers:
            all_trailers.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            return f"https://www.youtube.com/watch?v={all_trailers[0]['key']}"
            
        # 3. Official Teasers
        official_teasers = [v for v in yt_videos if v['type'] == 'Teaser' and v.get('official', False)]
        if official_teasers:
            official_teasers.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            return f"https://www.youtube.com/watch?v={official_teasers[0]['key']}"

        # 4. Unofficial Teasers (fallback)
        all_teasers = [v for v in yt_videos if v['type'] == 'Teaser']
        if all_teasers:
            all_teasers.sort(key=lambda x: x.get('published_at', ''), reverse=True)
            return f"https://www.youtube.com/watch?v={all_teasers[0]['key']}"

        return None # No YouTube trailer or teaser found
    except requests.exceptions.RequestException as e:
        print(f"Trailer request failed for movie ID {movie_id}: {e}")
        return None


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
    
    # Use a spinner that covers the recommendation fetch
    for p in movie_list:
        if p[0] < len(movies):
            movie_data = movies.iloc[p[0]]
            movie_id = movie_data.movie_id
            
            recommendations.append({
                'title': movie_data.title,
                'poster': fetch_poster(movie_id),
                'trailer_url': fetch_trailer(movie_id), # Fetch trailer
                'cast': movie_data.cast,
                'crew': movie_data.crew,
                'overview': movie_data.overview
            })
        else:
            print(f"Skipping index {p[0]} as it's out of bounds for movies (length {len(movies)}).")
            
    return recommendations

# --- Main App Layout ---

# Load all data
movies, similarity, unique_directors, unique_actors = load_data()

st.title('Movie Recommendation System')

# --- Control Section ---
with st.container(border=True):
    st.subheader("Find Your Next Movie")
    
    # Filter Section
    director_options = ['All Directors'] + unique_directors if unique_directors else ['All Directors']
    actor_options = ['All Actors'] + unique_actors if unique_actors else ['All Actors']

    col1, col2 = st.columns(2)
    with col1:
        selected_director = st.selectbox('Filter by Director', director_options)
    with col2:
        selected_actor = st.selectbox('Filter by Actor', actor_options)

    # Apply filters
    filtered_movies = movies.copy()

    if selected_director != 'All Directors':
        filtered_movies = filtered_movies[
            filtered_movies['crew'].apply(
                lambda crew_list: isinstance(crew_list, list) and selected_director in crew_list
            )
        ]

    if selected_actor != 'All Actors':
        filtered_movies = filtered_movies[
            filtered_movies['cast'].apply(
                lambda cast_list: isinstance(cast_list, list) and selected_actor in cast_list
            )
        ]

    # --- Movie Selection and Recommendation ---
    if filtered_movies.empty:
        st.warning("No movies match your filter criteria. Please broaden your search.")
    else:
        movie_titles = filtered_movies['title'].values
        if len(movie_titles) > 0:
            selected_movie = st.selectbox(
                'Select a Movie from the Filtered List', 
                movie_titles,
                index=None,
                placeholder="Choose a movie..."
            )

            # Recommend Button
            if st.button("Recommend") and selected_movie:
                with st.spinner('Finding movies you might like...'):
                    recommendations = recommend(selected_movie)
                
                if recommendations:
                    st.session_state.recommendations = recommendations # Store in session
                else:
                    st.session_state.recommendations = []
            elif not selected_movie and 'recommendations' in st.session_state:
                # Clear recommendations if no movie is selected
                del st.session_state.recommendations

        else:
            st.warning("No movie titles found for the filtered criteria.")

# --- Display Recommendations ---
if 'recommendations' in st.session_state and st.session_state.recommendations:
    st.markdown("<h2 class='recommend-header'>Here are 5 movies you might also like:</h2>", unsafe_allow_html=True)
    
    recommendations = st.session_state.recommendations
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

                # NEW: Check for trailer and create button HTML
                trailer_url = movie.get('trailer_url')
                trailer_button_html = ""
                if trailer_url:
                    # Escape the URL as well for safety
                    safe_trailer_url = html.escape(trailer_url)
                    trailer_button_html = f'<a href="{safe_trailer_url}" target="_blank" class="trailer-button"><i class="fa-solid fa-play"></i>&nbsp;&nbsp;Watch Trailer</a>'

                # Build HTML card
                html_card = f"""
                <div class="movie-card">
                    <img src="{movie['poster']}" class="movie-poster" alt="{title_safe} poster" 
                         onerror="this.onerror=null; this.src='https://placehold.co/500x750/2b2b2b/e0e0e0?text=Error';">
                    <div class="movie-title">{title_safe}</div>
                    <div class="movie-overlay">
                        <h4>{title_safe}</h4>
                        <div class="info-label"><strong><i class="fa-solid fa-clapperboard overlay-icon"></i> Director:</strong> <span>{director_safe}</span></div>
                        <div class="info-label"><strong><i class="fa-solid fa-users overlay-icon"></i> Cast:</strong> <span>{cast_safe}...</span></div>
                        <div class="overview-label"><strong><i class="fa-solid fa-file-alt overlay-icon"></i> Overview:</strong></div>
                        <p class="overview-text">{overview_safe}</p>
                        {trailer_button_html}
                    </div>
                </div>
                """
                st.markdown(html_card, unsafe_allow_html=True)