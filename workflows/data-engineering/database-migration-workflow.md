---
title: Database Migration Strategy
description: Comprehensive workflow for planning and executing database schema migrations safely in production environments
category: Data Engineering
subcategory: Database Management
tags: [database, migration, schema, postgres, alembic]
technologies: [PostgreSQL, Alembic, Python, SQL]
complexity: advanced
estimated_time_minutes: 60
use_cases: [Schema changes in production, Adding new tables, Modifying existing columns, Database versioning]
problem_statement: Making schema changes to production databases requires careful planning to avoid downtime, data loss, and application errors
author: Code Buddy Team
---

# Database Migration Strategy Workflow

## Overview

This workflow provides a systematic approach to planning, testing, and executing database schema migrations with minimal risk and downtime. Learn how to use Alembic for version control and implement zero-downtime deployment strategies.

## Prerequisites

- PostgreSQL database (or similar RDBMS)
- Python 3.8+ with SQLAlchemy
- Alembic: `pip install alembic sqlalchemy psycopg2-binary`
- Access to staging environment
- Database backup strategy in place

## Step 1: Initialize Alembic

Set up version control for your database schema:

```bash
# Initialize Alembic
alembic init alembic

# This creates:
# alembic/
#   ├── versions/          # Migration scripts
#   ├── env.py             # Migration environment
#   └── script.py.mako     # Template for new migrations
# alembic.ini              # Configuration
```

Configure `alembic.ini`:

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/mydb

# Or use environment variable
# sqlalchemy.url = driver://user:pass@localhost/dbname
```

## Step 2: Plan the Migration

### Assess Impact

Create a migration plan document:

```markdown
## Migration: Add User Preferences Table

### Goal
Store user preferences for notification settings

### Changes
1. Create new table: user_preferences
2. Add foreign key to users table
3. Create indexes on user_id and preference_type

### Risk Assessment
- **Downtime Required**: No
- **Data Migration**: No existing data
- **Rollback Plan**: Drop table if needed
- **Dependencies**: None

