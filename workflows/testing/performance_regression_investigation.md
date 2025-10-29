# Performance Regression Investigation

**ID:** tes-005  
**Category:** Testing  
**Priority:** MEDIUM  
**Complexity:** Advanced  
**Estimated Time:** 60-120 minutes  
**Last Updated:** 2025-10-26

---

## Purpose

**What:** Systematically identify, diagnose, and resolve performance degradations in code

**Why:** Performance regressions can silently degrade user experience and increase infrastructure costs. Catching them early prevents production issues and maintains system SLAs

**When to use:**
- After major refactorings or feature additions
- When users report slowness
- During code review with performance concerns
- After dependency upgrades
- Before production releases (as part of CI/CD)
- When monitoring shows increased latency/CPU/memory

---

## Prerequisites

**Required:**
- [ ] Baseline performance metrics from before regression
- [ ] Access to profiling tools (cProfile, perf, Chrome DevTools)
- [ ] Representative test data or production-like environment
- [ ] Version control history to identify changes
- [ ] Monitoring/APM data (if available)

**Check before starting:**
```bash
# Python profiling tools
python -m cProfile --help
pip show memory_profiler line_profiler

# System profiling
which perf  # Linux
which dtrace  # macOS
which perfmon  # Windows

# Load testing tools
which ab  # Apache Bench
which wrk
pip show locust

# Check git history is available
git log --oneline -20
```

---

## Implementation Steps

### Step 1: Confirm the Regression

**What:** Verify that performance has actually degraded and establish baseline metrics

**How:**

**Gather Evidence:**

```python
# Run performance comparison
import time
import statistics

def benchmark_function(func, *args, iterations=100):
    """Benchmark a function's execution time"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append(end - start)
    
    return {
        'mean': statistics.mean(times),
        'median': statistics.median(times),
        'stdev': statistics.stdev(times) if len(times) > 1 else 0,
        'min': min(times),
        'max': max(times),
        'p95': statistics.quantiles(times, n=20)[18],  # 95th percentile
        'p99': statistics.quantiles(times, n=100)[98]  # 99th percentile
    }

# Compare current vs baseline
current = benchmark_function(process_data, test_data)
baseline = load_baseline_metrics()  # From previous run

print(f"Current p95: {current['p95']*1000:.2f}ms")
print(f"Baseline p95: {baseline['p95']*1000:.2f}ms")
print(f"Regression: {(current['p95']/baseline['p95']-1)*100:+.1f}%")
```

**Load Testing (for APIs/services):**

```bash
# Baseline test
ab -n 1000 -c 10 http://localhost:8000/api/users/ > baseline.txt

# Current test  
ab -n 1000 -c 10 http://localhost:8000/api/users/ > current.txt

# Compare
echo "Baseline:"
grep "Requests per second" baseline.txt
echo "Current:"
grep "Requests per second" current.txt
```

```bash
# More sophisticated with wrk
wrk -t4 -c100 -d30s --latency http://localhost:8000/api/users/

# Results show:
# Requests/sec, Latency distribution (p50, p75, p90, p99)
```

**Decision Criteria:**

```python
def is_significant_regression(current, baseline, threshold=0.1):
    """Determine if performance difference is significant"""
    
    # Calculate percentage change
    change = (current['p95'] - baseline['p95']) / baseline['p95']
    
    # Check if exceeds threshold (e.g., 10% slower)
    if change > threshold:
        # Also check if it's statistically significant
        # (not just noise)
        combined_stdev = (current['stdev'] + baseline['stdev']) / 2
        
        if abs(current['mean'] - baseline['mean']) > 2 * combined_stdev:
            return True, f"Significant regression: {change*100:+.1f}%"
    
    return False, "No significant regression"
```

**Verification:**
- [ ] Regression is reproducible (not a one-time fluke)
- [ ] Measured on same hardware/environment
- [ ] Used representative data/load
- [ ] Compared apples-to-apples (same test conditions)

