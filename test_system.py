"""
Quick test script to verify the system works end-to-end.
"""

import sys
from etl import GameETL
from semantic_search import SemanticSearchEngine
from hybrid_recommender import HybridRecommender

def test_etl():
    """Test ETL pipeline."""
    print("=" * 60)
    print("Testing ETL Pipeline")
    print("=" * 60)
    
    etl = GameETL()
    try:
        df = etl.load_processed_data()
        print("✓ Loaded processed data from cache")
    except FileNotFoundError:
        print("Running ETL pipeline...")
        df = etl.run_pipeline()
        etl.save_processed_data()
        print("✓ ETL pipeline completed and saved")
    
    print(f"✓ Dataset shape: {df.shape}")
    print(f"✓ Columns: {len(df.columns)}")
    return df

def test_semantic_search(df):
    """Test semantic search engine."""
    print("\n" + "=" * 60)
    print("Testing Semantic Search Engine")
    print("=" * 60)
    
    search_engine = SemanticSearchEngine()
    try:
        search_engine.load()
        search_engine.df = df
        print("✓ Loaded search engine from cache")
    except FileNotFoundError:
        print("Training search engine...")
        search_engine.fit(df)
        search_engine.save()
        print("✓ Search engine trained and saved")
    
    # Test search
    print("\nTesting search query: 'space survival game'")
    indices, scores = search_engine.search("space survival game", top_k=5)
    print(f"✓ Found {len(indices)} results")
    for i, (idx, score) in enumerate(zip(indices[:3], scores[:3]), 1):
        print(f"  {i}. {df.iloc[idx]['name']} (score: {score:.4f})")
    
    return search_engine

def test_hybrid_recommender(search_engine, df):
    """Test hybrid recommender."""
    print("\n" + "=" * 60)
    print("Testing Hybrid Recommender")
    print("=" * 60)
    
    recommender = HybridRecommender(search_engine, df)
    
    # Test recommendation
    query = "I want a space survival game with crafting"
    print(f"\nQuery: '{query}'")
    results = recommender.recommend(
        query=query,
        filters={'max_price': 30.0},
        alpha=0.6,
        top_n=5
    )
    
    print(f"✓ Generated {len(results)} recommendations")
    for i, (idx, row) in enumerate(results.iterrows(), 1):
        print(f"\n  {i}. {row['name']}")
        print(f"     Genre: {row['primary_genre']}")
        print(f"     Price: ${row['price']:.2f}")
        print(f"     Final Score: {row['final_score']:.4f}")
    
    return recommender

def main():
    """Run all tests."""
    try:
        # Test ETL
        df = test_etl()
        
        # Test Semantic Search
        search_engine = test_semantic_search(df)
        
        # Test Hybrid Recommender
        recommender = test_hybrid_recommender(search_engine, df)
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start FastAPI backend: uvicorn main:app --reload")
        print("2. Start Streamlit frontend: streamlit run app.py")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

