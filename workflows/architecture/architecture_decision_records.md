# Architecture Decision Records

**ID:** arc-009  
**Category:** Architecture  
**Priority:** MEDIUM  
**Complexity:** Simple  
**Estimated Time:** 20-40 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Create and maintain Architecture Decision Records (ADRs) to document significant architectural choices

**Why:** ADRs provide historical context for decisions, prevent repeating past mistakes, onboard new team members faster, and create institutional memory that survives team turnover

**When to use:**
- Making significant architectural decisions
- Choosing between multiple technical alternatives
- Documenting technology stack choices
- Explaining trade-offs in system design
- Recording reasons for deviation from standards
- Onboarding new team members
- Resolving disagreements about past decisions

---

## Prerequisites

**Required:**
- [ ] Understanding of ADR format (context, decision, consequences)
- [ ] Version control access (Git repository)
- [ ] Markdown editing knowledge
- [ ] Team consensus on ADR process

**Check before starting:**
```bash
# Check if ADR directory exists
ls docs/adr/ || mkdir -p docs/adr/

# Check for ADR tools (optional)
which adr-tools
npm list -g adr-log
```

---

## Implementation Steps

### Step 1: Set Up ADR Directory Structure

**What:** Create organized location for storing ADRs in your repository

**How:**

**Directory Structure:**

```bash
# Create ADR directory
mkdir -p docs/adr/

# Create README
cat > docs/adr/README.md << 'EOF'
# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for this project.

## What is an ADR?

An ADR documents a significant architectural decision and its context and consequences.

## Format

Each ADR follows this format:
- Title
- Status (Proposed, Accepted, Deprecated, Superseded)
- Context
- Decision
- Consequences

## Naming Convention

ADRs are numbered sequentially:
- 0001-record-architecture-decisions.md
- 0002-use-postgresql-for-database.md
- 0003-implement-event-sourcing.md

## How to Create an ADR

1. Copy template.md to new file with next sequential number
2. Fill in sections
3. Submit pull request for team review
4. Update status once decision is made
EOF

# Create template
cat > docs/adr/template.md << 'EOF'
# [Number]. [Short title of solved problem]

Date: YYYY-MM-DD

## Status

[Proposed | Accepted | Deprecated | Superseded by [ADR-XXXX](XXXX-title.md)]

## Context

[Describe the issue motivating this decision and any context that influences it]

## Decision

[Describe the change we're proposing or have agreed to implement]

## Consequences

[Describe the resulting context after applying this decision. All consequences should be listed here, not just positive ones.]

### Positive

- [Positive consequence 1]
- [Positive consequence 2]

### Negative

- [Negative consequence 1]
- [Negative consequence 2]

### Neutral

- [Neutral consequence 1]

## Alternatives Considered

### [Alternative 1]

[Why it was not chosen]

### [Alternative 2]

[Why it was not chosen]

## References

- [Link to related documentation]
- [Link to discussions]
- [Link to research]
EOF
```

**Verification:**
- [ ] docs/adr/ directory created
- [ ] README.md explains ADR purpose
- [ ] template.md available for new ADRs
- [ ] Directory committed to version control

**If This Fails:**
→ Create directory manually
→ Use alternative location (architecture/decisions/)
→ Store ADRs in wiki if repo access limited

---

### Step 2: Create Your First ADR

**What:** Document the decision to use ADRs (meta-ADR)

**How:**

**First ADR - Record Architecture Decisions:**

