import os
from src.utils.load_yaml import ATTACHMENTS_SAVE_DIR#, NLG_GENERATED_CENSUS_DIR, NLG_QUOTATION_DIR, AURA_GENERATED_CENSUS_DIR, TAKAFUL_QUOTATION_DIR, MAIL_ZIP_FILES, COMPARISON_GENERATED_DIR, IQ2HEALTH_GENERATED_CENSUS_DIR, ORIENT_QUOTATION_DIR, RAK_QUOTATION_DIR,SUKOON_GENERATED_CENSUS_DIR,SUKOON_QUOTATION_DIR,MAXHEALTH_GENERATED_CENSUS_DIR,MAXHEALTH_QUOTATION_DIR, DUBAIINSURANCE_GENERATED_CENSUS_DIR, DUBAIINSURANCE_QUOTATION_DIR, UNIONINSURANCE_GENERATED_CENSUS_DIR, UNIONINSURANCE_QUOTATION_DIR, ADNIC_GENERATED_CENSUS_DIR, ADNIC_QUOTATION_DIR, ALSAGR_GENERATED_CENSUS_DIR, ALSAGR_QUOTATION_DIR,GIG_GENERATED_CENSUS_DIR,GIG_QUOTATION_DIR,ADNIC_HTML_DIR, MEDGULF_QUOTATION_DIR, ALITTIHAD_ALWATANI_QUOTATION_DIR,TEMP_FILES_DIR,DAMAN_GENERATED_CENSUS_DIR,DAMAN_QUOTATION_DIR


async def remove_files_from_subfolders(directory):
    """Removes all files within subfolders of the specified directory.

    Args:
      directory: The directory path.
    """

    for root, dirs, files in os.walk(directory):
        for file in files:
            os.remove(os.path.join(root, file))

async def remove_folders_in_directory(directory):
    """Removes all folders within the specified directory.
    
    Args:
      directory: The directory path.
    """
    try:
        # Get all items in the directory
        items = os.listdir(directory)
        
        # Iterate through items and remove folders
        for item in items:
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                # Remove all files and subdirectories recursively
                for root, dirs, files in os.walk(item_path, topdown=False):
                    # First remove all files in this directory
                    for file in files:
                        os.remove(os.path.join(root, file))
                    # Then remove the directory itself
                    for dir_name in dirs:
                        os.rmdir(os.path.join(root, dir_name))
                # Finally remove the top directory
                os.rmdir(item_path)
        return True
    except Exception as e:
        print(f"Error removing folders in {directory}: {str(e)}")
        return False
            

# Example usage:


async def clear_files():

    await remove_files_from_subfolders(ATTACHMENTS_SAVE_DIR)

