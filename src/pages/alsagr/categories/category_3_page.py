import asyncio
from src.utils.load_yaml import MED_SLEEP
from src.utils.logger import alsagr_logger

class Category3Page:
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
    
    async def fill_category_3(self, cat3):
        """Fill Category 3 benefits form with error handling"""
        alsagr_logger.debug("Filling Category 3 benefits")
        
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
        column = 3  # Category 3 uses column 3
        
        # Process each field
        for data_key, field_name, use_div, transform_func in field_configs:
            try:
                # Get value from data or use static value
                if data_key is None:
                    value = transform_func(None)
                else:
                    raw_value = cat3[data_key].iloc[0]
                    value = transform_func(raw_value)
                
                # Generate selector
                selector = self._get_selector(row, column, use_div)
                
                # Select field
                success = await self._select_field(selector, value, field_name)
                if not success:
                    alsagr_logger.error(f"Failed to fill Category 3 benefits at field: {field_name}")
                    return False
                
                row += 1
                
            except (KeyError, IndexError, AttributeError) as e:
                alsagr_logger.error(f"Data error for {field_name}: {e}")
                return False
            except Exception as e:
                alsagr_logger.error(f"Unexpected error processing {field_name}: {e}")
                return False
        
        alsagr_logger.debug("Category 3 completed successfully")
        return True
    
    async def fill_category_3_batch(self, cat3_list):
        """Fill multiple Category 3 records in batch"""
        results = []
        for i, cat3 in enumerate(cat3_list):
            alsagr_logger.info(f"Processing Category 3 record {i+1}/{len(cat3_list)}")
            result = await self.fill_category_3(cat3)
            results.append(result)
            if not result:
                alsagr_logger.warning(f"Failed to process record {i+1}")
        
        success_count = sum(results)
        alsagr_logger.info(f"Batch processing completed: {success_count}/{len(cat3_list)} successful")
        return results