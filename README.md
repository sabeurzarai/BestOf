# BestOf

Turn messy Amazon reviews into clear buying advice.

Upload a review CSV → the app cleans it, labels sentiment, discovers 4–10 product clusters, ranks the best and worst per cluster, and auto-generates a Markdown recommendation article for each category.

## Run it

**Docker (recommended):**

```bash
docker compose up --build
```

- Streamlit UI: http://18.157.233.122:8501
- API docs: http://18.157.233.122:8000/docs

**Locally:**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.main:app --reload   # terminal 1
streamlit run streamlit_app/app.py  # terminal 2
```

## Use it

1. Open http://18.157.233.122:8501
2. Go to **Analytics Pipeline** and drop a CSV from `data/raw/` or upload one
3. Click **Process reviews** — the 7-stage pipeline runs automatically
4. Browse **Categories** — click **View details** on any card to see top products, complaints, and a generated buying guide
5. Articles are generated automatically when you open a category detail

## Pages

| Page | What it does |
|---|---|
| **Home** | Overview dashboard — top products, category cards, review health |
| **Sentiment Analyzer** | Paste any review text and get an instant sentiment label |
| **Categories** | Browse product groups as cards; click View details for the full breakdown |
| **Analytics Pipeline** | 7-stage pipeline with configurable clustering, LLM, and run history |
| **Run History** | Compare silhouette scores, cluster names, and settings across runs |
| **Output Artifacts** | Download clustered CSV, insights JSON, figures, and blog posts |

## Pipeline stages

```
CSV → preprocessing → sentiment → feature extraction → clustering
    → aggregation & naming → FLAN-T5 article generation
```

| Stage | What happens |
|---|---|
| 1 Data input | CSV validated, incompatible schemas skipped |
| 2 Preprocessing | Category normalisation (5-step), text cleaning, deduplication |
| 3 Sentiment | Rating-based: ≤2 negative · 3 neutral · ≥4 positive |
| 4 Feature extraction | MiniLM embeddings / TF-IDF / Keyword taxonomy (configurable) |
| 5 Clustering | KMeans or Agglomerative; auto k by silhouette or forced k |
| 6 Aggregation | TF-IDF cluster naming; score = 0.5·rating + 0.3·pos_ratio + 0.2·norm_count |
| 7 LLM articles | FLAN-T5 generates one Markdown buying guide per category |

The LLM only sees aggregated stats — raw review text is never sent to the model.

## API endpoints

| Endpoint | What it does |
|---|---|
| `GET /health` | Health check |
| `POST /upload-reviews` | Upload a CSV and run the full pipeline |
| `POST /process-raw-data` | Merge every CSV in `data/raw/` and run the pipeline |
| `POST /predict-sentiment` | Sentiment for a single review text |
| `POST /cluster-products` | Cluster a batch of records inline |
| `GET /category-insights` | Return the latest saved insights |
| `POST /generate-summary` | Generate the article for one category |

## Tests

```bash
pytest
```

## Deploy on EC2

**Instance:** Ubuntu 22.04, `t3.medium` (4 GB RAM min), ports 22 / 8000 / 8501 open.

```bash
# 1 — install Docker
sudo apt update && sudo apt install -y docker.io git
sudo usermod -aG docker ubuntu
newgrp docker

# 2 — install Docker Compose (pick one)
sudo apt install -y docker-compose-plugin   # modern plugin  → use: docker compose
# OR if the plugin is unavailable:
sudo apt install -y docker-compose          # legacy v1      → use: docker-compose

# 3 — clone and start (existing repo: just git pull)
git clone https://github.com/sabeurzarai/BestOf
cd BestOf

# 4 — start (use whichever compose command is installed)
docker compose up --build -d       # plugin version
# docker-compose up --build -d     # legacy version

# 5 — visit
# UI  → http://<your-ec2-ip>:8501
# API → http://<your-ec2-ip>:8000/docs
```

**Update an existing deployment:**
```bash
git pull
docker compose up --build -d   # or docker-compose up --build -d
```

Data in `data/`, `outputs/`, and `models/` is mounted as a volume — never overwritten by builds.

Pre-download Hugging Face models into `models/` for air-gapped hosts. Recommend ≥ 4 GB RAM for ML inference.