**If This Fails:**
→ Ensure test environment is isolated (no background processes)
→ Run more iterations for statistical significance
→ Check if baseline data is from comparable conditions

---

### Step 2: Identify Changed Code

**What:** Narrow down which code changes caused the regression

**How:**

**Git Bisect (Automated):**

```bash
# Start bisect session
git bisect start

# Mark current version as bad
git bisect bad

# Mark last known good version
git bisect good v1.2.0  # or commit hash

# Git will checkout middle commit
# Run your performance test
./run_perf_test.sh

# If slow:
git bisect bad

# If fast:
git bisect good

# Git will narrow down to the commit that introduced regression
# After several iterations:
# "abc1234 is the first bad commit"
```

**Automated Bisect Script:**

```bash
#!/bin/bash
# bisect_perf.sh - Automated bisect

# Build/install
make build || exit 125  # 125 = skip this commit

# Run performance test
python -m pytest tests/test_performance.py::test_critical_path

# Check if performance is acceptable
python check_perf_threshold.py
exit $?  # 0 = good, 1 = bad, 125 = skip
```

```bash
git bisect start HEAD v1.2.0
git bisect run ./bisect_perf.sh
```

**Manual Code Review:**

```bash
# Show commits since last good version
git log --oneline v1.2.0..HEAD

# Show changes in specific path
git log --oneline --name-status v1.2.0..HEAD -- src/critical_module/

# View specific commit changes
git show abc1234

# Compare specific versions
git diff v1.2.0..HEAD -- src/critical_module/processor.py
```

**Analyze Changed Files:**

```python
# check_changes.py - Find changed hot path files
import subprocess
import json

def get_changed_files(since='v1.2.0'):
    """Get files changed since version"""
    result = subprocess.run(
        ['git', 'diff', '--name-only', f'{since}..HEAD'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip().split('\n')

def identify_hot_path_changes(changed_files, hot_paths):
    """Find if hot path code was changed"""
    hot_changes = []
    
    for file in changed_files:
        for hot_path in hot_paths:
            if hot_path in file:
                hot_changes.append(file)
    
    return hot_changes

# Known performance-critical paths
hot_paths = [
    'src/core/processor',
    'src/data/query',
    'src/api/handlers'
]

changed = get_changed_files('v1.2.0')
suspect_files = identify_hot_path_changes(changed, hot_paths)

print("Changed files in hot paths:")
for file in suspect_files:
    print(f"  - {file}")
```

**Verification:**
- [ ] Identified specific commit(s) that introduced regression
- [ ] Reviewed code changes in those commits
- [ ] Changes are in performance-critical path
- [ ] Have hypothesis about what caused slowdown

**If This Fails:**
→ Regression may be from cumulative changes, not single commit
→ Check dependency updates (requirements.txt, package.json)
→ Environment or data changes might be the cause

---

### Step 3: Profile the Slow Code

**What:** Use profiling tools to identify specific bottlenecks

**How:**

**Python - cProfile:**

```bash
# Profile entire script
python -m cProfile -o profile.stats script.py

# Analyze results
python -m pstats profile.stats
# In pstats shell:
# sort cumulative
# stats 20
```

```python
# Programmatic profiling
import cProfile
import pstats
from pstats import SortKey

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Code to profile
    result = slow_function()
    
    profiler.disable()
    
    # Print results
    stats = pstats.Stats(profiler)
    stats.sort_stats(SortKey.CUMULATIVE)
    stats.print_stats(20)  # Top 20 functions
    
    return result
```

**Python - line_profiler (line-by-line):**

```bash
# Install
pip install line_profiler

# Add @profile decorator to function
# No import needed!

# Run
kernprof -l -v script.py

# Shows time per line
```

```python
# Example output:
# Line #      Hits         Time  Per Hit   % Time  Line Contents
# ==============================================================
#      8                                           @profile
#      9                                           def slow_function():
#     10      1000      1000.0      1.0     10.0      result = []
#     11   1000000    500000.0      0.5     50.0      for i in range(1000):
#     12   1000000    400000.0      0.4     40.0          result.append(i ** 2)
#     13      1000      1000.0      1.0      1.0      return result
```

