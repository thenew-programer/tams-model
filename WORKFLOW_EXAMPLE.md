# TAMS API - Complete Workflow Example

This document demonstrates the complete workflow of storing anomalies and retrieving data with AI predictions.

## 1. Store Anomaly (AI Predictions Generated Automatically)

### API Call
```javascript
const anomalyData = {
    num_equipement: "EQ001",
    systeme: "Hydraulic",
    description: "Pressure drop detected in main valve"
};

const response = await fetch('http://localhost:8000/store/single', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(anomalyData)
});

const result = await response.json();
```

### Response (Storage Confirmation)
```json
{
    "success": true,
    "message": "Anomaly successfully stored",
    "anomaly_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

## 2. Retrieve Stored Data (With AI Predictions)

### API Call
```javascript
const response = await fetch(`http://localhost:8000/anomalies/${result.anomaly_id}`);
const anomaly = await response.json();
```

### Response (Complete Data with AI Predictions)
```json
{
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "num_equipement": "EQ001",
    "description": "Pressure drop detected in main valve",
    "service": "Hydraulic",
    "status": "nouvelle",
    "source_origine": "api",
    "created_at": "2025-07-09T14:30:00Z",
    "updated_at": "2025-07-09T14:30:00Z",
    
    // AI Generated Predictions (Automatically calculated and stored)
    "ai_fiabilite_integrite_score": 4,
    "ai_disponibilite_score": 3,
    "ai_process_safety_score": 5,
    "ai_criticality_level": 12,
    
    // Human Corrections (null initially, set by experts later)
    "human_fiabilite_integrite_score": null,
    "human_disponibilite_score": null,
    "human_process_safety_score": null,
    "human_criticality_level": null,
    
    // Final Scores (Computed automatically - uses human if available, otherwise AI)
    "final_fiabilite_integrite_score": 4,
    "final_disponibilite_score": 3,
    "final_process_safety_score": 5,
    "final_criticality_level": 12,
    
    // Additional fields
    "responsable": null,
    "estimated_hours": null,
    "priority": null,
    "maintenance_window_id": null,
    "import_batch_id": null
}
```

## 3. Frontend Usage Examples

### React Component for Displaying Anomaly with Scores
```jsx
import React from 'react';

const AnomalyCard = ({ anomaly }) => {
    const getScoreColor = (score) => {
        if (score <= 2) return '#28a745'; // Green
        if (score <= 3) return '#ffc107'; // Yellow
        return '#dc3545'; // Red
    };

    const getCriticalityColor = (level) => {
        if (level <= 6) return '#28a745';   // Low (3-6)
        if (level <= 10) return '#ffc107';  // Medium (7-10)
        return '#dc3545';                   // High (11-15)
    };

    return (
        <div className="anomaly-card">
            <h3>Equipment: {anomaly.num_equipement}</h3>
            <p><strong>Description:</strong> {anomaly.description}</p>
            <p><strong>System:</strong> {anomaly.service}</p>
            <p><strong>Status:</strong> {anomaly.status}</p>
            
            <div className="scores-section">
                <h4>AI Predictions</h4>
                <div className="score-grid">
                    <div className="score-item">
                        <span>Fiabilité Intégrité:</span>
                        <span 
                            className="score-badge"
                            style={{ backgroundColor: getScoreColor(anomaly.ai_fiabilite_integrite_score) }}
                        >
                            {anomaly.ai_fiabilite_integrite_score}/5
                        </span>
                    </div>
                    
                    <div className="score-item">
                        <span>Disponibilité:</span>
                        <span 
                            className="score-badge"
                            style={{ backgroundColor: getScoreColor(anomaly.ai_disponibilite_score) }}
                        >
                            {anomaly.ai_disponibilite_score}/5
                        </span>
                    </div>
                    
                    <div className="score-item">
                        <span>Process Safety:</span>
                        <span 
                            className="score-badge"
                            style={{ backgroundColor: getScoreColor(anomaly.ai_process_safety_score) }}
                        >
                            {anomaly.ai_process_safety_score}/5
                        </span>
                    </div>
                    
                    <div className="score-item">
                        <span>Criticality Level:</span>
                        <span 
                            className="criticality-badge"
                            style={{ backgroundColor: getCriticalityColor(anomaly.final_criticality_level) }}
                        >
                            {anomaly.final_criticality_level}/15
                        </span>
                    </div>
                </div>
                
                {/* Show if human corrections exist */}
                {anomaly.human_fiabilite_integrite_score && (
                    <div className="human-corrections">
                        <h5>Expert Corrections Applied</h5>
                        <p><em>Using expert-corrected values for final scores</em></p>
                    </div>
                )}
            </div>
            
            <div className="metadata">
                <small>Created: {new Date(anomaly.created_at).toLocaleString()}</small>
            </div>
        </div>
    );
};

export default AnomalyCard;
```

### Dashboard Summary Component
```jsx
import React, { useState, useEffect } from 'react';

