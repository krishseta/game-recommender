"""
Data Engineering Pipeline (ETL) for Game Recommender System
Handles data loading, cleaning, parsing, feature engineering, and text preparation.
"""

import pandas as pd
import numpy as np
import ast
import pickle
from datetime import datetime
from typing import Tuple
import re


class GameETL:
    """ETL pipeline for processing game data."""
    
    def __init__(self, csv_path: str = "games_march2025_cleaned.csv"):
        """
        Initialize the ETL pipeline.
        
        Args:
            csv_path: Path to the games CSV file
        """
        self.csv_path = csv_path
        self.df = None
        
    def load_data(self) -> pd.DataFrame:
        """
        Load the CSV file and perform initial cleaning.
        
        Returns:
            Cleaned DataFrame
        """
        print("Loading data from CSV...")
        self.df = pd.read_csv(self.csv_path, low_memory=False)
        
        # Drop rows with missing name or detailed_description
        initial_count = len(self.df)
        self.df = self.df.dropna(subset=['name', 'detailed_description'])
        final_count = len(self.df)
        print(f"Dropped {initial_count - final_count} rows with missing name or detailed_description")
        print(f"Remaining rows: {final_count}")
        
        return self.df
    
    def parse_tags(self, tags_str: str) -> str:
        """
        Parse tags from stringified dictionary to space-separated string.
        
        Args:
            tags_str: String representation of tags dict
            
        Returns:
            Space-separated string of tag keys
        """
        if pd.isna(tags_str) or tags_str == '':
            return ''
        
        try:
            # Try to parse as dictionary
            tags_dict = ast.literal_eval(tags_str)
            if isinstance(tags_dict, dict):
                # Extract keys and join with spaces
                return ' '.join(tags_dict.keys())
        except (ValueError, SyntaxError):
            # If parsing fails, try to extract keys using regex
            # Pattern: 'key': value
            keys = re.findall(r"'([^']+)':", tags_str)
            if keys:
                return ' '.join(keys)
        
        return ''
    
    def parse_genres(self, genres_str: str) -> list:
        """
        Parse genres from stringified list to Python list.
        
        Args:
            genres_str: String representation of genres list
            
        Returns:
            List of genre strings
        """
        if pd.isna(genres_str) or genres_str == '':
            return []
        
        try:
            genres_list = ast.literal_eval(genres_str)
            if isinstance(genres_list, list):
                return genres_list
        except (ValueError, SyntaxError):
            # Try regex extraction
            genres = re.findall(r"'([^']+)'", genres_str)
            return genres
        
        return []
    
    def parse_columns(self) -> pd.DataFrame:
        """
        Parse tags, genres, and release_date columns.
        
        Returns:
            DataFrame with parsed columns
        """
        print("Parsing columns...")
        
        # Parse tags
        print("  - Parsing tags...")
        self.df['tags_parsed'] = self.df['tags'].apply(self.parse_tags)
        
        # Parse genres
        print("  - Parsing genres...")
        self.df['genres_parsed'] = self.df['genres'].apply(self.parse_genres)
        
        # Parse release_date
        print("  - Parsing release_date...")
        self.df['release_date'] = pd.to_datetime(self.df['release_date'], errors='coerce')
        
        # Extract primary genre (first genre in the list)
        self.df['primary_genre'] = self.df['genres_parsed'].apply(
            lambda x: x[0] if isinstance(x, list) and len(x) > 0 else 'Unknown'
        )
        
        print("Column parsing complete!")
        return self.df
    
    def calculate_weighted_rating(self) -> pd.DataFrame:
        """
        Calculate IMDB Weighted Rating for each game.
        
        Formula: WR = (v/(v+m) * R) + (m/(v+m) * C)
        Where:
            v = number of votes (positive + negative)
            m = minimum votes required (90th percentile)
            R = average rating (positive / (positive + negative))
            C = mean vote across the whole dataset
        
        Returns:
            DataFrame with weighted_rating column
        """
        print("Calculating weighted ratings...")
        
        # Calculate votes and ratings
        self.df['votes'] = self.df['positive'] + self.df['negative']
        self.df['rating'] = self.df['positive'] / (self.df['votes'] + 1e-6)  # Avoid division by zero
        
        # Calculate minimum votes (90th percentile)
        m = self.df['votes'].quantile(0.90)
        print(f"  - Minimum votes threshold (90th percentile): {m:.0f}")
        
        # Calculate mean rating across all games
        C = self.df['rating'].mean()
        print(f"  - Mean rating across dataset: {C:.4f}")
        
        # Calculate weighted rating
        v = self.df['votes']
        R = self.df['rating']
        
        self.df['weighted_rating'] = (v / (v + m) * R) + (m / (v + m) * C)
        
        # Fill NaN values with 0
        self.df['weighted_rating'] = self.df['weighted_rating'].fillna(0)
        
        print("Weighted rating calculation complete!")
        return self.df
    
    def truncate_text(self, text: str, max_tokens: int = 512) -> str:
        """
        Truncate text to approximately max_tokens words.
        
        Args:
            text: Input text
            max_tokens: Maximum number of tokens (words)
            
        Returns:
            Truncated text
        """
        if pd.isna(text) or text == '':
            return ''
        
        # Simple word-based truncation
        words = text.split()
        if len(words) <= max_tokens:
            return text
        
        return ' '.join(words[:max_tokens])
    
    def create_combined_features(self) -> pd.DataFrame:
        """
        Create combined_features column by concatenating name, parsed tags, and truncated description.
        
        Returns:
            DataFrame with combined_features column
        """
        print("Creating combined features...")
        
        # Truncate detailed_description to first 512 tokens
        self.df['description_truncated'] = self.df['detailed_description'].apply(
            lambda x: self.truncate_text(str(x), max_tokens=512)
        )
        
        # Combine features
        self.df['combined_features'] = (
            self.df['name'].fillna('') + ' ' +
            self.df['tags_parsed'].fillna('') + ' ' +
            self.df['description_truncated'].fillna('')
        )
        
        # Clean up extra whitespace
        self.df['combined_features'] = self.df['combined_features'].apply(
            lambda x: ' '.join(str(x).split())
        )
        
        print("Combined features created!")
        return self.df
    
    def run_pipeline(self) -> pd.DataFrame:
        """
        Run the complete ETL pipeline.
        
        Returns:
            Processed DataFrame
        """
        print("=" * 60)
        print("Starting ETL Pipeline")
        print("=" * 60)
        
        # Step 1: Load and clean
        self.load_data()
        
        # Step 2: Parse columns
        self.parse_columns()
        
        # Step 3: Feature engineering (Weighted Rating)
        self.calculate_weighted_rating()
        
        # Step 4: Text preparation
        self.create_combined_features()
        
        print("=" * 60)
        print("ETL Pipeline Complete!")
        print("=" * 60)
        print(f"Final dataset shape: {self.df.shape}")
        print(f"Columns: {self.df.columns.tolist()}")
        
        return self.df
    
    def save_processed_data(self, output_path: str = "processed_games.pkl"):
        """
        Save processed DataFrame to pickle file.
        
        Args:
            output_path: Path to save the pickle file
        """
        if self.df is None:
            raise ValueError("No processed data available. Run run_pipeline() first.")
        
        print(f"Saving processed data to {output_path}...")
        with open(output_path, 'wb') as f:
            pickle.dump(self.df, f)
        print("Data saved successfully!")
    
    def load_processed_data(self, input_path: str = "processed_games.pkl") -> pd.DataFrame:
        """
        Load processed DataFrame from pickle file.
        
        Args:
            input_path: Path to the pickle file
            
        Returns:
            Loaded DataFrame
        """
        print(f"Loading processed data from {input_path}...")
        with open(input_path, 'rb') as f:
            self.df = pickle.load(f)
        print("Data loaded successfully!")
        return self.df


if __name__ == "__main__":
    # Run ETL pipeline
    etl = GameETL()
    df = etl.run_pipeline()
    
    # Save processed data
    etl.save_processed_data()
    
    # Display sample
    print("\nSample processed data:")
    print(df[['appid', 'name', 'primary_genre', 'weighted_rating', 'combined_features']].head(3))

