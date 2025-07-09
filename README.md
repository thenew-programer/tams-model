# TAMS Anomaly Prediction API

A FastAPI backend service that uses machine learning to predict anomaly criticality scores and stores them in a Supabase database.

## Features

- **Single Anomaly Prediction**: Predict scores for individual anomalies
- **Batch Prediction**: Predict scores for multiple anomalies at once
- **File Upload Support**: Process CSV and Excel files containing multiple anomalies
- **Supabase Integration**: Automatically store predictions in the database
- **RESTful API**: Clean and documented API endpoints

## Setup

### 1. Environment Setup

First, make sure you have Python 3.8+ installed. Then install the dependencies:

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Create a `.env` file in the root directory with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_ROLE_KEY=your_supabase_service_role_key_here
```

**Note:** The API uses `SUPABASE_ROLE_KEY` (service role key) to bypass Row Level Security (RLS) authentication rules for server-side operations. This provides full database access required for the anomaly prediction service.

### 3. Model Requirements

Ensure your trained model file `tams-prediction-model.pkl` is in the `ml_models/` directory.

### 4. Start the Server

```bash
# Make the start script executable
chmod +x start.sh

# Run the server
./start.sh
```

Or manually:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- `GET /` - Check if the API is running

### Predictions
- `POST /predict/single` - Predict scores for a single anomaly
- `POST /predict/batch` - Predict scores for multiple anomalies
- `POST /predict/file/csv` - Upload and process a CSV file
- `POST /predict/file/excel` - Upload and process an Excel file

### Data Retrieval
- `GET /anomalies` - Get list of anomalies (with pagination)
- `GET /anomalies/{anomaly_id}` - Get specific anomaly by ID

## Input Data Format

The API expects the following fields for each anomaly:

**Required fields:**
- `num_equipement`: Equipment number (string)
- `systeme`: System name (string)  
- `description`: Anomaly description (string)

**Optional fields:**
- `date_detection`: Detection date
- `description_equipement`: Equipment description
- `section_proprietaire`: Owner section

## File Upload Format

For CSV/Excel files, use these column headers:
- `Num_equipement`
- `Systeme`
- `Description`
- `Date de détéction de l'anomalie` (optional)
- `Description de l'équipement` (optional)
- `Section propriétaire` (optional)

## Response Format

The API returns predictions with scores from 1-5 for each metric:
- `ai_fiabilite_integrite_score`: Reliability/Integrity score
- `ai_disponibilite_score`: Availability score
- `ai_process_safety_score`: Process Safety score
- `ai_criticality_level`: Overall criticality (sum of the three scores)

## Example Usage

### Single Prediction

```bash
curl -X POST "http://localhost:8000/predict/single" \
  -H "Content-Type: application/json" \
  -d '{
    "num_equipement": "EQ001",
    "systeme": "Hydraulic",
    "description": "Pressure drop detected in main valve"
  }'
```

### File Upload

```bash
curl -X POST "http://localhost:8000/predict/file/csv" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@anomalies.csv"
```

## API Documentation

Once the server is running, visit:
- `http://localhost:8000/docs` - Interactive API documentation (Swagger UI)
- `http://localhost:8000/redoc` - Alternative API documentation

## Database Schema

The API stores predictions in the `anomalies` table with the following AI prediction fields:
- `ai_fiabilite_integrite_score` (1-5)
- `ai_disponibilite_score` (1-5)  
- `ai_process_safety_score` (1-5)
- `ai_criticality_level` (1-15, sum of the three scores)

## Error Handling

The API includes comprehensive error handling for:
- Invalid input data
- File processing errors
- Model prediction failures
- Database connection issues

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
