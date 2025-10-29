# Log Analysis

**ID:** dev-007  
**Category:** Development  
**Priority:** MEDIUM  
**Complexity:** Intermediate  
**Estimated Time:** 30-60 minutes  
**Last Updated:** 2025-10-25

---

## Purpose

**What:** Systematic workflow for analyzing application logs to diagnose issues, identify patterns, monitor performance, and improve system observability.

**Why:** Effective log analysis enables rapid issue diagnosis, proactive problem detection, performance optimization, and improved understanding of system behavior. Logs are often the first and most detailed source of information when investigating production issues.

**When to use:**
- Investigating production incidents or errors
- Debugging application behavior
- Performance troubleshooting and optimization
- Security incident investigation
- Understanding user behavior patterns
- Validating deployment success
- Proactive monitoring and alerting

---

## Prerequisites

**Required:**
- [ ] Access to application logs (files, aggregation platform, or cloud provider)
- [ ] Understanding of log levels (DEBUG, INFO, WARN, ERROR, FATAL)
- [ ] Basic command-line tools (grep, awk, sed) or log viewer
- [ ] Knowledge of application architecture and request flow
- [ ] Timestamps and timezone understanding

**Check before starting:**
```bash
# Verify log access
ls -lh /var/log/app/*.log
# or for Docker
docker logs container-name --tail 100

# Check log aggregation access (if applicable)
# ELK: http://localhost:5601
# Splunk: http://localhost:8000
# Datadog, CloudWatch, etc.

# Verify log format and parsing
head -n 10 /var/log/app/application.log
```

---

## Implementation Steps

### Step 1: Define Investigation Scope

**What:** Clearly identify what you're investigating and establish the time window and log sources to examine.

**How:**
1. Document the problem or question you're investigating
2. Identify relevant services/components
3. Determine the time window (start/end timestamps)
4. List all relevant log sources
5. Note any correlation IDs or request identifiers

**Code/Commands:**
```bash
# Define your investigation parameters
export INVESTIGATION="High error rate on /api/users endpoint"
export START_TIME="2025-10-25T14:00:00Z"
export END_TIME="2025-10-25T15:00:00Z"
export LOG_PATH="/var/log/app"
export CORRELATION_ID="req-abc123"  # if applicable

# Document the scope
cat << EOF > investigation_notes.md
# Log Investigation: $(date)

**Issue:** ${INVESTIGATION}
**Time Window:** ${START_TIME} to ${END_TIME}
**Services:** api-server, auth-service, database
**Correlation ID:** ${CORRELATION_ID}

## Timeline:
- Initial report: 14:30 UTC
- User impact: ~500 users
- Current status: Investigating

## Key Questions:
1. What errors are occurring?
2. What's the error rate?
3. When did it start?
4. Which endpoints/users affected?
5. Any pattern in failures?
EOF
```

**Verification:**
- [ ] Investigation scope clearly documented
- [ ] Time window identified
- [ ] Relevant log sources listed
- [ ] Key questions defined
- [ ] Expected log volume is manageable

**If This Fails:**
→ If time window unclear, start with recent logs (last hour) and expand
→ If too many log sources, prioritize based on architecture (start with failing component)
→ If unsure what to investigate, start with ERROR and FATAL level logs

---

### Step 2: Access and Aggregate Logs

**What:** Collect logs from all relevant sources into a format suitable for analysis.

**How:**
1. Download or access logs from all sources
2. Merge logs from multiple sources if needed
3. Ensure consistent timestamp format
4. Filter to relevant time window
5. Create working copies to avoid modifying originals

**Code/Commands:**
```bash
# Create investigation directory
mkdir -p log_investigation_$(date +%Y%m%d_%H%M)
cd log_investigation_$(date +%Y%m%d_%H%M)

# Method 1: Local log files
# Copy relevant logs to working directory
cp /var/log/app/application.log app_logs.log
cp /var/log/nginx/access.log nginx_logs.log

# Extract time window (adjust time format to match your logs)
grep -E "2025-10-25T(14|15):" app_logs.log > app_filtered.log

# Method 2: Docker logs
docker logs api-server --since "2025-10-25T14:00:00Z" \
    --until "2025-10-25T15:00:00Z" > api_server.log

# Method 3: Kubernetes logs
kubectl logs deployment/api-server --since-time="2025-10-25T14:00:00Z" \
    --timestamps > k8s_api.log

# Method 4: Cloud provider logs (AWS CloudWatch example)
aws logs filter-log-events \
    --log-group-name /aws/lambda/my-function \
    --start-time $(date -d "${START_TIME}" +%s)000 \
    --end-time $(date -d "${END_TIME}" +%s)000 \
    --output json > cloudwatch_logs.json

# Method 5: Using journalctl (systemd)
journalctl -u myapp.service \
    --since "${START_TIME}" \
    --until "${END_TIME}" > systemd_logs.log

# Merge multiple sources with timestamps
cat app_filtered.log nginx_logs.log | sort -k1,2 > merged_timeline.log
```

