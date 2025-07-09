# Database Setup for TAMS API

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
