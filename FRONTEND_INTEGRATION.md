# Frontend Integration Guide

## TAMS Anomaly Storage API - Frontend Integration

This guide provides complete examples for integrating the TAMS Anomaly Storage API into your frontend application.

## Quick Start

### Base URL
```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

### API Endpoints Overview

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/store/single` | Store a single anomaly |
| `POST` | `/store/batch` | Store multiple anomalies |
| `POST` | `/store/file/csv` | Upload and store CSV file |
| `POST` | `/store/file/excel` | Upload and store Excel file |

**Note**: Data retrieval is handled directly through your Supabase client, not through these API endpoints.

## Frontend Integration Examples

### 1. Single Anomaly Storage

#### JavaScript (Fetch API)
```javascript
async function storeAnomaly(anomalyData) {
    try {
        const response = await fetch('http://localhost:8000/store/single', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                num_equipement: anomalyData.equipmentNumber,
                systeme: anomalyData.system,
                description: anomalyData.description,
                date_detection: anomalyData.detectionDate,
                description_equipement: anomalyData.equipmentDescription,
                section_proprietaire: anomalyData.ownerSection
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Anomaly stored successfully:', result);
        return result;
    } catch (error) {
        console.error('Error storing anomaly:', error);
        throw error;
    }
}

// Usage example
const anomalyData = {
    equipmentNumber: "EQ001",
    system: "Hydraulic",
    description: "Pressure drop detected in main valve",
    detectionDate: "2025-01-15",
    equipmentDescription: "Main hydraulic valve",
    ownerSection: "Maintenance"
};

storeAnomaly(anomalyData)
    .then(result => {
        // Handle success
        alert(`Anomaly stored with ID: ${result.anomaly_id}`);
    })
    .catch(error => {
        // Handle error
        alert('Failed to store anomaly');
    });
```

#### React Component Example
```jsx
import React, { useState } from 'react';

const AnomalyForm = () => {
    const [formData, setFormData] = useState({
        equipmentNumber: '',
        system: '',
        description: '',
        detectionDate: '',
        equipmentDescription: '',
        ownerSection: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [message, setMessage] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        setMessage('');

        try {
            const response = await fetch('http://localhost:8000/store/single', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    num_equipement: formData.equipmentNumber,
                    systeme: formData.system,
                    description: formData.description,
                    date_detection: formData.detectionDate,
                    description_equipement: formData.equipmentDescription,
                    section_proprietaire: formData.ownerSection
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            setMessage(`Success: ${result.message}`);
            
            // Reset form
            setFormData({
                equipmentNumber: '',
                system: '',
                description: '',
                detectionDate: '',
                equipmentDescription: '',
                ownerSection: ''
            });
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Equipment Number (Required):</label>
                <input
                    type="text"
                    name="equipmentNumber"
                    value={formData.equipmentNumber}
                    onChange={handleChange}
                    required
                />
            </div>
            
            <div>
                <label>System (Required):</label>
                <select
                    name="system"
                    value={formData.system}
                    onChange={handleChange}
                    required
                >
                    <option value="">Select System</option>
                    <option value="Hydraulic">Hydraulic</option>
                    <option value="Electrical">Electrical</option>
                    <option value="Mechanical">Mechanical</option>
                    <option value="Pneumatic">Pneumatic</option>
                </select>
            </div>
            
            <div>
                <label>Description (Required):</label>
                <textarea
                    name="description"
                    value={formData.description}
                    onChange={handleChange}
                    required
                />
            </div>
            
            <div>
                <label>Detection Date:</label>
                <input
                    type="date"
                    name="detectionDate"
                    value={formData.detectionDate}
                    onChange={handleChange}
                />
            </div>
            
            <div>
                <label>Equipment Description:</label>
                <input
                    type="text"
                    name="equipmentDescription"
                    value={formData.equipmentDescription}
                    onChange={handleChange}
                />
            </div>
            
            <div>
                <label>Owner Section:</label>
                <input
                    type="text"
                    name="ownerSection"
                    value={formData.ownerSection}
                    onChange={handleChange}
                />
            </div>
            
            <button type="submit" disabled={isSubmitting}>
                {isSubmitting ? 'Storing...' : 'Store Anomaly'}
            </button>
            
            {message && <p>{message}</p>}
        </form>
    );
};

export default AnomalyForm;
```

### 2. Batch Storage

#### JavaScript Example
```javascript
async function storeBatchAnomalies(anomaliesArray) {
    try {
        const response = await fetch('http://localhost:8000/store/batch', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(anomaliesArray.map(anomaly => ({
                num_equipement: anomaly.equipmentNumber,
                systeme: anomaly.system,
                description: anomaly.description,
                date_detection: anomaly.detectionDate,
                description_equipement: anomaly.equipmentDescription,
                section_proprietaire: anomaly.ownerSection
            })))
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Batch stored successfully:', result);
        return result;
    } catch (error) {
        console.error('Error storing batch:', error);
        throw error;
    }
}

// Usage example
const anomaliesData = [
    {
        equipmentNumber: "EQ001",
        system: "Hydraulic",
        description: "Pressure drop detected",
        detectionDate: "2025-01-15"
    },
    {
        equipmentNumber: "EQ002",
        system: "Electrical",
        description: "Voltage fluctuation",
        detectionDate: "2025-01-15"
    }
];

storeBatchAnomalies(anomaliesData)
    .then(result => {
        alert(`${result.total_stored} anomalies stored successfully`);
    })
    .catch(error => {
        alert('Failed to store batch');
    });
```

