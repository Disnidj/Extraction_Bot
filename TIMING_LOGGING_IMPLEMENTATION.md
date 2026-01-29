# Timing and Logging Implementation Summary

## Overview
Implemented comprehensive timing tracking and logging for portal extractions with both portal-wise and full-flow duration tracking.

## Key Features Implemented

### 1. **Main Execution Log File**
- **File**: `logs/main_execution.log`
- **Purpose**: Centralized logging for overall flow timing and execution tracking
- **Output**: Both console and file for visibility

### 2. **Portal-Wise Timing**
Each portal now tracks:
- ✅ **Start Time**: Exact timestamp when portal processing begins
- ✅ **End Time**: Exact timestamp when portal processing completes
- ✅ **Duration**: Time taken in seconds and formatted as minutes:seconds
- ✅ **Status**: Success (✅) or Failure (❌) indicator

### 3. **Full Flow Timing**
- **Request-Level Tracking**: Total time for processing all portals in a request
- **API Mode Tracking**: Total time for API extraction flow
- **Overall Summary**: Complete execution statistics

## Log Output Format

### Portal-Wise Example:
```
2026-01-29 15:30:45 - INFO - main.py:112 - 🚀 Portal 'ADNIC' - Started at 2026-01-29 15:30:45
2026-01-29 15:32:15 - INFO - main.py:127 - ✅ Portal 'ADNIC' - Completed at 2026-01-29 15:32:15 | Duration: 90.25s (1m 30s)
```

### Summary Example:
```
======================================================================
📊 REQUEST 12345 PROCESSING SUMMARY
======================================================================
End Time: 2026-01-29 15:35:00
Total Duration: 280.50s (4m 40s)

📋 Portal-wise Timing:
  ✅ ADNIC: 90.25s (1m 30s) | 15:30:45 → 15:32:15
  ✅ Takaful: 105.30s (1m 45s) | 15:30:45 → 15:32:30
  ✅ Qatar: 84.95s (1m 24s) | 15:32:30 → 15:34:05

✅ Successful: 3/3 portals
   ADNIC, Takaful, Qatar
======================================================================
```

## Files Modified

### 1. **src/utils/logger.py**
- Added `datetime` import for timestamp tracking
- Created `main_execution_logger` - dedicated logger for execution flow
- Configured both file and console output for visibility

### 2. **main.py**
- Added `datetime` import
- Updated `login_portal_with_semaphore()`: Added timing tracking for each portal
- Updated `run_portals_with_concurrency_limit()`: Returns timing data along with results
- Enhanced `run_api_extraction_mode()`: Full timing implementation with summary
- Enhanced standard execution mode: Request-level timing with portal summaries

## Benefits

### 1. **Performance Monitoring**
- Identify slow portals that need optimization
- Track performance trends over time
- Detect anomalies in execution time

### 2. **Debugging Support**
- Quickly identify where time is being spent
- Correlate errors with timing information
- Better incident analysis

### 3. **Reporting & Accountability**
- Clear audit trail of execution times
- Documentation for stakeholders
- SLA compliance tracking

### 4. **Visibility**
- Real-time console output for operators
- Persistent logs for historical analysis
- Both portal-level and flow-level insights

## Usage

### For Standard Mode:
```bash
python main.py
# Select mode: 1 (Standard)
# Select portals: Choose your portals
# Timing will be automatically logged for each portal and overall request
```

### For API Mode:
```bash
python main.py
# Select mode: 2 (API)
# Select portals: Choose API-enabled portals
# Timing will be logged for each portal and overall API extraction
```

## Log File Locations

1. **Main Execution Log**: `logs/main_execution.log` - Overall flow timing
2. **Portal Logs**: `logs/<portal_name>.log` - Portal-specific logs
3. **Issues Log**: `logs/Issues.log` - Critical issues and request tracking

## Example Console Output

```
Starting portals with parallel execution (max concurrency: 3)...
2026-01-29 15:30:45 - INFO - 🚀 REQUEST 12345 PROCESSING STARTED
Started login for ADNIC
Started login for Takaful
Started login for Qatar
Completed login for ADNIC
2026-01-29 15:32:15 - INFO - ✅ Portal 'ADNIC' - Completed | Duration: 90.25s (1m 30s)
Completed login for Takaful
2026-01-29 15:32:30 - INFO - ✅ Portal 'Takaful' - Completed | Duration: 105.30s (1m 45s)
Completed login for Qatar
2026-01-29 15:34:05 - INFO - ✅ Portal 'Qatar' - Completed | Duration: 84.95s (1m 24s)

======================================================================
📊 REQUEST 12345 PROCESSING SUMMARY
Total Duration: 280.50s (4m 40s)
✅ Successful: 3/3 portals
======================================================================
```

## Notes

- All times are recorded using `datetime.now()` for precision
- Durations are calculated as delta between start and end times
- Both seconds (decimal) and mm:ss formats are provided
- Console and file logging work simultaneously
- Timing data is preserved in logs for historical analysis
