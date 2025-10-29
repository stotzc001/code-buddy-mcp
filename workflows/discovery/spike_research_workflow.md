# Spike Research Workflow

**ID:** disc-001  
**Category:** Discovery  
**Priority:** MEDIUM  
**Complexity:** Moderate  
**Estimated Time:** 2-8 hours (timeboxed)  
**Frequency:** As needed  
**Last Updated:** 2025-10-27  
**Status:** ✅ Complete

---

## Purpose

**What:** Time-boxed research and experimentation to reduce uncertainty, evaluate technologies, or validate technical approaches before committing to full implementation.

**Why:**
- Reduces risk of wrong technology choices
- Validates architectural decisions early
- Uncovers hidden complexity before sprint planning
- Provides concrete data for story estimation
- Prevents costly mid-sprint pivots
- Builds team knowledge

**When to use:**
- Evaluating new libraries or frameworks
- Assessing technical feasibility of a feature
- Comparing multiple solution approaches
- Investigating complex bug root causes
- Researching best practices for unfamiliar domains
- Validating performance requirements
- Exploring third-party API capabilities

---

## Prerequisites

**Required Knowledge:**
- [ ] Understanding of the problem or question to research
- [ ] Basic research and documentation skills
- [ ] Ability to timebox work effectively

**Required Tools:**
- [ ] Development environment
- [ ] Note-taking tool (markdown, wiki, docs)
- [ ] Timer or time tracking

**Required Files:**
- [ ] Spike research template (created in this workflow)
- [ ] Project documentation location

---

## Implementation Steps

### Step 1: Define Spike Objective and Timebox

**What:** Clearly define what you need to learn and set a strict time limit.

**Why:** Spikes can easily become rabbit holes without clear boundaries.

**How:**

Create a spike document:

**File: docs/spikes/YYYY-MM-DD-spike-name.md**
```markdown
# Spike: [Clear, Concise Title]

**Date:** 2025-10-27
**Researcher:** [Your Name]
**Timebox:** 4 hours
**Status:** In Progress

---

## Objective

**Problem Statement:**
[What problem are we trying to solve?]

**Research Questions:**
1. [Specific question 1]
2. [Specific question 2]
3. [Specific question 3]

**Success Criteria:**
- [ ] Answered research questions
- [ ] Have proof-of-concept code (if applicable)
- [ ] Documented findings and recommendations
- [ ] Identified risks and unknowns

**Out of Scope:**
- [What we're explicitly NOT investigating]
- [What can wait for implementation]

---

## Hypothesis

[What do you think the answer will be? What approach do you expect to work?]

---

## Timebox

- **Allocated Time:** 4 hours
- **Start Time:** [YYYY-MM-DD HH:MM]
- **End Time:** [YYYY-MM-DD HH:MM]
- **Actual Time Spent:** [Track as you go]

**Time Breakdown Plan:**
- Hour 1: Research and reading
- Hour 2: Proof-of-concept setup
- Hour 3: Implementation and testing
- Hour 4: Documentation and recommendations

---

## Research Notes

### [Topic/Area 1]

**What I learned:**
- Finding 1
- Finding 2

**Sources:**
- [Link to documentation]
- [Link to article]
- [Stack Overflow post]

**Code Examples:**
```python
# Example code that worked
def example():
    pass
```

---

## Proof of Concept

**Code Location:** `/experiments/spike-name/`

**Key Findings:**
- [What worked]
- [What didn't work]
- [Performance observations]

---

## Recommendations

### Recommended Approach
[Describe the recommended solution]

**Pros:**
- [Advantage 1]
- [Advantage 2]

**Cons:**
- [Limitation 1]
- [Limitation 2]

**Estimated Effort:** [X hours/days]

### Alternative Approaches Considered

**Option 2: [Name]**
- **Pros:** [...]
- **Cons:** [...]
- **Why not chosen:** [...]

---

## Risks and Unknowns

- [ ] Risk 1: [Description]
- [ ] Unknown 1: [Requires further investigation]

---

## Next Steps

1. [Action item 1]
2. [Action item 2]
3. [Action item 3]

---

## Conclusion

[Summary of findings and final recommendation]

**Decision:** [Proceed with X approach | Need more research | Abandon this direction]
```

**Verification:**
- [ ] Spike objective clearly defined
- [ ] Research questions specific and answerable
- [ ] Timebox set (typically 2-8 hours)
- [ ] Success criteria established

**If This Fails:**
→ Objective is too broad - break into smaller questions
→ Timebox too long - reduce scope or split into multiple spikes

---

### Step 2: Set Up Research Environment

