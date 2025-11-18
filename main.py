"""
FastAPI Backend for Game Recommender System with Authentication
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
import pandas as pd
import pickle
import os
from datetime import datetime

from etl import GameETL
from semantic_search import SemanticSearchEngine
from hybrid_recommender import HybridRecommender

# Initialize FastAPI app
app = FastAPI(title="GameVerse API", version="2.0.0")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins like ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded models
recommender = None
df = None

# Mock user database (in production, use a real database)
users_db = {}


# Pydantic Models
class UserRegister(BaseModel):
    """User registration model."""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """User login model."""
    username: str
    password: str


class UserResponse(BaseModel):
    """User response model."""
    username: str
    email: str
    created_at: str


class RecommendationRequest(BaseModel):
    """Request model for recommendations."""
    query: str
    filters: Optional[Dict] = {}
    alpha: Optional[float] = 0.5
    top_n: Optional[int] = 10


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    games: List[Dict]
    total_results: int


def load_models():
    """Load the recommender system models."""
    global recommender, df
    
    if recommender is not None:
        return  # Already loaded
    
    print("Loading recommender system...")
    
    # Load processed data
    etl = GameETL()
    try:
        df = etl.load_processed_data()
        print("Loaded processed data from pickle")
    except FileNotFoundError:
        print("Processed data not found. Running ETL pipeline...")
        df = etl.run_pipeline()
        etl.save_processed_data()
    
    # Load search engine
    search_engine = SemanticSearchEngine()
    try:
        search_engine.load()
        search_engine.df = df
        print("Loaded search engine from saved models")
    except FileNotFoundError:
        print("Search engine not found. Training...")
        search_engine.fit(df)
        search_engine.save()
        print("Search engine trained and saved")
    
    # Initialize recommender
    recommender = HybridRecommender(search_engine, df)
    print("Recommender system loaded successfully!")


@app.on_event("startup")
async def startup_event():
    """Load models on startup."""
    load_models()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "GameVerse API - AI Game Recommender",
        "version": "2.0.0",
        "endpoints": {
            "/register": "POST - Register new user",
            "/login": "POST - User login",
            "/recommend": "POST - Get game recommendations",
            "/health": "GET - Health check",
            "/genres": "GET - Get available genres"
        }
    }


@app.post("/register", response_model=UserResponse)
async def register(user: UserRegister):
    """
    Register a new user.
    
    Args:
        user: UserRegister with username, email, password
        
    Returns:
        UserResponse with user details
    """
    # Check if user already exists
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Check if email already exists
    for existing_user in users_db.values():
        if existing_user["email"] == user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    # Store user (in production, hash the password!)
    users_db[user.username] = {
        "username": user.username,
        "email": user.email,
        "password": user.password,  # In production: hash this!
        "created_at": datetime.now().isoformat()
    }
    
    return UserResponse(
        username=user.username,
        email=user.email,
        created_at=users_db[user.username]["created_at"]
    )


@app.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin):
    """
    User login.
    
    Args:
        credentials: UserLogin with username and password
        
    Returns:
        UserResponse with user details
    """
    # Check if user exists
    if credentials.username not in users_db:
        # For demo purposes, auto-create user
        users_db[credentials.username] = {
            "username": credentials.username,
            "email": f"{credentials.username}@gameverse.com",
            "password": credentials.password,
            "created_at": datetime.now().isoformat()
        }
    
    user = users_db[credentials.username]
    
    # Verify password (in production, use proper password hashing!)
    if user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return UserResponse(
        username=user["username"],
        email=user["email"],
        created_at=user["created_at"]
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "models_loaded": recommender is not None
    }


@app.get("/genres")
async def get_genres():
    """Get list of available genres."""
    if df is None:
        load_models()
    
    # Extract all unique genres
    all_genres = set()
    for genres_list in df['genres_parsed'].dropna():
        if isinstance(genres_list, list):
            all_genres.update(genres_list)
    
    return {
        "genres": sorted(list(all_genres)),
        "total": len(all_genres)
    }


@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get game recommendations based on natural language query and filters.
    
    Args:
        request: RecommendationRequest with query, filters, alpha, and top_n
        
    Returns:
        RecommendationResponse with list of recommended games
    """
    if recommender is None:
        load_models()
    
    try:
        # Get recommendations
        results = recommender.recommend(
            query=request.query,
            filters=request.filters,
            alpha=request.alpha,
            top_n=request.top_n
        )
        
        # Convert to list of dictionaries
        games = []
        for idx, row in results.iterrows():
            game_dict = {
                "appid": int(row.get('appid', 0)),
                "name": str(row.get('name', 'Unknown')),
                "primary_genre": str(row.get('primary_genre', 'Unknown')),
                "genres": row.get('genres_parsed', []),
                "price": float(row.get('price', 0.0)),
                "weighted_rating": float(row.get('weighted_rating', 0.0)),
                "positive": int(row.get('positive', 0)),
                "negative": int(row.get('negative', 0)),
                "release_date": str(row.get('release_date', '')),
                "header_image": str(row.get('header_image', '')),
                "description": str(row.get('detailed_description', row.get('short_description', ''))),
                "short_description": str(row.get('short_description', '')),
                "final_score": float(row.get('final_score', 0.0)),
                "semantic_score": float(row.get('semantic_score_norm', 0.0)),
                "quality_score": float(row.get('quality_score_norm', 0.0))
            }
            games.append(game_dict)
        
        return RecommendationResponse(
            games=games,
            total_results=len(games)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