**Python - memory_profiler:**

```bash
pip install memory_profiler

# Decorate function with @profile
python -m memory_profiler script.py
```

```python
from memory_profiler import profile

@profile
def memory_intensive():
    large_list = [i for i in range(1000000)]
    return sum(large_list)

# Output shows memory usage per line
```

**JavaScript - Chrome DevTools:**

```javascript
// 1. Open Chrome DevTools (F12)
// 2. Go to Performance tab
// 3. Click Record
// 4. Perform slow action
// 5. Stop recording
// 6. Analyze flame graph

// Programmatic profiling
console.time('operation');
expensiveOperation();
console.timeEnd('operation');

// More detailed
performance.mark('start');
expensiveOperation();
performance.mark('end');
performance.measure('operation', 'start', 'end');
console.log(performance.getEntriesByName('operation'));
```

**Node.js - Built-in Profiler:**

```bash
# Generate CPU profile
node --prof app.js

# Process the profile
node --prof-process isolate-0x*.log > processed.txt

# Look for hot functions in processed.txt
```

**System-Level Profiling (Linux):**

```bash
# CPU profiling with perf
sudo perf record -g ./myapp
sudo perf report

# Flame graph
perf record -F 99 -g ./myapp
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# I/O profiling
sudo iotop -o -b -n 10

# Memory profiling
valgrind --tool=massif ./myapp
```

**Verification:**
- [ ] Identified specific functions/lines that are slow
- [ ] Know what percentage of time is spent where
- [ ] Found the actual bottleneck (not just symptoms)
- [ ] Have concrete profiling data to guide fixes

**If This Fails:**
→ Profiling overhead might hide issue - use sampling profilers
→ Check if bottleneck is in I/O, not CPU
→ Look for network calls, database queries
→ Check system resources (disk, memory pressure)

---

### Step 4: Analyze Root Cause

**What:** Determine why the code is slow

**How:**

**Common Performance Issues:**

**1. Algorithmic Complexity**

```python
# BAD - O(n²) nested loop
def find_duplicates_slow(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
# Time: 50ms for 100 items, 5000ms for 1000 items

# GOOD - O(n) with set
def find_duplicates_fast(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
# Time: 1ms for 100 items, 10ms for 1000 items
```

**2. N+1 Query Problem**

```python
# BAD - Queries in loop (N+1 problem)
def get_user_posts_slow(user_ids):
    results = []
    for user_id in user_ids:  # 1 query
        user = db.query(User).get(user_id)
        posts = db.query(Post).filter_by(user_id=user_id).all()  # N queries
        results.append({'user': user, 'posts': posts})
    return results
# 101 queries for 100 users!

# GOOD - Eager loading
def get_user_posts_fast(user_ids):
    users = db.query(User).filter(User.id.in_(user_ids)).all()  # 1 query
    posts = db.query(Post).filter(Post.user_id.in_(user_ids)).all()  # 1 query
    
    # Group posts by user
    posts_by_user = {}
    for post in posts:
        posts_by_user.setdefault(post.user_id, []).append(post)
    
    return [{'user': u, 'posts': posts_by_user.get(u.id, [])} for u in users]
# 2 queries for 100 users!
```

**3. Memory Allocation**

```python
# BAD - Creates many intermediate objects
def process_data_slow(data):
    result = []
    for item in data:
        result = result + [item.upper()]  # Creates new list each time
    return result

# GOOD - Modifies in place
def process_data_fast(data):
    result = []
    for item in data:
        result.append(item.upper())  # Amortized O(1)
    return result

# BETTER - List comprehension (optimized in C)
def process_data_faster(data):
    return [item.upper() for item in data]
```

**4. Blocking I/O**

