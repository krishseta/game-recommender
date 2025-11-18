# 🌌 ARCADE - AI Game Discovery Platform

Ultra-high-end hybrid game recommendation system with cinematic dark mode UI. Combines semantic search with collaborative filtering for intelligent game discovery.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![React](https://img.shields.io/badge/React-18-61dafb?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-Latest-009688?style=flat-square)

![DATASET](https://drive.google.com/file/d/1JGUo-r4vOs21QRu3UvvfGEJ35ERTdiRg/view?ts=691cc33e)

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Process data (first time only)
python etl.py

# Train search engine (first time only)
python semantic_search.py

# Start FastAPI backend
uvicorn main:app --reload
```

Backend runs on: `http://localhost:8000`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs on: `http://localhost:3000`

### 3. Access the App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 Evaluation

Run comprehensive evaluation metrics:

```bash
python evaluation_metrics.py
```

Generates:
- NDCG@k, MRR, MAP
- Precision@k, Recall@k
- Coverage, Diversity, Novelty
- Visualization: `metrics_comparison.png`
