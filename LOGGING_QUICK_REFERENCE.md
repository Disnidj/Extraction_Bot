# Quick Reference: Using the Timing & Logging System

## Log Files Overview

### 1. Main Execution Log
**Location**: `logs/main_execution.log`
**Contains**:
- Overall flow start/end times
- Portal-wise timing summaries
- Request-level duration tracking
- Full flow completion statistics

### 2. Portal-Specific Logs
**Location**: `logs/<portal_name>.log` (e.g., `logs/adnic.log`)
**Contains**:
- Portal-specific detailed operations
- Portal-level errors and warnings
- Portal execution details

### 3. Issues Log
**Location**: `logs/Issues.log`
**Contains**:
- Critical issues across all portals
- Request start/completion tracking
- Consolidated error reporting

## Timing Information Structure

### Portal Level
Each portal execution logs:
```
🚀 Start: Portal 'PortalName' - Started at YYYY-MM-DD HH:MM:SS
✅ Complete: Portal 'PortalName' - Completed at YYYY-MM-DD HH:MM:SS | Duration: XX.XXs (Xm XXs)
```

### Request Level (Standard Mode)
```
🚀 REQUEST XXXXX PROCESSING STARTED
Start Time: YYYY-MM-DD HH:MM:SS
Portals to process: Portal1, Portal2, Portal3

📊 REQUEST XXXXX PROCESSING SUMMARY
End Time: YYYY-MM-DD HH:MM:SS
Total Duration: XXX.XXs (Xm XXs)

📋 Portal-wise Timing:
  ✅ Portal1: XX.XXs (Xm XXs) | HH:MM:SS → HH:MM:SS
  ✅ Portal2: XX.XXs (Xm XXs) | HH:MM:SS → HH:MM:SS
  ❌ Portal3: XX.XXs (Xm XXs) | HH:MM:SS → HH:MM:SS

✅ Successful: X/X portals
```

### API Extraction Mode
```
🚀 API EXTRACTION FLOW STARTED
Start Time: YYYY-MM-DD HH:MM:SS
Portals to process: Portal1, Portal2

📊 API EXTRACTION SUMMARY
Overall End Time: YYYY-MM-DD HH:MM:SS
Total Duration: XXX.XXs (Xm XXs)

📋 Portal-wise Timing:
  • Portal1: XX.XXs (Xm XXs) | HH:MM:SS → HH:MM:SS
  • Portal2: XX.XXs (Xm XXs) | HH:MM:SS → HH:MM:SS
```

## How to Read Timing Logs

### Time Formats
- **Timestamp**: `YYYY-MM-DD HH:MM:SS` (e.g., 2026-01-29 15:30:45)
- **Duration (seconds)**: `XX.XXs` (e.g., 90.25s)
- **Duration (formatted)**: `(Xm XXs)` (e.g., (1m 30s))
- **Time Range**: `HH:MM:SS → HH:MM:SS` (e.g., 15:30:45 → 15:32:15)

### Status Icons
- ✅ Success - Portal completed successfully
- ❌ Failed - Portal encountered an error
- 🚀 Start - Process/Portal started
- 📊 Summary - Summary information
- 📋 Details - Detailed breakdown

## Analyzing Performance

### Identifying Slow Portals
Look for portals with high duration values in the summary:
```
📋 Portal-wise Timing:
  ✅ Portal1: 45.20s (0m 45s)    ← Fast
  ✅ Portal2: 120.50s (2m 0s)    ← Moderate
  ✅ Portal3: 300.75s (5m 0s)    ← SLOW - Investigate!
```

### Checking Success Rate
```
✅ Successful: 8/10 portals      ← 80% success rate
   Portal1, Portal2, ... Portal8
❌ Failed: Portal9, Portal10      ← 20% failure - Check these!
```

### Monitoring Trends
Compare durations across multiple runs to identify:
- Performance degradation
- Improvement after optimizations
- Consistent slow performers

## Best Practices

### 1. Regular Monitoring
- Check `main_execution.log` daily for performance trends
- Review portal-wise timing to identify bottlenecks
- Monitor success rates in summaries

### 2. Troubleshooting
- If portal shows ❌: Check `logs/<portal_name>.log` for details
- Compare duration to baseline for anomalies
- Cross-reference with Issues.log for critical errors

### 3. Performance Optimization
- Focus on portals with highest duration
- Review parallel execution (MAX_PARALLEL_PORTALS = 3)
- Consider optimizing slow operations

### 4. Reporting
- Use timing summaries for status reports
- Track total duration for SLA compliance
- Document performance improvements

## Example Analysis Session

1. **Check overall execution**:
   ```bash
   tail -n 50 logs/main_execution.log
   ```

2. **Find slow portals**:
   Look for high duration values in summary sections

3. **Investigate failures**:
   ```bash
   tail -n 100 logs/Issues.log
   grep "❌" logs/main_execution.log
   ```

4. **Compare trends**:
   Review multiple summary sections to spot patterns

## Maintenance

### Log Rotation
Logs are in append mode. Consider implementing rotation:
- Archive old logs monthly
- Keep last 90 days of logs
- Compress archived logs

### Disk Space
Monitor log directory size:
```powershell
Get-ChildItem logs -Recurse | Measure-Object -Property Length -Sum
```

### Cleanup
Old logs can be safely deleted if archived:
```powershell
# Backup first!
# Then remove logs older than 90 days
Get-ChildItem logs/*.log | Where-Object {$_.LastWriteTime -lt (Get-Date).AddDays(-90)} | Remove-Item
```

## Common Scenarios

### Scenario 1: Portal Taking Too Long
**Symptom**: Portal shows 5+ minutes duration
**Action**:
1. Check `logs/<portal_name>.log` for what it's doing
2. Review network/API calls in portal code
3. Consider timeout adjustments or optimization

### Scenario 2: Parallel Execution Issues
**Symptom**: All portals finish at similar time despite parallelism
**Action**:
1. Check MAX_PARALLEL_PORTALS setting (default: 3)
2. Verify concurrency is actually happening
3. Review semaphore implementation

### Scenario 3: High Failure Rate
**Symptom**: Many ❌ in portal-wise timing
**Action**:
1. Check Issues.log for common error patterns
2. Review portal-specific logs
3. Check network/authentication issues

## Additional Resources

- Main implementation: `main.py`
- Logger configuration: `src/utils/logger.py`
- Documentation: `TIMING_LOGGING_IMPLEMENTATION.md`