### 3. File Upload

#### JavaScript File Upload
```javascript
async function uploadCSVFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await fetch('http://localhost:8000/store/file/csv', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('File uploaded successfully:', result);
        return result;
    } catch (error) {
        console.error('Error uploading file:', error);
        throw error;
    }
}

// Usage with file input
document.getElementById('fileInput').addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        uploadCSVFile(file)
            .then(result => {
                alert(`${result.total_stored} anomalies stored from file`);
            })
            .catch(error => {
                alert('Failed to upload file');
            });
    }
});
```

#### React File Upload Component
```jsx
import React, { useState } from 'react';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) return;

        setUploading(true);
        setMessage('');

        const formData = new FormData();
        formData.append('file', file);

        try {
            const endpoint = file.name.endsWith('.csv') 
                ? '/store/file/csv' 
                : '/store/file/excel';

            const response = await fetch(`http://localhost:8000${endpoint}`, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            setMessage(`Success: ${result.message}`);
            setFile(null);
        } catch (error) {
            setMessage(`Error: ${error.message}`);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={handleFileChange}
            />
            <button 
                onClick={handleUpload} 
                disabled={!file || uploading}
            >
                {uploading ? 'Uploading...' : 'Upload File'}
            </button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default FileUpload;
```

## Data Retrieval

**Important**: Data retrieval is handled directly through your Supabase client in your frontend application, not through the TAMS API endpoints.

### Supabase Client Example
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'your-supabase-url'
const supabaseKey = 'your-supabase-anon-key'
const supabase = createClient(supabaseUrl, supabaseKey)

// Fetch anomalies directly from Supabase
async function fetchAnomalies() {
    const { data, error } = await supabase
        .from('anomalies')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(50)
    
    if (error) {
        console.error('Error fetching anomalies:', error)
        return []
    }
    
    return data
}

// Get specific anomaly
async function getAnomaly(anomalyId) {
    const { data, error } = await supabase
        .from('anomalies')
        .select('*')
        .eq('id', anomalyId)
        .single()
    
    if (error) {
        console.error('Error fetching anomaly:', error)
        return null
    }
    
    return data
}
```

## Error Handling

### Common Error Responses
```javascript
// 400 Bad Request
{
    "detail": "No anomalies provided"
}

// 422 Validation Error
{
    "detail": [
        {
            "loc": ["body", "num_equipement"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}

// 500 Internal Server Error
{
    "detail": "Internal server error: Database connection failed"
}
```

### Error Handling Best Practices
```javascript
async function handleApiCall(apiFunction) {
    try {
        const result = await apiFunction();
        return { success: true, data: result };
    } catch (error) {
        if (error.response) {
            // API returned an error response
            return { 
                success: false, 
                error: error.response.data.detail || 'API Error' 
            };
        } else if (error.request) {
            // Network error
            return { 
                success: false, 
                error: 'Network error - please check your connection' 
            };
        } else {
            // Other error
            return { 
                success: false, 
                error: error.message || 'Unknown error' 
            };
        }
    }
}
```

## Response Formats

### Single Storage Response
```json
{
    "success": true,
    "message": "Anomaly successfully stored",
    "anomaly_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Batch Storage Response
```json
{
    "success": true,
    "message": "5 anomalies successfully stored",
    "total_stored": 5,
    "import_batch_id": "batch-123e4567-e89b-12d3-a456-426614174000"
}
```

### Anomaly Data Response (When Retrieving Data)
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "num_equipement": "EQ001",
    "description": "Pressure drop detected in main valve",
    "service": "Hydraulic",
    "status": "nouvelle",
    "created_at": "2025-01-15T10:30:00Z",
    
    "ai_fiabilite_integrite_score": 4,
    "ai_disponibilite_score": 3,
    "ai_process_safety_score": 5,
    "ai_criticality_level": 12,
    
    "human_fiabilite_integrite_score": null,
    "human_disponibilite_score": null,
    "human_process_safety_score": null,
    "human_criticality_level": null,
    
    "final_fiabilite_integrite_score": 4,
    "final_disponibilite_score": 3,
    "final_process_safety_score": 5,
    "final_criticality_level": 12
}
```

**Note about scores:**
- `ai_*` scores: Original AI predictions (always preserved)
- `human_*` scores: Manual corrections by experts (null if not corrected)
- `final_*` scores: Best available scores (human takes precedence over AI)

## Testing

### Test with curl
```bash
# Store single anomaly
curl -X POST http://localhost:8000/store/single \
  -H "Content-Type: application/json" \
  -d '{
    "num_equipement": "EQ001",
    "systeme": "Hydraulic",
    "description": "Test anomaly"
  }'

# Upload CSV file
curl -X POST http://localhost:8000/store/file/csv \
  -F "file=@anomalies.csv"

# Note: Data retrieval is done directly through Supabase client
```

## Production Considerations

1. **CORS Configuration**: Update CORS settings for production domains
2. **Authentication**: Implement API key or OAuth authentication
3. **Rate Limiting**: Add rate limiting to prevent abuse
4. **Validation**: Client-side validation for better UX
5. **Error Logging**: Implement comprehensive error logging
6. **Caching**: Consider caching for frequently accessed data

## API Documentation

- **Swagger UI**: Visit `/docs` for interactive API documentation
- **ReDoc**: Visit `/redoc` for alternative documentation
- **OpenAPI Schema**: Available at `/openapi.json`

## Support

For technical support or questions about the API integration, contact the TAMS team at support@tams.com.