**Verification:**
- [ ] Logs successfully accessed from all sources
- [ ] Time window correctly filtered
- [ ] Timestamps are in consistent format
- [ ] Working copies created
- [ ] Log volume is reasonable (not empty, not too large)

**If This Fails:**
→ If logs are too large (>1GB), use streaming tools or break into chunks
→ If timestamps inconsistent, normalize them with awk/sed before merging
→ If access denied, verify permissions or credentials
→ If logs missing, check log rotation or archival systems

---

### Step 3: Filter and Search for Patterns

**What:** Use command-line tools or log viewers to filter, search, and identify relevant log entries.

**How:**
1. Start with high-level filtering (ERROR/WARN levels)
2. Search for error messages and exceptions
3. Look for frequency patterns
4. Extract relevant fields (status codes, durations, IPs)
5. Create focused subsets for deeper analysis

**Code/Commands:**
```bash
# Count log entries by level
grep -oP '(DEBUG|INFO|WARN|ERROR|FATAL)' merged_timeline.log | sort | uniq -c

# Extract all ERROR and FATAL entries
grep -E '(ERROR|FATAL)' merged_timeline.log > errors_only.log

# Count occurrences of specific errors
grep "ERROR" errors_only.log | cut -d':' -f4- | sort | uniq -c | sort -rn | head -20

# Search for specific error patterns
grep -i "connection timeout" merged_timeline.log
grep -i "null pointer" merged_timeline.log
grep -i "database" errors_only.log

# Extract HTTP status codes (for web logs)
grep -oP 'HTTP/\d\.\d" \d{3}' nginx_logs.log | \
    awk '{print $2}' | sort | uniq -c | sort -rn

# Find slow requests (example: > 1000ms)
grep -oP 'duration=\d+' app_filtered.log | \
    awk -F'=' '$2 > 1000 {print}' | wc -l

# Extract correlation IDs for failed requests
grep "ERROR" app_filtered.log | grep -oP 'request_id=[a-zA-Z0-9-]+' | \
    cut -d'=' -f2 > failed_request_ids.txt

# Timeline of errors (hourly buckets)
grep "ERROR" merged_timeline.log | \
    awk '{print $1" "$2}' | cut -d':' -f1 | uniq -c

# Search for user impact
grep "user_id=" errors_only.log | grep -oP 'user_id=\d+' | \
    sort -u | wc -l  # Unique affected users

# Performance analysis - extract response times
grep "duration=" app_filtered.log | \
    grep -oP 'duration=\d+' | \
    awk -F'=' '{sum+=$2; count++} END {print "Avg:", sum/count "ms"}'

# Find correlated events
for req_id in $(head -5 failed_request_ids.txt); do
    echo "=== Request: $req_id ==="
    grep "$req_id" merged_timeline.log
    echo ""
done
```

**Verification:**
- [ ] Error count and distribution identified
- [ ] Common error patterns extracted
- [ ] Affected users/requests quantified
- [ ] Performance metrics calculated
- [ ] Timeline of issues established
- [ ] Correlation IDs identified for deep dive

**If This Fails:**
→ If no patterns found, expand time window or check log level configuration
→ If too many results, add more specific filters (endpoint, user, error type)
→ If grep is slow, use awk or consider indexed tools (ripgrep, ag)
→ If log format unclear, sample a few entries manually first

---

### Step 4: Analyze Error Patterns and Root Causes

**What:** Deep-dive into specific errors to understand their root causes, identify commonalities, and determine system behavior.

**How:**
1. Group similar errors together
2. Extract full stack traces
3. Identify error propagation chains
4. Correlate with external events (deployments, traffic spikes)
5. Look for cascading failures