```markdown
# 0001. Record Architecture Decisions

Date: 2025-10-26

## Status

Accepted

## Context

We need to record the architectural decisions made on this project to:

- Help new team members understand why the system is built the way it is
- Prevent revisiting decisions that have already been made and rejected
- Create a historical record of the evolution of the architecture
- Provide context for future architectural decisions
- Enable better decision-making by learning from past choices

Teams often lose institutional knowledge when members leave, leading to:
- Repeated discussions about solved problems
- Unknown reasons for current design choices
- Difficulty onboarding new members
- Resistance to change due to lack of context

## Decision

We will use Architecture Decision Records (ADRs) to document architecturally significant decisions: those that affect the structure, non-functional characteristics, dependencies, interfaces, or construction techniques.

An ADR will be:
- Written using Markdown
- Stored in docs/adr/ in version control
- Numbered sequentially with a short descriptive title
- Structured with: Status, Context, Decision, Consequences, Alternatives

ADRs will be created for decisions such as:
- Technology stack choices (databases, frameworks, languages)
- Architectural patterns (microservices, event-driven, layered)
- Major library or tool selections
- Significant integration approaches
- Security architecture decisions
- Infrastructure choices

ADRs will NOT be required for:
- Routine implementation decisions
- Tactical bug fixes
- Code style choices (covered by style guide)
- Minor dependency updates

## Consequences

### Positive

- **Historical context**: Future developers will understand why decisions were made
- **Knowledge retention**: Institutional knowledge survives team turnover
- **Better decisions**: Comparing current situations to past decisions improves outcomes
- **Reduced bikeshedding**: Settled decisions are documented and don't need re-litigation
- **Onboarding**: New team members can read ADRs to understand system evolution
- **Auditability**: Compliance and audit requirements can reference decision records

### Negative

- **Initial overhead**: Writing ADRs takes time (15-30 minutes per ADR)
- **Maintenance burden**: ADRs need updates when superseded or deprecated
- **Discipline required**: Team must commit to writing ADRs consistently
- **Review overhead**: ADRs add to pull request review load

### Neutral

- ADRs are part of the codebase and follow standard Git workflow
- ADR quality varies with author skill (mitigated by template and review)
- Some decisions will be recorded after the fact (acceptable)

## Alternatives Considered

### Confluence/Wiki Pages

**Pros:**
- Rich formatting
- Easy to edit
- Good for long-form documentation

**Cons:**
- Not version controlled with code
- Harder to keep in sync with codebase
- No built-in review process
- Often becomes stale

**Why not chosen:** We want decisions tracked alongside code changes in version control.

### GitHub/GitLab Issues

**Pros:**
- Already using for task tracking
- Good discussion threads
- Searchable

**Cons:**
- Not permanent (can be closed/deleted)
- Hard to browse historically
- Mixed with other issues
- No structured format

**Why not chosen:** Issues are for work tracking, not permanent documentation.

### Email/Slack Threads

**Pros:**
- Natural discussion medium
- Already used for decisions

**Cons:**
- Not searchable long-term
- Lost when people leave
- No structure
- Hard to reference

**Why not chosen:** Discussions should happen in these channels, but decisions need permanent documentation.

## References

- [Michael Nygard's ADR template](https://github.com/joelparkerhenderson/architecture-decision-record)
- [ThoughtWorks Technology Radar](https://www.thoughtworks.com/radar/techniques/lightweight-architecture-decision-records)
- [ADR tools](https://github.com/npryce/adr-tools)
```

**Save this as:** `docs/adr/0001-record-architecture-decisions.md`

**Verification:**
- [ ] First ADR created and committed
- [ ] Team reviewed and accepted ADR
- [ ] Format matches template
- [ ] All sections completed

**If This Fails:**
→ Start with shorter ADRs and expand later
→ Use team meeting to review and approve first ADR
→ Iterate on template based on feedback

---

### Step 3: Write ADRs for New Decisions

**What:** Document new architectural decisions as they arise

**How:**

**When to Write an ADR:**

```
Write an ADR when:
✅ Choosing between multiple viable technical options
✅ Making a decision that's hard to reverse
✅ Selecting core technologies (database, framework, cloud provider)
✅ Changing system architecture (monolith to microservices)
✅ Deviating from established patterns
✅ Making security/compliance decisions
✅ Choosing between build vs. buy

Don't write an ADR for:
❌ Routine implementation details
❌ Obvious choices with no alternatives
❌ Temporary workarounds or experiments
❌ Personal code style preferences
❌ Minor library updates
```

**Writing Process:**

```bash
# 1. Determine next ADR number
ls docs/adr/*.md | tail -1
# Shows: 0005-use-graphql-for-api.md
# Next number: 0006

# 2. Create new ADR from template
cp docs/adr/template.md docs/adr/0006-implement-event-sourcing.md

# 3. Write ADR (see example below)

# 4. Commit and create pull request
git add docs/adr/0006-implement-event-sourcing.md
git commit -m "docs: ADR-0006 implement event sourcing"
git push origin adr/0006-event-sourcing

# 5. Team reviews ADR in pull request
# 6. Merge when accepted
```

**Example ADR - Technology Choice:**

