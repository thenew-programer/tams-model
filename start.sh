#!/bin/bash

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables (you'll need to replace these with your actual Supabase credentials)
source .env
# Start the FastAPI server
echo "Starting TAMS Anomaly Prediction API..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