**Code/Commands:**
```bash
# Extract full stack traces
awk '/ERROR/{p=1} p; /^[^\s]/ && !/ERROR/{p=0}' errors_only.log > stack_traces.log

# Group by exception type
grep -oP 'Exception: \K[^:]+' stack_traces.log | sort | uniq -c | sort -rn

# Find first occurrence of each error type
for error_type in $(grep -oP 'Exception: \K[^:]+' stack_traces.log | sort -u); do
    echo "=== First occurrence of $error_type ==="
    grep -m 1 "$error_type" stack_traces.log | head -20
    echo ""
done

# Analyze error rate over time (10-minute buckets)
grep "ERROR" merged_timeline.log | \
    awk '{print substr($2,1,5)}' | \
    uniq -c | \
    awk '{printf "%s: %d errors\n", $2, $1}'

# Check for correlation with specific actions
grep "database connection failed" errors_only.log | \
    grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}' | \
    uniq -c | \
    awk '{if ($1 > 10) print "Spike at", $2, "with", $1, "failures"}'

# Find cascading failures
# Look for rapid succession of errors
awk '{print $1, $2}' errors_only.log | \
    uniq -c | \
    awk '$1 > 5 {print "Burst of", $1, "errors at", $2, $3}'

# Identify potential triggers
echo "=== Checking deployment logs ==="
grep -E "(deployed|rollback|restart)" /var/log/deployment.log

echo "=== Checking resource metrics ==="
grep -E "(memory|cpu|disk)" /var/log/system.log | \
    awk -F'[=%]' '$2 > 90 {print}'

# Create error summary
cat << EOF > error_summary.md
# Error Analysis Summary

## Top 5 Errors:
$(grep "ERROR" errors_only.log | cut -d':' -f4- | sort | uniq -c | sort -rn | head -5)

## Error Timeline:
$(grep "ERROR" merged_timeline.log | awk '{print substr($2,1,5)}' | uniq -c)

## Affected Components:
$(grep "ERROR" errors_only.log | grep -oP 'component=\K[^,\s]+' | sort | uniq -c | sort -rn)

## Root Cause Hypothesis:
[Fill in based on findings]

## Contributing Factors:
- Factor 1
- Factor 2
EOF
```

**Verification:**
- [ ] Error types categorized and counted
- [ ] Root cause hypotheses documented
- [ ] Timeline of error onset identified
- [ ] Cascading effects understood
- [ ] External triggers checked (deployments, traffic)
- [ ] Summary document created

**If This Fails:**
→ If root cause unclear, trace specific request IDs through entire flow
→ If multiple simultaneous issues, analyze each independently
→ If errors intermittent, look for time-based patterns (hourly, daily)
→ If stack traces incomplete, check log level configuration

---

### Step 5: Trace Request Flows

**What:** Follow specific requests through multiple services to understand the complete failure path.

**How:**
1. Select representative failed requests
2. Extract all log entries for those correlation IDs
3. Reconstruct the timeline of events
4. Identify where and why the request failed
5. Document the flow for reference

**Code/Commands:**
```bash
# Select a sample of failed requests
head -3 failed_request_ids.txt > sample_requests.txt

# Trace each request through all logs
while read req_id; do
    echo "========================================" >> traces.log
    echo "REQUEST TRACE: $req_id" >> traces.log
    echo "========================================" >> traces.log
    
    # Search all log sources
    grep "$req_id" merged_timeline.log | sort >> traces.log
    
    # Extract key events
    echo -e "\nKey Events:" >> traces.log
    grep "$req_id" merged_timeline.log | \
        grep -E "(received|started|completed|failed|ERROR)" >> traces.log
    
    echo -e "\n" >> traces.log
done < sample_requests.txt

# Create visual timeline
cat << 'EOF' > create_timeline.py
import sys
import re
from datetime import datetime

req_id = sys.argv[1] if len(sys.argv) > 1 else None

print(f"Timeline for request: {req_id}\n")
print("Time          | Service        | Event")
print("--------------|----------------|----------------------------------")

with open('merged_timeline.log', 'r') as f:
    for line in f:
        if req_id and req_id not in line:
            continue
        
        # Extract timestamp, service, event
        match = re.search(r'(\d{2}:\d{2}:\d{2})', line)
        if match:
            timestamp = match.group(1)
            
            # Extract service (adjust pattern to your logs)
            service_match = re.search(r'service=(\w+)', line)
            service = service_match.group(1) if service_match else 'unknown'
            
            # Extract event type
            event = 'unknown'
            if 'started' in line.lower():
                event = '→ Request started'
            elif 'completed' in line.lower():
                event = '✓ Completed'
            elif 'error' in line.lower():
                event = '✗ ERROR'
                # Add error details
                error_match = re.search(r'ERROR:([^:]+)', line)
                if error_match:
                    event += f': {error_match.group(1).strip()}'
            elif 'calling' in line.lower():
                event = '↪ External call'
            
            print(f"{timestamp} | {service:14} | {event}")
EOF

# Run timeline for a specific request
python3 create_timeline.py "$(head -1 failed_request_ids.txt)"

# Calculate request latency at each stage
grep "$(head -1 failed_request_ids.txt)" merged_timeline.log | \
    awk '{print $2, $0}' | \
    awk '
        /started/ {start=$1}
        /completed|failed/ {
            end=$1
            split(start,s,":")
            split(end,e,":")
            duration=(e[3]-s[3])+(e[2]-s[2])*60+(e[1]-s[1])*3600
            print "Total duration:", duration, "seconds"
        }
    '

# Identify bottlenecks
grep "duration=" traces.log | \
    awk -F'[= ]' '{
        if ($0 ~ /service=/) {
            match($0, /service=([^ ]+)/, s);
            match($0, /duration=([0-9]+)/, d);
            if (length(d[1]) > 0) {
                sum[s[1]] += d[1];
                count[s[1]]++;
            }
        }
    }
    END {
        for (svc in sum) {
            avg = sum[svc]/count[svc];
            print svc ":", avg "ms average"
        }
    }' | sort -t':' -k2 -rn
```