const AnomaliesDashboard = () => {
    const [anomalies, setAnomalies] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchAnomalies();
    }, []);

    const fetchAnomalies = async () => {
        try {
            const response = await fetch('http://localhost:8000/anomalies?limit=50');
            const data = await response.json();
            setAnomalies(data);
        } catch (error) {
            console.error('Error fetching anomalies:', error);
        } finally {
            setLoading(false);
        }
    };

    const getStatistics = () => {
        const total = anomalies.length;
        const highCriticality = anomalies.filter(a => a.final_criticality_level >= 11).length;
        const mediumCriticality = anomalies.filter(a => a.final_criticality_level >= 7 && a.final_criticality_level <= 10).length;
        const lowCriticality = anomalies.filter(a => a.final_criticality_level <= 6).length;
        const withHumanCorrections = anomalies.filter(a => a.human_fiabilite_integrite_score !== null).length;

        return { total, highCriticality, mediumCriticality, lowCriticality, withHumanCorrections };
    };

    if (loading) return <div>Loading...</div>;

    const stats = getStatistics();

    return (
        <div className="dashboard">
            <h2>Anomalies Dashboard</h2>
            
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>{stats.total}</h3>
                    <p>Total Anomalies</p>
                </div>
                
                <div className="stat-card high">
                    <h3>{stats.highCriticality}</h3>
                    <p>High Criticality (11-15)</p>
                </div>
                
                <div className="stat-card medium">
                    <h3>{stats.mediumCriticality}</h3>
                    <p>Medium Criticality (7-10)</p>
                </div>
                
                <div className="stat-card low">
                    <h3>{stats.lowCriticality}</h3>
                    <p>Low Criticality (3-6)</p>
                </div>
                
                <div className="stat-card">
                    <h3>{stats.withHumanCorrections}</h3>
                    <p>Expert Reviewed</p>
                </div>
            </div>
            
            <div className="anomalies-list">
                {anomalies.map(anomaly => (
                    <AnomalyCard key={anomaly.id} anomaly={anomaly} />
                ))}
            </div>
        </div>
    );
};

export default AnomaliesDashboard;
```

## 4. Database Update Examples (For Expert Corrections)

### Add Human Corrections
```sql
-- Expert reviews AI prediction and provides corrections
UPDATE anomalies 
SET 
    human_fiabilite_integrite_score = 3,  -- Expert corrects from AI's 4 to 3
    human_disponibilite_score = 4,        -- Expert corrects from AI's 3 to 4
    human_process_safety_score = 5,       -- Expert agrees with AI's 5
    human_criticality_level = 12,         -- Sum: 3+4+5=12
    updated_at = now()
WHERE id = '123e4567-e89b-12d3-a456-426614174000';

-- The final_* columns will automatically update due to GENERATED ALWAYS AS
```

### Query Final vs AI Scores
```sql
-- Compare AI predictions vs final scores (after human corrections)
SELECT 
    num_equipement,
    description,
    
    -- AI Predictions
    ai_fiabilite_integrite_score,
    ai_disponibilite_score, 
    ai_process_safety_score,
    ai_criticality_level,
    
    -- Final Scores (AI + Human corrections)
    final_fiabilite_integrite_score,
    final_disponibilite_score,
    final_process_safety_score,
    final_criticality_level,
    
    -- Check if human corrections exist
    CASE 
        WHEN human_fiabilite_integrite_score IS NOT NULL THEN 'Expert Reviewed'
        ELSE 'AI Only'
    END as review_status
    
FROM anomalies 
ORDER BY final_criticality_level DESC;
```

## 5. Key Benefits of This Architecture

### For AI Development
- **AI predictions are always preserved** in `ai_*` columns
- **Easy to compare AI vs human expert decisions**
- **Training data collection** for model improvement

### For Operations Teams  
- **Final scores always represent best available assessment**
- **Clear visibility** into which anomalies have been expert-reviewed
- **Confidence levels** based on AI vs human decisions

### For Frontend Development
- **Simple storage workflow** - just submit data, get confirmation
- **Rich retrieval** - get all scores and metadata when needed
- **Flexible display** - show AI, human, or final scores as appropriate

## 6. Complete CSS for Example Components

```css
.anomaly-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 16px;
    margin: 16px 0;
    background: white;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.scores-section {
    margin: 16px 0;
    padding: 16px;
    background: #f8f9fa;
    border-radius: 6px;
}

.score-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 12px;
    margin: 12px 0;
}

.score-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: white;
    border-radius: 4px;
}

.score-badge, .criticality-badge {
    padding: 4px 8px;
    color: white;
    border-radius: 12px;
    font-weight: bold;
    font-size: 12px;
}

.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 16px;
    margin: 20px 0;
}

.stat-card {
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    background: #f8f9fa;
    border: 1px solid #dee2e6;
}

.stat-card.high { border-color: #dc3545; background: #f8d7da; }
.stat-card.medium { border-color: #ffc107; background: #fff3cd; }
.stat-card.low { border-color: #28a745; background: #d4edda; }

.human-corrections {
    margin-top: 12px;
    padding: 8px;
    background: #cce5ff;
    border-radius: 4px;
    border-left: 4px solid #007bff;
}
```

This workflow ensures that:
1. **AI predictions are generated and stored automatically** when anomalies are submitted
2. **Storage operations return simple confirmations** for easy frontend handling  
3. **Rich data with all score types** is available when retrieving anomalies
4. **Expert corrections can be added later** without losing original AI predictions
5. **Final scores always represent the best available assessment**
