# Database Setup for TAMS API

## Complete Database Schema

The TAMS API requires specific table structures in your Supabase database. Here are the complete schemas:

### 1. Import Batches Table (Optional but Recommended)

```sql
-- Create import_batches table for tracking file upload batches
CREATE TABLE IF NOT EXISTS import_batches (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    filename text NOT NULL,
    total_records integer NOT NULL DEFAULT 0,
    processed_records integer DEFAULT 0,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_import_batches_status ON import_batches(status);
CREATE INDEX IF NOT EXISTS idx_import_batches_created_at ON import_batches(created_at);
```

### 2. Anomalies Table (Required)

```sql
-- Table: anomalies
CREATE TABLE IF NOT EXISTS anomalies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    num_equipement text NOT NULL,
    description text,
    service text,
    responsable text,
    status text DEFAULT 'nouvelle' CHECK (status IN ('nouvelle', 'en_cours', 'traite', 'cloture')),
    source_origine text,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    
    -- AI predicted scores (1-5 for individual scores, 3-15 for criticality)
    ai_fiabilite_integrite_score integer CHECK (ai_fiabilite_integrite_score >= 1 AND ai_fiabilite_integrite_score <= 5),
    ai_disponibilite_score integer CHECK (ai_disponibilite_score >= 1 AND ai_disponibilite_score <= 5),
    ai_process_safety_score integer CHECK (ai_process_safety_score >= 1 AND ai_process_safety_score <= 5),
    ai_criticality_level integer CHECK (ai_criticality_level >= 3 AND ai_criticality_level <= 15),
    
    -- Human corrected scores (when AI predictions need adjustment)
    human_fiabilite_integrite_score integer CHECK (human_fiabilite_integrite_score >= 1 AND human_fiabilite_integrite_score <= 5),
    human_disponibilite_score integer CHECK (human_disponibilite_score >= 1 AND human_disponibilite_score <= 5),
    human_process_safety_score integer CHECK (human_process_safety_score >= 1 AND human_process_safety_score <= 5),
    human_criticality_level integer CHECK (human_criticality_level >= 3 AND human_criticality_level <= 15),
    
    -- Final scores (human takes precedence over AI if available)
    final_fiabilite_integrite_score integer GENERATED ALWAYS AS (COALESCE(human_fiabilite_integrite_score, ai_fiabilite_integrite_score)) STORED,
    final_disponibilite_score integer GENERATED ALWAYS AS (COALESCE(human_disponibilite_score, ai_disponibilite_score)) STORED,
    final_process_safety_score integer GENERATED ALWAYS AS (COALESCE(human_process_safety_score, ai_process_safety_score)) STORED,
    final_criticality_level integer GENERATED ALWAYS AS (COALESCE(human_criticality_level, ai_criticality_level)) STORED,
    
    -- Additional fields
    estimated_hours integer,
    priority integer,
    maintenance_window_id uuid,
    import_batch_id uuid REFERENCES import_batches(id)
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_anomalies_num_equipement ON anomalies(num_equipement);
CREATE INDEX IF NOT EXISTS idx_anomalies_status ON anomalies(status);
CREATE INDEX IF NOT EXISTS idx_anomalies_created_at ON anomalies(created_at);
CREATE INDEX IF NOT EXISTS idx_anomalies_ai_criticality ON anomalies(ai_criticality_level);
CREATE INDEX IF NOT EXISTS idx_anomalies_final_criticality ON anomalies(final_criticality_level);
```

## How the Scoring System Works

### 1. **AI Predictions Storage**
When you submit anomalies via the API, the system:
- Generates AI predictions for each metric (1-5 scale)
- Stores them in `ai_*` columns
- Calculates and stores `ai_criticality_level` as the sum of the three scores (3-15)

### 2. **Human Corrections** 
When humans need to adjust AI predictions:
- Update the `human_*` columns with corrected scores
- The `final_*` columns automatically update to use human values

### 3. **Final Scores (Computed Automatically)**
The `final_*` columns use PostgreSQL GENERATED ALWAYS AS:
- Use human scores if available
- Fall back to AI scores if no human corrections exist
- Always represent the "current best" scores

## API Behavior

### What the API Stores
```json
{
  "ai_fiabilite_integrite_score": 4,
  "ai_disponibilite_score": 3,
  "ai_process_safety_score": 5,
  "ai_criticality_level": 12
}
```

### What You Retrieve
```json
{
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

## Issue: Foreign Key Constraint Error

If you're getting the error:
```
Key (import_batch_id)=(xxx) is not present in table "import_batches"
```

This means the `import_batches` table doesn't exist in your Supabase database.

## Quick Fix Options:

### Option 1: Create the import_batches table (Recommended)

Run this SQL in your Supabase SQL Editor:

```sql
-- Create import_batches table for tracking file upload batches
CREATE TABLE IF NOT EXISTS import_batches (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    filename text NOT NULL,
    total_records integer NOT NULL DEFAULT 0,
    processed_records integer DEFAULT 0,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message text,
    created_at timestamp with time zone DEFAULT now(),
    completed_at timestamp with time zone
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_import_batches_status ON import_batches(status);
CREATE INDEX IF NOT EXISTS idx_import_batches_created_at ON import_batches(created_at);
```

### Option 2: Remove the foreign key constraint (If you don't need batch tracking)

If you don't need import batch tracking, you can remove the foreign key constraint:

```sql
-- Remove the foreign key constraint
ALTER TABLE anomalies DROP CONSTRAINT IF EXISTS anomalies_import_batch_id_fkey;

-- Or make the column nullable and set existing values to NULL
UPDATE anomalies SET import_batch_id = NULL WHERE import_batch_id IS NOT NULL;
```

### Option 3: Remove the import_batch_id column entirely

```sql
-- Remove the column entirely if you don't need batch tracking
ALTER TABLE anomalies DROP COLUMN IF EXISTS import_batch_id;
```

## How to Access Supabase SQL Editor:

1. Go to your Supabase dashboard
2. Select your project
3. Go to "SQL Editor" in the sidebar
4. Paste and run one of the SQL commands above

## Current API Behavior:

The API has been updated to handle this gracefully:
- It tries to create import batch records
- If that fails, it retries without the import_batch_id
- This ensures file uploads work even if the table doesn't exist

## Recommended Solution:

Use **Option 1** to create the `import_batches` table. This provides:
- Better tracking of file uploads
- Audit trail of batch operations
- Performance monitoring capabilities

## Files Updated:

- `database.py` - Enhanced error handling for missing import_batches table
- `database_setup.sql` - SQL script for creating the table
- This guide for troubleshooting

Run the SQL from Option 1 and your API should work perfectly!