**Verification:**
- [ ] Complete request flows documented
- [ ] Failure points identified
- [ ] Latency at each stage measured
- [ ] Bottlenecks or slow operations found
- [ ] Service dependencies understood
- [ ] Timeline makes logical sense

**If This Fails:**
→ If correlation ID missing, try tracing by timestamp + user ID
→ If logs from different services don't align, check timezone settings
→ If timeline confusing, visualize manually or use tools like Jaeger/Zipkin
→ If distributed tracing not implemented, recommend adding it

---

### Step 6: Extract Metrics and Statistics

**What:** Quantify the issue with concrete metrics to understand severity, impact, and trends.

**How:**
1. Calculate error rates and percentages
2. Measure performance metrics (latency, throughput)
3. Identify affected users and endpoints
4. Compare to baseline/historical data
5. Create summary statistics

**Code/Commands:**
```bash
# Calculate overall error rate
total_requests=$(grep -c "request_id=" merged_timeline.log)
total_errors=$(grep -c "ERROR" merged_timeline.log)
error_rate=$(echo "scale=2; ($total_errors / $total_requests) * 100" | bc)

echo "Error Rate: $error_rate% ($total_errors errors out of $total_requests requests)"

# Error rate by endpoint
echo -e "\n=== Error Rate by Endpoint ===" > metrics_summary.txt
grep "ERROR" merged_timeline.log | \
    grep -oP 'path=[^ ]+' | \
    sort | uniq -c | sort -rn | \
    head -10 >> metrics_summary.txt

# Response time percentiles
echo -e "\n=== Response Time Statistics ===" >> metrics_summary.txt
grep "duration=" merged_timeline.log | \
    grep -oP 'duration=\d+' | \
    awk -F'=' '{print $2}' | \
    sort -n | \
    awk '
        {
            values[NR] = $1
            sum += $1
        }
        END {
            count = NR
            print "Count:", count
            print "Min:", values[1] "ms"
            print "Max:", values[count] "ms"
            print "Average:", sum/count "ms"
            print "P50:", values[int(count*0.5)] "ms"
            print "P95:", values[int(count*0.95)] "ms"
            print "P99:", values[int(count*0.99)] "ms"
        }
    ' >> metrics_summary.txt

# Unique affected users
echo -e "\n=== User Impact ===" >> metrics_summary.txt
affected_users=$(grep "ERROR" merged_timeline.log | \
    grep -oP 'user_id=\d+' | \
    sort -u | wc -l)
echo "Affected Users: $affected_users" >> metrics_summary.txt

# Error distribution by HTTP status code
echo -e "\n=== HTTP Status Codes ===" >> metrics_summary.txt
grep "status=" merged_timeline.log | \
    grep -oP 'status=\d+' | \
    awk -F'=' '{print $2}' | \
    sort | uniq -c | sort -rn >> metrics_summary.txt

# Time to first error (incident detection lag)
first_error=$(grep "ERROR" merged_timeline.log | head -1 | awk '{print $1, $2}')
echo -e "\n=== Timeline ===" >> metrics_summary.txt
echo "First Error: $first_error" >> metrics_summary.txt
echo "Investigation Started: $(date -Iseconds)" >> metrics_summary.txt

# Throughput analysis
echo -e "\n=== Throughput ===" >> metrics_summary.txt
grep "completed" merged_timeline.log | \
    awk '{print substr($2,1,5)}' | \
    uniq -c | \
    awk '{print $2": "$1" req/min"}' >> metrics_summary.txt

# Success vs Failure comparison
successful=$(grep "completed.*status=200" merged_timeline.log | wc -l)
failed=$(grep "ERROR\|status=[45]" merged_timeline.log | wc -l)
echo -e "\n=== Overall Health ===" >> metrics_summary.txt
echo "Successful: $successful" >> metrics_summary.txt
echo "Failed: $failed" >> metrics_summary.txt
echo "Success Rate: $(echo "scale=2; ($successful / ($successful + $failed)) * 100" | bc)%" >> metrics_summary.txt

# Display summary
cat metrics_summary.txt
```

