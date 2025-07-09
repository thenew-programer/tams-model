from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List, Dict, Any
import uuid
from datetime import datetime
import os

from models import AnomalyInput, AnomalyResponse, BatchPredictionResponse
from predictor import predictor
from database import supabase_client
from file_processor import FileProcessor

app = FastAPI(
    title="TAMS Anomaly Prediction API",
    description="""
    ## TAMS Anomaly Prediction API
    
    A comprehensive machine learning API for predicting anomaly criticality scores and managing anomaly data.
    
    ### Features:
    * **Single Anomaly Prediction**: Predict scores for individual anomalies
    * **Batch Prediction**: Process multiple anomalies at once
    * **File Upload**: Support for CSV and Excel file processing
    * **Database Integration**: Automatic storage in Supabase
    * **AI Scoring**: Predicts Fiabilité Intégrité, Disponibilité, and Process Safety scores
    
    ### Input Data:
    The API requires equipment number, system name, and description for predictions.
    
    ### Scoring System:
    * Each metric is scored from 1-5 (1=low risk, 5=high risk)
    * Criticality level is the sum of all three scores (3-15)
    """,
    version="1.0.0",
    contact={
        "name": "TAMS Team",
        "email": "support@tams.com",
    },
    license_info={
        "name": "MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI schema
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/api-docs", tags=["Documentation"])
async def get_api_docs():
    """
    Get custom API documentation page
    
    Returns a custom HTML documentation page with examples and usage instructions.
    """
    static_file = os.path.join(os.path.dirname(__file__), "static", "docs.html")
    if os.path.exists(static_file):
        return FileResponse(static_file, media_type="text/html")
    else:
        return {"message": "Documentation page not found. Visit /docs for Swagger UI."}

@app.get("/", tags=["Health"])
async def root():
    """
    Health check endpoint
    
    Returns the API status and version information.
    """
    return {"message": "TAMS Anomaly Prediction API is running", "version": "1.0.0"}

@app.post("/predict/single", response_model=AnomalyResponse, tags=["Predictions"])
async def predict_single_anomaly(anomaly: AnomalyInput):
    """
    Predict scores for a single anomaly
    
    This endpoint processes a single anomaly and returns AI-predicted scores for:
    - **Fiabilité Intégrité** (Reliability/Integrity): 1-5 scale
    - **Disponibilité** (Availability): 1-5 scale  
    - **Process Safety**: 1-5 scale
    - **Criticité** (Criticality): Sum of above scores (3-15)
    
    The prediction is automatically stored in the database with status 'nouvelle'.
    
    ### Required Fields:
    - `num_equipement`: Equipment identification number
    - `systeme`: System name (e.g., "Hydraulic", "Electrical")
    - `description`: Detailed description of the anomaly
    
    ### Optional Fields:
    - `date_detection`: Date when anomaly was detected
    - `description_equipement`: Equipment description
    - `section_proprietaire`: Owner section
    """
    try:
        # Validate input data
        anomaly_data = FileProcessor.validate_anomaly_data(anomaly.dict())
        
        # Make prediction
        predictions = predictor.predict_single(anomaly_data)
        
        # Prepare data for database
        db_data = FileProcessor.prepare_for_database(anomaly_data, predictions)
        
        # Store in database
        stored_anomaly = await supabase_client.create_anomaly(db_data)
        
        if not stored_anomaly:
            raise HTTPException(status_code=500, detail="Failed to store anomaly in database")
        
        # Return response
        return AnomalyResponse(
            id=stored_anomaly['id'],
            num_equipement=stored_anomaly['num_equipement'],
            description=stored_anomaly['description'],
            service=stored_anomaly['service'],
            status=stored_anomaly['status'],
            ai_fiabilite_integrite_score=stored_anomaly['ai_fiabilite_integrite_score'],
            ai_disponibilite_score=stored_anomaly['ai_disponibilite_score'],
            ai_process_safety_score=stored_anomaly['ai_process_safety_score'],
            ai_criticality_level=stored_anomaly['ai_criticality_level'],
            created_at=datetime.fromisoformat(stored_anomaly['created_at'].replace('Z', '+00:00'))
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/predict/batch", response_model=List[AnomalyResponse], tags=["Predictions"])
async def predict_batch_anomalies(anomalies: List[AnomalyInput]):
    """
    Predict scores for multiple anomalies in batch
    
    Process multiple anomalies at once for efficient bulk predictions.
    All anomalies are processed and stored with the same import batch ID.
    
    ### Input:
    Array of anomaly objects, each containing the same fields as single prediction.
    
    ### Output:
    Array of prediction results with database IDs and timestamps.
    
    ### Use Cases:
    - Bulk processing of maintenance reports
    - Historical data analysis
    - System-wide anomaly assessment
    """
    try:
        if not anomalies:
            raise HTTPException(status_code=400, detail="No anomalies provided")
        
        # Validate input data
        validated_data = []
        for anomaly in anomalies:
            validated_data.append(FileProcessor.validate_anomaly_data(anomaly.dict()))
        
        # Make predictions
        predictions_list = predictor.predict_batch(validated_data)
        
        # Prepare data for database
        db_data_list = []
        for anomaly_data, predictions in zip(validated_data, predictions_list):
            db_data = FileProcessor.prepare_for_database(anomaly_data, predictions)
            db_data_list.append(db_data)
        
        # Create batch ID
        batch_id = str(uuid.uuid4())
        
        # Store in database
        stored_anomalies = await supabase_client.create_anomalies_batch(db_data_list, batch_id)
        
        if not stored_anomalies:
            raise HTTPException(status_code=500, detail="Failed to store anomalies in database")
        
        # Return response
        response_list = []
        for stored_anomaly in stored_anomalies:
            response_list.append(AnomalyResponse(
                id=stored_anomaly['id'],
                num_equipement=stored_anomaly['num_equipement'],
                description=stored_anomaly['description'],
                service=stored_anomaly['service'],
                status=stored_anomaly['status'],
                ai_fiabilite_integrite_score=stored_anomaly['ai_fiabilite_integrite_score'],
                ai_disponibilite_score=stored_anomaly['ai_disponibilite_score'],
                ai_process_safety_score=stored_anomaly['ai_process_safety_score'],
                ai_criticality_level=stored_anomaly['ai_criticality_level'],
                created_at=datetime.fromisoformat(stored_anomaly['created_at'].replace('Z', '+00:00'))
            ))
        
        return response_list
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/predict/file/csv", response_model=BatchPredictionResponse, tags=["File Upload"])
async def predict_from_csv_file(file: UploadFile = File(...)):
    """
    Process CSV file with multiple anomalies
    
    Upload a CSV file containing multiple anomaly records for batch processing.
    
    ### CSV Format:
    The CSV file should contain these columns:
    - `Num_equipement` (required)
    - `Systeme` (required) 
    - `Description` (required)
    - `Date de détéction de l'anomalie` (optional)
    - `Description de l'équipement` (optional)
    - `Section propriétaire` (optional)
    
    ### Features:
    - Automatic data validation and cleaning
    - Batch processing for efficiency
    - Import tracking with unique batch ID
    - Error handling for malformed data
    
    ### Response:
    Returns all processed predictions with batch statistics.
    """
    try:
        if not file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Process file
        anomalies_data = await FileProcessor.process_csv_file(file)
        
        if not anomalies_data:
            raise HTTPException(status_code=400, detail="No valid anomaly data found in file")
        
        # Make predictions
        predictions_list = predictor.predict_batch(anomalies_data)
        
        # Prepare data for database
        db_data_list = []
        for anomaly_data, predictions in zip(anomalies_data, predictions_list):
            db_data = FileProcessor.prepare_for_database(anomaly_data, predictions)
            db_data_list.append(db_data)
        
        # Create batch ID
        batch_id = await supabase_client.create_import_batch(file.filename, len(anomalies_data))
        
        # Store in database
        stored_anomalies = await supabase_client.create_anomalies_batch(db_data_list, batch_id)
        
        if not stored_anomalies:
            raise HTTPException(status_code=500, detail="Failed to store anomalies in database")
        
        # Prepare response
        response_list = []
        for stored_anomaly in stored_anomalies:
            response_list.append(AnomalyResponse(
                id=stored_anomaly['id'],
                num_equipement=stored_anomaly['num_equipement'],
                description=stored_anomaly['description'],
                service=stored_anomaly['service'],
                status=stored_anomaly['status'],
                ai_fiabilite_integrite_score=stored_anomaly['ai_fiabilite_integrite_score'],
                ai_disponibilite_score=stored_anomaly['ai_disponibilite_score'],
                ai_process_safety_score=stored_anomaly['ai_process_safety_score'],
                ai_criticality_level=stored_anomaly['ai_criticality_level'],
                created_at=datetime.fromisoformat(stored_anomaly['created_at'].replace('Z', '+00:00'))
            ))
        
        return BatchPredictionResponse(
            predictions=response_list,
            total_processed=len(stored_anomalies),
            import_batch_id=batch_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV file: {str(e)}")

@app.post("/predict/file/excel", response_model=BatchPredictionResponse, tags=["File Upload"])
async def predict_from_excel_file(file: UploadFile = File(...)):
    """
    Process Excel file with multiple anomalies
    
    Upload an Excel file (.xlsx or .xls) containing multiple anomaly records.
    
    ### Excel Format:
    Same column structure as CSV format. Supports both .xlsx and .xls files.
    
    ### Features:
    - Supports multiple Excel formats
    - Automatic data type detection
    - Sheet processing (uses first sheet)
    - Header row detection
    """
    try:
        if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
        
        # Process file
        anomalies_data = await FileProcessor.process_excel_file(file)
        
        if not anomalies_data:
            raise HTTPException(status_code=400, detail="No valid anomaly data found in file")
        
        # Make predictions
        predictions_list = predictor.predict_batch(anomalies_data)
        
        # Prepare data for database
        db_data_list = []
        for anomaly_data, predictions in zip(anomalies_data, predictions_list):
            db_data = FileProcessor.prepare_for_database(anomaly_data, predictions)
            db_data_list.append(db_data)
        
        # Create batch ID
        batch_id = await supabase_client.create_import_batch(file.filename, len(anomalies_data))
        
        # Store in database
        stored_anomalies = await supabase_client.create_anomalies_batch(db_data_list, batch_id)
        
        if not stored_anomalies:
            raise HTTPException(status_code=500, detail="Failed to store anomalies in database")
        
        # Prepare response
        response_list = []
        for stored_anomaly in stored_anomalies:
            response_list.append(AnomalyResponse(
                id=stored_anomaly['id'],
                num_equipement=stored_anomaly['num_equipement'],
                description=stored_anomaly['description'],
                service=stored_anomaly['service'],
                status=stored_anomaly['status'],
                ai_fiabilite_integrite_score=stored_anomaly['ai_fiabilite_integrite_score'],
                ai_disponibilite_score=stored_anomaly['ai_disponibilite_score'],
                ai_process_safety_score=stored_anomaly['ai_process_safety_score'],
                ai_criticality_level=stored_anomaly['ai_criticality_level'],
                created_at=datetime.fromisoformat(stored_anomaly['created_at'].replace('Z', '+00:00'))
            ))
        
        return BatchPredictionResponse(
            predictions=response_list,
            total_processed=len(stored_anomalies),
            import_batch_id=batch_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing Excel file: {str(e)}")

@app.get("/anomalies/{anomaly_id}", response_model=AnomalyResponse, tags=["Data Retrieval"])
async def get_anomaly(anomaly_id: str):
    """
    Get a specific anomaly by ID
    
    Retrieve detailed information about a specific anomaly using its unique identifier.
    
    ### Parameters:
    - `anomaly_id`: UUID of the anomaly record
    
    ### Returns:
    Complete anomaly record with all AI predictions and metadata.
    """
    try:
        anomaly = await supabase_client.get_anomaly_by_id(anomaly_id)
        
        if not anomaly:
            raise HTTPException(status_code=404, detail="Anomaly not found")
        
        return AnomalyResponse(
            id=anomaly['id'],
            num_equipement=anomaly['num_equipement'],
            description=anomaly['description'],
            service=anomaly['service'],
            status=anomaly['status'],
            ai_fiabilite_integrite_score=anomaly['ai_fiabilite_integrite_score'],
            ai_disponibilite_score=anomaly['ai_disponibilite_score'],
            ai_process_safety_score=anomaly['ai_process_safety_score'],
            ai_criticality_level=anomaly['ai_criticality_level'],
            created_at=datetime.fromisoformat(anomaly['created_at'].replace('Z', '+00:00'))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching anomaly: {str(e)}")

@app.get("/anomalies", response_model=List[AnomalyResponse], tags=["Data Retrieval"])
async def get_anomalies(limit: int = 100, offset: int = 0):
    """
    Get a list of anomalies with pagination
    
    Retrieve a paginated list of anomaly records from the database.
    
    ### Parameters:
    - `limit`: Maximum number of records to return (default: 100, max: 1000)
    - `offset`: Number of records to skip for pagination (default: 0)
    
    ### Pagination:
    Use `offset` and `limit` to implement pagination:
    - Page 1: offset=0, limit=100
    - Page 2: offset=100, limit=100
    - Page 3: offset=200, limit=100
    
    ### Returns:
    Array of anomaly records ordered by creation date (newest first).
    """
    try:
        anomalies = await supabase_client.get_anomalies(limit=limit, offset=offset)
        
        response_list = []
        for anomaly in anomalies:
            response_list.append(AnomalyResponse(
                id=anomaly['id'],
                num_equipement=anomaly['num_equipement'],
                description=anomaly['description'],
                service=anomaly['service'],
                status=anomaly['status'],
                ai_fiabilite_integrite_score=anomaly['ai_fiabilite_integrite_score'],
                ai_disponibilite_score=anomaly['ai_disponibilite_score'],
                ai_process_safety_score=anomaly['ai_process_safety_score'],
                ai_criticality_level=anomaly['ai_criticality_level'],
                created_at=datetime.fromisoformat(anomaly['created_at'].replace('Z', '+00:00'))
            ))
        
        return response_list
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching anomalies: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
