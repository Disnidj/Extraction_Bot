# Al Sagr API Extraction - Complete Guide

## Overview
Al Sagr API extraction retrieves benefit values for insurance plans using the portal's backend APIs.

## Key Information Needed

### Required Parameters
1. **quotationId** - The ID of the quotation (e.g., 530746)
2. **proposalId** - Extracted from API response (automatically obtained)
3. **planId** - Extracted from benefit structure (automatically obtained)

### How to Get quotationId

There are **3 approaches** to obtain the quotationId:

---

## Approach 1: Use Existing Quotation ID (Fastest)

If you already have a quotation from the portal:

```python
from patchright.async_api import async_playwright
from src.pages.alsagr.alsagr_main_api import run_alsagr_api_extraction

async with async_playwright() as playwright:
    result = await run_alsagr_api_extraction(
        playwright, 
        quotation_id=530746  # ← Your existing quotation ID
    )
```

**Where to find quotationId:**
- Navigate to the benefit structure page in Al Sagr portal
- Check the URL: `https://miportal.alsagrins.ae/.../groupquotationbenefitstructure?quotationId=530746`
- The number after `quotationId=` is your quotation ID

---

## Approach 2: Auto-Extract from Portal (Recommended for Manual Testing)

Navigate to the benefit structure page, and the script will extract the ID automatically:

```python
from patchright.async_api import async_playwright
from src.pages.alsagr.alsagr_main_api import run_alsagr_api_extraction

async with async_playwright() as playwright:
    # Script will:
    # 1. Login to portal
    # 2. Extract JWT token
    # 3. Wait for you to navigate to a quotation
    # 4. Auto-extract quotationId from URL
    result = await run_alsagr_api_extraction(playwright)
```

**Steps:**
1. Script opens browser and logs in
2. Browser stays open (headless=False)
3. Manually navigate to: **Medical Portal → SME/Group/EBP B2B → Quotation Information**
4. Click on an existing quotation (or create new one)
5. Go to the **Benefit Structure** page
6. Script automatically detects quotationId from the URL
7. Extraction proceeds automatically

---

## Approach 3: Automated Form Fill (Production Use)

Use existing form automation to create a quotation and extract benefits:

```python
from patchright.async_api import async_playwright, Playwright
from src.pages.alsagr.login_page import LoginPage
from src.pages.alsagr.process_page import ProcessPage
from src.pages.alsagr.api import AlSagrAuthToken, AlSagrAPIExtractor, AlSagrFormatter
from src.services.excel_service.read_excel import read_excel

async def automated_extraction(playwright: Playwright, referral_id):
    # Step 1: Get data from Excel
    df1, df2 = read_excel('AL SAGR INSURANCE COMPANY', referral_id)
    
    # Step 2: Launch browser and login
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()
    
    login_page = LoginPage(page)
    await login_page.login()
    
    # Step 3: Extract JWT token
    auth = AlSagrAuthToken()
    await auth.extract_token_from_browser(page)
    
    # Step 4: Fill process forms (creates quotation)
    process_page = ProcessPage(page)
    cat1 = df2[df2['Category'] == unique_categories_list[0]]
    await process_page.fill_process_form(df1, cat1, "AL SAGR INSURANCE COMPANY")
    
    # Step 5: Extract quotationId from page
    quotation_info = await auth.extract_quotation_info_from_page(page)
    quotation_id = quotation_info["quotationId"]
    
    # Step 6: Run API extraction
    extractor = AlSagrAPIExtractor(auth, quotation_id=quotation_id)
    results = await extractor.extract_all_benefits()
    
    # Step 7: Format and save
    formatter = AlSagrFormatter()
    formatter.write_records(results.get("records", []))
    
    await browser.close()
```

---

## API Flow Explained

### Pre-Level: Get TPA Options
**API:** `GetTPAMastersByProductType?productTypeId=183`

**Returns:**
```json
[
  {"domainValue": 1, "domainValueName": "NEXT CARE MANAGEMENT LLC"},
  {"domainValue": 4, "domainValueName": "NAS ADMINISTRATION SERVICES CO. LLC"}
]
```

This is a dropdown extraction (like other portals) - gets the available TPA options.

