# 🚀 Multi-Broker API Extraction System - Quick Start Guide

## 📋 Overview

The multi-broker system enables simultaneous API extraction for multiple brokers with zero hardcoded configurations. All broker-portal mappings are stored in the `Medical_CTN_Broker_Portal_Mapping` database table.

---

## 🎯 Key Features

✅ **Database-driven portal mapping** - No hardcoded broker IDs  
✅ **Shared portal optimization** - ADNIC extracted once, applied to all brokers  
✅ **Interactive broker selection** - Choose which brokers to run  
✅ **CLI support** - Perfect for scheduled automation  
✅ **Multi-broker replication** - Data automatically copied to each broker's staging table  

---

## 📊 Database Structure

### Medical_CTN_Broker_Portal_Mapping

| Column | Type | Description |
|--------|------|-------------|
| Broker_ID | INT | Unique broker identifier (2, 3, 6, etc.) |
| Broker_Name | VARCHAR(100) | Broker display name |
| Portal_Name | VARCHAR(100) | Portal name (must match API_PORTAL_GROUPS) |
| Created_At | DATETIME | Record creation timestamp |
| Updated_At | DATETIME | Last modification timestamp |

**Current Active Brokers:**
- Broker 2: Unitrust
- Broker 3: Lifecare International  
- Broker 6: VIVA

---

## 🔧 Usage Methods

### **Method 1: Interactive Mode (Recommended for Testing)**

```bash
python main.py
```

**Steps:**
1. Select extraction mode: `api`
2. Broker selection menu appears:
   ```
   ╔═══════════════════════════════════════════════╗
   ║          SELECT BROKERS FOR EXTRACTION        ║
   ╚═══════════════════════════════════════════════╝
   
   Available Brokers:
     1. Broker 2 - Unitrust
     2. Broker 3 - Lifecare International
     3. Broker 6 - VIVA
   
   Options:
     • Enter broker numbers (comma-separated): 2,3
     • Enter 'all' to select all brokers
     • Enter 'q' to cancel
   
   Your selection:
   ```
3. System fetches portals from database for selected brokers
4. Displays portal breakdown (shared vs unique)
5. Confirms selection before starting extraction

---

### **Method 2: CLI Mode (For Scheduled Tasks)**

#### Run for all brokers:
```bash
python main.py --mode=api --brokers=all --scheduled
```

#### Run for specific brokers:
```bash
python main.py --mode=api --brokers=2,3 --scheduled
```

#### Run for single broker:
```bash
python main.py --mode=api --brokers=6 --scheduled
```

**CLI Arguments:**
- `--mode=api` - Force API extraction mode (skips interactive mode selection)
- `--brokers=all` - Run for all active brokers
- `--brokers=2,3,6` - Run for specific broker IDs (comma-separated)
- `--scheduled` - Skip confirmation prompts (auto-start extraction)

---

### **Method 3: Windows Task Scheduler (Automated)**

Use the provided batch file:
```batch
scheduled_api_extraction.bat
```

**What it does:**
- Runs: `python main.py --mode=api --brokers=all --scheduled`
- Logs to: `logs/scheduled_run_YYYYMMDD.log`
- Handles errors with exit codes

**Setup Windows Task Scheduler:**
1. Open Task Scheduler
2. Create New Task → "Multi-Broker API Extraction"
3. Trigger: Daily at 2:00 AM (or your preferred time)
4. Action: Run `C:\path\to\scheduled_api_extraction.bat`
5. Settings: Stop if runs longer than 3 hours

---

## 🧪 Testing the System

### **Test 1: Verify Database Connection**

Create `test_portal_mapper.py`:
```python
from src.services.broker_service.portal_mapper import PortalMapper

# Test portal mapper
mapper = PortalMapper()

# Test 1: Fetch portals for Broker 2
print("Test 1: Fetch portals for Broker 2")
portals = mapper.fetch_portals_for_broker(2)
print(f"Found {len(portals)} portals: {portals}\n")

# Test 2: Analyze portal distribution
print("Test 2: Analyze portal distribution for all brokers")
analysis = mapper.analyze_portal_distribution([2, 3, 6])
print(f"Total unique portals: {analysis['total_unique']}")
print(f"Shared portals: {list(analysis['shared'].keys())}")
print(f"Unique portals: {list(analysis['unique'].keys())}\n")

# Test 3: Find which brokers use ADNIC
print("Test 3: Find which brokers use ADNIC")
brokers_using_adnic = mapper.get_brokers_using_portal("adnic")
print(f"Brokers using ADNIC: {brokers_using_adnic}")
```

