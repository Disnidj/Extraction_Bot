from src.utils import load_yaml
import json

def write_json_to_file(json_data):
    """Helper function to write JSON data to file"""
    try:
        with open(load_yaml.EXTRACTED_DATA_DIR, "a", encoding="utf-8") as f:
            f.write(json.dumps(json_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error writing JSON to file: {e}")

async def brocker_margin(portal_name: str, dropdown_selector: str):
    try:
        # dropdown = page.locator(dropdown_selector)

        if not await dropdown_selector.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown_selector.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "Field": "Brocker Margin",
                "values": values
            }
        }

        # Write JSON to file
        write_json_to_file(json_data)

        print("Extracted values:", values)
        return values

    except Exception as e:
        print(f"Error: {e}")
        return []

async def extract_tpa(portal_name: str, field_name: str, dropdown_selector: str):
    try:
        if not await dropdown_selector.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown_selector.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "field name": field_name,
                "values": values
            }
        }

        # Write JSON to file
        write_json_to_file(json_data)

        print("Extracted values:", values)
        return values

    except Exception as e:
        print(f"Error: {e}")
        return []

async def extract_network(portal_name: str,  tpa: str, field_name: str, dropdown_selector: str):
    try:
        if not await dropdown_selector.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown_selector.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "TPA": tpa,
                "field name": field_name,
                "values": values
            }
        }

        # Write JSON to file
        write_json_to_file(json_data)

        print("Extracted values:", values)
        return values

    except Exception as e:
        print(f"Error: {e}")
        return []
    
async def extract_dropdown_values(tpa, network, field_name: str, dropdown_selector: str, portal_name: str, region: str = "Dubai") -> list:
    print(f"Extracting values from: {dropdown_selector}")
    # config = BenefitConfig(tpa=tpa, network=network, region=region)
    
    try:
        # dropdown = page.locator(dropdown_selector)
        
        if not await dropdown_selector.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown_selector.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "TPA": tpa,
                "Region": region,
                "Network": network,
                "field name": field_name,
                "values": values
            }
        }

        # Write JSON to file
        write_json_to_file(json_data)

        # print(f"Extracted {len(values)} values written to {load_yaml.EXTRACTED_DATA_DIR}")
        print("Extracted values:", values)
        return values
        
    except Exception as e:
        print(f"Error: {e}")
        return []