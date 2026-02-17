Based on the screenshot and request data, here's the **Orient Aura Portal Field Mapping**:

## Plan Selection Page (Choose Plans)

| **Portal Field Name** | **JSON Field Name** | **Example Value** |
|----------------------|---------------------|-------------------|
| Territorial Scope of Coverage | `Territory` | "Worldwide" |
| Aggregate Annual Limit | `Annual Limit` | "AED 2 Million" |
| Medical Network | `Network` | "NEXTCARE CN+ (IP) / GN Excluding Mediclinic, Al Zahra & Hmg (Op)" |
| In-patient Room Type | `Room Category` | "Private" |
| Deductible per Consultation | `Deductable` | "20% Max AED 50/-" |
| Prescribed Drugs & Medicines Annual Limit | `Limit of Phamacy` | "Up to AAL" |
| Prescribed Drugs & Medicines Co-pay | `Pharmacy` | "NIL Co-pay" |
| Diagnostics Co-pay | `Diagnostic Copay` or `Op Co Insurance` | "NIL Co-pay" |
| Dental benefit | `Dental` | "AED 500 with 30% Co-pay" |
| Optical benefit | `Optical` | "Not Covered" |

## Quotation Details Page (Earlier Form)

| **Portal Field Name** | **JSON Field Name** | **Example Value** |
|----------------------|---------------------|-------------------|
| Company Name | `generalData.Company Name` | "IIB User" |
| Trade License Number | `generalData.Trade License Number` | "234" |
| Email Address | `generalData.Email` | "user1@lifecare.com" |
| Contact Number | `generalData.Contact Number` | "971545079578" |
| Business Nature | `Business Nature` | "Other Industries" |
| Policy Start Date | `generalData.Effective from` | "03/08/2026" |
| Number of Categories | `generalData.Category` (length) | 2 (array: ["A", "B"]) |
| Broker Commission | `Broker Commission` | "5" |
| Previous Insured | `Previous Insured` | "No" |
| Group/Product Type | `TPA` | "Nextcare Sme - Nextcare" |
| Emirates (Category 1) | `Emirates` | "Dubai" |
| Emirates (Category 2) | `Emirates` | "Dubai" |
| TPA (Category 1) | `TPA` (extract after "-") | "Nextcare" |
| TPA (Category 2) | `TPA` (extract after "-") | "Nextcare" |
| Plan (Category 1) | `Network` | "Plan1 GN Excluding Mediclinic, Al Zahra & Hmg" |
| Plan (Category 2) | `Network` | "Plan1 GN+ (Ip) / Gn Excluding Mediclinic, Al Zahra & Hmg (Op)" |

## Column Headers

| **Portal Column** | **JSON Category** |
|------------------|-------------------|
| Category A | `individualDataList[0]` where `Category` = "A" |
| Category B | `individualDataList[1]` where `Category` = "B" |
| Category C | `individualDataList[2]` where `Category` = "C" |

## Special Field Name Variations (Aliases)

Some fields have multiple possible JSON names:

- **OP Co-pay**: Could be `Op Co Insurance`, `Diagnostic Copay`, or `Diagnostics Co-pay`
- **Pharmacy Limit**: Could be `Limit of Phamacy` or `Pharmacy limit`
- **Room Type**: Could be `Room Category` or `In-patient Room Type`

The code uses these field names to locate dropdowns via XPath:
```python
selector = f"//td[normalize-space(.)='{field_name}' or contains(normalize-space(.), '{field_name}')]/following-sibling::td[{column}]/select"
```