```python
# BAD - Sequential blocking calls
def fetch_all_slow(urls):
    results = []
    for url in urls:
        response = requests.get(url)  # Blocks
        results.append(response.json())
    return results
# Time: 10s for 10 URLs (1s each)

# GOOD - Concurrent requests
import asyncio
import aiohttp

async def fetch_all_fast(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [session.get(url) for url in urls]
        responses = await asyncio.gather(*tasks)
        return [await r.json() for r in responses]
# Time: 1s for 10 URLs (parallel)
```

**5. Inefficient Data Structures**

```python
# BAD - Linear search in list
items = []  # List
def contains_slow(item):
    return item in items  # O(n)

# GOOD - Constant time lookup in set
items = set()  # Set
def contains_fast(item):
    return item in items  # O(1)
```

**Diagnostic Questions:**

- Is the algorithm optimal for the data size?
- Are there unnecessary database queries?
- Is there blocking I/O that could be async?
- Are objects being created/destroyed excessively?
- Is the right data structure being used?
- Are there missing indexes on database queries?
- Is computation being repeated unnecessarily?
- Are resources being leaked (connections, file handles)?

**Verification:**
- [ ] Identified specific anti-pattern or inefficiency
- [ ] Understand why it's slow (not just what is slow)
- [ ] Have a concrete hypothesis to test
- [ ] Can explain the root cause

**If This Fails:**
→ Compare with previous fast version side-by-side
→ Ask: "What changed in the slow version?"
→ Look for added features that might be expensive

---

### Step 5: Implement and Verify Fix

**What:** Fix the performance issue and confirm improvement

**How:**

**Make Targeted Fix:**

```python
# Before: O(n²) algorithm
def merge_datasets_slow(list1, list2):
    result = []
    for item1 in list1:
        for item2 in list2:
            if item1['id'] == item2['id']:
                result.append({**item1, **item2})
    return result

# After: O(n) with hash map
def merge_datasets_fast(list1, list2):
    lookup = {item['id']: item for item in list2}  # O(n)
    result = []
    for item1 in list1:  # O(n)
        if item1['id'] in lookup:
            result.append({**item1, **lookup[item1['id']]})
    return result
```

**Add Performance Test:**

```python
# tests/test_performance.py
import pytest
import time

def test_merge_performance():
    """Ensure merge stays fast"""
    # Generate test data
    list1 = [{'id': i, 'name': f'item{i}'} for i in range(1000)]
    list2 = [{'id': i, 'value': i*2} for i in range(1000)]
    
    # Benchmark
    start = time.perf_counter()
    result = merge_datasets_fast(list1, list2)
    duration = time.perf_counter() - start
    
    # Assert performance threshold
    assert duration < 0.1, f"merge took {duration:.3f}s, expected < 0.1s"
    assert len(result) == 1000

@pytest.mark.benchmark
def test_merge_benchmark(benchmark):
    """Continuous performance monitoring with pytest-benchmark"""
    list1 = [{'id': i, 'name': f'item{i}'} for i in range(1000)]
    list2 = [{'id': i, 'value': i*2} for i in range(1000)]
    
    result = benchmark(merge_datasets_fast, list1, list2)
    assert len(result) == 1000
```

**Verify Improvement:**

```python
# compare_performance.py
import time
import statistics

def compare_implementations(func_old, func_new, *args, iterations=100):
    """Compare old vs new implementation"""
    
    # Benchmark old
    old_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func_old(*args)
        old_times.append(time.perf_counter() - start)
    
    # Benchmark new
    new_times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func_new(*args)
        new_times.append(time.perf_counter() - start)
    
    old_p95 = statistics.quantiles(old_times, n=20)[18]
    new_p95 = statistics.quantiles(new_times, n=20)[18]
    
    improvement = (old_p95 - new_p95) / old_p95 * 100
    
    print(f"Old p95: {old_p95*1000:.2f}ms")
    print(f"New p95: {new_p95*1000:.2f}ms")
    print(f"Improvement: {improvement:.1f}%")
    
    return improvement

# Run comparison
improvement = compare_implementations(
    merge_datasets_slow,
    merge_datasets_fast,
    test_list1,
    test_list2
)

assert improvement > 50, "Expected at least 50% improvement"
```

