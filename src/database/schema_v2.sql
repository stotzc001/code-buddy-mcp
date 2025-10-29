-- Enhanced Schema with Workflows, Tasks, and Skills
-- Version 2.0 - Granular, Token-Efficient Architecture

-- Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================================
-- WORKFLOWS TABLE (High-level overview)
-- ============================================================================
CREATE TABLE workflows (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Overview content (summary only, not full content)
    overview TEXT NOT NULL,  -- High-level summary (~200-500 tokens)
    
    -- Categorization
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    tags TEXT[],
    
    -- Technical metadata
    technologies TEXT[],
    complexity VARCHAR(20) CHECK (complexity IN ('beginner', 'intermediate', 'advanced', 'expert')),
    estimated_time_minutes INTEGER,
    
    -- Use cases and problem
    use_cases TEXT[],
    problem_statement TEXT,
    
    -- Semantic search (for workflow-level queries)
    embedding vector(1024),
    
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

-- ============================================================================
-- TASKS TABLE (Individual executable steps)
-- ============================================================================
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    
    name VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Position in workflow
    step_number INTEGER NOT NULL,  -- Order within the workflow
    
    -- Task content (the actual "how to" - this is what gets loaded)
    content TEXT NOT NULL,  -- Detailed instructions (~300-800 tokens)
    
    -- Quick reference
    prerequisites TEXT[],  -- What's needed before this task
    commands TEXT[],       -- Key commands/code snippets
    verification_checks TEXT[],  -- How to verify completion
    
    -- Time estimation
    estimated_time_minutes INTEGER,
    
    -- Semantic search (for task-level queries)
    embedding vector(1024),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure tasks are ordered within workflow
    UNIQUE(workflow_id, step_number)
);

-- ============================================================================
-- SKILLS TABLE (Reusable patterns and techniques)
-- ============================================================================
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    
    name VARCHAR(255) NOT NULL UNIQUE,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    
    -- Skill content (focused technique/pattern)
    content TEXT NOT NULL,  -- Specific how-to (~200-500 tokens)
    
    -- Categorization
    category VARCHAR(100) NOT NULL,  -- e.g., 'Python', 'Git', 'Docker'
    tags TEXT[],
    
    -- When to use this skill
    use_cases TEXT[],
    problem_solved TEXT,
    
    -- Code/commands
    example_code TEXT,
    example_usage TEXT,
    
    -- Semantic search (for skill-level queries)
    embedding vector(1024),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    author VARCHAR(255),
    
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================================
-- RELATIONSHIPS
-- ============================================================================

-- Task-to-Skill mapping (tasks use skills)
CREATE TABLE task_skills (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    relevance_score DECIMAL(3,2) DEFAULT 1.0,  -- How relevant is this skill to the task
    PRIMARY KEY (task_id, skill_id)
);

-- Workflow relationships (prerequisite, next step, etc.)
CREATE TABLE workflow_relationships (
    id SERIAL PRIMARY KEY,
    source_workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    target_workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (
        relationship_type IN ('prerequisite', 'next_step', 'alternative', 'related', 'complementary')
    ),
    strength DECIMAL(3,2) DEFAULT 1.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_workflow_id, target_workflow_id, relationship_type)
);

-- Task relationships (within and across workflows)
CREATE TABLE task_relationships (
    id SERIAL PRIMARY KEY,
    source_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    target_task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL CHECK (
        relationship_type IN ('prerequisite', 'next_step', 'alternative', 'blocks')
    ),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_task_id, target_task_id, relationship_type)
);

-- ============================================================================
-- USAGE ANALYTICS
-- ============================================================================