### Step 1: Get Benefit Structure
**API:** `GetGroupQuotationBenefitStructure?quotationId={id}`

**Returns:**
- `planBenefits[]` - List of available plans
  - `planId`: e.g., 882
  - `planName`: e.g., "Plan A"
  - `categoryId`: e.g., 2 (Category B)
  - `categoryName`: e.g., "Category B"

- `proposalMasters[]` - Proposal information
  - `proposalId`: e.g., 139987 ← **Needed for next API call**

- `benefitStructure[]` - Benefit field definitions
  - `benefitId`: e.g., 8, 9, 10, ...
  - Maps to field names (see mapping.py)

### Step 2: Get Benefit Values for Each Plan
**API:** `GetBenefitsByPlan?planId={id}&categoryId={id}&quotationId={id}&proposalId={id}`

**Parameters:**
- `planId`: From Step 1 (e.g., 882)
- `categoryId`: Any value (e.g., 2) - benefits are identical across categories
- `quotationId`: Your quotation ID (e.g., 530746)
- `proposalId`: From Step 1 (e.g., 139987)

**Returns:**
Array of benefit objects:
```json
[
  {"benefitId": 8, "value": "GCC"},
  {"benefitId": 9, "value": "Network A"},
  {"benefitId": 10, "value": "80%"},
  ...
]
```

### Optimization Discovery
**Important:** Benefits are IDENTICAL across categories for the same plan!
- You only need **1 API call per plan** (not per plan+category combination)
- Use any `categoryId` (e.g., 2) - the response will be the same

---

## Benefit Field Mapping

The `benefitId` maps to benefit field names:

| benefitId | Field Name |
|-----------|------------|
| 8 | Visa Region |
| 9 | Network |
| 10 | OP Co-Insurance |
| 11 | Pharmacy Co-Ins |
| 12 | Aggregate Limit |
| 13 | Geographical Area |
| 14 | Consult Deductible |
| 15 | Maternity Limit |
| 16 | Nursing Home |
| 17 | Repatriation |
| 18 | Psychiatric |
| 57 | Dental |
| 58 | Optical |
| 125 | Pharmacy Limit |
| 126 | IP Room & Board |
| 165 | Plan Type |

See `api/mapping.py` for complete list.

---

## Output Files

Extraction creates two files:

1. **JSON Results:** `extracted_data/alsagr/alsagr_api_results_YYYYMMDD_HHMMSS.json`
   - Full extraction data with metadata
   - Nested structure with plans and benefits

2. **Database Format:** `extracted_data/alsagr/alsagr_extracted_YYYYMMDD_HHMMSS.txt`
   - Flat format for database import
   - One line per record:
   ```json
   {"Broker_ID": 3, "Company": "AL SAGR INSURANCE COMPANY", "TPA": "", "Network": "Plan A", "Region": "Dubai", "Dropdown_Name": "Visa Region", "Selection_Value": "GCC"}
   ```

---

## Example: Complete Extraction Script

```python
import asyncio
from patchright.async_api import async_playwright

async def main():
    async with async_playwright() as playwright:
        from src.pages.alsagr.alsagr_main_api import run_alsagr_api_extraction
        
        # Option 1: With known quotation ID
        result = await run_alsagr_api_extraction(
            playwright,
            quotation_id=530746
        )
        
        # Option 2: Auto-extract from page
        # result = await run_alsagr_api_extraction(playwright)
        # # Then manually navigate to benefit structure page
        
        if result["success"]:
            print("✅ Extraction successful!")
            print(f"Records extracted: {result['results']['records']}")
        else:
            print("❌ Extraction failed!")
            for error in result["errors"]:
                print(f"  - {error}")

asyncio.run(main())
```

---

## Troubleshooting

### "No quotation_id available"
**Solution:** Navigate to the benefit structure page or provide quotation_id parameter

### "Failed to extract token"
**Solution:** Check if login was successful. Token should be in localStorage after SSO login.

### "No plans extracted"
**Solution:** Verify quotation_id is valid and quotation exists in portal

### API calls return empty data
**Solution:** 
- Check JWT token is valid (not expired)
- Verify you're logged in
- Ensure quotation_id and proposal_id are correct
