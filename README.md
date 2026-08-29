<div align="center">
<img width="3567" height="1073" alt="image" src="https://github.com/user-attachments/assets/899ab4eb-5a47-432b-9502-3a784d61a2f2" />
</div>

# GTFS Realtime Streaming Pipeline

A production-grade, Kappa-style real-time transit streaming platform. The system continuously ingests GTFS-Realtime events, processes them using event-time-aware Spark Structured Streaming, stores durable Bronze and Silver data in a MinIO-backed Delta Lakehouse, republishes derived events to Kafka, and serves them through independent real-time (Redis/FastAPI) and historical (DuckDB/Chainlit) serving layers.

---

## **Architecture Overview**

```text
GTFS Realtime Feeds (Vehicle Positions / Trip Updates / Service Alerts)
                            │
                  ingestion/fetcher.py
                            │
                  ingestion/producer.py (Kafka Producer #1)
                            │
                    raw.* Kafka Topics
                            │
                 streaming/consumer.py (Kafka Consumer #1)
                            │
                  streaming/bronze.py ──► Bronze Delta Lake (MinIO)
                            │
                  streaming/silver.py ──► Silver Delta Lake (MinIO)
                            │
             streaming/realtime_stream.py (Spark Kafka Producer #2)
                            │
                   result.* Kafka Topics
                            │
       ┌────────────────────┴────────────────────┐
       ▼                                         ▼
serving/realtime/consumer.py            serving/batch/consumer.py
(Kafka Consumer #2)                     (Kafka Consumer #3)
       │                                         │
  redis_store.py                            DuckDB Storage
       │                                         │
  FastAPI Backend                        Chainlit AI Assistant
       │                                 (Groq Llama-3.3-70B)
Streamlit Dashboard

```

---

## **Key Features**

* **Kappa Streaming Architecture:** Strict single directional data path: GTFS Feed $\rightarrow$ Raw Kafka $\rightarrow$ Spark Bronze/Silver $\rightarrow$ Result Kafka $\rightarrow$ Dual Serving Paths.
* **Event-Time Processing & Watermarking:** Native handling of out-of-order events, late-arriving data, and stateful windowed aggregations.
* **Independent Dual Serving Path:**
* **Real-Time:** Sub-second latency state updates in Redis served via FastAPI & Streamlit.
* **Batch & Analytics:** Fast OLAP historical processing via DuckDB with a natural-language AI SQL interface powered by Chainlit & Groq LLMs.


* **Production Observability & Monitoring:** Full Prometheus and Grafana integration monitoring Kafka consumer lag, Spark throughput, and FastAPI metrics.

---

## **Repository Structure**

```text
gtfs-streaming-pipeline/
├── ingestion/               # Feed fetching and raw Kafka production
│   ├── fetcher.py
│   ├── producer.py
│   └── config.py
├── streaming/               # Spark Structured Streaming pipeline
│   ├── consumer.py          # Kafka Consumer #1
│   ├── bronze.py            # Raw Kafka -> Bronze Delta
│   ├── silver.py            # Validation, deduplication & enrichment
│   └── realtime_stream.py   # Silver -> result.* Kafka topics
├── serving/
│   ├── realtime/            # Consumer #2: Redis + FastAPI + Streamlit
│   │   ├── consumer.py
│   │   ├── redis_store.py
│   │   ├── main.py
│   │   └── dashboard.py
│   └── batch/               # Consumer #3: DuckDB + Chainlit AI
│       ├── consumer.py
│       ├── processor.py
│       └── app.py
├── infrastructure/          # Docker Compose & Prometheus/Grafana configs
│   ├── docker-compose.yml
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana_datasource.yml
├── tests/                   # Pytest suite (ingestion, streaming, serving)
├── docs/                    # Architectural runbooks & recovery guides
├── Makefile
└── requirements.txt

```

---

## **Prerequisites**

* **Docker & Docker Compose**
* **Python 3.12+**
* **Groq API Key** (for Chainlit natural language SQL generation)

---

## **Quickstart Guide**

### **1. Clone & Set Up Environment**

```bash
git clone https://github.com/abhirajadhikary06/gtfs-streaming-pipeline.git
cd gtfs-streaming-pipeline

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### **2. Launch Infrastructure**

Start Kafka, Redis, MinIO, Prometheus, and Grafana containers:

```bash
make up
# Or: docker compose up -d

```

### **3. Run Pipeline Components**

Execute components in separate terminal windows (with active `venv`):

* **Ingestion Producer:**
```bash
python -m ingestion.producer

```


* **Spark Streaming Engine:**
```bash
python -m streaming.runner

```


* **Real-Time Serving Path (FastAPI + Streamlit):**
```bash
python -m serving.realtime.consumer
uvicorn serving.realtime.main:app --port 8000
streamlit run serving/realtime/dashboard.py

```


* **Batch Analytics Path (DuckDB + Chainlit AI):**
```bash
export GROQ_API_KEY="your-groq-api-key"
python -m serving.batch.consumer
chainlit run serving/batch/app.py --port 8001

```



---

## **Testing & Verification**

Run the automated `pytest` suite across ingestion, streaming transformations, and serving layers:

```bash
python -m pytest tests/ -v

```

---

## **Service Endpoints & Monitoring Dashboards**

| Component | Endpoint | Description |
| --- | --- | --- |
| **Real-Time API** | `http://localhost:8000` | FastAPI low-latency serving endpoints |
| **Real-Time Dashboard** | `http://localhost:8501` | Streamlit live bus tracking dashboard |
| **Batch AI Assistant** | `http://localhost:8001` | Chainlit DuckDB natural-language SQL interface |
| **Prometheus** | `http://localhost:9090` | System metrics & target health status |
| **Grafana** | `http://localhost:3000` | Observability dashboards (`admin`/`admin`) |
| **MinIO Console** | `http://localhost:9001` | Delta Lake storage browser |