**Add Monitoring:**

```python
# Add timing decorator for production monitoring
import functools
import time

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            duration = time.perf_counter() - start
            # Log to monitoring system
            metrics.timing(f'{func.__name__}.duration', duration)
            
            # Alert if too slow
            if duration > THRESHOLD:
                logger.warning(
                    f'{func.__name__} took {duration:.3f}s (threshold: {THRESHOLD}s)'
                )
    
    return wrapper

@monitor_performance
def merge_datasets(list1, list2):
    # Implementation
    pass
```

**Verification:**
- [ ] Fix improves performance significantly (>20%)
- [ ] Fix doesn't break existing functionality (tests pass)
- [ ] Performance test added to prevent regression
- [ ] Monitoring in place to catch future issues

**If This Fails:**
→ Fix might address symptoms, not root cause
→ Test if bottleneck moved to different area
→ Check if fix introduces new problems

---

### Step 6: Document and Prevent Recurrence

**What:** Document findings and add safeguards against future regressions

**How:**

**Document the Investigation:**

```markdown
# Performance Regression Investigation - 2025-10-26

## Issue
API response time increased from 50ms to 500ms (10x slower) for `/api/users` endpoint.

## Root Cause
Commit abc1234 changed user query from indexed lookup to full table scan:
- Before: `SELECT * FROM users WHERE id = ?` (indexed)
- After: `SELECT * FROM users WHERE LOWER(email) LIKE ?` (full scan)

## Impact
- 10x slower for single user queries
- Database CPU increased 5x
- User complaints about slow page loads

## Solution
Added database index on `LOWER(email)`:
```sql
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

## Results
- Response time back to 45ms (10% faster than baseline!)
- Database CPU usage normal
- 1000 req/s throughput maintained

## Prevention
- Added performance test that fails if > 100ms
- Added query review checklist (check for indexes)
- Set up APM alerts for p95 > 200ms
```

**Add Performance Tests to CI:**

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [pull_request]

jobs:
  perf-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Run performance tests
        run: |
          pytest tests/test_performance.py --benchmark-only
      
      - name: Check regression
        run: |
          python scripts/check_perf_regression.py \
            --baseline performance_baseline.json \
            --threshold 0.20  # Fail if 20% slower
```

**Performance Test Suite:**

```python
# tests/test_performance.py
import pytest

# Mark performance-critical functions
PERF_THRESHOLDS = {
    'query_users': 0.050,  # 50ms
    'process_batch': 1.0,  # 1s
    'generate_report': 5.0,  # 5s
}

@pytest.mark.performance
class TestPerformance:
    def test_query_users_performance(self, benchmark):
        """Ensure user queries stay fast"""
        result = benchmark(query_users, limit=100)
        assert len(result) == 100
        
        # Benchmark plugin automatically tracks timing
        # and compares to baseline
    
    def test_batch_processing_scale(self):
        """Verify batch processing scales linearly"""
        times = {}
        
        for size in [100, 1000, 10000]:
            start = time.perf_counter()
            process_batch(generate_test_data(size))
            times[size] = time.perf_counter() - start
        
        # Should be roughly linear (within 2x)
        ratio = times[10000] / times[1000]
        assert 8 < ratio < 12, f"Non-linear scaling: {ratio}x"
```

**Code Review Checklist:**

```markdown
## Performance Review Checklist

Before approving changes to hot paths, verify:

- [ ] No N+1 query problems (check for queries in loops)
- [ ] Database queries have appropriate indexes
- [ ] Algorithm complexity is reasonable for data size
- [ ] No unnecessary data copies or allocations
- [ ] I/O operations are async where possible
- [ ] Caching used for expensive operations
- [ ] Resource cleanup (connections, files) happens
- [ ] Performance tests pass in CI
- [ ] Large data tested (not just small examples)
```

