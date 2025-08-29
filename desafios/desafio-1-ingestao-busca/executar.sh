#!/bin/bash

echo "🚀 Iniciando Sistema RAG..."

echo "1️⃣ Subindo banco de dados..."
docker compose up -d

echo "2️⃣ Executando ingestão do PDF..."
python src/ingest.py

echo "3️⃣ Iniciando chat..."
python src/chat.py
