# import time
# from src.utils.load_yaml import MED_SLEEP
# from src.utils.logger import alsagr_logger

# # class for the Category 2 benefits mapping
# class Category2Page:
#     def __init__(self, page):
#         self.page = page

#     async def fill_category_2(self, cat2):
#         # Ensure all values are strings and select options for Category 2

#         alsagr_logger.debug("Filling Category 2 benefits")
#         # # Cat A Plan
#         # network = str(cat2['Network'].iloc[0])
#         # print(network)
#         # await self.page.select_option('#category2', value=network)
#         # time.sleep(MED_SLEEP)
#         # alsagr_logger.debug("Network selected: " + network)
#         row = 2
#         column = 2

#         # Region
#         # Region
#         region = str(cat2['Region'].iloc[0])    
#         alsagr_logger.debug(f"Region (Before Apply): {region}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/select', value=region)  
#         alsagr_logger.debug(f"Region (After Apply): {region}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # Network
#         network = str(cat2['Network'].iloc[0]).strip()
#         alsagr_logger.debug(f"Network (Before Apply): {network}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/select', value=network)
#         alsagr_logger.debug(f"Network (After Apply): {network}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # Remarks
#         remarks = "None"
#         alsagr_logger.debug(f"Remarks (Before Apply): {remarks}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/div/select', value=remarks)
#         alsagr_logger.debug(f"Remarks (After Apply): {remarks}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # OP Co-Insurance
#         op_co_insurance = str(cat2['Op Co Insurance'].iloc[0])
#         alsagr_logger.debug(f"OP Co-Insurance (Before Apply): {op_co_insurance}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/div/select', value=op_co_insurance)
#         alsagr_logger.debug(f"OP Co-Insurance (After Apply): {op_co_insurance}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # Phar.Co-Ins
#         phar_co_ins = str(cat2['Pharmacy'].iloc[0])
#         alsagr_logger.debug(f"Phar.Co-Ins (Before Apply): {phar_co_ins}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/div/select', value=phar_co_ins)
#         alsagr_logger.debug(f"Phar.Co-Ins (After Apply): {phar_co_ins}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # Dental
#         dental = str(cat2['Dental'].iloc[0])
#         alsagr_logger.debug(f"Dental (Before Apply): {dental}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/div/select', value=dental)
#         alsagr_logger.debug(f"Dental (After Apply): {dental}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         # Optical
#         optical = str(cat2['Optical'].iloc[0])
#         alsagr_logger.debug(f"Optical (Before Apply): {optical}")
#         await self.page.select_option(f'//table/tbody/tr[{row}]/td[{column}]/div/select', value=optical)
#         alsagr_logger.debug(f"Optical (After Apply): {optical}")
#         time.sleep(MED_SLEEP)
#         row += 1

#         alsagr_logger.debug("Category 2 completed")

import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import alsagr_logger

class Category2Page:
    def __init__(self, page):
        self.page = page
    
    async def _select_field(self, selector, value, field_name, timeout=5000):
        """Helper method to select a field with error handling"""
        try:
            alsagr_logger.debug(f"{field_name} (Before Apply): {value}")
            await self.page.select_option(selector, value=value, timeout=timeout)
            alsagr_logger.debug(f"{field_name} (After Apply): {value}")
            await asyncio.sleep(MED_SLEEP)
            return True
        except Exception as e:
            alsagr_logger.error(f"Error occurred while selecting {field_name}: {e}")
            return False
    
    def _get_selector(self, row, column, use_div=False):
        """Generate XPath selector based on row, column, and element type"""
        base_path = f'//table/tbody/tr[{row}]/td[{column}]'
        return f'{base_path}/div/select' if use_div else f'{base_path}/select'
    
    async def fill_category_2(self, cat2):
        """Fill Category 2 benefits form with error handling"""
        alsagr_logger.debug("Filling Category 2 benefits")
        
        # Define field configurations: (data_key, field_name, use_div, transform_func)
        field_configs = [
            ('Region', 'Region', False, lambda x: str(x).strip()),
            ('Network', 'Network', False, lambda x: str(x).strip()),
            (None, 'Remarks', True, lambda x: "None"),  # Static value
            ('Op Co Insurance', 'OP Co-Insurance', True, lambda x: str(x).strip()),
            ('Pharmacy', 'Phar.Co-Ins', True, lambda x: str(x).strip()),
            ('Dental', 'Dental', True, lambda x: str(x).strip()),
            ('Optical', 'Optical', True, lambda x: str(x).strip())
        ]
        
        row = 2
        column = 2  # Category 2 uses column 2
        
        # Process each field
        for data_key, field_name, use_div, transform_func in field_configs:
            try:
                # Get value from data or use static value
                if data_key is None:
                    value = transform_func(None)
                else:
                    raw_value = cat2[data_key].iloc[0]
                    value = transform_func(raw_value)
                
                # Generate selector
                selector = self._get_selector(row, column, use_div)
                
                # Select field
                success = await self._select_field(selector, value, field_name)
                if not success:
                    alsagr_logger.error(f"Failed to fill Category 2 benefits at field: {field_name}")
                    return False
                
                row += 1
                
            except (KeyError, IndexError, AttributeError) as e:
                alsagr_logger.error(f"Data error for {field_name}: {e}")
                return False
            except Exception as e:
                alsagr_logger.error(f"Unexpected error processing {field_name}: {e}")
                return False
        
        alsagr_logger.debug("Category 2 completed successfully")
        return True
    
    async def fill_category_2_batch(self, cat2_list):
        """Fill multiple Category 2 records in batch"""
        results = []
        for i, cat2 in enumerate(cat2_list):
            alsagr_logger.info(f"Processing Category 2 record {i+1}/{len(cat2_list)}")
            result = await self.fill_category_2(cat2)
            results.append(result)
            if not result:
                alsagr_logger.warning(f"Failed to process record {i+1}")
        
        success_count = sum(results)
        alsagr_logger.info(f"Batch processing completed: {success_count}/{len(cat2_list)} successful")
        return results

