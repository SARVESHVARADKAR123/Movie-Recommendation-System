import streamlit as st
import pandas as pd
import pickle 
import os
import requests
import random

# Page configuration
st.set_page_config(
    page_title="Movie Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background-color: #0e1117;
    }

    .stButton>button {
        background: linear-gradient(90deg, #ff4b2b, #ff416c);
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        width: 100%;
    }

    .movie-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 10px;
        text-align: center;
        transition: transform 0.2s;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    .movie-card:hover {
        transform: scale(1.02);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }

    .rating-badge {
        background: #f1c40f;
        color: #000;
        padding: 2px 8px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_resource
def load_data():
    try:
        dataframe = pickle.load(open("app_data/datadict.pkl", 'rb'))
        movie = pd.DataFrame(dataframe)
        Similarities = pickle.load(open("app_data/Similarities.pkl", 'rb'))
        return movie, Similarities
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

movie, Similarities = load_data()

if movie is not None:
    movie_list = movie['title'].values

    # --- API Functions ---
    API_KEY = "5e72a0d99a34a95a327beb04c54da972"

    @st.cache_data
    def fetch_movie_details(movie_id):
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
        try:
            response = requests.get(url, timeout=5)
            data = response.json()
            poster_path = data.get('poster_path')
            full_path = f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Poster"
            return {
                "poster": full_path,
                "overview": data.get('overview', 'No description available.'),
                "rating": round(data.get('vote_average', 0), 1),
                "release_date": data.get('release_date', 'Unknown'),
                "genres": [g['name'] for g in data.get('genres', [])]
            }
        except:
            return {
                "poster": "https://via.placeholder.com/500x750?text=Error",
                "overview": "Could not fetch details.",
                "rating": 0,
                "release_date": "N/A",
                "genres": []
            }

    def get_recommendations(movie_title):
        movie_index = movie[movie['title'] == movie_title].index[0]
        distances = Similarities[movie_index]
        top_indices = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
        
        recs = []
        for i in top_indices:
            m_id = movie.iloc[i[0]].id
            m_title = movie.iloc[i[0]].title
            details = fetch_movie_details(m_id)
            recs.append({
                "id": m_id,
                "title": m_title,
                **details
            })
        return recs

    # --- Sidebar ---
    with st.sidebar:
        st.title("🎬 Movie System")
        mode = st.radio("Navigation", ["Home", "About"])
        st.divider()
        if st.button("🎲 Random Movie"):
            random_movie = random.choice(movie_list)
            st.session_state.selected_movie = random_movie
            st.rerun()

    # --- Main App ---
    if mode == "Home":
        st.title("Movie Recommendation System")
        
        if 'selected_movie' not in st.session_state:
            st.session_state.selected_movie = movie_list[0]

        selected_movie_name = st.selectbox(
            "Select a movie you liked:",
            movie_list,
            index=list(movie_list).index(st.session_state.selected_movie)
        )
        st.session_state.selected_movie = selected_movie_name

        if st.button("Show Recommendations"):
            with st.spinner('Fetching recommendations...'):
                recommendations = get_recommendations(selected_movie_name)
                
                # Show details of selected movie
                sel_id = movie[movie['title'] == selected_movie_name].id.values[0]
                sel_details = fetch_movie_details(sel_id)
                
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(sel_details['poster'], use_container_width=True)
                with col2:
                    st.header(selected_movie_name)
                    st.write(f"**Rating:** ⭐ {sel_details['rating']}/10")
                    st.write(f"**Genres:** {', '.join(sel_details['genres'])}")
                    st.write(f"**Release Date:** {sel_details['release_date']}")
                    st.write(f"**Overview:** {sel_details['overview']}")
                
                st.markdown("---")
                st.subheader("Recommended for you:")
                
                # Original 5-column layout
                cols = st.columns(5)
                for idx, rec in enumerate(recommendations):
                    with cols[idx]:
                        st.markdown(f"""
                        <div class="movie-card">
                            <img src="{rec['poster']}" style="width:100%; border-radius:10px; margin-bottom:10px;">
                            <div style="font-size: 0.9rem; font-weight:bold; height: 3rem; overflow: hidden;">{rec['title']}</div>
                            <span class="rating-badge">⭐ {rec['rating']}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        with st.expander("Details"):
                            st.write(rec['overview'])

    elif mode == "About":
        st.title("About the System")
        st.write("This application uses machine learning to recommend movies based on content similarity.")

else:
    st.error("Could not load application data. Please ensure app_data/ directory exists and contains correct files.")