**What:** Create an isolated experiment space for spike work.

**How:**

```bash
# Create spike workspace
mkdir -p experiments/spike-$(date +%Y%m%d)-spike-name
cd experiments/spike-$(date +%Y%m%d)-spike-name

# Initialize if needed
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Create README
cat > README.md << EOF
# Spike: [Name]

**Date:** $(date +%Y-%m-%d)
**Timebox:** X hours
**Status:** In Progress

## Objective
[Brief description]

## How to Run
\`\`\`bash
# Steps to reproduce experiments
python experiment.py
\`\`\`

## Results
[To be filled]
EOF

# Track time
echo "Spike started: $(date)" > time_log.txt
```

**For web/API research:**
```bash
# Create test script
touch test_api.py
touch requirements_spike.txt
```

**Verification:**
- [ ] Experiment directory created
- [ ] Virtual environment set up (if needed)
- [ ] Time tracking started
- [ ] README created

---

### Step 3: Conduct Time-Boxed Research

**What:** Execute the research within the allocated time, tracking findings.

**How:**

**Research Techniques:**

**1. Documentation Review**
```markdown
## Documentation Review

**Official Docs:**
- [Library Name](https://example.com/docs)
  - ✅ Well documented
  - ❌ Missing examples for use case X
  - Key sections: Installation, Getting Started, Advanced Usage

**Community Resources:**
- [Tutorial](https://example.com/tutorial)
- [Blog post](https://example.com/blog)
- [Stack Overflow discussion](https://stackoverflow.com/...)
```

**2. Proof of Concept Code**
```python
# experiment.py
"""
Spike: Testing [Technology/Approach]

Goal: Determine if [Technology] can handle [Use Case]
"""
import time

def main():
    print("=== Spike Experiment ===")
    
    # Test 1: Basic functionality
    print("\nTest 1: Basic usage")
    start = time.time()
    try:
        # Your experimental code here
        result = test_basic_usage()
        print(f"✅ Success: {result}")
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        print(f"Duration: {time.time() - start:.2f}s")
    
    # Test 2: Performance
    print("\nTest 2: Performance check")
    start = time.time()
    # Performance test code
    print(f"Duration: {time.time() - start:.2f}s")
    
    # Test 3: Edge cases
    print("\nTest 3: Edge cases")
    # Edge case testing

if __name__ == "__main__":
    main()
```

**3. Comparison Matrix** (when evaluating multiple options)
```markdown
## Option Comparison

| Criteria | Option A | Option B | Option C |
|----------|----------|----------|----------|
| Ease of use | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Performance | Fast | Very Fast | Medium |
| Documentation | Excellent | Poor | Good |
| Community | Large | Small | Medium |
| License | MIT | Apache 2.0 | GPL |
| Maintenance | Active | Active | Inactive |
| Learning curve | Low | High | Medium |
| **Score** | **9/10** | **6/10** | **7/10** |

**Winner:** Option A - Best balance of usability and performance
```

**Verification:**
- [ ] Time tracked throughout research
- [ ] Findings documented as discovered
- [ ] Code examples captured
- [ ] Performance metrics recorded (if relevant)

**If This Fails:**
→ Stop at timebox end, document what you learned
→ Schedule additional spike if more research needed

---

### Step 4: Document Findings and Recommendations

**What:** Synthesize research into clear, actionable recommendations.

**How:**

**Complete the spike document sections:**

