-- AI Content Agency Database Schema
-- Simplified schema for learning LangGraph features
-- To be executed in Supabase SQL Editor

-- Enable UUID extension for automatic UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========================================
-- Main State Table
-- ========================================
-- Stores the current state of each content creation project
CREATE TABLE IF NOT EXISTS project_states (
    project_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    thread_id TEXT UNIQUE NOT NULL,
    topic TEXT NOT NULL,
    mode TEXT DEFAULT 'standard' CHECK (mode IN ('standard', 'quick')),
    status TEXT DEFAULT 'created',
    state_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE project_states IS 'Main table storing the current state of each content creation project';
COMMENT ON COLUMN project_states.project_id IS 'Unique identifier for the project';
COMMENT ON COLUMN project_states.thread_id IS 'LangGraph thread ID for checkpointing';
COMMENT ON COLUMN project_states.topic IS 'The blog topic requested by the user';
COMMENT ON COLUMN project_states.mode IS 'Workflow mode: standard (full) or quick (simplified)';
COMMENT ON COLUMN project_states.status IS 'Current workflow status';
COMMENT ON COLUMN project_states.state_data IS 'Complete state stored as JSON';

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_project_states_status ON project_states(status);
CREATE INDEX IF NOT EXISTS idx_project_states_mode ON project_states(mode);
CREATE INDEX IF NOT EXISTS idx_project_states_created_at ON project_states(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_project_states_updated_at ON project_states(updated_at DESC);

-- ========================================
-- State History Table (Time Travel)
-- ========================================
-- Stores checkpoints of state for time travel functionality
CREATE TABLE IF NOT EXISTS state_history (
    checkpoint_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES project_states(project_id) ON DELETE CASCADE,
    checkpoint_name TEXT NOT NULL,
    state_snapshot JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE state_history IS 'Stores state checkpoints for time travel functionality';
COMMENT ON COLUMN state_history.checkpoint_id IS 'Unique identifier for the checkpoint';
COMMENT ON COLUMN state_history.project_id IS 'Reference to the parent project';
COMMENT ON COLUMN state_history.checkpoint_name IS 'Human-readable name for the checkpoint';
COMMENT ON COLUMN state_history.state_snapshot IS 'Complete state at the time of checkpoint';

-- Create index for efficient checkpoint queries
CREATE INDEX IF NOT EXISTS idx_state_history_project_id ON state_history(project_id, created_at DESC);

-- ========================================
-- Human Feedback Table
-- ========================================
-- Stores human feedback for human-in-the-loop functionality
CREATE TABLE IF NOT EXISTS human_feedback (
    feedback_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES project_states(project_id) ON DELETE CASCADE,
    feedback TEXT,
    action TEXT CHECK (action IN ('approve', 'revise', 'reject')),
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add comments for documentation
COMMENT ON TABLE human_feedback IS 'Stores human feedback for human-in-the-loop functionality';
COMMENT ON COLUMN human_feedback.feedback_id IS 'Unique identifier for the feedback';
COMMENT ON COLUMN human_feedback.project_id IS 'Reference to the parent project';
COMMENT ON COLUMN human_feedback.feedback IS 'The feedback text from the human reviewer';
COMMENT ON COLUMN human_feedback.action IS 'Action taken: approve, revise, or reject';
COMMENT ON COLUMN human_feedback.approved IS 'Whether the content was approved';

-- Create index for feedback queries
CREATE INDEX IF NOT EXISTS idx_human_feedback_project_id ON human_feedback(project_id, created_at DESC);

-- ========================================
-- Triggers for automatic timestamp updates
-- ========================================

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically update updated_at on project_states
CREATE TRIGGER update_project_states_updated_at
    BEFORE UPDATE ON project_states
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ========================================
-- Helper Views (Optional but useful)
-- ========================================

-- View for active projects
CREATE OR REPLACE VIEW active_projects AS
SELECT 
    project_id,
    topic,
    mode,
    status,
    created_at,
    updated_at
FROM project_states
WHERE status NOT IN ('completed', 'failed')
ORDER BY updated_at DESC;

-- View for project statistics
CREATE OR REPLACE VIEW project_stats AS
SELECT 
    mode,
    status,
    COUNT(*) as count,
    DATE(created_at) as date
FROM project_states
GROUP BY mode, status, DATE(created_at)
ORDER BY date DESC;

-- ========================================
-- Row Level Security (RLS) - Optional
-- ========================================
-- Uncomment if you want to enable RLS for additional security

-- ALTER TABLE project_states ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE state_history ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE human_feedback ENABLE ROW LEVEL SECURITY;

-- ========================================
-- Sample Test Query
-- ========================================
-- Run this to verify tables were created successfully:
/*
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
    AND table_name IN ('project_states', 'state_history', 'human_feedback')
ORDER BY table_name;
*/