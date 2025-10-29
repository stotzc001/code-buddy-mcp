# Railway Deployment Guide

Deploy your PostgreSQL database to Railway for cloud-hosted, accessible-anywhere workflow storage.

## Why Railway?

- ✅ **Free tier** with generous limits
- ✅ **PostgreSQL 15+** with pgvector support
- ✅ **Automatic backups**
- ✅ **Global CDN** for low latency
- ✅ **Easy setup** (5 minutes)
- ✅ **No credit card** required for trial

## Step-by-Step Deployment

### 1. Create Railway Account

1. Go to https://railway.app
2. Sign up with GitHub (recommended) or email
3. Verify your email

### 2. Create New Project

1. Click "**New Project**"
2. Select "**Deploy PostgreSQL**"
3. Wait 30-60 seconds for provisioning

### 3. Get Connection Details

Two methods to get your `DATABASE_URL`:

#### Method A: Railway Dashboard

1. Click on your PostgreSQL service
2. Go to "**Variables**" tab
3. Look for `DATABASE_URL` or `POSTGRES_URL`
4. Click the copy icon

Format will be:
```
postgresql://postgres:PASSWORD@containers-us-west-xxx.railway.app:PORT/railway
```

#### Method B: Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# View variables
railway variables

# Get DATABASE_URL
railway variables | grep DATABASE_URL
```

### 4. Enable pgvector Extension

Railway PostgreSQL includes pgvector by default! Just connect and run:

```bash
# Using psql
psql "postgresql://postgres:PASSWORD@containers-us-west-xxx.railway.app:PORT/railway"

# Or using Railway CLI
railway run psql $DATABASE_URL
```

Then execute:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
\dx  -- Verify extension is installed
```

### 5. Configure Code Buddy

Update your `.env` file:

```env
DATABASE_URL=postgresql://postgres:PASSWORD@containers-us-west-xxx.railway.app:PORT/railway
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
```

### 6. Initialize Schema

```bash
python scripts/setup_database.py
```

### 7. Import Workflows

```bash
python scripts/import_workflows.py --directory ./workflows
```

## Railway Configuration Tips

### Database Settings

In Railway dashboard, you can adjust:

1. **Compute Resources**
   - Free tier: Shared CPU, 512MB RAM
   - Upgrade for more: $5-20/month

2. **Storage**
   - Free tier: 1GB
   - Upgrade: $0.25/GB/month

3. **Backups**
   - Automatic daily backups (free)
   - Retention: 7 days (free) or 30 days (paid)

### Connection Pooling

For production use, consider connection pooling:

1. **PgBouncer** (built into Railway):
   - Enable in Railway dashboard
   - Reduces connection overhead
   - Better for multiple clients

2. **Update connection string**:
   ```env
   DATABASE_URL=postgresql://postgres:PASSWORD@containers-us-west-xxx.railway.app:PORT/railway?pgbouncer=true
   ```

### Environment Variables

Set these in Railway dashboard for auto-deployment:

```
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=1536
LOG_LEVEL=INFO
```

## Security Best Practices

### 1. Use Environment Variables

Never hardcode credentials:

```python
# ❌ BAD
DATABASE_URL = "postgresql://postgres:mypassword@..."

# ✅ GOOD
DATABASE_URL = os.getenv("DATABASE_URL")
```

### 2. Restrict IP Access

In Railway dashboard:
1. Go to your PostgreSQL service
2. Settings → Network
3. Add allowed IP addresses

### 3. Use SSL Connections

Railway enforces SSL by default. Ensure your connection string uses SSL:

```env
DATABASE_URL=postgresql://...?sslmode=require
```

### 4. Rotate Passwords

Periodically rotate database passwords:
1. Railway dashboard → PostgreSQL → Settings
2. Click "Reset Password"
3. Update `.env` and Claude Desktop config

## Monitoring

### Railway Dashboard

Track your database:
- **Metrics**: CPU, RAM, Disk usage
- **Query Performance**: Slow queries
- **Connection Stats**: Active connections
- **Backup Status**: Last backup time

### Database Queries