```markdown
# 0006. Implement Event Sourcing for Order System

Date: 2025-10-26

## Status

Accepted

Implements: [ADR-0003](0003-microservices-architecture.md)

## Context

Our order management system currently uses CRUD operations with a traditional relational database. We face several challenges:

1. **Audit Requirements**: Regulatory compliance requires complete audit trail of all order changes
2. **Complex State Transitions**: Orders go through 15+ states with complex business rules
3. **Retroactive Queries**: Business intelligence team needs to answer "what was the state at time X?"
4. **Race Conditions**: Multiple services updating orders simultaneously causes conflicts
5. **Lost Context**: Current state doesn't explain how we got there

Current system limitations:
- Update operations overwrite previous state
- Hard to debug production issues without historical state
- Cannot replay events to test new business rules
- Compensating transactions are complex and error-prone

We evaluated three approaches:
1. Continue with current CRUD + audit log table
2. Implement event sourcing
3. Use hybrid approach (event sourcing for critical entities only)

## Decision

We will implement **event sourcing** for the order management system using:

- **Event Store**: PostgreSQL with dedicated events table
- **Event Bus**: RabbitMQ for publishing events to subscribers
- **Read Models**: Separate materialized views for queries
- **Snapshotting**: Every 50 events to optimize replay performance

Implementation approach:
1. Events are append-only (never updated or deleted)
2. Current state reconstructed by replaying events
3. Separate read models optimized for different query patterns
4. Snapshots stored periodically to speed up reconstruction
5. Event schema versioning to handle evolution

Architecture:

```
Write Side:                      Read Side:
┌─────────────┐                 ┌─────────────┐
│   Command   │                 │    Query    │
│   Handler   │                 │   Handler   │
└──────┬──────┘                 └──────┬──────┘
       │                                │
       v                                v
┌─────────────┐    Events      ┌─────────────┐
│Event Store  │───────────────>│ Read Model  │
│(PostgreSQL) │                │  (Redis)    │
└─────────────┘                └─────────────┘
       │
       │ Publish
       v
┌─────────────┐
│  Event Bus  │
│ (RabbitMQ)  │
└─────────────┘
```

## Consequences

### Positive

- **Complete Audit Trail**: Every change is recorded as immutable event
- **Temporal Queries**: Can answer "what was state at time X?" by replaying to that point
- **Debugging**: Can replay events to reproduce production issues locally
- **Business Intelligence**: Can analyze event stream for insights and patterns
- **Conflict Resolution**: Optimistic concurrency through event versioning
- **Testing**: Can test business logic by asserting on generated events
- **Flexibility**: Can create new read models from event stream without migration
- **Event-Driven**: Natural fit for microservices and asynchronous processing

### Negative

- **Complexity**: More moving parts than CRUD (event store, bus, projections)
- **Eventual Consistency**: Read models may lag behind writes (acceptable for our use case)
- **Learning Curve**: Team needs training on event sourcing patterns
- **Storage Growth**: Events accumulate over time (mitigated by archiving old events)
- **Query Complexity**: Some queries require denormalized read models
- **Event Schema Evolution**: Need versioning strategy for events
- **Increased Infrastructure**: Need event bus and additional databases

### Neutral

- Events become the contract between services (versioning required)
- Snapshots needed for performance (rebuild time would be too slow)
- Some CRUD operations still acceptable for non-critical entities

## Alternatives Considered

### Alternative 1: CRUD + Audit Log Table

**Approach:**
- Continue current CRUD operations
- Add separate audit_log table to record all changes
- Trigger on UPDATE to capture before/after state

**Pros:**
- Simple, well-understood pattern
- No architectural changes needed
- Lower learning curve

**Cons:**
- Audit log is separate concern (often forgotten)
- Hard to reconstruct past state reliably
- Doesn't solve race condition issues
- Business logic scattered between app and database triggers
- Audit table becomes huge with performance implications

**Why not chosen:** Doesn't solve our core problems with state management and temporal queries.

### Alternative 2: Full Event Sourcing for Entire System

**Approach:**
- Implement event sourcing for ALL entities (users, products, orders, etc.)
- Standardize on event-driven architecture throughout

**Pros:**
- Consistent architecture across all services
- Maximum flexibility and auditability

**Cons:**
- Massive scope, high risk
- Overkill for simple CRUD entities (user profiles)
- Team doesn't have enough event sourcing experience
- Would delay delivery significantly

**Why not chosen:** Too risky for first implementation. Start with orders, expand if successful.

### Alternative 3: Change Data Capture (CDC)

**Approach:**
- Use database CDC (Debezium + Kafka) to capture all database changes
- Stream changes to event bus for downstream consumers

**Pros:**
- Transparent to application code
- Works with existing CRUD operations
- Provides event stream for integration

**Cons:**
- Database-centric approach, couples schema to events
- Limited control over event format
- Doesn't solve temporal query problem
- Still requires read models for efficient queries

**Why not chosen:** Doesn't give us control over event design and doesn't solve our core problems.

## Implementation Plan

Phase 1 (2 weeks):
- Set up event store table in PostgreSQL
- Implement basic event sourcing infrastructure
- Convert OrderCreated, OrderPaid events
- Create basic read model in Redis

Phase 2 (2 weeks):
- Add remaining order events (Shipped, Delivered, Cancelled, etc.)
- Implement snapshotting
- Migrate existing orders to events

Phase 3 (1 week):
- Add RabbitMQ integration
- Publish events for downstream consumers
- Monitoring and alerting

Phase 4 (ongoing):
- Additional read models as needed
- Performance tuning
- Team training

## References

- [Event Sourcing Pattern](https://martinfowler.com/eaaDev/EventSourcing.html) - Martin Fowler
- [CQRS Journey](https://docs.microsoft.com/en-us/previous-versions/msp-n-p/jj554200(v=pandp.10)) - Microsoft Patterns & Practices
- [Eventstore](https://www.eventstore.com/blog/what-is-event-sourcing) - Event Store documentation
- Internal: Slack discussion in #architecture (Oct 20-25, 2025)
- [ADR-0003: Microservices Architecture](0003-microservices-architecture.md)
```

