-- Manual SQL to create references table
-- Copy this SQL and run it directly in your PostgreSQL database

-- Check if table exists first
DROP TABLE IF EXISTS references_temp;

-- Create the references table
CREATE TABLE references (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id UUID NOT NULL REFERENCES candidates(id),
    name VARCHAR(500) NOT NULL,
    company VARCHAR(500),
    position VARCHAR(500),
    email VARCHAR(255),
    phone VARCHAR(100),
    relationship VARCHAR(200),
    display_order INTEGER DEFAULT 0
);

-- Create index for performance
CREATE INDEX idx_references_candidate_id ON references(candidate_id);

-- Verify table creation
SELECT 'References table created successfully!' as status;