Run: `python test_portal_mapper.py`

---

### **Test 2: Verify Broker Selection Menu**

Create `test_broker_selection.py`:
```python
from src.services.broker_service.broker_manager import select_brokers_interactive
from src.config.broker_config import get_broker_summary

# Test interactive selection
print("Testing interactive broker selection...\n")
selected_brokers = select_brokers_interactive()

if selected_brokers:
    print(f"\n✅ Selected {len(selected_brokers)} broker(s):")
    for bid in selected_brokers:
        print(f"   • {get_broker_summary(bid)}")
else:
    print("\n❌ No brokers selected")
```

Run: `python test_broker_selection.py`

---

### **Test 3: Dry Run Extraction**

```bash
# Test with single broker (Broker 2)
python main.py --mode=api --brokers=2
```

**Expected Flow:**
1. CLI arguments parsed → Broker 2 selected
2. Portal mapper queries database → finds portals for Broker 2
3. Displays portal breakdown
4. Prompts for confirmation (press Enter to continue)
5. Extracts data from each portal
6. Multi-broker uploader replicates data to Broker 2's staging table
7. Generates PDF report and logs

---

## 📂 File Structure

```
Extraction_Bot/
├── main.py                                    # Modified: CLI args + broker selection
├── scheduled_api_extraction.bat              # NEW: Windows scheduler batch file
│
├── src/
│   ├── config/
│   │   └── broker_config.py                  # NEW: Active broker definitions
│   │
│   ├── services/
│   │   ├── broker_service/
│   │   │   ├── __init__.py                   # NEW: Module exports
│   │   │   ├── broker_manager.py             # NEW: Interactive selection menu
│   │   │   └── portal_mapper.py              # NEW: Database query service
│   │   │
│   │   └── db_service/
│   │       └── api_data/
│   │           ├── multi_broker_upload.py    # NEW: Multi-broker upload handler
│   │           └── staging_upload.py         # MODIFIED: Added broker methods
│   │
│   └── utils/
│       └── cli_args.py                       # NEW: CLI argument parser
│
└── logs/
    └── scheduled_run_YYYYMMDD.log            # Auto-generated by batch file
```

---

## 🔍 How It Works

### **Phase 1: Broker Selection**
```
Interactive Mode: User selects from menu
CLI Mode: --brokers=all or --brokers=2,3
```

### **Phase 2: Portal Mapping (Database Query)**
```sql
SELECT DISTINCT Portal_Name 
FROM Medical_CTN_Broker_Portal_Mapping 
WHERE Broker_ID IN (2, 3, 6)
```

**Example Result:**
- Shared: ADNIC → [Broker 2, Broker 3, Broker 6]
- Unique: Daman → Broker 2
- Unique: Orient → Broker 3

### **Phase 3: Portal Extraction**
```
For each unique portal:
  - Extract data once (e.g., ADNIC)
  - Save to extracted_data/YYYYMMDD_HHMMSS/adnic_data.json
```

### **Phase 4: Multi-Broker Upload**
```
For shared portal (ADNIC):
  1. Upload to Medical_CTN_Cascading_Dropdown_Staging (Broker_ID = 2)
  2. Replicate to Medical_CTN_Cascading_Dropdown_Staging (Broker_ID = 3)
  3. Replicate to Medical_CTN_Cascading_Dropdown_Staging (Broker_ID = 6)

For unique portal (Daman):
  1. Upload to Medical_CTN_Cascading_Dropdown_Staging (Broker_ID = 2 only)
```

---

## 🎛️ Configuration

### **Activate/Deactivate Brokers**

Edit `src/config/broker_config.py`:
```python
ACTIVE_BROKERS = {
    2: {"name": "Unitrust", "enabled": True},
    3: {"name": "Lifecare International", "enabled": True},
    6: {"name": "VIVA", "enabled": False},  # Disabled
}
```

### **Add New Broker**

1. **Add to broker_config.py:**
```python
ACTIVE_BROKERS = {
    2: {"name": "Unitrust", "enabled": True},
    3: {"name": "Lifecare International", "enabled": True},
    6: {"name": "VIVA", "enabled": True},
    7: {"name": "New Broker", "enabled": True},  # NEW
}
```

2. **Add portal mapping to database:**
```sql
INSERT INTO Medical_CTN_Broker_Portal_Mapping 
(Broker_ID, Broker_Name, Portal_Name, Created_At, Updated_At)
VALUES 
(7, 'New Broker', 'adnic', NOW(), NOW()),
(7, 'New Broker', 'daman', NOW(), NOW());
```