**Verification:**
- [ ] Error rate calculated and documented
- [ ] Performance percentiles measured
- [ ] User impact quantified
- [ ] Endpoint-level metrics extracted
- [ ] Trends over time identified
- [ ] Metrics match observed behavior

**If This Fails:**
→ If metrics don't align with reported issue, verify time window
→ If numbers seem off, check for timezone issues or duplicate logs
→ If missing data points, verify log completeness
→ If baseline unavailable, document current state for future comparison

---

### Step 7: Generate Insights and Recommendations

**What:** Synthesize findings into actionable insights, root cause analysis, and recommendations for prevention.

**How:**
1. Summarize key findings
2. Identify root cause(s)
3. Document contributing factors
4. Create recommendations for fixes
5. Suggest preventive measures
6. Define monitoring improvements

**Code/Commands:**
```bash
# Create comprehensive incident report
cat << EOF > incident_report.md
# Log Analysis Report: ${INVESTIGATION}
**Date:** $(date -Iseconds)  
**Analyst:** $(whoami)  
**Time Window:** ${START_TIME} to ${END_TIME}

---

## Executive Summary

**Issue:** ${INVESTIGATION}  
**Impact:** ${affected_users} users affected, ${error_rate}% error rate  
**Root Cause:** [Based on analysis]  
**Status:** Under investigation / Resolved / Mitigated  

---

## Timeline

| Time | Event |
|------|-------|
| $(grep -m 1 "ERROR" merged_timeline.log | awk '{print $1" "$2}') | First error detected |
| [Time] | [Event] |
| $(date -Iseconds) | Analysis completed |

---

## Key Findings

### 1. Error Distribution
\`\`\`
$(grep "ERROR" errors_only.log | cut -d':' -f4- | sort | uniq -c | sort -rn | head -5)
\`\`\`

### 2. Affected Components
- Component 1: [Details]
- Component 2: [Details]

### 3. Performance Impact
- Average response time: [X]ms (baseline: [Y]ms)
- P95 latency: [X]ms
- Throughput: [X] req/min (baseline: [Y] req/min)

### 4. User Impact
- Total affected users: ${affected_users}
- Most affected user segments: [Details]
- Geographic distribution: [If available]

---

## Root Cause Analysis

### Primary Cause
[Detailed explanation of the root cause]

**Evidence:**
- Log entries showing [specific evidence]
- Timeline correlation with [event]
- Error patterns indicating [conclusion]

### Contributing Factors
1. **[Factor 1]**: [Description]
2. **[Factor 2]**: [Description]
3. **[Factor 3]**: [Description]

### Why It Wasn't Caught Earlier
- Monitoring gap: [Details]
- Alert threshold: [Details]
- Test coverage: [Details]

---

## Recommendations

### Immediate Actions (Fix)
- [ ] **[Action 1]**: [Description]
  - Priority: HIGH
  - Owner: [Team/Person]
  - ETA: [Timeframe]

- [ ] **[Action 2]**: [Description]
  - Priority: MEDIUM
  - Owner: [Team/Person]
  - ETA: [Timeframe]

### Short-term Improvements (Prevent)
- [ ] Add specific error handling for [scenario]
- [ ] Implement circuit breaker for [dependency]
- [ ] Increase timeout from X to Y seconds
- [ ] Add retry logic with exponential backoff

### Long-term Improvements (Systemic)
- [ ] Implement distributed tracing (Jaeger/Zipkin)
- [ ] Add structured logging with correlation IDs
- [ ] Create dashboard for [specific metric]
- [ ] Set up alerts for [pattern]
- [ ] Add integration tests covering [scenario]
- [ ] Conduct load testing for [component]

### Monitoring Enhancements
- [ ] Alert on error rate > X% for endpoint Y
- [ ] Track P95 latency for critical paths
- [ ] Monitor [specific metric] with threshold [value]
- [ ] Create runbook for this error pattern

---

## Lessons Learned

### What Went Well
- Quick log access
- Clear error messages
- [Other positives]

### What Could Be Improved
- Earlier detection (add alerting)
- Faster diagnosis (better tooling)
- [Other improvements]

---

## Appendix

### Log Samples
\`\`\`
$(grep "ERROR" errors_only.log | head -3)
\`\`\`

### Query Commands Used
\`\`\`bash
# Error extraction
grep "ERROR" merged_timeline.log | wc -l

# Performance analysis
grep "duration=" app_filtered.log | awk ...
\`\`\`

### Related Incidents
- [Previous similar incident]
- [Related issue]

---

**Report Generated:** $(date -Iseconds)  
**Next Review:** [Date]
EOF

cat incident_report.md

# Create actionable tickets template
cat << EOF > action_items.md
# Action Items from Log Analysis

## Critical Fixes (Do First)
- [ ] **FIX-001**: [Fix description]
  - Context: [Why this is happening]
  - Solution: [What to do]
  - Files: \`path/to/file.py\`
  - Testing: [How to verify]

## Monitoring Improvements
- [ ] **MON-001**: Add alert for [condition]
  - Threshold: [Value]
  - Notification: [Channel/Team]
  - Query: \`[Example query]\`

## Technical Debt
- [ ] **DEBT-001**: Refactor [component]
  - Issue: [Current problem]
  - Improvement: [Proposed change]
  - Benefit: [Why it matters]

## Documentation
- [ ] **DOC-001**: Create runbook for [scenario]
  - Incident: [This analysis]
  - Symptoms: [What to look for]
  - Resolution: [Step-by-step fix]
EOF

echo -e "\n✅ Report generated: incident_report.md"
echo "✅ Action items created: action_items.md"
echo "✅ Metrics summary: metrics_summary.txt"
```

