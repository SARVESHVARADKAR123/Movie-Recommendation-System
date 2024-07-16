import streamlit as st
import pandas as pd
import pickle 

st.title("Movie Recommendation System")
dataframe=pickle.load(open("datadict.pkl",'rb'))
movie=pd.DataFrame(dataframe)
movie_list=movie['title'].values
Similarities=pickle.load(open("Similarities.pkl",'rb'))
import requests


def fetch_poster(movies_id):
    response=requests.get("https://api.themoviedb.org/3/movie/{}?api_key=5e72a0d99a34a95a327beb04c54da972&language-en-US".format(movies_id))
    data=response.json()
    
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']


def Recommend(movie_title):
    # Locate the movie by title and get its index
        movie_index = movie[movie['title'] == movie_title].index[0]
        # Example of similarity matrix handling (assuming it's a 2D array)
        distances = Similarities[movie_index]
        # Sort movies based on similarity scores
        movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recommended_movies = [ ]
        recommended_movies_posters=[]
        for i in movie_list:
            recommended_movies.append(movie.iloc[i[0]].title)
            recommended_movies_posters.append(fetch_poster(movie.iloc[i[0]].id))
        
        return recommended_movies,recommended_movies_posters




selected_option=st.selectbox("which movies you want to recommend ?",movie_list)
    
if st.button("Recommend"):
    names,posters=Recommend(selected_option)
    col1,col2,col3,col4,col5=st.columns(5)
    with col1:
        st.image(posters[0])
        st.write(names[0])
        
    with col2:
        st.image(posters[1])
        st.write(names[1])
        
    with col3:
        st.image(posters[2])
        st.write(names[2])
        
    with col4:
        st.image(posters[3])
        st.write(names[3])
        
    with col5:
        st.image(posters[4])
        st.write(names[4])