```markdown
## Key Findings

### Technical Feasibility: ✅ Feasible / ⚠️ Possible with caveats / ❌ Not recommended

**Summary:**
[Brief overview of whether the approach works]

**Details:**
1. **Finding 1:** [Description]
   - Impact: [High/Medium/Low]
   - Evidence: [Code snippet, benchmark, or reference]

2. **Finding 2:** [Description]
   - Impact: [High/Medium/Low]
   - Evidence: [...]

---

## Proof of Concept Results

**What Worked:**
- [Feature/aspect 1]
- [Feature/aspect 2]

**What Didn't Work:**
- [Problem 1]
  - Attempted solution: [What I tried]
  - Result: [Still not working | Partial success]

**Performance:**
- [Metric 1]: [Result]
- [Metric 2]: [Result]

**Code Quality:**
- Complexity: [Simple/Moderate/Complex]
- Testability: [Easy/Medium/Hard]
- Maintainability: [Good/Fair/Poor]

---

## Recommendation

### Recommended Approach: [Name/Description]

**Rationale:**
[Why this is the best option based on research]

**Implementation Estimate:**
- Setup: [X hours]
- Core functionality: [X hours]
- Testing: [X hours]
- Documentation: [X hours]
- **Total: [X hours/days]**

**Dependencies:**
- [Library 1] (version X.X)
- [Service/Tool 2]

**Risks:**
1. [Risk 1] - Mitigation: [Strategy]
2. [Risk 2] - Mitigation: [Strategy]

**Unknown Unknowns:**
- [Area that needs more investigation]
- [Potential complexity not fully explored]

---

## Alternatives Considered

**Option 2: [Name]**
- Why not chosen: [Reason]
- When to reconsider: [Condition]

**Option 3: [Name]**
- Why not chosen: [Reason]
- When to reconsider: [Condition]

---

## Next Steps

**Immediate Actions:**
1. [ ] Share findings with team
2. [ ] Update story estimates based on findings
3. [ ] Create implementation tasks

**Before Implementation:**
- [ ] Review architectural implications
- [ ] Confirm approach with [Stakeholder/Tech Lead]
- [ ] Update technical design document

**If Proceeding:**
- [ ] Clean up POC code for reuse
- [ ] Add chosen library to requirements.txt
- [ ] Create implementation workflow/guide

---

## Lessons Learned

**What went well:**
- [Insight 1]

**What could be improved:**
- [Insight 2]

**Would I timebox differently?**
- [Reflection on time allocation]
```

**Verification:**
- [ ] Findings clearly documented
- [ ] Recommendation justified with evidence
- [ ] Risks and unknowns identified
- [ ] Next steps defined
- [ ] Actual time tracked

---

### Step 5: Share and Archive

**What:** Communicate findings to team and preserve knowledge.

**How:**

**1. Create Summary for Team:**

```markdown
# Spike Results: [Name]

**TL;DR:** [One sentence recommendation]

**Recommendation:** [Proceed | More research needed | Don't proceed]

**Key Findings:**
- [Finding 1]
- [Finding 2]

**Estimated Implementation Effort:** [X hours/days]

**Full Document:** [Link to detailed spike doc]
```

**2. Present findings:**
- Quick team meeting (10-15 minutes)
- Include demos if applicable
- Discuss any concerns or questions

**3. Archive spike:**
```bash
# Move spike doc to permanent location
mv docs/spikes/YYYY-MM-DD-spike-name.md docs/spikes/archived/

# Update spike index
echo "- [Spike: Name](archived/YYYY-MM-DD-spike-name.md) - Status: Complete" >> docs/spikes/INDEX.md

# Commit to version control
git add docs/spikes/
git commit -m "docs: complete spike research on [topic]"
```

**4. Update project documentation:**
```markdown
# Add to technical decisions log
## Decision: Use [Technology/Approach]

**Date:** 2025-10-27
**Status:** Accepted
**Context:** [Brief context]
**Decision:** [What we decided]
**Consequences:** [Impact of decision]
**Research:** See spike document [link]
```

**Verification:**
- [ ] Team informed of findings
- [ ] Spike documented and archived
- [ ] Decision recorded if applicable
- [ ] POC code preserved or documented

---

## Verification Checklist

After completing this workflow:

- [ ] Spike objective achieved or clarified why not
- [ ] Time box respected (or noted if exceeded with reason)
- [ ] All research questions answered or flagged as needing more research
- [ ] Proof-of-concept code created (if applicable)
- [ ] Findings documented with evidence
- [ ] Clear recommendation provided
- [ ] Risks and unknowns identified
- [ ] Team informed of results
- [ ] Spike archived for future reference
- [ ] Next steps defined

---

## Common Issues & Solutions

### Issue: Spike Taking Too Long

**Symptoms:**
- Timebox exceeded
- Still no clear answer
- Scope creep

**Solution:**
```markdown
## When to Stop

**At timebox end, ask:**
1. Do I have enough information to make a recommendation?
   - Yes → Document and conclude
   - No → Assess if more time would help

2. Is additional time likely to provide significantly more clarity?
   - Yes → Schedule follow-up spike with new timebox
   - No → Make recommendation based on current findings

3. What's blocking progress?
   - Rabbit hole → Step back, refocus on original questions
   - Missing information → Note as unknown, recommend next steps
   - Technical blocker → Document blocker, recommend alternative investigation
```

---

### Issue: Too Many Unknowns Remain

**Symptoms:**
- Research raises more questions than answers
- Uncertainty hasn't decreased
- Multiple directions to explore

