"""
Hybrid Recommender System combining semantic search with collaborative filtering signals.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from semantic_search import SemanticSearchEngine


class HybridRecommender:
    """Hybrid recommender combining semantic search and quality signals."""
    
    def __init__(self, search_engine: SemanticSearchEngine, df: pd.DataFrame):
        """
        Initialize the hybrid recommender.
        
        Args:
            search_engine: Trained SemanticSearchEngine instance
            df: DataFrame with game data (must match the search engine's data)
        """
        self.search_engine = search_engine
        self.df = df.copy()
        
    def normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """
        Normalize scores to 0-1 range using min-max normalization.
        
        Args:
            scores: Array of scores
            
        Returns:
            Normalized scores
        """
        if len(scores) == 0:
            return scores
        
        min_score = scores.min()
        max_score = scores.max()
        
        if max_score == min_score:
            return np.ones_like(scores)
        
        return (scores - min_score) / (max_score - min_score)
    
    def apply_filters(self, candidate_indices: np.ndarray, filters: Dict) -> np.ndarray:
        """
        Apply user-defined filters to candidate games.
        
        Args:
            candidate_indices: Positional indices of candidate games in dataframe
            filters: Dictionary of filter criteria
        
        Returns:
            Filtered positional indices
        """
        if not filters:
            return candidate_indices
        
        # Get candidate dataframe using positional indices
        candidate_df = self.df.iloc[candidate_indices].copy()
        candidate_df['_original_position'] = candidate_indices  # Store original positions
        
        # Price filter
        if 'max_price' in filters and filters['max_price'] is not None:
            candidate_df = candidate_df[candidate_df['price'] <= filters['max_price']]
        
        if 'min_price' in filters and filters['min_price'] is not None:
            candidate_df = candidate_df[candidate_df['price'] >= filters['min_price']]
        
        # Genre filter
        if 'genres' in filters and filters['genres']:
            genre_list = filters['genres'] if isinstance(filters['genres'], list) else [filters['genres']]
            mask = candidate_df['genres_parsed'].apply(
                lambda x: any(genre in x for genre in genre_list) if isinstance(x, list) else False
            )
            candidate_df = candidate_df[mask]
        
        # Platform filters
        if 'windows' in filters and filters['windows']:
            candidate_df = candidate_df[candidate_df['windows'] == True]
        
        if 'mac' in filters and filters['mac']:
            candidate_df = candidate_df[candidate_df['mac'] == True]
        
        if 'linux' in filters and filters['linux']:
            candidate_df = candidate_df[candidate_df['linux'] == True]
        
        # Minimum rating filter
        if 'min_rating' in filters and filters['min_rating'] is not None:
            candidate_df = candidate_df[candidate_df['weighted_rating'] >= filters['min_rating']]
        
        # Return filtered positional indices
        return candidate_df['_original_position'].values
    
    def recommend(
        self,
        query: str,
        filters: Optional[Dict] = None,
        alpha: float = 0.5,
        top_n: int = 10,
        semantic_top_k: int = 50
    ) -> pd.DataFrame:
        """
        Generate hybrid recommendations.
        
        Args:
            query: Natural language query
            filters: Dictionary of filter criteria
            alpha: Weight for semantic score (1-alpha for quality score)
            top_n: Number of final recommendations to return
            semantic_top_k: Number of candidates from semantic search
            
        Returns:
            DataFrame with recommendations and scores
        """
        if filters is None:
            filters = {}
        
        # Step 1: Semantic Search - Get top candidates
        candidate_indices, semantic_scores = self.search_engine.search(query, top_k=semantic_top_k)
        
        # Step 2: Apply Filters
        filtered_indices = self.apply_filters(candidate_indices, filters)
        
        if len(filtered_indices) == 0:
            # No results after filtering, return empty dataframe
            return pd.DataFrame()
        
        # Get filtered data using positional indices
        filtered_df = self.df.iloc[filtered_indices].copy()
        
        # Get semantic scores for filtered results
        # Map candidate indices to semantic scores
        candidate_to_score = dict(zip(candidate_indices, semantic_scores))
        filtered_df['semantic_score'] = [candidate_to_score.get(idx, 0) for idx in filtered_indices]
        
        # Step 3: Normalize Scores
        semantic_scores_normalized = self.normalize_scores(filtered_df['semantic_score'].values)
        quality_scores_normalized = self.normalize_scores(filtered_df['weighted_rating'].values)
        
        # Step 4: Fusion
        final_scores = alpha * semantic_scores_normalized + (1 - alpha) * quality_scores_normalized
        
        filtered_df['final_score'] = final_scores
        filtered_df['semantic_score_norm'] = semantic_scores_normalized
        filtered_df['quality_score_norm'] = quality_scores_normalized
        
        # Step 5: Sort and return top N
        result_df = filtered_df.sort_values('final_score', ascending=False).head(top_n)
        
        # Select relevant columns for output
        output_columns = [
            'appid', 'name', 'primary_genre', 'genres_parsed', 'price',
            'weighted_rating', 'positive', 'negative', 'release_date',
            'header_image', 'detailed_description', 'short_description',
            'final_score', 'semantic_score_norm', 'quality_score_norm'
        ]
        
        # Only include columns that exist
        available_columns = [col for col in output_columns if col in result_df.columns]
        result_df = result_df[available_columns].copy()
        
        return result_df


if __name__ == "__main__":
    # Test the hybrid recommender
    from etl import GameETL
    from semantic_search import SemanticSearchEngine
    
    # Load data
    etl = GameETL()
    try:
        df = etl.load_processed_data()
    except FileNotFoundError:
        df = etl.run_pipeline()
        etl.save_processed_data()
    
    # Load search engine
    search_engine = SemanticSearchEngine()
    try:
        search_engine.load()
        search_engine.df = df  # Ensure dataframe is set
    except FileNotFoundError:
        search_engine.fit(df)
        search_engine.save()
    
    # Initialize recommender
    recommender = HybridRecommender(search_engine, df)
    
    # Test recommendation
    print("Testing hybrid recommendation...")
    results = recommender.recommend(
        query="I want a space survival game with crafting",
        filters={'max_price': 30.0, 'genres': ['Action', 'Adventure']},
        alpha=0.6,
        top_n=5
    )
    
    print(f"\nFound {len(results)} recommendations:")
    for idx, row in results.iterrows():
        print(f"\n{row['name']}")
        print(f"  Genre: {row['primary_genre']}")
        print(f"  Price: ${row['price']:.2f}")
        print(f"  Final Score: {row['final_score']:.4f}")
        print(f"  Semantic: {row['semantic_score_norm']:.4f}, Quality: {row['quality_score_norm']:.4f}")

