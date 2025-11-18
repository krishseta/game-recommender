"""
Semantic Search Engine using sentence-transformers and FAISS for vector storage.
"""

import numpy as np
import pandas as pd
import pickle
import os
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import faiss


class SemanticSearchEngine:
    """Semantic search engine using sentence transformers and FAISS."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic search engine.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        self.model_name = model_name
        self.model = None
        self.index = None
        self.df = None
        self.embeddings = None
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def load_model(self):
        """Load the sentence transformer model."""
        print(f"Loading sentence transformer model: {self.model_name}...")
        self.model = SentenceTransformer(self.model_name)
        print("Model loaded successfully!")
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            self.load_model()
        
        print(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        print("Embeddings generated successfully!")
        return embeddings
    
    def build_index(self, embeddings: np.ndarray):
        """
        Build FAISS index for fast similarity search.
        
        Args:
            embeddings: Numpy array of embeddings
        """
        print("Building FAISS index...")
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index (Inner Product for cosine similarity after normalization)
        self.dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(self.dimension)
        
        # Add embeddings to index
        self.index.add(embeddings.astype('float32'))
        
        print(f"Index built with {self.index.ntotal} vectors!")
    
    def search(self, query: str, top_k: int = 50) -> Tuple[np.ndarray, np.ndarray]:
        """
        Search for similar games using a natural language query.
        
        Args:
            query: Natural language query string
            top_k: Number of top results to return
            
        Returns:
            Tuple of (indices, similarity_scores)
        """
        if self.model is None:
            self.load_model()
        
        if self.index is None:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Encode query
        query_embedding = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)
        
        # Search
        query_embedding = query_embedding.astype('float32')
        similarities, indices = self.index.search(query_embedding, top_k)
        
        # Return indices and similarity scores
        return indices[0], similarities[0]
    
    def fit(self, df: pd.DataFrame, text_column: str = "combined_features"):
        """
        Fit the search engine on a dataframe.
        
        Args:
            df: DataFrame with game data
            text_column: Column name containing text to embed
        """
        self.df = df.copy()
        
        # Generate embeddings
        texts = df[text_column].fillna('').tolist()
        self.embeddings = self.generate_embeddings(texts)
        
        # Build index
        self.build_index(self.embeddings)
    
    def save(self, directory: str = "models"):
        """
        Save the model, index, and metadata.
        
        Args:
            directory: Directory to save files
        """
        os.makedirs(directory, exist_ok=True)
        
        print(f"Saving model and index to {directory}...")
        
        # Save model (sentence transformer)
        model_path = os.path.join(directory, "sentence_model")
        self.model.save(model_path)
        
        # Save FAISS index
        index_path = os.path.join(directory, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        
        # Save embeddings
        embeddings_path = os.path.join(directory, "embeddings.npy")
        np.save(embeddings_path, self.embeddings)
        
        # Save metadata
        metadata = {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'num_vectors': self.index.ntotal
        }
        metadata_path = os.path.join(directory, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata, f)
        
        print("Model and index saved successfully!")
    
    def load(self, directory: str = "models"):
        """
        Load the model, index, and metadata.
        
        Args:
            directory: Directory containing saved files
        """
        print(f"Loading model and index from {directory}...")
        
        # Load model
        model_path = os.path.join(directory, "sentence_model")
        if os.path.exists(model_path):
            self.model = SentenceTransformer(model_path)
        else:
            self.load_model()
        
        # Load FAISS index
        index_path = os.path.join(directory, "faiss_index.bin")
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            self.dimension = self.index.d
        else:
            raise FileNotFoundError(f"Index file not found: {index_path}")
        
        # Load embeddings
        embeddings_path = os.path.join(directory, "embeddings.npy")
        if os.path.exists(embeddings_path):
            self.embeddings = np.load(embeddings_path)
        
        # Load metadata
        metadata_path = os.path.join(directory, "metadata.pkl")
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                metadata = pickle.load(f)
                self.model_name = metadata.get('model_name', self.model_name)
        
        print("Model and index loaded successfully!")


if __name__ == "__main__":
    # Test the semantic search engine
    from etl import GameETL
    
    # Load processed data
    etl = GameETL()
    try:
        df = etl.load_processed_data()
    except FileNotFoundError:
        df = etl.run_pipeline()
        etl.save_processed_data()
    
    # Initialize and fit search engine
    search_engine = SemanticSearchEngine()
    search_engine.fit(df)
    
    # Save the model
    search_engine.save()
    
    # Test search
    print("\nTesting search...")
    indices, scores = search_engine.search("I want a space survival game", top_k=5)
    
    print("\nTop 5 results:")
    for idx, score in zip(indices, scores):
        print(f"  {df.iloc[idx]['name']}: {score:.4f}")