**Verification:**
- [ ] Context explains the problem clearly
- [ ] Decision is specific and actionable
- [ ] All consequences documented (positive, negative, neutral)
- [ ] Alternatives compared fairly
- [ ] References provided for further reading
- [ ] Team reviewed and approved

**If This Fails:**
→ Focus on Context section first - if problem isn't clear, decision won't make sense
→ Use diagrams/code examples to clarify complex decisions
→ Break very large decisions into multiple ADRs

---

### Step 4: Manage ADR Lifecycle

**What:** Update ADR status as decisions evolve over time

**How:**

**ADR Status Transitions:**

```
Proposed ──> Accepted ──> [Active]
                │
                ├──> Deprecated ──> Superseded
                │
                └──> Rejected
```

**Status Definitions:**

- **Proposed**: Under discussion, not yet decided
- **Accepted**: Approved and being implemented
- **Deprecated**: Still in use but discouraged for new work
- **Superseded**: Replaced by a newer ADR
- **Rejected**: Considered but not chosen

**Updating Status:**

```markdown
# When a decision is superseded
# Update OLD ADR:

## Status

~~Accepted~~

Superseded by [ADR-0012](0012-migrate-to-kubernetes.md)

## Note

As of 2026-03-15, we migrated from EC2 to Kubernetes. See ADR-0012 for rationale.

---

# In NEW ADR:

## Status

Accepted

Supersedes: [ADR-0008](0008-deploy-on-ec2.md)

## Context

ADR-0008 decided to deploy on EC2, but we now face scalability issues...
```

**Deprecation Process:**

```markdown
# When deprecating a decision without immediate replacement:

## Status

Deprecated

## Deprecation Notice

Date: 2026-01-15  
Reason: Security vulnerabilities in chosen library  
Timeline: Remove by 2026-06-01  
Migration Guide: See [migration-guide.md](../guides/migration-guide.md)

## Context

[Original context...]

## Decision

[Original decision...]

## Consequences

[Original consequences...]

### Update (2026-01-15)

We discovered critical security issues in the chosen library:
- CVE-2025-12345: Remote code execution
- No patch available from maintainer
- Library is no longer maintained

Action: Migrate to alternative by June 2026.
```

**Verification:**
- [ ] Status kept up-to-date
- [ ] Superseded ADRs link to replacements
- [ ] Deprecated ADRs include timeline and migration info
- [ ] Git history shows status changes

**If This Fails:**
→ Schedule quarterly ADR reviews
→ Add ADR review to architectural review checklist
→ Link ADRs in code comments to keep them discoverable