Check workflow statistics:

```sql
-- Total workflows
SELECT COUNT(*) FROM workflows WHERE is_active = TRUE;

-- Workflows by category
SELECT category, COUNT(*) 
FROM workflows 
WHERE is_active = TRUE 
GROUP BY category;

-- Usage statistics
SELECT COUNT(*) as total_uses 
FROM workflow_usage;

-- Most popular workflows
SELECT 
    w.title,
    COUNT(wu.id) as usage_count,
    AVG(CASE WHEN wu.was_helpful THEN 1 ELSE 0 END)::NUMERIC(3,2) as helpfulness
FROM workflows w
LEFT JOIN workflow_usage wu ON w.id = wu.workflow_id
GROUP BY w.id, w.title
ORDER BY usage_count DESC
LIMIT 10;
```

## Scaling Considerations

### When to Upgrade

Consider upgrading if:
- [ ] Database size > 1GB
- [ ] Response times > 500ms
- [ ] Active connections > 20
- [ ] Daily requests > 10,000

### Performance Optimization

1. **Indexes** (already included in schema):
   ```sql
   -- Check index usage
   SELECT 
       tablename,
       indexname,
       idx_scan as index_scans
   FROM pg_stat_user_indexes
   ORDER BY idx_scan DESC;
   ```

2. **Vacuum regularly** (Railway does this automatically):
   ```sql
   VACUUM ANALYZE workflows;
   ```

3. **Refresh materialized views**:
   ```sql
   REFRESH MATERIALIZED VIEW CONCURRENTLY popular_workflows;
   ```

### Horizontal Scaling

For very large deployments:
1. **Read replicas**: Railway supports replicas
2. **Sharding**: Split workflows by category
3. **Caching**: Add Redis for hot workflows

## Backup and Recovery

### Manual Backup

```bash
# Using Railway CLI
railway run pg_dump $DATABASE_URL > backup.sql

# Restore
railway run psql $DATABASE_URL < backup.sql
```

### Automated Backups

Railway provides:
- **Daily automatic backups** (free tier)
- **7-day retention** (free tier)
- **30-day retention** (paid plans)

Restore from Railway dashboard:
1. Go to PostgreSQL service
2. Backups tab
3. Select backup → Restore

## Migration from Other Providers

### From Heroku

```bash
# Export from Heroku
heroku pg:backups:capture
heroku pg:backups:download

# Import to Railway
railway run psql $DATABASE_URL < latest.dump
```

### From AWS RDS

```bash
# Dump from RDS
pg_dump -h your-rds-instance.amazonaws.com -U username dbname > backup.sql

# Import to Railway
railway run psql $DATABASE_URL < backup.sql
```

## Cost Estimates

### Free Tier (Trial)
- **PostgreSQL**: 500 hours/month
- **Storage**: 1GB
- **Bandwidth**: 100GB
- **Perfect for**: Development, testing, small teams

### Starter Plan ($5/month)
- **PostgreSQL**: Unlimited hours
- **Storage**: 5GB included
- **Bandwidth**: 100GB
- **Perfect for**: Small production use

### Pro Plan ($20/month)
- **PostgreSQL**: High-performance instances
- **Storage**: 50GB included
- **Bandwidth**: 1TB
- **Perfect for**: Production, large teams

## Troubleshooting

### Connection Refused

```bash
# Test connection
psql "postgresql://your-connection-string"

# Check Railway status
railway status
```

### Slow Queries

```sql
-- Enable query logging
ALTER DATABASE railway SET log_statement = 'all';
ALTER DATABASE railway SET log_min_duration_statement = 1000;

-- View slow queries
SELECT 
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
```

### Out of Connections

```sql
-- Check current connections
SELECT COUNT(*) FROM pg_stat_activity;

-- Kill idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND state_change < NOW() - INTERVAL '1 hour';
```

## Support

- **Railway Docs**: https://docs.railway.app
- **Railway Discord**: https://discord.gg/railway
- **Railway Status**: https://status.railway.app

---

**Next**: Return to [Quick Start Guide](QUICKSTART.md) to complete setup
