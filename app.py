"""
Streamlit Frontend for Game Recommender System
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List
import os

# Page configuration
st.set_page_config(
    page_title="Game Recommender System",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")


@st.cache_data
def get_genres():
    """Get available genres from API."""
    try:
        response = requests.get(f"{API_URL}/genres")
        if response.status_code == 200:
            return response.json()["genres"]
        return []
    except Exception as e:
        st.error(f"Error fetching genres: {e}")
        return []


def get_recommendations(query: str, filters: Dict, alpha: float, top_n: int):
    """Get recommendations from API."""
    try:
        response = requests.post(
            f"{API_URL}/recommend",
            json={
                "query": query,
                "filters": filters,
                "alpha": alpha,
                "top_n": top_n
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        st.info("Make sure the FastAPI server is running: `uvicorn main:app --reload`")
        return None


def main():
    """Main Streamlit application."""
    
    # Title and description
    st.title("🎮 Hybrid Game Recommender System")
    st.markdown("""
    This system uses **semantic search** and **collaborative filtering** to recommend games based on your natural language queries.
    """)
    
    # Sidebar for filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Price filter
        st.subheader("Price Range")
        price_range = st.slider(
            "Maximum Price (USD)",
            min_value=0.0,
            max_value=100.0,
            value=100.0,
            step=5.0
        )
        
        # Genre filter
        st.subheader("Genres")
        genres = get_genres()
        selected_genres = st.multiselect(
            "Select Genres (optional)",
            options=genres,
            default=[]
        )
        
        # Platform filters
        st.subheader("Platforms")
        windows = st.checkbox("Windows", value=False)
        mac = st.checkbox("Mac", value=False)
        linux = st.checkbox("Linux", value=False)
        
        # Alpha slider (semantic vs quality balance)
        st.subheader("Recommendation Balance")
        alpha = st.slider(
            "Semantic vs Quality Balance",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher values prioritize semantic similarity, lower values prioritize game quality"
        )
        
        # Number of results
        top_n = st.slider(
            "Number of Results",
            min_value=5,
            max_value=50,
            value=10,
            step=5
        )
    
    # Main area
    tab1, tab2 = st.tabs(["🔎 Search", "📊 Metrics"])
    
    with tab1:
        # Query input
        st.subheader("Describe the game you want to play")
        query = st.text_area(
            "Enter your query (e.g., 'I want a space survival game with crafting')",
            height=100,
            placeholder="I want a space survival game with crafting and base building..."
        )
        
        # Search button
        if st.button("🔍 Get Recommendations", type="primary", use_container_width=True):
            if not query.strip():
                st.warning("Please enter a query!")
            else:
                with st.spinner("Searching for games..."):
                    # Build filters
                    filters = {
                        "max_price": price_range if price_range < 100.0 else None,
                        "genres": selected_genres if selected_genres else None,
                        "windows": windows,
                        "mac": mac,
                        "linux": linux
                    }
                    
                    # Remove None values
                    filters = {k: v for k, v in filters.items() if v is not None and v != []}
                    
                    # Get recommendations
                    result = get_recommendations(query, filters, alpha, top_n)
                    
                    if result:
                        games = result["games"]
                        total = result["total_results"]
                        
                        if total == 0:
                            st.warning("No games found matching your criteria. Try adjusting your filters.")
                        else:
                            st.success(f"Found {total} recommendations!")
                            
                            # Display results
                            for i, game in enumerate(games, 1):
                                with st.container():
                                    col1, col2 = st.columns([1, 3])
                                    
                                    with col1:
                                        if game.get("header_image"):
                                            st.image(game["header_image"], use_container_width=True)
                                        else:
                                            st.info("No image available")
                                    
                                    with col2:
                                        st.subheader(f"{i}. {game['name']}")
                                        
                                        # Metadata
                                        col_meta1, col_meta2, col_meta3 = st.columns(3)
                                        with col_meta1:
                                            st.metric("Price", f"${game['price']:.2f}")
                                        with col_meta2:
                                            st.metric("Rating", f"{game['weighted_rating']:.3f}")
                                        with col_meta3:
                                            pos = game.get('positive', 0)
                                            neg = game.get('negative', 0)
                                            total_reviews = pos + neg
                                            if total_reviews > 0:
                                                pct = (pos / total_reviews) * 100
                                                st.metric("Positive Reviews", f"{pct:.1f}%")
                                        
                                        # Genre tags
                                        genres_str = ", ".join(game.get('genres', []))
                                        st.caption(f"**Genres:** {genres_str}")
                                        
                                        # Description
                                        description = game.get('short_description') or game.get('description', '')
                                        if description:
                                            st.text(description[:300] + "..." if len(description) > 300 else description)
                                        
                                        # Scores (collapsible)
                                        with st.expander("View Scores"):
                                            col_score1, col_score2, col_score3 = st.columns(3)
                                            with col_score1:
                                                st.metric("Final Score", f"{game['final_score']:.4f}")
                                            with col_score2:
                                                st.metric("Semantic Score", f"{game['semantic_score']:.4f}")
                                            with col_score3:
                                                st.metric("Quality Score", f"{game['quality_score']:.4f}")
                                        
                                        st.divider()
    
    with tab2:
        st.header("📊 Evaluation Metrics")
        
        st.subheader("About the Metrics")
        st.markdown("""
        These visualizations help understand how the recommender system works:
        - **Precision-Recall Curve**: Shows the trade-off between precision and recall for recommendations
        - **UMAP Visualization**: Shows how games are clustered in the semantic embedding space
        """)
        
        # Note about metrics
        st.info("""
        **Note**: To view the Precision-Recall curve and UMAP visualization, run the evaluation script:
        ```bash
        python evaluation.py
        ```
        This will generate `precision_recall_curve.png` and `umap_visualization.html` files.
        """)
        
        # Check if visualization files exist
        if os.path.exists("precision_recall_curve.png"):
            st.subheader("Precision-Recall Curve")
            st.image("precision_recall_curve.png", use_container_width=True)
        
        if os.path.exists("umap_visualization.html"):
            st.subheader("UMAP Embedding Space Visualization")
            with open("umap_visualization.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=700, scrolling=True)


if __name__ == "__main__":
    main()

