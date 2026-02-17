I'll help you create an API extraction for the Orient Aura portal. Let me first examine the existing API implementations for Takaful, Qatar, and Adnic to understand the pattern, then analyze the Orient Aura RPA flow.    

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/takafulmain_api.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/qatar/qatar_main_api.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/adnic/adnicmain_api.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/auth.py#1-1), lines 1 to 100

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/client.py#1-1), lines 1 to 100

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/extractor.py#1-1), lines 1 to 150

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/qatar/api/extractor.py#1-1), lines 1 to 150

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/adnic/api/extractor.py#1-1), lines 1 to 150

Now let me read the Orient Aura RPA flow files and check the JSON structure:   

Read [](file:///e%3A/Algospring/rpa_system_dev%201/rpa_system_dev/src/pages/orient_aura/categories/category_1_page.py#1-1), lines 1 to 100

Read [](file:///e%3A/Algospring/rpa_system_dev%201/rpa_system_dev/src/pages/orient_aura/categories/category_2_page.py#1-1), lines 1 to 100

Read [](file:///e%3A/Algospring/rpa_system_dev%201/rpa_system_dev/src/pages/orient_aura/categories/category_3_page.py#1-1), lines 1 to 100

Let me check the mapping files to understand the API structure better:   

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/mapping.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/qatar/api/mapping.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/adnic/api/mapping.py#1-1), lines 1 to 150

Now let me check the `__init__.py` files to see what's exported:   

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/__init__.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/qatar/api/__init__.py)

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/adnic/api/__init__.py)

Now let me check the formatter files to understand the output format:     

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/takaful/api/formatter.py#1-1), lines 1 to 100

Read [](file:///c%3A/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/qatar/api/formatter.py#1-1), lines 1 to 100

Perfect! Now I have a clear understanding of the API extraction pattern. Let me check one more important file to understand the quotation page flow in Orient Aura:  

Read [](file:///e%3A/Algospring/rpa_system_dev%201/rpa_system_dev/src/pages/orient_aura/categories/category_1_page.py#1-1), lines 1 to 100

Read [](file:///e%3A/Algospring/rpa_system_dev%201/rpa_system_dev/src/pages/orient_aura/categories/category_1_page.py#100-100), lines 100 to 230

Excellent! Now I have a complete understanding. Let me create a comprehensive guide for you:

---

## 📋 **Orient Aura API Extraction - Implementation Guide**

Based on my analysis of Takaful, Qatar, and Adnic API extractions, Orient Aura follows the **same Aura platform pattern** as Takaful and Qatar. Here's what you need to provide and what I'll create:

---

### **🔍 What I Found:**

**Orient Aura Portal Structure:**
- **Platform**: Aura Insurance Platform (same as Takaful & Qatar)
- **Base URL**: `https://smehealth.aurainsure.tech/08/orient/login`
- **API Base URL**: `https://smehealth-api.aurainsure.tech` (same as Takaful/Qatar)
- **Pattern**: Very similar to Takaful - uses same API endpoints with different group_id

**Key Dropdowns from RPA Flow:**
1. **TPA** (Third Party Administrator)
2. **Network/Medical Network** (Plan)
3. **Territory/Geographical Coverage**
4. **Annual Limit**
5. **Room Category**
6. **Deductible**
7. **Pharmacy Limit & Co-pay**
8. **Diagnostics Co-pay**
9. **Dental & Optical benefits**
10. **Maternity benefits**
11. **Alternative Medicine**
12. **Various other medical benefits**

---

### **📦 What You Need to Provide:**

To create the API extraction, I need the following **API network data** from the Orient Aura portal:

#### **Step 1: Login & Get Auth Token**
1. Open Orient Aura portal in browser
2. Open **Developer Tools** (F12) → **Network Tab**
3. Login to the portal
4. Look in **Application** → **Local Storage** → Find the auth token
   
**Please provide:**
- ✅ Auth token storage key name (e.g., `"token"`, `"authToken"`)

---

#### **Step 2: Create New Quote & Capture API Calls**

After login, click **"Create new quote"** and fill the initial form. Monitor the **Network tab** for these API calls:

##### **A. Pre-Level: Industry Categories (Business Nature)**
**API Call:** `/quotes/generate/industry`
```
GET https://smehealth-api.aurainsure.tech/quotes/generate/industry
```

**Please provide:**
- ✅ Full API URL
- ✅ Query parameters (if any)
- ✅ Sample JSON response

---

##### **B. Level 0: Get Emirates**
**API Call:** `/quotes/generate/emirates`
```
GET https://smehealth-api.aurainsure.tech/quotes/generate/emirates?groupId=XXX
```

**Please provide:**
- ✅ `groupId` value for Orient Aura (e.g., Takaful=31, Qatar=272, Orient=?)
- ✅ Sample JSON response showing available emirates

---

##### **C. Level 1: Get TPAs for Dubai**
**API Call:** `/quotes/generate/tpa`
```
GET https://smehealth-api.aurainsure.tech/quotes/generate/tpa?emiratesId=XXX
```

**Please provide:**
- ✅ `emiratesId` for Dubai in Orient portal
- ✅ Sample JSON response showing all TPAs (Aafiya, Nextcare, etc.)
- ✅ For each TPA, note the `tpa_id` and `reinsurer_company_id`

---

##### **D. Level 2: Get Plans for each TPA**
**API Call:** `/quotes/generate/plan`
```
GET https://smehealth-api.aurainsure.tech/quotes/generate/plan?tpaId=XXX
```

**Please provide:**
- ✅ Sample API call for ONE TPA (e.g., Nextcare)
- ✅ JSON response showing all available plans/networks

---

##### **E. Level 3: Get Benefits for each Plan**
**API Call:** `/quotes/generate/benefits`
```
GET https://smehealth-api.aurainsure.tech/quotes/generate/benefits?planId=XXX&reinsurerCompanyId=XXX
```

**Please provide:**
- ✅ Sample API call for ONE plan
- ✅ JSON response showing all benefit dropdowns (Annual Limit, Room Category, Pharmacy, Dental, Optical, etc.)

---

### **📸 Example of What to Capture:**

For each API call in Network tab:
1. **Right-click** on the API call
2. **Copy** → **Copy as cURL**
3. OR note down:
   - Request URL
   - Query parameters
   - Response JSON

**Example Format:**
```
API: /quotes/generate/tpa?emiratesId=123
Response:
{
  "response": [
    {
      "tpa_id": "456",
      "tpa_name": "Nextcare",
      "reinsurer_company_id": 8
    },
    ...
  ]
}
```

---

### **🎯 What I'll Create For You:**

Once you provide the API data above, I'll create:

```
c:/Users/mandinu.m/Documents/GitHub/Extraction_Bot/src/pages/orient_aura/
├── orient_aura_main_api.py      ← Main entry point
└── api/
    ├── __init__.py               ← Module exports
    ├── auth.py                   ← Token extraction from browser
    ├── client.py                 ← HTTP client for API calls
    ├── extractor.py              ← API extraction orchestrator
    ├── formatter.py              ← Output formatter
    └── mapping.py                ← Hardcoded Orient Aura config
```

**Files will include:**
- ✅ Login & token extraction
- ✅ Hierarchical API extraction (Industry → Emirates → TPAs → Plans → Benefits)
- ✅ JSON output with all dropdown values
- ✅ Formatted text output for database import
- ✅ Logging & error handling
- ✅ Same pattern as Takaful/Qatar for consistency

---

### **🚀 Next Steps:**

1. **You**: Provide the API data from Network tab (see "What You Need to Provide" section above)
2. **Me**: Create all the API extraction files based on the data
3. **You**: Test the extraction
4. **Me**: Fix any issues and refine

---

### **💡 Tips for Capturing API Data:**

- Clear Network tab before each action
- Use **XHR/Fetch filter** in Network tab
- Look for URLs containing `/quotes/generate/`
- Most important: Get the **complete JSON responses** for each API
- Note any **required headers** (usually just Authorization with Bearer token)

---

**Ready when you are!** Just provide the API network data and I'll build the complete Orient Aura API extraction system. 🎯