**Verification:**
- [ ] Investigation documented with root cause
- [ ] Performance tests added to prevent regression
- [ ] Team knows how to avoid similar issues
- [ ] Monitoring/alerts in place

**If This Fails:**
→ Document anyway - learning from incidents is valuable
→ Schedule team review/retro to discuss findings
→ Add to onboarding materials

---

## Verification Checklist

After completing this workflow:

- [ ] Regression confirmed with reproducible benchmarks
- [ ] Root cause identified through profiling
- [ ] Fix implemented and improves performance significantly
- [ ] No functional regressions introduced
- [ ] Performance tests added to prevent recurrence
- [ ] Investigation documented for team learning
- [ ] Monitoring/alerts configured
- [ ] Code review checklist updated

---

## Common Issues & Solutions

### Issue: Can't reproduce the regression

**Symptoms:**
- Performance varies wildly between runs
- Can't get consistent measurements
- Production is slow but dev is fast

**Solution:**
```python
# Ensure consistent environment
def setup_test_environment():
    # Fix random seeds
    random.seed(42)
    np.random.seed(42)
    
    # Clear caches
    cache.clear()
    
    # Ensure fresh database
    db.session.rollback()
    
    # Disable background tasks
    scheduler.pause()
    
    # Run garbage collection
    import gc
    gc.collect()

# Run multiple iterations and use median
def stable_benchmark(func, iterations=10):
    times = []
    
    for _ in range(iterations):
        setup_test_environment()
        
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    
    # Use median (more stable than mean)
    return statistics.median(times)
```

**Prevention:**
- Use production-like data and load
- Test on similar hardware
- Isolate test environment
- Run enough iterations for statistical significance

---

### Issue: Fix causes other problems

**Symptoms:**
- Performance improved but functionality broke
- Memory usage increased
- Different part of code is now slow

**Solution:**
```python
# Test comprehensively
def test_fix_thoroughly():
    # 1. Functional correctness
    assert process_data(input) == expected_output
    
    # 2. Performance improvement
    assert benchmark(process_data) < baseline * 0.8
    
    # 3. Memory usage
    import tracemalloc
    tracemalloc.start()
    process_data(large_input)
    current, peak = tracemalloc.get_traced_memory()
    assert peak < 100 * 1024 * 1024  # 100MB limit
    
    # 4. Edge cases
    assert process_data([]) == []
    assert process_data(None) raises ValueError
    
    # 5. Full integration test
    end_to_end_test()
```

**Prevention:**
- Run full test suite, not just perf tests
- Profile memory, not just CPU
- Check for moved bottlenecks
- Get code review before merging

---

### Issue: Regression is environmental, not code

**Symptoms:**
- Same code, different performance
- Varies by machine/time/load
- Profiler doesn't show code issues

**Solution:**
```bash
# Check system resources
top  # CPU usage
free -h  # Memory
iostat  # Disk I/O
netstat -s  # Network stats

# Check database
EXPLAIN ANALYZE SELECT ...;  # Slow query analysis
SHOW PROCESSLIST;  # Active queries

# Check for resource contention
docker stats  # If containerized
kubectl top pods  # If Kubernetes

# Check logs for anomalies
grep -i "error\|slow\|timeout" app.log

# Check external services
curl -w "@curl-format.txt" https://api.external.com
```

**Prevention:**
- Monitor system resources
- Use APM (Application Performance Monitoring)
- Set up alerts for anomalies
- Load test in production-like environment

---

## Examples

### Example 1: Django ORM N+1 Query

**Context:** API endpoint fetching users with their posts became 100x slower

**Investigation:**
```python
# Profile queries with django-debug-toolbar
from django.db import connection
from django.test.utils import override_settings

@override_settings(DEBUG=True)
def test_query_count():
    connection.queries_log.clear()
    
    # Call the slow endpoint
    response = client.get('/api/users-with-posts/')
    
    # Check query count
    num_queries = len(connection.queries)
    print(f"Queries: {num_queries}")
    
    for query in connection.queries:
        print(query['sql'])
    
    # For 100 users, saw 201 queries! (1 + 100*2)
```

