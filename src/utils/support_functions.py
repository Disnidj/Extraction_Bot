from src.utils.load_yaml import BASE_PATH
from vertexai.generative_models import GenerativeModel, Part
import vertexai
from datetime import datetime
import os
import json
from src.utils import load_yaml
import asyncio
import base64


# Keep your existing helper functions
def convert_to_int(dropdownValue, excelValue):
    try:
        if excelValue is None:
            return dropdownValue
        else:
            return str(int(excelValue))
    except ValueError:
        return excelValue

def get_replaced_referral_id(value):
    try:
        return value.replace("/", "-")
    except Exception as e:
        return Exception(f"Error replacing value: {e}")

async def extract_json_from_markdown(markdown_text):
    """
    Extracts JSON data from a Markdown string with ```json formatting.
    """
    parts = markdown_text.split('```json')
    
    if len(parts) > 1:
        json_part = parts[1].split('```')[0]
    else:
        json_part = markdown_text
    
    json_part = json_part.strip()
    json_part = json_part.replace("True", "true").replace("False", "false")
    try:
        return json.loads(json_part)
    except json.JSONDecodeError as e:
        raise ValueError(f"Could not extract valid JSON from the markdown text: {e}\nExtracted: {json_part}")

def write_json_to_file(json_data):
    """Helper function to write JSON data to file"""
    try:
        with open(load_yaml.EXTRACTED_DATA_DIR, "a", encoding="utf-8") as f:
            f.write(json.dumps(json_data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"Error writing JSON to file: {e}")

async def extract_dropdown_values(page, region, tpa, network, field_name: str, dropdown_selector: str, portal_name: str, outpatient_plan=None, additionaly_benefits_plan=None) -> list:
    print(f"Extracting values from: {dropdown_selector}")

    def clean_text(text):
        if not text:
            return ""
        return text.replace('\r\n', ' ').strip('')

    try:
        dropdown = page.locator(dropdown_selector)
        if not await dropdown.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        if portal_name in ['Orient Insurance PJSC','Dubai National Insurance And Reinsurance Co', 'RAK INSURANCE']:
            await dropdown.click()
            await page.wait_for_timeout(500)
            try:
                await page.wait_for_selector('.dx-list-item', timeout=2000)
            except Exception as e:
                print(f"Timeout waiting for .dx-list-item: {e}")

            dropdown_containers = await page.locator('.dx-overlay-content, .dx-popup-content, .dx-dropdownlist-popup').all()
            values = []
            for container in dropdown_containers[::-1]:
                items = await container.locator('.dx-list-item').all()
                if items:
                    raw_values = [await item.text_content() for item in items if await item.text_content()]
                    values = [clean_text(v) for v in raw_values if clean_text(v)]
                    break

            if not values:
                parent_container = dropdown.locator('xpath=ancestor::*[contains(@class, "dx-select")]').first
                options_fallback = await parent_container.locator('.dx-list-item, .dx-item, [role="option"], .dropdown-item').all()
                raw_values = [await opt.text_content() for opt in options_fallback if await opt.text_content()]
                values = [clean_text(v) for v in raw_values if clean_text(v)]

            print(f"{field_name} options: {values}")

            # Add extra fields for IQ companies
            json_data = {
                "data": {
                    "Portal": portal_name,
                    "TPA": tpa,
                    "Region": region,
                    "Network": network,
                    "Outpatient Plan": outpatient_plan,
                    "Additional Benefits Plan": additionaly_benefits_plan ,
                    "field name": field_name,
                    "values": values
                }
            }
        else:
            options = await dropdown.locator("option").all_inner_texts()
            values = [clean_text(opt) for opt in options if clean_text(opt)]

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

        write_json_to_file(json_data)
        print("Extracted values:", values)
        return values

    except Exception as e:
        print(f"Error: {e}")
        return []

async def extract_mui_dropdown_values(page, region, tpa, network, field_name: str, dropdown_selector: str, portal_name: str) -> list:
    """
    Extracts dropdown values from a Material-UI dropdown (list of <li> elements).
    """
    print(f"Extracting values from: {dropdown_selector}")
    try:
        max_attempts = 5
        for attempt in range(max_attempts):
            # Check if dropdown options are already visible
            options = await page.locator("//li[contains(@class, 'MuiMenuItem-root')]").all_text_contents()
            if options:
                break
            # If not, close any open dropdowns and click to open
            await page.keyboard.press("Escape")
            await asyncio.sleep(0.5)
            await page.click(dropdown_selector)
            await asyncio.sleep(1)
        
        # After attempts, get the options
        options = await page.locator("//li[contains(@class, 'MuiMenuItem-root')]").all_text_contents()
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

        print("Extracted values:", values)
        return values

    except Exception as e:
        print(f"Error: {e}")
        return []

# async def extract_dropdown_values_iq(page, region, tpa, network, outpatient_plan, additionaly_benefits_plan, field_name: str, dropdown_selector: str, portal_name: str) -> list:
#     """
#     Extract dropdown values for IQ portals, including plan value.
#     Uses custom dropdown extraction logic.
#     """
#     print(f"Extracting values from: {dropdown_selector} (IQ Portal)")

#     def clean_text(text):
#         if not text:
#             return ""
#         return text.replace('\r\n', '').strip()

#     try:
#         dropdown = page.locator(dropdown_selector)
#         if not await dropdown.is_visible():
#             raise Exception(f"Dropdown {dropdown_selector} not visible")

#         await dropdown.click()
#         await page.wait_for_timeout(500)

#         try:
#             await page.wait_for_selector('.dx-list-item', timeout=2000)
#         except Exception as e:
#             print(f"Timeout waiting for .dx-list-item: {e}")

#         dropdown_containers = await page.locator('.dx-overlay-content, .dx-popup-content, .dx-dropdownlist-popup').all()
#         values = []
#         for container in dropdown_containers[::-1]:  # check from last (topmost overlay)
#             items = await container.locator('.dx-list-item').all()
#             if items:
#                 raw_values = [await item.text_content() for item in items if await item.text_content()]
#                 values = [clean_text(v) for v in raw_values if clean_text(v)]
#                 break

#         # Fallback: If still empty, try the previous logic
#         if not values:
#             parent_container = dropdown.locator('xpath=ancestor::*[contains(@class, "dx-select")]').first
#             options_fallback = await parent_container.locator('.dx-list-item, .dx-item, [role="option"], .dropdown-item').all()
#             raw_values = [await opt.text_content() for opt in options_fallback if await opt.text_content()]
#             values = [clean_text(v) for v in raw_values if clean_text(v)]

#         json_data = {
#             "data": {
#                 "Portal": portal_name,
#                 "TPA": tpa,
#                 "Region": region,
#                 "Network": network,
#                 "Outpatient Plan": outpatient_plan,
#                 "Additional Benefits Plan": additionaly_benefits_plan,
#                 "field name": field_name,
#                 "values": values
#             }
#         }

#         write_json_to_file(json_data)
#         print("Extracted values:", values)
#         return values

#     except Exception as e:
#         print(f"Error: {e}")
#         return []
        
async def extract_region(page, portal_name: str, field: str, dropdown_selector: str):
    try:
        dropdown = page.locator(dropdown_selector)

        if not await dropdown.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "Field": field,
                "values": values
            }
        }

        # Write JSON to file
        write_json_to_file(json_data)

    except Exception as e:
        print(f"Error: {e}")
        return []

