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

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_import_batches_status ON import_batches(status);
CREATE INDEX IF NOT EXISTS idx_import_batches_created_at ON import_batches(created_at);

-- Ensure the foreign key exists on anomalies table (optional - only if you want strict referential integrity)
-- If this fails, it means the column doesn't exist or the constraint already exists
-- ALTER TABLE anomalies ADD CONSTRAINT anomalies_import_batch_id_fkey 
--   FOREIGN KEY (import_batch_id) REFERENCES import_batches(id) ON DELETE SET NULL;