**Root Cause:**
```python
# BAD - N+1 queries
def get_users_with_posts():
    users = User.objects.all()  # 1 query
    result = []
    for user in users:
        posts = user.posts.all()  # N queries!
        comments = [p.comments.count() for p in posts]  # N*M queries!
        result.append({'user': user, 'posts': posts})
    return result
```

**Fix:**
```python
# GOOD - Eager loading
def get_users_with_posts():
    users = User.objects.prefetch_related(
        'posts',
        'posts__comments'
    ).all()  # 3 queries total!
    
    result = []
    for user in users:
        result.append({
            'user': user,
            'posts': user.posts.all()  # No query - already loaded
        })
    return result
```

**Result:** 201 queries → 3 queries, 100x faster

---

### Example 2: React Component Re-rendering

**Context:** Dashboard page became sluggish with large datasets

**Investigation:**
```javascript
// Profile with React DevTools Profiler
import { Profiler } from 'react';

function Dashboard() {
  return (
    <Profiler id="Dashboard" onRender={onRenderCallback}>
      <UserList users={users} />
    </Profiler>
  );
}

function onRenderCallback(id, phase, actualDuration) {
  console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

// Found: UserList re-renders every second even when data unchanged!
```

**Root Cause:**
```javascript
// BAD - Creates new object every render
function Dashboard() {
  const [users, setUsers] = useState([]);
  
  // This object is recreated every render!
  const config = { sortBy: 'name', limit: 100 };
  
  return <UserList users={users} config={config} />;
}
```

**Fix:**
```javascript
// GOOD - Memoize objects and callbacks
import { useMemo, useCallback } from 'react';

function Dashboard() {
  const [users, setUsers] = useState([]);
  
  // Same object unless dependencies change
  const config = useMemo(
    () => ({ sortBy: 'name', limit: 100 }),
    []
  );
  
  // Wrap UserList in React.memo to prevent unnecessary re-renders
  return <UserList users={users} config={config} />;
}

const UserList = React.memo(function UserList({ users, config }) {
  // Only re-renders when users or config actually change
  return users.map(u => <UserCard key={u.id} user={u} />);
});
```

**Result:** 60 FPS → smooth scrolling, CPU usage down 80%

---

## Best Practices

### DO:
✅ Establish baseline metrics before investigating
✅ Use profiling tools to find actual bottlenecks
✅ Focus on the hottest paths (80/20 rule)
✅ Make one change at a time and measure
✅ Add performance tests to prevent regressions
✅ Document findings for team learning
✅ Consider trade-offs (speed vs memory vs complexity)
✅ Test with production-like data and load
✅ Monitor performance in production
✅ Review performance implications in code reviews

### DON'T:
❌ Optimize without profiling first (premature optimization)
❌ Trust intuition over measurements
❌ Ignore the 80/20 rule (focus on hot paths)
❌ Make multiple changes at once
❌ Fix without verifying improvement
❌ Skip documentation of root cause
❌ Forget to add regression tests
❌ Sacrifice correctness for speed
❌ Over-optimize cold paths
❌ Ignore memory while optimizing CPU

---

## Related Workflows

**Prerequisites:**
- `dev-008`: Unit Testing Setup - Testing infrastructure for perf tests
- `devops-008`: Application Performance Monitoring - Production monitoring
- `qa-009`: Regression Test Suite - Adding perf tests to suite

**Next Steps:**
- `devops-003`: Profiling and Optimization - Systematic optimization techniques
- `qa-007`: Test Coverage Analysis - Understanding code hot paths
- `devops-008`: Application Performance Monitoring - Continuous monitoring

**Alternatives:**
- Load testing (`devops-006`) - Proactive performance testing
- Chaos engineering - Testing under adverse conditions
- Capacity planning - Scaling instead of optimizing

---

## Tags
`testing` `performance` `optimization` `profiling` `regression` `debugging` `benchmarking` `monitoring` `performance-testing` `bottleneck-analysis`