async def extract_tpa(page, portal_name: str, region: str, field: str, dropdown_selector: str):
    try:
        dropdown = page.locator(dropdown_selector)

        if not await dropdown.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "Region": region,
                "field name": field,
                "values": values
            }
        }

        print("Extracted values:", values)

        # Write JSON to file
        write_json_to_file(json_data)

    except Exception as e:
        print(f"Error: {e}")
        return []

async def extract_network(page, portal_name: str, region: str, tpa: str, field: str, dropdown_selector: str):
    try:
        dropdown = page.locator(dropdown_selector)

        if not await dropdown.is_visible():
            raise Exception(f"Dropdown {dropdown_selector} not visible")

        options = await dropdown.locator("option").all_inner_texts()
        values = [opt for opt in options if opt]

        # Create JSON structure
        json_data = {
            "data": {
                "Portal": portal_name,
                "Region": region,
                "TPA": tpa,
                "field name": field,
                "values": values
            }
        }

        print("Extracted values:", values)

        # Write JSON to file
        write_json_to_file(json_data)

    except Exception as e:
        print(f"Error: {e}")
        return []


# Screenshot and comparison functions
async def take_screenshot(page, file_name):
    """
    Takes a screenshot of the current page using Playwright.
    """
    file_path = f"{BASE_PATH}\\image\\{file_name}.png"
    try:
        await page.screenshot(path=file_path, full_page=True)
        print(f"Screenshot saved to {file_path}")
        return file_path
    except Exception as e:
        print(f"Error taking screenshot: {e}")

