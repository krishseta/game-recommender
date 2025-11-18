# Hybrid Game Recommender System

A comprehensive game recommendation system that combines semantic search with collaborative filtering signals. Built with FastAPI backend and Streamlit frontend.

## Features

- **Semantic Search**: Uses sentence-transformers (all-MiniLM-L6-v2) to understand natural language queries
- **Hybrid Recommendation**: Combines semantic similarity with IMDB-weighted quality scores
- **Advanced Filtering**: Filter by price, genre, platform (Windows/Mac/Linux)
- **Vector Storage**: Uses FAISS for efficient similarity search
- **Evaluation Metrics**: Precision-Recall curves and UMAP visualizations

## Project Structure

```
.
├── etl.py                  # Data processing pipeline
├── semantic_search.py      # Semantic search engine with FAISS
├── hybrid_recommender.py   # Hybrid recommendation logic
├── evaluation.py           # Evaluation and visualization tools
├── main.py                 # FastAPI backend
├── app.py                  # Streamlit frontend
├── requirements.txt        # Python dependencies
└── games_march2025_cleaned.csv  # Dataset
```

## Installation

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Ensure your dataset is in the root directory:**
   - The system expects `games_march2025_cleaned.csv` in the project root

## Usage

### Step 1: Run ETL Pipeline (First Time Only)

The ETL pipeline processes the raw CSV data:
```bash
python etl.py
```

This will:
- Load and clean the data
- Parse tags, genres, and dates
- Calculate weighted ratings
- Create combined text features
- Save processed data to `processed_games.pkl`

### Step 2: Train Semantic Search Engine (First Time Only)

Train and save the semantic search model:
```bash
python semantic_search.py
```

This will:
- Generate embeddings for all games
- Build FAISS index
- Save model to `models/` directory

### Step 3: Start FastAPI Backend

In Terminal 1:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Step 4: Start Streamlit Frontend

In Terminal 2:
```bash
streamlit run app.py
```

The frontend will open in your browser at `http://localhost:8501`

## API Endpoints

### GET `/`
Root endpoint with API information

### GET `/health`
Health check endpoint

### GET `/genres`
Get list of available genres

### POST `/recommend`
Get game recommendations

**Request Body:**
```json
{
  "query": "I want a space survival game",
  "filters": {
    "max_price": 30.0,
    "genres": ["Action", "Adventure"],
    "windows": true
  },
  "alpha": 0.5,
  "top_n": 10
}
```

**Response:**
```json
{
  "games": [
    {
      "appid": 123,
      "name": "Game Name",
      "primary_genre": "Action",
      "genres": ["Action", "Adventure"],
      "price": 29.99,
      "weighted_rating": 0.85,
      "positive": 10000,
      "negative": 500,
      "release_date": "2023-01-01",
      "header_image": "https://...",
      "description": "...",
      "final_score": 0.92,
      "semantic_score": 0.88,
      "quality_score": 0.95
    }
  ],
  "total_results": 10
}
```

## Evaluation

Generate evaluation metrics and visualizations:
```bash
python evaluation.py
```

This creates:
- `precision_recall_curve.png`: Precision-Recall curve
- `umap_visualization.html`: Interactive UMAP visualization

## Configuration

### Adjusting Recommendation Balance

The `alpha` parameter controls the balance between semantic similarity and quality:
- `alpha = 1.0`: Pure semantic search (only query similarity)
- `alpha = 0.0`: Pure quality-based (only weighted rating)
- `alpha = 0.5`: Balanced (default)

### Model Parameters

- **Embedding Model**: `all-MiniLM-L6-v2` (384 dimensions)
- **Vector Index**: FAISS with cosine similarity
- **Weighted Rating**: IMDB formula with 90th percentile threshold

## Technical Details

### Data Processing
- Drops rows with missing `name` or `detailed_description`
- Parses tags from stringified dictionaries
- Parses genres from stringified lists
- Calculates IMDB-weighted ratings
- Combines name, tags, and description (truncated to 512 tokens) for embeddings

### Hybrid Recommendation Algorithm
1. **Semantic Search**: Retrieve top 50 candidates using vector similarity
2. **Filtering**: Apply user-defined filters (price, genre, platform)
3. **Normalization**: Normalize semantic and quality scores to 0-1 range
4. **Fusion**: Combine scores: `final_score = α × semantic + (1-α) × quality`
5. **Ranking**: Return top N results sorted by final score

## Troubleshooting

### "No processed data available"
Run `python etl.py` first to process the raw data.

### "Index file not found"
Run `python semantic_search.py` to train and save the search engine.

### API connection errors in Streamlit
Make sure the FastAPI server is running on `http://localhost:8000`

### Memory issues with large datasets
The system uses efficient vector storage (FAISS) and processes data in batches. If you encounter memory issues, consider:
- Reducing the number of games processed
- Using a smaller embedding model
- Processing data in chunks

## License

This project is for educational purposes.