### Testing Plan
1. Test in local environment
2. Deploy to staging
3. Verify with sample data
4. Performance test with production data volume
```

### Types of Migrations

**Low Risk** (Safe to deploy):
- Adding new tables
- Adding nullable columns
- Creating indexes (with CONCURRENTLY)
- Adding new constraints (if data already valid)

**Medium Risk** (Requires testing):
- Adding non-nullable columns (with default)
- Modifying column types (if compatible)
- Renaming columns/tables (requires app changes)

**High Risk** (Multi-step deployment):
- Dropping columns/tables
- Changing column types (incompatible)
- Modifying foreign key constraints
- Large data transformations

## Step 3: Create Migration Script

Generate migration:

```bash
alembic revision -m "add_user_preferences_table"
```

Edit the generated file in `alembic/versions/`:

```python
"""add_user_preferences_table

Revision ID: 1234567890ab
Revises: abcdef123456
Create Date: 2025-01-15 10:30:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '1234567890ab'
down_revision = 'abcdef123456'
branch_labels = None
depends_on = None


def upgrade():
    """Apply migration."""
    # Create table
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('preference_type', sa.String(50), nullable=False),
        sa.Column('preference_value', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id', 'preference_type', name='uq_user_pref')
    )
    
    # Create indexes
    op.create_index(
        'idx_user_preferences_user_id',
        'user_preferences',
        ['user_id']
    )
    
    op.create_index(
        'idx_user_preferences_type',
        'user_preferences',
        ['preference_type']
    )


def downgrade():
    """Rollback migration."""
    op.drop_index('idx_user_preferences_type')
    op.drop_index('idx_user_preferences_user_id')
    op.drop_table('user_preferences')
```

## Step 4: Test Migration Locally

```bash
# Check current version
alembic current

# Preview SQL (dry run)
alembic upgrade head --sql

# Apply migration
alembic upgrade head

# Verify
psql -d mydb -c "SELECT * FROM user_preferences LIMIT 1;"

# Test rollback
alembic downgrade -1

# Re-apply
alembic upgrade head
```

## Step 5: Zero-Downtime Deployment Strategy

For production deployments, use a multi-phase approach:

### Phase 1: Add New Column (Nullable)

```python
def upgrade():
    # Add nullable column first
    op.add_column('users', 
        sa.Column('email_verified', sa.Boolean(), nullable=True))
```

Deploy application that:
- ✅ Can handle NULL values
- ✅ Writes to new column for new records
- ✅ Still works without the column

### Phase 2: Backfill Data

```python
def upgrade():
    # Backfill existing records
    op.execute("""
        UPDATE users 
        SET email_verified = FALSE 
        WHERE email_verified IS NULL
    """)
```

### Phase 3: Make Column Non-Nullable

```python
def upgrade():
    # Now safe to add constraint
    op.alter_column('users', 'email_verified',
                    existing_type=sa.Boolean(),
                    nullable=False)
```

## Step 6: Complex Migration Patterns

### Renaming Column (Zero-Downtime)

**Phase 1**: Add new column, dual-write
```python
def upgrade():
    op.add_column('users', sa.Column('full_name', sa.String(200)))
    
    # Copy existing data
    op.execute("UPDATE users SET full_name = name")
```

**Phase 2**: Update application to use new column

**Phase 3**: Remove old column
```python
def upgrade():
    op.drop_column('users', 'name')
```

### Splitting Table

**Phase 1**: Create new table, dual-write
```python
def upgrade():
    op.create_table('user_profiles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), unique=True),
        sa.Column('bio', sa.Text()),
        sa.Column('avatar_url', sa.String(500))
    )
    
    # Copy data
    op.execute("""
        INSERT INTO user_profiles (user_id, bio, avatar_url)
        SELECT id, bio, avatar_url FROM users
    """)
```

**Phase 2**: Update application to use new table

**Phase 3**: Remove old columns
```python
def upgrade():
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')
```

### Large Data Migration

For millions of records, batch the updates:

```python
def upgrade():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    engine = create_engine(op.get_bind().engine.url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    BATCH_SIZE = 10000
    total = session.execute("SELECT COUNT(*) FROM users").scalar()
    
    for offset in range(0, total, BATCH_SIZE):
        session.execute(f"""
            UPDATE users 
            SET email_verified = FALSE 
            WHERE id IN (
                SELECT id FROM users 
                WHERE email_verified IS NULL 
                LIMIT {BATCH_SIZE}
            )
        """)
        session.commit()
        print(f"Processed {min(offset + BATCH_SIZE, total)}/{total}")
    
    session.close()
```

## Step 7: Deploy to Staging

```bash
# Deploy migration to staging
ENVIRONMENT=staging alembic upgrade head

# Run automated tests
pytest tests/integration/ -v

# Manual verification
- Create test records
- Verify constraints
- Check indexes with EXPLAIN
- Load test with production-like data
```

## Step 8: Production Deployment

### Pre-Deployment Checklist

- [ ] Migration tested in staging
- [ ] Rollback plan documented
- [ ] Database backup taken
- [ ] Team notified of deployment
- [ ] Monitoring alerts configured
- [ ] Performance impact assessed

### Deployment Steps

```bash
# 1. Take database backup
pg_dump -Fc mydb > backup_$(date +%Y%m%d_%H%M%S).dump

# 2. Preview migration
alembic upgrade head --sql > migration.sql
# Review migration.sql

# 3. Apply migration
alembic upgrade head

# 4. Verify
psql -d mydb -c "\d+ user_preferences"

# 5. Check application logs
tail -f /var/log/app/app.log

# 6. Monitor performance
# Check slow query log, connection pool, etc.
```

### Rollback Procedure

If issues arise:

```bash
# Rollback to previous version
alembic downgrade -1

# Or specific revision
alembic downgrade <revision_id>

# Restart application
systemctl restart myapp
```

## Step 9: Post-Deployment

### Verify Migration

```sql
-- Check table exists
\dt user_preferences

-- Verify indexes
\di user_preferences*

-- Check constraints
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'user_preferences';

-- Verify data
SELECT COUNT(*) FROM user_preferences;
```

### Monitor Performance

```sql
-- Check index usage
SELECT 
    schemaname, tablename, indexname, idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE tablename = 'user_preferences';

-- Slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
WHERE query LIKE '%user_preferences%'
ORDER BY mean_exec_time DESC
LIMIT 10;
```

## Best Practices

### 1. Always Version Control
- Every schema change goes through Alembic
- Never make manual schema changes in production
- Keep migrations in git alongside code

### 2. Write Reversible Migrations
- Always implement `downgrade()`
- Test rollback in staging
- Document any data loss in rollback

### 3. Use Transactions
```python
def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', sa.String(20)))
```

### 4. Index Creation (PostgreSQL)
```python
# Use CONCURRENTLY to avoid locks
op.create_index(
    'idx_users_email',
    'users',
    ['email'],
    postgresql_concurrently=True
)
# Note: This must run outside transaction
```

### 5. Naming Conventions
```python
# Follow consistent naming
naming_convention = {
    "ix": "idx_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
```

## Common Pitfalls

### ❌ Don't: Drop columns immediately
```python
# BAD - causes errors if old code deployed
def upgrade():
    op.drop_column('users', 'old_field')
```

### ✅ Do: Multi-phase deployment
```python
# GOOD - Phase 1: Make nullable
# Phase 2: Update code to not use field
# Phase 3: Drop column
```

### ❌ Don't: Change types directly
```python
# BAD - can fail with existing data
op.alter_column('users', 'age', type_=sa.String())
```

### ✅ Do: Add new column, migrate, drop old
```python
# GOOD
op.add_column('users', sa.Column('age_str', sa.String()))
op.execute("UPDATE users SET age_str = age::text")
op.drop_column('users', 'age')
op.alter_column('users', 'age_str', new_column_name='age')
```

## Troubleshooting

### Migration fails mid-way
```bash
# Check current state
alembic current

# Mark as complete if manually fixed
alembic stamp <revision_id>
```

### Locked database during migration
```sql
-- Check locks
SELECT * FROM pg_locks WHERE NOT granted;

-- Kill blocking queries (carefully!)
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' AND pid != pg_backend_pid();
```

### Can't rollback
- Check `downgrade()` implementation
- May need manual SQL to fix
- Always test rollback in staging first

## Estimated Time

- Planning: 15 minutes
- Creating migration: 10 minutes
- Local testing: 10 minutes
- Staging deployment: 15 minutes
- Production deployment: 10 minutes

**Total**: ~60 minutes for safe, zero-downtime migration

## References

- [Alembic Documentation](https://alembic.sqlalchemy.org)
- [PostgreSQL ALTER TABLE](https://www.postgresql.org/docs/current/sql-altertable.html)
- [Zero-Downtime Deployments](https://brandur.org/postgres-sequences)
