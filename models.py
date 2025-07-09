from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class AnomalyInput(BaseModel):
    """Input model for anomaly prediction requests"""
    num_equipement: str = Field(..., description="Equipment identification number", example="EQ001")
    systeme: str = Field(..., description="System name (e.g., Hydraulic, Electrical)", example="Hydraulic")
    description: str = Field(..., description="Detailed description of the anomaly", example="Pressure drop detected in main valve")
    date_detection: Optional[str] = Field(None, description="Date when anomaly was detected (YYYY-MM-DD)", example="2025-01-15")
    description_equipement: Optional[str] = Field(None, description="Equipment description", example="Main hydraulic valve")
    section_proprietaire: Optional[str] = Field(None, description="Owner section", example="Maintenance")

    class Config:
        schema_extra = {
            "example": {
                "num_equipement": "EQ001",
                "systeme": "Hydraulic",
                "description": "Pressure drop detected in main valve",
                "date_detection": "2025-01-15",
                "description_equipement": "Main hydraulic valve",
                "section_proprietaire": "Maintenance"
            }
        }

class AnomalyPrediction(BaseModel):
    num_equipement: str
    systeme: str
    description: str
    ai_fiabilite_integrite_score: int = Field(..., ge=1, le=5)
    ai_disponibilite_score: int = Field(..., ge=1, le=5)
    ai_process_safety_score: int = Field(..., ge=1, le=5)
    ai_criticality_level: int = Field(..., ge=1, le=15)

class AnomalyResponse(BaseModel):
    """Response model for anomaly predictions with database information"""
    id: str = Field(..., description="Unique anomaly identifier (UUID)")
    num_equipement: str = Field(..., description="Equipment identification number")
    description: Optional[str] = Field(None, description="Anomaly description")
    service: Optional[str] = Field(None, description="Service/System name")
    status: str = Field(default="nouvelle", description="Anomaly status")
    ai_fiabilite_integrite_score: int = Field(..., ge=1, le=5, description="AI-predicted Reliability/Integrity score (1-5)")
    ai_disponibilite_score: int = Field(..., ge=1, le=5, description="AI-predicted Availability score (1-5)")
    ai_process_safety_score: int = Field(..., ge=1, le=5, description="AI-predicted Process Safety score (1-5)")
    ai_criticality_level: int = Field(..., ge=3, le=15, description="AI-predicted Criticality level (sum of above scores)")
    created_at: datetime = Field(..., description="Record creation timestamp")

    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "num_equipement": "EQ001",
                "description": "Pressure drop detected in main valve",
                "service": "Hydraulic",
                "status": "nouvelle",
                "ai_fiabilite_integrite_score": 4,
                "ai_disponibilite_score": 3,
                "ai_process_safety_score": 5,
                "ai_criticality_level": 12,
                "created_at": "2025-01-15T10:30:00Z"
            }
        }

class BatchPredictionResponse(BaseModel):
    """Response model for batch prediction operations"""
    predictions: List[AnomalyResponse] = Field(..., description="List of processed anomaly predictions")
    total_processed: int = Field(..., description="Total number of records processed")
    import_batch_id: str = Field(..., description="Unique identifier for this import batch")

    class Config:
        schema_extra = {
            "example": {
                "predictions": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "num_equipement": "EQ001",
                        "description": "Pressure drop detected",
                        "service": "Hydraulic",
                        "status": "nouvelle",
                        "ai_fiabilite_integrite_score": 4,
                        "ai_disponibilite_score": 3,
                        "ai_process_safety_score": 5,
                        "ai_criticality_level": 12,
                        "created_at": "2025-01-15T10:30:00Z"
                    }
                ],
                "total_processed": 1,
                "import_batch_id": "batch-123e4567-e89b-12d3-a456-426614174000"
            }
        }
