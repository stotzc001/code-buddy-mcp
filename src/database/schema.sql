-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Workflows table with rich metadata
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Content
    content TEXT NOT NULL,
    content_hash VARCHAR(64), -- SHA256 for change detection
    
    -- Categorization
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    tags TEXT[], -- Array of tags
    
    -- Technical metadata
    technologies TEXT[], -- e.g., ['Python', 'FastAPI', 'PostgreSQL']
    complexity VARCHAR(20) CHECK (complexity IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_time_minutes INTEGER,
    
    -- Use cases
    use_cases TEXT[], -- Specific scenarios this workflow applies to
    problem_statement TEXT, -- What problem does this solve?
    
    -- Prerequisites and relationships
    prerequisites INTEGER[], -- Array of workflow IDs that should be completed first
    
    -- Semantic search
    embedding vector(1024), -- Cohere: 1024, Ollama: 768, OpenAI: 1536
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    version INTEGER DEFAULT 1,
    author VARCHAR(255),
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_deprecated BOOLEAN DEFAULT FALSE,
    deprecated_reason TEXT,
    replaced_by_id INTEGER REFERENCES workflows(id)
);

-- Workflow relationships for graph traversal
CREATE TABLE workflow_relationships (
    id SERIAL PRIMARY KEY,
    source_workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    target_workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (
        relationship_type IN ('prerequisite', 'successor', 'alternative', 'related', 'extends')
    ),
    strength DECIMAL(3,2) DEFAULT 1.0, -- 0.0 to 1.0, how strong is the relationship
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_workflow_id, target_workflow_id, relationship_type)
);

-- Usage analytics for intelligent ranking
CREATE TABLE workflow_usage (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    user_id VARCHAR(255), -- Optional: track per-user usage
    session_id VARCHAR(255),
    
    -- Context
    query TEXT, -- What was the user searching for?
    selected_rank INTEGER, -- What position was this in search results?
    
    -- Outcome
    was_helpful BOOLEAN,
    feedback TEXT,
    time_spent_seconds INTEGER,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories for browsing
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(50), -- emoji or icon name
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_workflows_category ON workflows(category);
CREATE INDEX idx_workflows_tags ON workflows USING GIN(tags);
CREATE INDEX idx_workflows_technologies ON workflows USING GIN(technologies);
CREATE INDEX idx_workflows_use_cases ON workflows USING GIN(use_cases);
CREATE INDEX idx_workflows_complexity ON workflows(complexity);
CREATE INDEX idx_workflows_active ON workflows(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_workflows_created ON workflows(created_at DESC);

-- Vector similarity index (IVFFlat for large datasets)
CREATE INDEX idx_workflows_embedding ON workflows USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100); -- Adjust based on dataset size

-- Relationship indexes
CREATE INDEX idx_relationships_source ON workflow_relationships(source_workflow_id);
CREATE INDEX idx_relationships_target ON workflow_relationships(target_workflow_id);
CREATE INDEX idx_relationships_type ON workflow_relationships(relationship_type);

-- Usage analytics indexes
CREATE INDEX idx_usage_workflow ON workflow_usage(workflow_id);
CREATE INDEX idx_usage_created ON workflow_usage(created_at DESC);
CREATE INDEX idx_usage_helpful ON workflow_usage(was_helpful) WHERE was_helpful IS NOT NULL;

-- Full-text search index for content
CREATE INDEX idx_workflows_fulltext ON workflows USING gin(to_tsvector('english', title || ' ' || description || ' ' || content));

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Materialized view for popular workflows
CREATE MATERIALIZED VIEW popular_workflows AS
SELECT 
    w.id,
    w.name,
    w.title,
    w.category,
    COUNT(wu.id) as usage_count,
    AVG(CASE WHEN wu.was_helpful THEN 1 ELSE 0 END) as helpfulness_ratio,
    MAX(wu.created_at) as last_used
FROM workflows w
LEFT JOIN workflow_usage wu ON w.id = wu.workflow_id
WHERE w.is_active = TRUE
GROUP BY w.id, w.name, w.title, w.category;

CREATE UNIQUE INDEX idx_popular_workflows_id ON popular_workflows(id);

-- Refresh the materialized view (call periodically)
-- REFRESH MATERIALIZED VIEW CONCURRENTLY popular_workflows;

-- Seed some common categories
INSERT INTO categories (name, description, display_order, icon) VALUES
    ('Development', 'Software development workflows', 1, '💻'),
    ('Data Engineering', 'Data pipelines and processing', 2, '📊'),
    ('DevOps', 'CI/CD and infrastructure', 3, '🚀'),
    ('Architecture', 'System design patterns', 4, '🏗️'),
    ('Project Management', 'Planning and execution', 5, '📋'),
    ('Discovery', 'Research and exploration', 6, '🔍')
ON CONFLICT (name) DO NOTHING;
