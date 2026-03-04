# Al Sagr API - Quick Reference

## 🎯 What You Need

```
Step 0: Get TPA Options (Pre-Level)
    ↓
productTypeId (183 for SME)
    ↓
API Call: GetTPAMastersByProductType
    ↓
TPA Options List

Step 1: Get Quotation Structure
    ↓
quotationId (e.g., 530746)
    ↓
API Call: GetGroupQuotationBenefitStructure
    ↓
proposalId (auto-extracted from response, e.g., 139987)
planId (auto-extracted from response, e.g., 882)
    ↓
Step 2: Get Benefit Values
    ↓
API Call: GetBenefitsByPlan (for each plan)
    ↓
Benefit Values
```

## 📋 How to Get quotationId

### Option 1: From Portal URL ✅ EASIEST
1. Login to Al Sagr portal
2. Navigate to benefit structure page
3. Look at URL: `...groupquotationbenefitstructure?quotationId=530746`
4. Copy the number after `quotationId=`

### Option 2: Let Script Auto-Extract
```python
# Script will detect quotationId from URL automatically
result = await run_alsagr_api_extraction(playwright)
# Navigate to benefit structure page in browser
# Script continues automatically
```

### Option 3: Use Existing Form Fill
```python
# Use process_page.py to create quotation
# Then extract quotationId from page
quotation_info = await auth.extract_quotation_info_from_page(page)
```

## 🔌 API Endpoints

### Base URL
```
https://ndapi.alsagrins.ae/MiCore/api/GroupQuotation/
```

### Endpoint 0: Get TPA Options (Pre-Level)
```
POST /GetTPAMastersByProductType?productTypeId=183

Returns:
[
  {"domainValue": 1, "domainValueName": "NEXT CARE MANAGEMENT LLC"},
  {"domainValue": 4, "domainValueName": "NAS ADMINISTRATION SERVICES CO. LLC"}
]
```

### Endpoint 1: Get Structure
```
GET /GetGroupQuotationBenefitStructure?quotationId=530746

Returns:
{
  "planBenefits": [...],        // Plans with planId
  "proposalMasters": [...],     // proposalId here
  "benefitStructure": [...],    // Field definitions
  "category": [...]             // Categories
}
```

### Endpoint 2: Get Benefit Values
```
GET /GetBenefitsByPlan?planId=882&categoryId=2&quotationId=530746&proposalId=139987

Returns:
[
  {"benefitId": 8, "value": "GCC"},        // Visa Region
  {"benefitId": 9, "value": "Network A"},  // Network
  {"benefitId": 10, "value": "80%"},       // OP Co-Insurance
  ...
]
```

## 🔑 Authentication

JWT Token from localStorage (auto-extracted after login)
```
Headers: {
  "Authorization": "Bearer eyJhbGciOiJ..."
}
```

## 💎 Key Optimization

**Benefits are IDENTICAL across categories for same plan!**
- ❌ Don't call API for each category
- ✅ Call API once per plan (use any categoryId, e.g., 2)

Example:
```
Plan 882 + Category B (categoryId=2)  → Same benefits
Plan 882 + Category B1 (categoryId=47) → Same benefits

Only need 1 call for Plan 882!
```

## 📂 File Structure

```
src/pages/alsagr/
├── alsagr_main_api.py      # Main entry point
└── api/
    ├── auth.py             # Token extraction
    ├── client.py           # API calls
    ├── extractor.py        # Orchestration
    ├── formatter.py        # Output formatting
    └── mapping.py          # Config & field mappings
```

## 🚀 Quick Start

```python
from patchright.async_api import async_playwright

async with async_playwright() as playwright:
    from src.pages.alsagr.alsagr_main_api import run_alsagr_api_extraction
    
    # With known quotation ID
    result = await run_alsagr_api_extraction(
        playwright,
        quotation_id=530746  # ← Your quotation ID
    )
```

## 📊 Output

**JSON:** `extracted_data/alsagr/alsagr_api_results_20260303_123456.json`
**Text:** `extracted_data/alsagr/alsagr_extracted_20260303_123456.txt`

Database format:
```json
{
  "Broker_ID": 3,
  "Company": "AL SAGR INSURANCE COMPANY",
  "TPA": "",
  "Network": "Plan A",
  "Region": "Dubai",
  "Dropdown_Name": "Visa Region",
  "Selection_Value": "GCC"
}
```