---

### Step 5: Integrate ADRs Into Workflow

**What:** Make ADRs a natural part of development process

**How:**

**Pull Request Template:**

```markdown
<!-- .github/pull_request_template.md -->

## Description
[Describe your changes]

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Architecture change

## Architecture Changes

**Does this PR include architectural decisions?**
- [ ] Yes - ADR created/updated (link below)
- [ ] No - No architectural impact

**ADR:**
- [ ] [ADR-XXXX: Title](../docs/adr/XXXX-title.md)

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] ADR created (if applicable)
```

**Code Comments Linking ADRs:**

```python
# Order processing using event sourcing
# Decision documented in ADR-0006:
# docs/adr/0006-implement-event-sourcing.md

class OrderEventStore:
    """
    Event store for order management.
    
    Implements event sourcing pattern as per ADR-0006.
    Events are append-only and never modified.
    """
    
    def append_event(self, event: OrderEvent) -> None:
        # Store event (immutable)
        pass
    
    def get_events(self, order_id: str) -> List[OrderEvent]:
        # Retrieve all events for order
        pass
```

**Automated ADR Generation:**

```bash
# Install ADR tools (optional)
npm install -g adr-log

# Or Python version
pip install adr-tools-python

# Create new ADR with template
adr new "Use PostgreSQL for database"
# Creates: docs/adr/0007-use-postgresql-for-database.md

# Generate ADR index/table of contents
adr generate toc > docs/adr/README.md
```

**ADR Review Checklist:**

```markdown
# Architecture Review Checklist

Before approving architectural changes:

- [ ] Is the problem/context clearly explained?
- [ ] Are multiple alternatives considered?
- [ ] Are trade-offs explicitly stated?
- [ ] Are negative consequences acknowledged?
- [ ] Is the decision reversible? (If not, is extra scrutiny applied?)
- [ ] Does the decision align with system goals?
- [ ] Are implementation implications understood?
- [ ] Is the ADR written clearly for future readers?
- [ ] Are references provided for further reading?
- [ ] Have relevant stakeholders reviewed the ADR?
```

**Onboarding with ADRs:**

```markdown
# New Developer Onboarding Checklist

## Week 1: Understanding Architecture

Read these ADRs to understand key architectural decisions:

**Foundation:**
- [ ] [ADR-0001: Record Architecture Decisions](docs/adr/0001-record-architecture-decisions.md)
- [ ] [ADR-0003: Microservices Architecture](docs/adr/0003-microservices-architecture.md)
- [ ] [ADR-0005: Use GraphQL for API](docs/adr/0005-use-graphql-for-api.md)

**Data Layer:**
- [ ] [ADR-0006: Implement Event Sourcing](docs/adr/0006-implement-event-sourcing.md)
- [ ] [ADR-0007: PostgreSQL for Database](docs/adr/0007-use-postgresql-for-database.md)

**Infrastructure:**
- [ ] [ADR-0012: Deploy on Kubernetes](docs/adr/0012-migrate-to-kubernetes.md)
- [ ] [ADR-0015: Use GitHub Actions for CI/CD](docs/adr/0015-use-github-actions.md)

## Week 2: Deep Dive

Review ADRs related to your team's area...
```

**Verification:**
- [ ] ADRs referenced in pull requests
- [ ] Code links to relevant ADRs
- [ ] New team members read ADRs during onboarding
- [ ] ADRs reviewed in architectural review meetings
- [ ] ADR tool integrated (optional)

**If This Fails:**
→ Make ADR creation part of definition of done
→ Add ADR reminder to PR template
→ Designate architecture champion to shepherd process

---

## Verification Checklist

After completing this workflow:

- [ ] ADR directory structure created
- [ ] Template and README in place
- [ ] First ADR (record decisions) written
- [ ] Process for creating new ADRs established
- [ ] Team trained on ADR format
- [ ] ADRs integrated into development workflow
- [ ] Status update process defined
- [ ] ADRs used in onboarding

---

## Common Issues & Solutions

### Issue: ADRs become stale and outdated

**Symptoms:**
- ADRs reference deprecated technologies
- Status not updated when decisions change
- New team members don't trust ADRs