CREATE TABLE workflow_usage (
    id SERIAL PRIMARY KEY,
    workflow_id INTEGER NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    query TEXT,
    selected_rank INTEGER,
    was_helpful BOOLEAN,
    feedback TEXT,
    time_spent_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE task_usage (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    query TEXT,
    was_helpful BOOLEAN,
    feedback TEXT,
    time_spent_seconds INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE skill_usage (
    id SERIAL PRIMARY KEY,
    skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
    session_id VARCHAR(255),
    query TEXT,
    was_helpful BOOLEAN,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INDEXES
-- ============================================================================

-- Workflows
CREATE INDEX idx_workflows_category ON workflows(category);
CREATE INDEX idx_workflows_tags ON workflows USING GIN(tags);
CREATE INDEX idx_workflows_technologies ON workflows USING GIN(technologies);
CREATE INDEX idx_workflows_active ON workflows(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_workflows_embedding ON workflows USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Tasks
CREATE INDEX idx_tasks_workflow ON tasks(workflow_id);
CREATE INDEX idx_tasks_step ON tasks(workflow_id, step_number);
CREATE INDEX idx_tasks_embedding ON tasks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Skills
CREATE INDEX idx_skills_category ON skills(category);
CREATE INDEX idx_skills_tags ON skills USING GIN(tags);
CREATE INDEX idx_skills_active ON skills(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_skills_embedding ON skills USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Relationships
CREATE INDEX idx_task_skills_task ON task_skills(task_id);
CREATE INDEX idx_task_skills_skill ON task_skills(skill_id);
CREATE INDEX idx_workflow_rel_source ON workflow_relationships(source_workflow_id);
CREATE INDEX idx_workflow_rel_target ON workflow_relationships(target_workflow_id);
CREATE INDEX idx_task_rel_source ON task_relationships(source_task_id);
CREATE INDEX idx_task_rel_target ON task_relationships(target_task_id);

-- Usage
CREATE INDEX idx_workflow_usage_workflow ON workflow_usage(workflow_id);
CREATE INDEX idx_task_usage_task ON task_usage(task_id);
CREATE INDEX idx_skill_usage_skill ON skill_usage(skill_id);

-- ============================================================================
-- TRIGGERS
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_skills_updated_at BEFORE UPDATE ON skills
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- MATERIALIZED VIEWS
-- ============================================================================

-- Popular workflows
CREATE MATERIALIZED VIEW popular_workflows AS
SELECT 
    w.id,
    w.name,
    w.title,
    w.category,
    COUNT(DISTINCT wu.id) as usage_count,
    AVG(CASE WHEN wu.was_helpful THEN 1.0 ELSE 0.0 END) as helpfulness_ratio,
    MAX(wu.created_at) as last_used
FROM workflows w
LEFT JOIN workflow_usage wu ON w.id = wu.workflow_id
WHERE w.is_active = TRUE
GROUP BY w.id, w.name, w.title, w.category;

CREATE UNIQUE INDEX idx_popular_workflows_id ON popular_workflows(id);

-- Popular tasks
CREATE MATERIALIZED VIEW popular_tasks AS
SELECT 
    t.id,
    t.workflow_id,
    t.name,
    t.title,
    COUNT(DISTINCT tu.id) as usage_count,
    AVG(CASE WHEN tu.was_helpful THEN 1.0 ELSE 0.0 END) as helpfulness_ratio,
    MAX(tu.created_at) as last_used
FROM tasks t
LEFT JOIN task_usage tu ON t.id = tu.id
GROUP BY t.id, t.workflow_id, t.name, t.title;

CREATE UNIQUE INDEX idx_popular_tasks_id ON popular_tasks(id);

-- Popular skills
CREATE MATERIALIZED VIEW popular_skills AS
SELECT 
    s.id,
    s.name,
    s.title,
    s.category,
    COUNT(DISTINCT su.id) as usage_count,
    AVG(CASE WHEN su.was_helpful THEN 1.0 ELSE 0.0 END) as helpfulness_ratio,
    MAX(su.created_at) as last_used
FROM skills s
LEFT JOIN skill_usage su ON s.id = su.skill_id
WHERE s.is_active = TRUE
GROUP BY s.id, s.name, s.title, s.category;

CREATE UNIQUE INDEX idx_popular_skills_id ON popular_skills(id);

-- ============================================================================
-- SEED DATA - Categories
-- ============================================================================

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    description TEXT,
    display_order INTEGER DEFAULT 0,
    icon VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO categories (name, description, display_order, icon) VALUES
    ('Development', 'Software development workflows', 1, '💻'),
    ('DevOps', 'CI/CD and infrastructure', 2, '🚀'),
    ('Data Engineering', 'Data pipelines and processing', 3, '📊'),
    ('Architecture', 'System design patterns', 4, '🏗️'),
    ('Security', 'Security and secrets management', 5, '🔒'),
    ('Testing', 'Testing strategies and practices', 6, '🧪'),
    ('Quality Assurance', 'Code quality and review', 7, '✅'),
    ('Frontend Development', 'UI/UX development', 8, '🎨'),
    ('Machine Learning', 'ML workflows and deployment', 9, '🤖'),
    ('Project Management', 'Planning and execution', 10, '📋'),
    ('Discovery', 'Research and exploration', 11, '🔍')
ON CONFLICT (name) DO NOTHING;
