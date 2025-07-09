# TAMS API - Summary & Key Features

## 🎯 What This API Does

The TAMS Anomaly Storage API is designed for **storing anomaly data with automatic AI predictions**. It focuses on:

1. **Simple Storage Operations** - Submit data, get confirmation
2. **Automatic AI Scoring** - Predictions generated and stored transparently  
3. **Expert Review Workflow** - Human corrections don't overwrite AI predictions
4. **Frontend-Friendly** - Easy integration with React, Vue, Angular, etc.

## 🏗️ Architecture Overview

```
Frontend Application
        ↓
   Store Anomaly (Simple JSON)
        ↓
   TAMS API (AI Processing)
        ↓
   Supabase Database (AI + Human + Final Scores)
        ↓
   Retrieve Data (Rich Response with All Scores)
```

## 📊 Database Score Structure

| Column Type | Purpose | Example |
|-------------|---------|---------|
| `ai_*_score` | Original AI predictions (preserved forever) | `ai_fiabilite_integrite_score: 4` |
| `human_*_score` | Expert corrections (optional) | `human_fiabilite_integrite_score: 3` |
| `final_*_score` | Best available score (computed automatically) | `final_fiabilite_integrite_score: 3` |

**Key Benefit**: You can track AI accuracy vs expert opinions and always have the current best assessment.

## 🚀 Storage Workflow

### 1. Submit Anomaly (Minimal Data Required)
```javascript
POST /store/single
{
    "num_equipement": "EQ001",
    "systeme": "Hydraulic", 
    "description": "Pressure drop detected"
}
```

### 2. Get Confirmation (Simple Response)
```javascript
{
    "success": true,
    "message": "Anomaly successfully stored",
    "anomaly_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 3. Retrieve When Needed (Rich Data)
```javascript
GET /anomalies/123e4567-e89b-12d3-a456-426614174000
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "num_equipement": "EQ001",
    "description": "Pressure drop detected",
    "ai_fiabilite_integrite_score": 4,      // AI prediction
    "ai_disponibilite_score": 3,            // AI prediction  
    "ai_process_safety_score": 5,           // AI prediction
    "ai_criticality_level": 12,             // AI calculated sum
    "final_fiabilite_integrite_score": 4,   // Current best (AI until expert corrects)
    "final_disponibilite_score": 3,         // Current best
    "final_process_safety_score": 5,        // Current best
    "final_criticality_level": 12           // Current best
}
```

## 🎨 Frontend Integration Benefits

### ✅ Simple Storage
- **One API call** to store data
- **Instant confirmation** of success/failure
- **No complex response parsing** needed

### ✅ Rich Retrieval  
- **All score types available** when displaying data
- **Easy differentiation** between AI and expert assessments
- **Automatic final score calculation**

### ✅ Flexible Display Options
```javascript
// Show only final scores (simplest)
`Criticality: ${anomaly.final_criticality_level}/15`

// Show AI predictions with confidence indicator
`AI Prediction: ${anomaly.ai_criticality_level}/15 ${anomaly.human_criticality_level ? '(Expert Reviewed)' : '(AI Only)'}`

// Show comparison between AI and expert
if (anomaly.human_criticality_level) {
    `AI: ${anomaly.ai_criticality_level} → Expert: ${anomaly.human_criticality_level}`
}
```

## 🔧 Technical Features

### Storage Endpoints
- **`/store/single`** - Store one anomaly
- **`/store/batch`** - Store multiple anomalies  
- **`/store/file/csv`** - Upload CSV file
- **`/store/file/excel`** - Upload Excel file

### Retrieval Endpoints
- **`/anomalies`** - List anomalies (paginated)
- **`/anomalies/{id}`** - Get specific anomaly

### AI Prediction System
- **Automatic scoring** on storage
- **Fallback logic** if ML model unavailable
- **Rule-based predictions** for reliability

### Database Features
- **PostgreSQL GENERATED columns** for automatic final score calculation
- **Constraint validation** ensures score ranges (1-5 for individual, 3-15 for total)
- **Audit trail** preserves both AI and human assessments

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `README.md` | Main documentation and setup |
| `FRONTEND_INTEGRATION.md` | Complete integration examples |
| `DATABASE_SETUP.md` | Database schema and setup |
| `WORKFLOW_EXAMPLE.md` | End-to-end workflow examples |
| `test_storage_api.py` | API testing script |

## 🐳 Deployment

### Docker (Recommended)
```bash
docker-compose up --build
# API available at http://localhost:8000
```

### Local Development  
```bash
pip install -r requirements.txt
python main.py
# API available at http://localhost:8000
```

## 🔗 API Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc  
- **Custom Examples**: http://localhost:8000/api-docs

## 💡 Use Cases

### Manufacturing
- **Equipment anomaly reporting**
- **Predictive maintenance scoring**
- **Expert validation workflow**

### Operations Teams
- **Quick anomaly submission via mobile/web**
- **Prioritization based on AI criticality scores**
- **Expert review and correction process**

### Data Science Teams
- **AI model performance tracking**
- **Training data collection** (AI vs expert decisions)
- **Model improvement feedback loop**

## 🎉 Key Benefits Summary

1. **Developer-Friendly**: Simple REST API with clear responses
2. **AI-Powered**: Automatic criticality scoring saves manual effort  
3. **Expert-Enhanced**: Human corrections improve over time
4. **Audit-Ready**: Full trail of AI predictions and human adjustments
5. **Production-Ready**: Docker deployment, comprehensive error handling
6. **Documentation-Rich**: Multiple guides and examples for easy integration

**Perfect for teams that want AI-assisted anomaly management with human oversight capabilities!**
