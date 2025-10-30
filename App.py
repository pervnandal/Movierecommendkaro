import streamlit as st
import pickle as pkl
import pandas as pd
import requests
import time

movies_dict = pkl.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pkl.load(open('similarity.pkl', 'rb'))

# def fetch_poster(movie_id):
#     response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=6d90565f372a61b80c2880887efb194c&language=en-US'.format(movie_id))
#     data = response.json()
#     return "https://image.tmdb.org/t/p/w500" + data['poster_path']

# made by gpt, agr connection ki vjh se photo nhi milti to bina photo ke print kr dega
def fetch_poster(movie_id):
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key=6d90565f372a61b80c2880887efb194c&language=en-US'

    for i in range(3):  # try up to 3 times
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            return "https://image.tmdb.org/t/p/w500" + data['poster_path']
        except requests.exceptions.RequestException:
            print(f"Retrying... attempt {i + 1}")
            time.sleep(1)  # wait 1 second and try again

    # if all retries fail, show placeholder
    return "https://via.placeholder.com/500x750?text=No+Image"


def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []
    for p in movie_list:
        movie_id = movies.iloc[p[0]].movie_id
        recommended_movies.append(movies.iloc[p[0]].title)
        #fetch movie poster through API
        time.sleep(1)  # wait for 1 second before each request
        recommended_movies_posters.append(fetch_poster(movie_id))
    return recommended_movies, recommended_movies_posters

st.title('Movie Recommendation System')

selected_movie = st.selectbox('Select Movie', movies['title'].values)

if st.button("Recommend"):
    names,posters = recommend(selected_movie)

    col1,col2,col3,col4,col5 = st.columns(5)
    with col1:
        st.image(posters[0])
        st.text(names[0])
    with col2:
        st.image(posters[1])
        st.text(names[1])
    with col3:
        st.image(posters[2])
        st.text(names[2])
    with col4:
        st.image(posters[3])
        st.text(names[3])
    with col5:
        st.image(posters[4])
        st.text(names[4])