**Verification:**
- [ ] Incident report is comprehensive and clear
- [ ] Root cause is well-supported by evidence
- [ ] Recommendations are specific and actionable
- [ ] Priority is assigned to each action item
- [ ] Monitoring improvements identified
- [ ] Report suitable for sharing with team/stakeholders

**If This Fails:**
→ If root cause still unclear, mark as "Under investigation" and document hypotheses
→ If recommendations seem vague, tie each to specific log evidence
→ If stakeholder needs different format, adapt template accordingly
→ If multiple root causes, prioritize by impact and likelihood

---

### Step 8: Archive and Share Findings

**What:** Preserve the analysis for future reference and communicate findings to relevant stakeholders.

**How:**
1. Archive all artifacts (logs, scripts, reports)
2. Share incident report with team
3. Update runbooks/documentation
4. Create or update dashboards
5. Schedule follow-up on action items

**Code/Commands:**
```bash
# Create organized archive
archive_dir="log_analysis_$(date +%Y%m%d_%H%M)"
mkdir -p "$archive_dir"/{logs,reports,scripts}

# Copy all artifacts
cp merged_timeline.log errors_only.log traces.log "$archive_dir/logs/"
cp incident_report.md action_items.md metrics_summary.txt "$archive_dir/reports/"
cp create_timeline.py *.sh "$archive_dir/scripts/" 2>/dev/null

# Create README for archive
cat << EOF > "$archive_dir/README.md"
# Log Analysis Archive: ${INVESTIGATION}

**Date:** $(date -Iseconds)  
**Analyst:** $(whoami)  
**Issue:** ${INVESTIGATION}  

## Contents

- \`logs/\`: Raw and filtered log files
- \`reports/\`: Incident report and metrics
- \`scripts/\`: Analysis scripts for reproduction

## Quick Reference

**Error Rate:** ${error_rate}%  
**Affected Users:** ${affected_users}  
**Root Cause:** [Summary]  

## Key Files

- \`reports/incident_report.md\`: Complete analysis
- \`reports/action_items.md\`: Follow-up tasks
- \`logs/errors_only.log\`: Filtered errors for quick review

## Reproduction

To re-run analysis:
\`\`\`bash
cd logs/
../scripts/analyze.sh
\`\`\`
EOF

# Compress archive
tar -czf "${archive_dir}.tar.gz" "$archive_dir"
echo "✅ Archive created: ${archive_dir}.tar.gz"

# Generate shareable summary for Slack/Teams
cat << EOF > slack_summary.txt
:warning: *Log Analysis Complete: ${INVESTIGATION}*

*Impact:* ${affected_users} users, ${error_rate}% error rate
*Root Cause:* [Brief summary]
*Status:* [Resolved/Mitigating/Investigating]

*Key Findings:*
• [Finding 1]
• [Finding 2]
• [Finding 3]

*Actions Taken:*
✅ [Immediate action]
⏳ [In progress]
📋 [Planned]

*Full Report:* [Link to incident_report.md]
*Next Steps:* [Summary of action items]

cc @team @oncall
EOF

echo -e "\n📋 Slack summary created: slack_summary.txt"

# Update team documentation
cat << EOF

Next Steps:
1. Share incident_report.md with team
2. Create tickets from action_items.md
3. Update runbook at docs/runbooks/[scenario].md
4. Add dashboard for monitoring (if needed)
5. Schedule post-mortem meeting (if major incident)
6. Archive materials in [shared location]

Commands to share:
# Copy to shared drive
cp "${archive_dir}.tar.gz" /mnt/shared/incident-logs/

# Create Jira tickets (example)
# Use action_items.md as template

# Update monitoring
# Add new alerts based on recommendations
EOF
```

