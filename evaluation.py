"""
Evaluation and Visualization functions for the Game Recommender System.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import precision_recall_curve, auc
from typing import Tuple, List, Optional
import plotly.graph_objects as go
import plotly.express as px
from umap import UMAP
from semantic_search import SemanticSearchEngine


class RecommenderEvaluator:
    """Evaluation and visualization tools for the recommender system."""
    
    def __init__(self, recommender, df: pd.DataFrame):
        """
        Initialize the evaluator.
        
        Args:
            recommender: HybridRecommender instance
            df: DataFrame with game data
        """
        self.recommender = recommender
        self.df = df.copy()
    
    def simulate_ground_truth(self, query: str, top_result_genre: str) -> pd.Series:
        """
        Simulate ground truth by assuming games with the same primary genre
        as the top result are "relevant".
        
        Args:
            query: Search query
            top_result_genre: Primary genre of the top result
            
        Returns:
            Series with binary relevance labels (1 = relevant, 0 = not relevant)
        """
        # Get all candidate results from semantic search
        candidate_indices, _ = self.recommender.search_engine.search(query, top_k=100)
        candidate_df = self.df.iloc[candidate_indices].copy()
        
        # Mark games with same primary genre as relevant
        relevance = (candidate_df['primary_genre'] == top_result_genre).astype(int)
        
        return relevance
    
    def calculate_precision_recall(
        self,
        query: str,
        recommendations: pd.DataFrame,
        ground_truth: pd.Series
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate precision-recall curve for recommendations.
        
        Args:
            query: Search query
            recommendations: DataFrame with recommendations
            ground_truth: Series with binary relevance labels
            
        Returns:
            Tuple of (precision, recall, thresholds)
        """
        # Get scores for all candidates
        candidate_indices, semantic_scores = self.recommender.search_engine.search(query, top_k=100)
        
        # Create score array matching ground truth order
        scores = semantic_scores
        
        # Calculate precision-recall curve
        precision, recall, thresholds = precision_recall_curve(ground_truth, scores)
        
        return precision, recall, thresholds
    
    def plot_precision_recall_curve(
        self,
        query: str,
        recommendations: pd.DataFrame,
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot precision-recall curve.
        
        Args:
            query: Search query
            recommendations: DataFrame with recommendations
            save_path: Optional path to save the figure
            
        Returns:
            Matplotlib figure
        """
        if len(recommendations) == 0:
            raise ValueError("No recommendations to evaluate")
        
        # Get top result genre for ground truth simulation
        top_result_genre = recommendations.iloc[0]['primary_genre']
        
        # Simulate ground truth
        ground_truth = self.simulate_ground_truth(query, top_result_genre)
        
        # Calculate precision-recall
        precision, recall, thresholds = self.calculate_precision_recall(
            query, recommendations, ground_truth
        )
        
        # Calculate AUC
        pr_auc = auc(recall, precision)
        
        # Plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(recall, precision, linewidth=2, label=f'PR Curve (AUC = {pr_auc:.3f})')
        ax.set_xlabel('Recall', fontsize=12)
        ax.set_ylabel('Precision', fontsize=12)
        ax.set_title(f'Precision-Recall Curve\nQuery: "{query}"', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        return fig
    
    def create_umap_visualization(
        self,
        n_samples: int = 1000,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        n_components: int = 2
    ) -> go.Figure:
        """
        Create UMAP visualization of game embeddings colored by primary genre.
        
        Args:
            n_samples: Number of games to visualize (for performance)
            n_neighbors: UMAP n_neighbors parameter
            min_dist: UMAP min_dist parameter
            n_components: Number of dimensions (2 for visualization)
            
        Returns:
            Plotly figure
        """
        # Sample games if dataset is large
        if len(self.df) > n_samples:
            sample_df = self.df.sample(n=n_samples, random_state=42)
        else:
            sample_df = self.df.copy()
        
        # Get embeddings for sampled games
        if self.recommender.search_engine.embeddings is None:
            raise ValueError("Embeddings not available. Please ensure search engine is fitted.")
        
        # Get indices of sampled games
        sample_indices = sample_df.index.values
        sample_embeddings = self.recommender.search_engine.embeddings[sample_indices]
        
        print(f"Reducing {len(sample_embeddings)} embeddings to 2D using UMAP...")
        
        # Apply UMAP
        umap_model = UMAP(
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            n_components=n_components,
            random_state=42
        )
        embeddings_2d = umap_model.fit_transform(sample_embeddings)
        
        # Create DataFrame for plotting
        plot_df = pd.DataFrame({
            'x': embeddings_2d[:, 0],
            'y': embeddings_2d[:, 1],
            'genre': sample_df['primary_genre'].values,
            'name': sample_df['name'].values,
            'weighted_rating': sample_df['weighted_rating'].values
        })
        
        # Create interactive scatter plot
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='genre',
            hover_data=['name', 'weighted_rating'],
            title='Game Embedding Space Visualization (UMAP)',
            labels={'x': 'UMAP Dimension 1', 'y': 'UMAP Dimension 2'},
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            width=1000,
            height=700,
            showlegend=True
        )
        
        return fig


if __name__ == "__main__":
    # Test evaluation functions
    from etl import GameETL
    from semantic_search import SemanticSearchEngine
    from hybrid_recommender import HybridRecommender
    
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
        search_engine.df = df
    except FileNotFoundError:
        search_engine.fit(df)
        search_engine.save()
    
    # Initialize recommender
    recommender = HybridRecommender(search_engine, df)
    
    # Initialize evaluator
    evaluator = RecommenderEvaluator(recommender, df)
    
    # Test recommendation
    query = "I want a space survival game"
    results = recommender.recommend(query, top_n=10)
    
    print(f"Generated {len(results)} recommendations for query: '{query}'")
    
    # Plot precision-recall curve
    print("\nGenerating Precision-Recall curve...")
    fig = evaluator.plot_precision_recall_curve(query, results)
    plt.savefig("precision_recall_curve.png", dpi=300, bbox_inches='tight')
    print("Saved precision_recall_curve.png")
    
    # Create UMAP visualization
    print("\nGenerating UMAP visualization...")
    umap_fig = evaluator.create_umap_visualization(n_samples=500)
    umap_fig.write_html("umap_visualization.html")
    print("Saved umap_visualization.html")