3. **Done!** System will automatically include Broker 7 in selections.

---

## 📊 Monitoring & Logs

### **Execution Logs**
- Location: `logs/extraction_flow_execution_YYYYMMDD.log`
- Contains: Full extraction flow, database operations, timing details

### **Scheduled Run Logs**
- Location: `logs/scheduled_run_YYYYMMDD.log`
- Contains: Batch file execution, errors, exit codes

### **Sample Log Output**
```
======================================================================
🚀 API EXTRACTION MODE (Multi-Broker Support)
======================================================================

✅ Running extraction for 3 broker(s):
   • Broker 2 - Unitrust
   • Broker 3 - Lifecare International
   • Broker 6 - VIVA

🔍 Fetching portals from database...

✅ Found 5 unique portals

📋 Shared Portals (2):
   • adnic → Broker 2, Broker 3, Broker 6
   • orient → Broker 2, Broker 3

📋 Broker-Specific Portals (3):
   • daman → Broker 2
   • gig → Broker 3
   • medgulf → Broker 6

======================================================================
📤 DATABASE UPLOAD (Multi-Broker)
======================================================================

✅ Multi-Broker Upload Complete
   • Portals processed: 5
   • Total uploads: 15
   • Successful: 15
   • Failed: 0

📊 Breakdown by Broker:
   • Broker 2 (Unitrust): 4 portals
   • Broker 3 (Lifecare International): 4 portals
   • Broker 6 (VIVA): 3 portals
```

---

## ❓ FAQ

### **Q: How do I add a new portal to existing brokers?**
```sql
INSERT INTO Medical_CTN_Broker_Portal_Mapping 
(Broker_ID, Broker_Name, Portal_Name, Created_At, Updated_At)
VALUES 
(2, 'Unitrust', 'new_portal', NOW(), NOW()),
(3, 'Lifecare International', 'new_portal', NOW(), NOW());
```

### **Q: How do I remove a portal from a broker?**
```sql
DELETE FROM Medical_CTN_Broker_Portal_Mapping 
WHERE Broker_ID = 2 AND Portal_Name = 'unwanted_portal';
```

### **Q: Can I run for brokers not in broker_config.py?**
No. Only brokers with `enabled: True` in `broker_config.py` will appear in selections. This prevents accidentally running for inactive/test brokers.

### **Q: What happens if a portal has no API implementation?**
The system will warn you:
```
⚠️  No API extraction implemented yet for: portal_name
   These will be skipped.
```
Only portals defined in `API_PORTAL_GROUPS["api_portals"]` will be extracted.

---

## 🎯 Next Steps

1. **Verify Database Mapping:**
   ```sql
   SELECT * FROM Medical_CTN_Broker_Portal_Mapping ORDER BY Broker_ID, Portal_Name;
   ```

2. **Test Interactive Mode:**
   ```bash
   python main.py
   # Select api → Choose broker 2 → Verify extraction
   ```

3. **Test CLI Mode:**
   ```bash
   python main.py --mode=api --brokers=2 --scheduled
   ```

4. **Schedule Task:**
   - Open Task Scheduler
   - Create task using `scheduled_api_extraction.bat`
   - Set daily trigger
   - Monitor logs folder

---

## 🚨 Troubleshooting

### **Error: "No brokers found in configuration"**
- Check `src/config/broker_config.py`
- Ensure at least one broker has `enabled: True`

### **Error: "No portals found for broker X"**
- Query database: `SELECT * FROM Medical_CTN_Broker_Portal_Mapping WHERE Broker_ID = X`
- Ensure portal names match those in `API_PORTAL_GROUPS["api_portals"]`

### **Error: "Database connection failed"**
- Check `config.yaml` database credentials
- Verify MySQL service is running
- Test connection: `mysql -u user -p database_name`

### **Portals not being extracted**
- Verify portal names in database exactly match `API_PORTAL_GROUPS` (case-sensitive)
- Check portal implementation exists in `src/pages/`
- Review logs: `logs/extraction_flow_execution_*.log`

---

## 📞 Support

For issues or questions:
1. Check execution logs: `logs/extraction_flow_execution_*.log`
2. Review scheduled run logs: `logs/scheduled_run_*.log`
3. Query database for mapping issues
4. Verify broker_config.py settings

---

**System Status:** ✅ Ready for Production  
**Last Updated:** 2026-03-04  
**Version:** 1.0.0