**Verification:**
- [ ] Archive created with all artifacts
- [ ] Incident report shared with team
- [ ] Action items converted to tickets/issues
- [ ] Runbooks updated with new knowledge
- [ ] Monitoring/alerting enhanced
- [ ] Follow-up meeting scheduled (if needed)
- [ ] Archive stored in accessible location

**If This Fails:**
→ If sharing blocked, summarize key points in email/chat
→ If runbook doesn't exist, create new one from template
→ If monitoring changes require approval, document for next sprint
→ If team communication delayed, ensure at least owner/manager informed

---

## Best Practices

### DO:
✅ **Start with clear investigation scope** - Define what you're looking for before diving into logs  
✅ **Work with copies of logs** - Never modify original log files  
✅ **Document as you go** - Keep notes of queries, findings, and hypotheses  
✅ **Use correlation IDs** - Track requests across service boundaries  
✅ **Look for patterns, not just individual errors** - Identify systemic issues  
✅ **Calculate error rates** - Absolute numbers can be misleading without context  
✅ **Verify timezone consistency** - Ensure all timestamps are in same timezone  
✅ **Compare to baseline** - Context from normal operation helps identify anomalies  
✅ **Create reproducible analysis** - Save scripts and commands for future use  
✅ **Focus on actionable insights** - Every finding should lead to action or learning  

### DON'T:
❌ **Jump to conclusions** - Verify hypotheses with evidence from logs  
❌ **Analyze without time bounds** - Always define start/end window  
❌ **Ignore context** - Consider deployments, traffic patterns, external dependencies  
❌ **Overlook cascading failures** - One error can trigger many downstream effects  
❌ **Forget about log levels** - Ensure appropriate verbosity for investigation  
❌ **Analyze solely via manual grep** - Use tools (ELK, Splunk) for large volumes  
❌ **Skip documentation** - Future-you (and your team) will thank present-you  
❌ **Miss related services** - Check all dependencies and upstream/downstream services  
❌ **Ignore successful requests** - Sometimes what works reveals why failures happen  
❌ **Forget to follow up** - Create tickets, update monitoring, close the loop  

---

## Common Patterns

### Error Rate Spike Analysis
```bash
# Quick error spike detection
grep "ERROR" app.log | awk '{print substr($2,1,5)}' | uniq -c | \
  awk '$1 > THRESHOLD {print "Spike at", $2, ":", $1, "errors"}'

# Correlate with deployments
git log --since="$START_TIME" --until="$END_TIME" --oneline
```

### Performance Degradation Pattern
```bash
# P95 latency over time
grep "duration=" app.log | awk '{
  bucket=substr($2,1,5);
  match($0, /duration=([0-9]+)/, d);
  durations[bucket,count[bucket]++] = d[1];
}
END {
  for (b in count) {
    n = asort(durations[b], sorted);
    p95_idx = int(n * 0.95);
    print b, sorted[p95_idx] "ms";
  }
}'
```

### User Impact Quantification
```bash
# Affected users with error counts
grep "ERROR" app.log | grep -oP 'user_id=\d+' | \
  awk -F'=' '{count[$2]++} END {
    for (user in count) print user, count[user]
  }' | sort -k2 -rn | head -20
```

### Correlation ID Tracing
```bash
# Extract full request flow
trace_request() {
  local req_id=$1
  echo "=== Tracing $req_id ==="
  grep -r "$req_id" /var/log/ | sort -k1,2
}

# Use it
trace_request "req-abc123"
```

### Log Aggregation Setup (ELK Stack)
```yaml
# filebeat.yml - Ship logs to Elasticsearch
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/app/*.log
    fields:
      service: api-server
      environment: production

output.elasticsearch:
  hosts: ["localhost:9200"]
  index: "app-logs-%{+yyyy.MM.dd}"

# Kibana query examples:
# - Error spike: service:"api-server" AND level:"ERROR"
# - Slow requests: service:"api-server" AND duration:>1000
# - User impact: service:"api-server" AND user_id:* AND level:"ERROR"
```

### Structured Logging Pattern
```python
# Python: Use structured logging for better analysis
import structlog

logger = structlog.get_logger()

# Good: Structured fields
logger.info(
    "request_completed",
    request_id=req_id,
    user_id=user_id,
    duration_ms=duration,
    status_code=200,
    endpoint="/api/users"
)

# Bad: Unstructured string
logger.info(f"Request {req_id} completed in {duration}ms")
```

---

## Troubleshooting

### Issue: Logs Too Large to Process

**Symptoms:**
- grep/awk commands hang or take too long
- Out of memory errors
- Cannot open files in text editor

