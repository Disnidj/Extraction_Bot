import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_region, extract_tpa, extract_network, extract_dropdown_values, screenshot_and_compare
from src.utils.logger import daman_logger

class Category1Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_1(self, catA, salary_A, region, tpa, network, portal_name):
        daman_logger.info("Category A Started")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "daman", "DAMAN_INSURANCE_2")
            await asyncio.sleep(MAX_SLEEP)
        except Exception as e:
            daman_logger.error(f"An error occurred while marking the checkbox: {e}")
        
        # Initialize field tracking
        initial_successful_fields = 0
        initial_failed_fields = []
        
        # Select option for 'CAT A' with timeout protection
        try:
            category = "CAT " + str(catA['Category'].iloc[0]).strip()
            daman_logger.info(f"category name: {category}")
            
            try:
                await asyncio.wait_for(
                    self.page.fill('input[name="smeQuotationDTO.categories[0].categoryName"]', value=category.rstrip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Category Name filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Category Name: Fill timeout after 10 seconds")
                initial_failed_fields.append("Category Name")
            except Exception as e:
                daman_logger.error(f"❌ Category Name: Fill failed - {e}")
                initial_failed_fields.append("Category Name")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category Name: {e}")
            initial_failed_fields.append("Category Name")

        # Select option for 'Visa' - Using extract_region with timeout protection
        try:
            visa = str(catA['Region'].iloc[0])
            daman_logger.info(f"visa value: {visa}")
            selector = 'select[name="smeQuotationDTO.categories[0].visa"]'
            field = 'Region'
            
            try:
                await extract_region(self.page, portal_name, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ Visa: Failed to extract region values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=visa.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Visa value filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Visa: Selection timeout after 10 seconds")
                initial_failed_fields.append("Visa")
            except Exception as e:
                daman_logger.error(f"❌ Visa: Selection failed - {e}")
                initial_failed_fields.append("Visa")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Visa: {e}")
            initial_failed_fields.append("Visa")
    
        # Select option for 'Plan' - Using extract_tpa with timeout protection
        try:
            plan = str(catA['TPA'].iloc[0])
            daman_logger.debug("TPA Value:" + plan)
            selector = 'select[name="smeQuotationDTO.categories[0].plan"]'
            field = 'TPA'
            
            try:
                await extract_tpa(self.page, portal_name, region, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ TPA: Failed to extract TPA values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=plan.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ TPA value filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ TPA: Selection timeout after 10 seconds")
                initial_failed_fields.append("TPA")
            except Exception as e:
                daman_logger.error(f"❌ TPA: Selection failed - {e}")
                initial_failed_fields.append("TPA")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing TPA: {e}")
            initial_failed_fields.append("TPA")
        
        # Select option for 'Salary Band' with timeout protection
        try:
            success = await self.select_option_with_error_handling(region, tpa, network, "Salary Band", salary_A, 'select[name="smeQuotationDTO.categories[0].salaryBand"]', portal_name)
            if success:
                initial_successful_fields += 1
                daman_logger.debug("✅ Salary Band value filled")
            else:
                initial_failed_fields.append("Salary Band")
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Salary Band: {e}")
            initial_failed_fields.append("Salary Band")

        # Select option for 'network UAE' with timeout protection
        try:
            networkUAE = str(catA['Network'].iloc[0])
            daman_logger.debug("Network UAE Value:" + networkUAE)
            selector = 'select[name="smeQuotationDTO.categories[0].benefits.networkUAE"]'
            field = 'Network'
            
            try:
                await extract_network(self.page, portal_name, region, tpa, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ Network UAE: Failed to extract network values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=networkUAE.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Network UAE filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Network UAE: Selection timeout after 10 seconds")
                initial_failed_fields.append("Network UAE")
            except Exception as e:
                daman_logger.error(f"❌ Network UAE: Selection failed - {e}")
                initial_failed_fields.append("Network UAE")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Network UAE: {e}")
            initial_failed_fields.append("Network UAE")
        
        # Log initial fields summary
        daman_logger.info(f"📊 Initial fields processing summary: {initial_successful_fields}/5 successful")
        if initial_failed_fields:
            daman_logger.warning(f"⚠️ Failed initial fields: {', '.join(initial_failed_fields)}")

        #---------------------------------------------------------------------------#
        
        # Click Customized Benefits
        await self.page.wait_for_selector('//*[@id="sme-benefit-0"]/a/span', timeout=5000)
        await self.page.click('//*[@id="sme-benefit-0"]/a/span')
        await asyncio.sleep(10)
        daman_logger.debug("Clicked Customized Benefits ")

        try:
            await asyncio.sleep(10)
            await screenshot_and_compare(self.page, "daman", "DAMAN_INSURANCE_3")
            await asyncio.sleep(MAX_SLEEP)
        except Exception as e:
            daman_logger.error(f"An error occurred while marking the checkbox: {e}")

        fields_to_fill = [
            ('//*[@id="smeQuotationDTO.categories[0].benefits.annualLimit"]', str(catA['Annual Limit'].iloc[0]), "Annual Limit"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.territorialLimit"]', str(catA['Territory'].iloc[0]), "Territorial Limit"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.nonNetwork"]', str(catA['Reimbursement'].iloc[0]), "Non Network"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.pcDeductible"]', str(catA['Deductable'].iloc[0]), "PC Deductible"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.pcCopay"]', str(catA['Diagnostic/Lab Copay'].iloc[0]), "PC Copay"),#
            ('//*[@id="smeQuotationDTO.categories[0].benefits.pcOutOfPocket"]', str(catA['Consultation Limit'].iloc[0]), "PC Out of Pocket"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.pharmacyLimit"]', str(catA['Limit of Phamacy'].iloc[0]), "Pharmacy Limit"),#
            ('//*[@id="smeQuotationDTO.categories[0].benefits.pharmacyCoverage"]', str(catA['Pharmacy'].iloc[0]), "Pharmacy Coverage"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.dentalCoverage"]', str(catA['Dental Copay'].iloc[0]), "Dental Coverage"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.dentalLimit"]', str(catA['Dental'].iloc[0]), "Dental Limit"),#
            ('//*[@id="smeQuotationDTO.categories[0].benefits.opticalCoverage"]', str(catA['Optical CO'].iloc[0]), "Optical Coverage"),
            ('//*[@id="smeQuotationDTO.categories[0].benefits.opticalLimit"]', str(catA['Optical'].iloc[0]), "Optical Limit"),#
            ('//*[@id="smeQuotationDTO.categories[0].benefits.ipMat"]', str(catA['Maternity - Married Females'].iloc[0]), "IP Mat"),
        ]

        # Process fields with resilient error handling
        successful_fields = 0
        failed_fields = []
        
        for xpath, value, field_name in fields_to_fill:
            try:
                success = await self.select_option_with_error_handling(region, tpa, network, field_name, value, xpath, portal_name)
                
                if success:
                    successful_fields += 1
                    daman_logger.info(f"✅ Successfully processed field: {field_name}")
                else:
                    failed_fields.append(field_name)
                    daman_logger.warning(f"⚠️ Skipping field due to timeout or error: {field_name}")
                    daman_logger.error(f"Failed XPath: {xpath}")
                    
            except Exception as e:
                failed_fields.append(field_name)
                daman_logger.error(f"❌ Exception while processing field {field_name}: {e}")
        
        # Log summary
        total_fields = len(fields_to_fill)
        daman_logger.info(f"📊 Field processing summary: {successful_fields}/{total_fields} successful")
        
        if failed_fields:
            daman_logger.warning(f"⚠️ Failed fields: {', '.join(failed_fields)}")

        #---------------------------------------------------------------------#
        
        # Click Save button with timeout protection
        try:
            await asyncio.wait_for(
                self.page.wait_for_selector('//*[@id="sme_plan_benefits_wrap_0"]/div/div[2]/input[3]', timeout=5000),
                timeout=10
            )
            await asyncio.wait_for(
                self.page.click('//*[@id="sme_plan_benefits_wrap_0"]/div/div[2]/input[3]'),
                timeout=10
            )
            await asyncio.sleep(10)
            daman_logger.debug("✅ Clicked Save Button")
            save_success = True
        except asyncio.TimeoutError:
            daman_logger.error("⏰ Save Button: Click timeout after 10 seconds")
            save_success = False
        except Exception as e:
            daman_logger.error(f"❌ Save Button: Click failed - {e}")
            save_success = False
        
        # Calculate total success
        total_successful = initial_successful_fields + successful_fields
        total_fields = 5 + len(fields_to_fill)  # 5 initial fields + dynamic fields
        
        daman_logger.info(f"📊 Overall processing summary: {total_successful}/{total_fields} successful")
        
        # Combine all failed fields
        all_failed_fields = initial_failed_fields + failed_fields
        if not save_success:
            all_failed_fields.append("Save Button")
            
        if all_failed_fields:
            daman_logger.warning(f"⚠️ All failed fields: {', '.join(all_failed_fields)}")
        
        daman_logger.debug("Category A Completed")
        print('Category A Completed')
        
        # Return True if at least some critical fields were processed successfully
        # This allows the process to continue even if some fields timeout
        return total_successful > 0

    async def select_option_with_error_handling(self, region, tpa, network, field_name, value, selector, portal_name):
        """
        Selects an option from a dropdown with error handling and extraction of dropdown values.
        """
        try:
            cleaned_value = str(value).strip()
            if cleaned_value.lower() == 'nan' or cleaned_value == '':
                daman_logger.debug(f"Skipping {field_name} as value is empty or NaN")
                return True
                
            daman_logger.debug(f"{field_name} Value (Before Apply): {cleaned_value}")
            
            # Extract dropdown values with error handling
            try:
                await extract_dropdown_values(self.page, region, tpa, network, field_name, selector, portal_name)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ {field_name}: Failed to extract dropdown values - {extract_error}")
                # Continue with selection attempt even if extraction fails
            
            # Apply selection with timeout protection
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=cleaned_value.rstrip()),
                    timeout=10  # 10 second timeout for selection
                )
                daman_logger.debug(f"{field_name} Value (After Apply): {cleaned_value}")
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug(f"✅ {field_name} Filled")
                return True
                
            except asyncio.TimeoutError:
                daman_logger.error(f"⏰ {field_name}: Selection timeout after 10 seconds - skipping this field")
                return False
            except Exception as select_error:
                daman_logger.error(f"❌ {field_name}: Selection failed - {select_error}")
                return False
                
        except Exception as e:
            daman_logger.error(f"❌ Unexpected error in {field_name}: {e}")
            return False