**Solution:**
```bash
# Quarterly ADR review script
#!/bin/bash

echo "=== Quarterly ADR Review ==="
echo "Review date: $(date)"
echo ""

# Find all Accepted ADRs older than 1 year
find docs/adr -name "*.md" -type f | while read adr; do
    status=$(grep "^## Status" "$adr" -A 1 | tail -1)
    date=$(grep "^Date:" "$adr" | cut -d: -f2-)
    
    if [[ "$status" == "Accepted" ]]; then
        age_days=$(( ($(date +%s) - $(date -d "$date" +%s)) / 86400 ))
        
        if [ $age_days -gt 365 ]; then
            echo "⚠️  $adr"
            echo "   Status: Accepted"
            echo "   Age: $age_days days"
            echo "   Action: Review if still accurate"
            echo ""
        fi
    fi
done

echo "=== Review complete ==="
echo "Schedule next review: $(date -d '+3 months')"
```

**Prevention:**
- Schedule quarterly ADR reviews
- Assign architecture champion to maintain ADRs
- Include ADR review in architectural review meetings
- Update ADRs when refactoring related code

---

### Issue: Team doesn't write ADRs consistently

**Symptoms:**
- Major decisions made without ADRs
- Only architect writes ADRs
- ADRs written retroactively

**Solution:**
```markdown
# Make ADRs part of Definition of Done

## Pull Request Checklist

For PRs that introduce architectural changes:

- [ ] **ADR created** before implementation
- [ ] **Team reviewed** ADR (not just code)
- [ ] **Alternatives considered** explicitly
- [ ] **Consequences documented**
- [ ] **ADR linked** in PR description

## When to Create an ADR

✅ **Must create ADR:**
- Choosing core technology (database, framework, language)
- Changing system architecture
- Making security/compliance decisions
- Decisions that are hard to reverse

⚠️ **Consider creating ADR:**
- Choosing between viable technical alternatives
- Deviating from established patterns
- Making decisions that affect multiple teams

❌ **No ADR needed:**
- Routine implementation details
- Bug fixes
- Code style choices

## Enforcement

PRs introducing architectural changes without ADR:
→ Request ADR in review
→ Block merge until ADR created
```

**Prevention:**
- Add ADR check to PR template
- Make ADR creation part of architectural review
- Celebrate ADR contributions in team meetings
- Keep ADR process lightweight (15-30 min to write)

---

### Issue: ADRs too long and detailed

**Symptoms:**
- ADRs take hours to write
- Team avoids writing them
- ADRs are difficult to read

**Solution:**
```markdown
# Keep ADRs Concise

## Good ADR Structure

**Context**: 2-4 paragraphs explaining the problem
**Decision**: 1-2 paragraphs stating the choice
**Consequences**: Bulleted lists of impacts
**Alternatives**: 1 paragraph per alternative

## Target Length

- Simple decision: 300-500 words (5-10 min read)
- Complex decision: 500-1000 words (10-20 min read)
- Very complex: 1000-2000 words (20-30 min read)

If longer than 2000 words, consider:
- Breaking into multiple ADRs
- Moving details to separate documentation
- Focusing on the decision, not implementation

## Example - Too Long

```markdown
# Context (10 paragraphs, 1500 words)

We need a database... [extensive research dump]
[Complete history of databases]
[Detailed benchmark results]
[Performance graphs]
...
```

## Example - Just Right

```markdown
# Context (3 paragraphs, 300 words)

We need a database for our application. Key requirements:
- ACID transactions
- <1ms query latency at 10k req/sec
- JSON support
- Managed service preferred

We evaluated PostgreSQL, MongoDB, and DynamoDB based on:
performance benchmarks, operational complexity, and cost.

Our application is read-heavy (90% reads) with complex queries
involving multiple tables and aggregations.
```
```

**Prevention:**
- Use template consistently
- Focus on decision, not implementation
- Link to detailed docs/research separately
- Review ADRs for clarity, not just correctness

---

## Examples

### Example 1: Database Selection ADR