**Solution:**
```markdown
## Dealing with Uncertainty

**Options:**
1. **Break down further:** Create multiple smaller spikes
2. **Prototype differently:** Try faster/simpler POC approach
3. **Seek expert input:** Consult someone with experience
4. **Incremental approach:** Recommend starting with simplest solution
5. **Accept uncertainty:** Acknowledge risk and plan for flexibility

**Document:**
- What we learned (even if it's what doesn't work)
- Remaining unknowns and their potential impact
- Recommended approach despite uncertainty
- Plan for learning during implementation
```

---

## Best Practices

### DO:
✅ **Define clear, specific research questions**
   - Bad: "Research machine learning"
   - Good: "Can scikit-learn handle our 100k row dataset in < 5 seconds?"

✅ **Set and respect timeboxes**
   - Use timer/tracking
   - Stop at time limit
   - Document why if you need more time

✅ **Focus on answering questions, not perfection**
   - POC code can be messy
   - Goal is learning, not production code

✅ **Document as you go**
   - Don't wait until end
   - Capture thoughts and findings immediately

✅ **Include quantitative data**
   - Performance metrics
   - Benchmark results
   - Comparison numbers

✅ **Identify what you didn't learn**
   - Remaining unknowns are valuable
   - Help scope future work

✅ **Share negative findings**
   - "This doesn't work" is a valid outcome
   - Saves team from repeating investigation

### DON'T:
❌ **Don't skip defining objectives**
   - Undefined spike = wasted time

❌ **Don't let spikes become implementation**
   - Spike code is exploratory, not production

❌ **Don't ignore the timebox**
   - Discipline is key to spike effectiveness

❌ **Don't research without documenting**
   - Lost knowledge helps no one

❌ **Don't keep findings to yourself**
   - Share even if inconclusive

❌ **Don't feel pressure to have "the answer"**
   - "Need more info" is a valid conclusion

❌ **Don't perfect POC code**
   - Good enough to learn is enough

---

## Examples

### Example 1: Technology Evaluation

**Spike: Evaluate Redis vs Memcached for Caching**

**Timebox:** 3 hours

**Research Questions:**
1. Which has better performance for our use case?
2. Which has better Python library support?
3. Which is easier to deploy/maintain?

**POC Code:**
```python
# benchmark_cache.py
import time
import redis
import memcache

def benchmark_redis():
    r = redis.Redis()
    start = time.time()
    for i in range(10000):
        r.set(f'key_{i}', f'value_{i}')
        r.get(f'key_{i}')
    return time.time() - start

def benchmark_memcached():
    mc = memcache.Client(['127.0.0.1:11211'])
    start = time.time()
    for i in range(10000):
        mc.set(f'key_{i}', f'value_{i}')
        mc.get(f'key_{i}')
    return time.time() - start

# Results:
# Redis: 0.82s
# Memcached: 0.91s
```

**Recommendation:** Use Redis
- Better performance (10% faster)
- Better Python library (redis-py)
- More features (persistence, pub/sub) for future needs

---

### Example 2: Bug Investigation

**Spike: Investigate Intermittent Database Connection Failures**

**Timebox:** 4 hours

**Findings:**
- Connection pool exhaustion under load
- No connection timeout configured
- Long-running queries holding connections

**Recommendation:**
- Set connection pool size to 20 (from 10)
- Add 30s connection timeout
- Implement connection health checks
- Add query performance monitoring

---

### Example 3: Architecture Decision

**Spike: Microservices vs Monolith for New Feature**

**Comparison:**
| Criterion | Microservice | Monolith |
|-----------|--------------|----------|
| Development speed | Slower (new service) | Faster |
| Deployment complexity | Higher | Lower |
| Future flexibility | Higher | Lower |
| Team familiarity | Low | High |
| Current load | Overkill | Sufficient |

**Recommendation:** Start with monolith
- Faster to market
- Team familiar with codebase
- Current scale doesn't justify microservice
- Can extract later if needed

---

## Related Workflows

**Before This Workflow:**
- [[pm-001]](../project-management/progress_tracking.md) - Identify need for research

**After This Workflow:**
- [[dev-001]](../development/environment_initialization.md) - Set up for implementation
- [[dev-010]](../development/refactoring_strategy.md) - Implement findings

**Complementary Workflows:**
- [[arch-001]](../architecture/system_architecture_design.md) - Architecture decisions
- [[dev-011]](../development/technical_debt_mgmt.md) - Managing technical debt

---

## Tags
`research` `spike` `discovery` `prototyping` `investigation` `time-boxing` `decision-making`

## Additional Metadata
**Automation Potential:** Low (inherently exploratory)
**Risk Level:** Low (time-boxed, low commitment)
**Team Size:** Solo (occasionally paired)
**Environment:** Development
**Last Reviewed:** 2025-10-27
**Next Review Due:** 2026-04-27