**Solution:**
```bash
# Stream processing instead of loading entire file
grep "ERROR" huge_log.log | head -1000 > sample_errors.log

# Process in chunks
split -l 100000 huge_log.log chunk_
for chunk in chunk_*; do
  grep "ERROR" "$chunk" >> all_errors.log
done

# Use more efficient tools
apt-get install ripgrep  # Much faster than grep
rg "ERROR" huge_log.log

# Sampling for very large datasets
awk 'NR % 100 == 0' huge_log.log > sampled.log  # Every 100th line
```

**Prevention:**
- Implement log rotation
- Use log aggregation systems (ELK, Splunk)
- Archive old logs to compressed storage

---

### Issue: Timestamps Don't Match Across Services

**Symptoms:**
- Events appear out of order when merging logs
- Request flow timeline doesn't make sense
- Can't correlate events across services

**Solution:**
```bash
# Check timezone in logs
head -1 service1.log  # Shows: 2025-10-25T14:00:00Z (UTC)
head -1 service2.log  # Shows: 2025-10-25T09:00:00-05:00 (CDT)

# Convert all to UTC
awk '{
  # Convert timestamps to UTC (adjust based on your format)
  # This is service-specific - example for ISO 8601
  gsub(/-05:00/, "+00:00", $0);
  print
}' service2.log > service2_utc.log

# Or use date command
while read line; do
  timestamp=$(echo "$line" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}')
  utc_time=$(date -d "$timestamp" -u +"%Y-%m-%dT%H:%M:%SZ")
  echo "$line" | sed "s/$timestamp/$utc_time/"
done < service2.log > service2_utc.log
```

**Prevention:**
- Configure all services to log in UTC
- Use ISO 8601 format with timezone indicator
- Include timezone in log format documentation

---

### Issue: Missing Correlation IDs

**Symptoms:**
- Cannot trace requests across services
- Difficult to follow user journeys
- Can only analyze single-service logs

**Solution:**
```bash
# Fallback: Trace by timestamp + user + endpoint
# Find likely related events
user_id="12345"
time_window="14:30:4[0-5]"  # 40-45 seconds

grep "$user_id" service1.log | grep -E "$time_window" > correlated.log
grep "$user_id" service2.log | grep -E "$time_window" >> correlated.log
sort correlated.log > timeline.log

# Use heuristics to connect events
awk '
  /user_id=12345.*endpoint=\/api\/users.*started/ {request_start=$2}
  /user_id=12345.*external_call/ {
    if ($2 > request_start && $2 < request_start+5) {
      print "Likely related:", $0
    }
  }
' timeline.log
```

**Prevention:**
- Implement request ID generation at API gateway
- Propagate correlation IDs via headers (X-Request-ID)
- Include correlation ID in all log statements
- Use distributed tracing (OpenTelemetry)

---

### Issue: Log Format Changed After Deployment

**Symptoms:**
- Parsing scripts break mid-analysis
- Missing expected fields
- Different field names or structure

**Solution:**
```bash
# Detect format changes
head -1 old_logs.log
# 2025-10-25 14:00:00 INFO [service] Message

head -1 new_logs.log
# {"timestamp":"2025-10-25T14:00:00Z","level":"INFO","service":"api","message":"..."}

# Create adaptive parser
parse_log() {
  local line=$1
  
  # Check if JSON
  if echo "$line" | jq . >/dev/null 2>&1; then
    # Parse JSON format
    echo "$line" | jq -r '[.timestamp, .level, .message] | @tsv'
  else
    # Parse old text format
    echo "$line" | awk '{print $1"T"$2, $3, $4, $5}'
  fi
}

# Use it
while read line; do
  parse_log "$line"
done < mixed_format.log > normalized.log
```

**Prevention:**
- Version log formats
- Support both old and new formats during transitions
- Document format changes in deployment notes
- Test log parsing in CI/CD

---

## Related Workflows

**Prerequisites:**
- `dev-xxx_application_monitoring_setup.md` - Setting up logging infrastructure
- `devops-xxx_log_aggregation_elk.md` - Centralized log management
- `dev-xxx_error_handling_strategy.md` - Proper error logging patterns

**Next Steps:**
- `devops-xxx_incident_response.md` - Acting on log analysis findings
- `dev-xxx_performance_tuning.md` - Optimizing based on log insights
- `qa-xxx_test_failure_investigation.md` - Using logs in test debugging

**Alternatives:**
- `devops-xxx_application_monitoring_setup.md` - Real-time monitoring vs. log analysis
- `qa-xxx_debugging_workflow.md` - Interactive debugging vs. log analysis
- `dev-xxx_profiling_workflow.md` - Performance profiling for deeper analysis

---

## Tags
`development` `debugging` `observability` `logs` `troubleshooting` `monitoring` `incident-response` `performance` `analysis`