```markdown
# 0007. Use PostgreSQL for Primary Database

Date: 2025-10-26

## Status

Accepted

## Context

We need to select a primary database for our SaaS application. Requirements:

- ACID transactions for payment processing
- Complex relational queries (joins, aggregations)
- JSON support for flexible product attributes
- Mature ecosystem and tooling
- Managed service available (AWS RDS)
- Cost effective at scale (projected 100k users)

Our data model includes:
- Relational data (users, orders, invoices)
- Document-like data (product catalogs with varying schemas)
- Full-text search for products
- Time-series data for analytics

Team expertise:
- Strong SQL experience (PostgreSQL, MySQL)
- Limited NoSQL experience
- No dedicated DBA

## Decision

Use **PostgreSQL 15** as our primary database, deployed on AWS RDS.

Rationale:
- Excellent ACID compliance for financial transactions
- Advanced JSON support (JSONB type with indexing)
- Rich full-text search capabilities
- Mature replication and backup solutions
- Strong AWS RDS support with automated backups
- pg_stat_statements for query performance monitoring
- Cost-effective for our scale

Configuration:
- AWS RDS Multi-AZ for high availability
- Daily automated backups retained for 30 days
- Read replicas for analytics queries
- Connection pooling via PgBouncer

## Consequences

### Positive

- ACID guarantees protect payment integrity
- Team already has PostgreSQL expertise
- JSONB handles flexible product schemas
- Built-in full-text search avoids additional services
- Strong ecosystem (ORMs, tools, extensions)
- AWS RDS handles operations (backups, updates, monitoring)

### Negative

- Vertical scaling limits (~64 vCPUs in RDS)
- Schema migrations require careful planning
- Not ideal for write-heavy workloads (but we're read-heavy)
- Cost increases with storage and IOPS

### Neutral

- Will need read replicas for analytics (acceptable)
- Some queries may need optimization for performance
- May need separate time-series database for metrics (future)

## Alternatives Considered

### MongoDB

**Pros:**
- Flexible schema
- Horizontal scaling
- Good for document data

**Cons:**
- No multi-document ACID transactions in our MongoDB version
- Team lacks experience
- More complex operations
- Higher RDS cost than PostgreSQL

**Why not chosen:** ACID transactions are critical for payments; risk not worth flexibility gains.

### DynamoDB

**Pros:**
- Serverless, auto-scaling
- Low latency at scale
- No operational overhead

**Cons:**
- Complex relational queries difficult
- No ACID across multiple items/tables
- Query patterns must be known upfront
- Hard to iterate on schema
- Cost unpredictable at scale

**Why not chosen:** Our query patterns are too complex and evolving; want SQL flexibility.

### MySQL

**Pros:**
- Similar to PostgreSQL
- Team has experience
- Strong RDS support

**Cons:**
- Inferior JSON support
- Weaker full-text search
- Less feature-rich than PostgreSQL
- Similar cost to PostgreSQL

**Why not chosen:** PostgreSQL offers better features for same cost and operations.

## References

- [PostgreSQL vs MySQL JSON](https://www.postgresql.org/docs/current/datatype-json.html)
- [AWS RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/)
- Internal benchmarks: /docs/benchmarks/database-comparison.md
```

---

## Best Practices

### DO:
✅ Write ADRs for significant architectural decisions
✅ Create ADRs **before** implementing (when possible)
✅ Keep ADRs concise and focused (300-1000 words)
✅ Document consequences honestly (positive and negative)
✅ Consider alternatives explicitly
✅ Update status when decisions change
✅ Link ADRs to related code and documentation
✅ Review ADRs during onboarding
✅ Use consistent format/template
✅ Store ADRs in version control with code

### DON'T:
❌ Write ADRs for trivial decisions
❌ Make ADRs too long or detailed (>2000 words)
❌ Skip alternatives section
❌ Only list positive consequences
❌ Write ADRs after the fact (when avoidable)
❌ Let ADRs become stale
❌ Store ADRs in wikis separate from code
❌ Require approval from everyone for every ADR
❌ Use ADRs to justify poor decisions retroactively
❌ Make ADR process bureaucratic or heavyweight

---

## Related Workflows

**Prerequisites:**
- `dev-013`: Technical Debt Identification - ADRs help document debt
- `arc-001`: API Design Best Practices - ADRs document API choices

**Next Steps:**
- `dev-007`: Developer Onboarding - Use ADRs in onboarding
- `dev-017`: Technical Debt Management - Track debt from ADRs
- `pro-001`: Knowledge Transfer - ADRs are knowledge artifacts

**Alternatives:**
- Design docs (more implementation-focused)
- RFC process (more formal, for cross-team decisions)
- Wiki documentation (less tied to code changes)

---

## Tags
`architecture` `adr` `documentation` `decision-making` `governance` `knowledge-management` `best-practices`