async def screenshot_and_compare(page, reference_image_path, screenshot_name):
    """
    Takes a screenshot of the current page, compares it with a reference image, and outputs if they are different.
    """
    reference_image_path = f"{BASE_PATH}\\image\\{reference_image_path}\\{screenshot_name}.png"
    print(f"Reference image path: {reference_image_path}")
    screenshot_path = await take_screenshot(page, screenshot_name)
    are_same = await gemini(screenshot_path, reference_image_path)
    result = await extract_json_from_markdown(are_same)

    print("Comparison Result:", result)
    if result.get("are_images_same", True):
        print("\033[92mImages are similar.\033[0m")
        return True
    else:
        print("\033[91mImages are different.\033[0m")
        return False

def load_image_as_part(image_path):
    """
    Load an image file and convert it to a Part object for Gemini.
    """
    try:
        with open(image_path, 'rb') as image_file:
            image_data = image_file.read()
        
        # Create a Part object with the image data
        return Part.from_data(
            data=image_data,
            mime_type="image/png"
        )
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None

async def gemini(image1_path, image2_path):
    try:
        # Set the environment variable for credentials
        GOOGLE_APPLICATION_CREDENTIALS = f"{BASE_PATH}\\ocr\\gcp\\viva-project-467813-65f5e24b2c67.json"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
        
        # Verify credentials file exists
        if not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
            raise FileNotFoundError(f"Credentials file not found: {GOOGLE_APPLICATION_CREDENTIALS}")
        

        # Initialize Vertex AI with the correct project ID (not the service account filename)
        vertexai.init(
            project="viva-project-467813", 
            location="us-central1",
        )

        # Initialize the model
        model = GenerativeModel("gemini-2.0-flash-001")  

        # Load images as Part objects
        image1_part = load_image_as_part(image1_path)
        image2_part = load_image_as_part(image2_path)
        
        if not image1_part or not image2_part:
            print("Failed to load one or both images")
            return '{"are_images_same": false, "differences": [{"category": "Error", "description": "Failed to load images"}]}'

        print("Images loaded successfully, generating content...")
        
    except Exception as setup_error:
        print(f"Error during setup: {setup_error}")
        return f'{{"are_images_same": false, "differences": [{{"category": "Error", "description": "Setup failed: {str(setup_error)}"}}]}}'

    # Updated prompt - removed the file paths since we're sending actual images
    prompt = """
        You are a specialized document comparison expert focusing on insurance-related forms. Your task is to analyze two images and compare them **strictly for the existence and type of text elements** (labels, field names, headings, etc.), while completely ignoring all input values, numbers, or user-entered data.

        1. **Ignore completely**:
        - All input values, numbers, or user-filled data fields
        - Layout, formatting, font styles, colors, or visual design
        - Structural variations (e.g., forms vs. tables, bullet points vs. columns)
        - Empty form fields or placeholders

        2. **Focus only on**:
        - Presence or absence of text elements (labels, field names, headings, section titles)
        - **Type of UI element** (e.g., input box, dropdown, checkbox) for each field/label
        - Mismatched, missing, or changed text elements and UI element types between the two images

        3. **Output requirements**:
        - If **all text elements and their UI types exist in both images** (regardless of order or structure), return:
            ```json
            {"are_images_same": true, "differences": []}
            ```
        - Otherwise, list **only missing, extra, or changed text elements/UI types** in this JSON format:
            ```json
            {
            "are_images_same": false,
            "differences": [
                {
                "category": "Field or label name",
                "image1_value": "UI element type in image 1 (e.g., input, dropdown, etc.)",
                "image2_value": "UI element type in image 2",
                "description": "Describe if the text element is missing, extra, or if the UI element type changed (e.g., 'Changed from input box to dropdown')"
                }
            ]
            }
            ```

        4. **Key directives**:
        - Never compare or mention input values or user data.
        - Only compare the existence and type of text elements.
        - If a UI element changes type (e.g., input box to dropdown), include this in the differences.
        - Ignore duplicates and focus on unique text elements.
        
        Please analyze the two images provided and return only the JSON response.
    """
    
    try:
        # Generate the response with both images and the prompt
        response = model.generate_content([prompt, image1_part, image2_part])
        print("Content generated successfully")
        print(response.text)
        return response.text
    except Exception as e:
        error_msg = str(e)
        print(f"Error generating content: {error_msg}")
        
        # Check for specific permission errors
        if "403" in error_msg or "Permission denied" in error_msg:
            print("Permission error detected. Please check:")
            print("1. Service account has 'Vertex AI User' role")
            print("2. Vertex AI API is enabled in the project")
            print("3. Service account key is valid and not expired")
            
        return f'{{"are_images_same": false, "differences": [{{"category": "Error", "description": "Failed to analyze images: {error_msg}"}}]}}'
