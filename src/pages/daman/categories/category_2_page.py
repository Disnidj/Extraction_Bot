import asyncio
from src.utils.load_yaml import MAX_SLEEP
from src.utils.support_functions import extract_region, extract_tpa, extract_network, extract_dropdown_values, screenshot_and_compare
from src.utils.logger import daman_logger

class Category2Page:
    def __init__(self, page):
        self.page = page

    async def fill_category_2(self, catB, salary_B, region, tpa, network, portal_name):
        daman_logger.debug("Category B Started")

        # try:
        #     await asyncio.sleep(10)
        #     await screenshot_and_compare(self.page, "daman", "DAMAN_INSURANCE_4")
        #     await asyncio.sleep(MAX_SLEEP)
        # except Exception as e:
        #     daman_logger.error(f"An error occurred while taking screenshot: {e}")
        
        # Initialize field tracking
        initial_successful_fields = 0
        initial_failed_fields = []
        
        # Click Add Another Category with timeout protection
        try:
            await asyncio.wait_for(
                self.page.wait_for_selector('//input[@type="button" and contains(@value,"Add Another Category")]', timeout=5000),
                timeout=10
            )
            await asyncio.wait_for(
                self.page.click('//input[@type="button" and contains(@value,"Add Another Category")]'),
                timeout=10
            )
            await asyncio.sleep(1)
            daman_logger.debug("✅ Clicked Add Another Category")
            initial_successful_fields += 1
        except asyncio.TimeoutError:
            daman_logger.error("⏰ Add Another Category: Click timeout after 10 seconds")
            initial_failed_fields.append("Add Another Category")
        except Exception as e:
            daman_logger.error(f"❌ Add Another Category: Click failed - {e}")
            initial_failed_fields.append("Add Another Category")

        # Select option for 'CAT B' with timeout protection
        try:
            b_category = "CAT " + str(catB['Category'].iloc[0]).strip()
            daman_logger.info(f"Category B name: {b_category}")
            
            try:
                await asyncio.wait_for(
                    self.page.fill('input[name="smeQuotationDTO.categories[1].categoryName"]', value=b_category.rstrip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Category B Name filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Category B Name: Fill timeout after 10 seconds")
                initial_failed_fields.append("Category B Name")
            except Exception as e:
                daman_logger.error(f"❌ Category B Name: Fill failed - {e}")
                initial_failed_fields.append("Category B Name")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category B Name: {e}")
            initial_failed_fields.append("Category B Name")

        # Select option for 'Visa' - Using extract_region with timeout protection
        try:
            visa = str(catB['Region'].iloc[0])
            daman_logger.info(f"Category B visa: {visa}")
            selector = 'select[name="smeQuotationDTO.categories[1].visa"]'
            field = 'Region'
            
            try:
                await extract_region(self.page, portal_name, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ Category B Visa: Failed to extract region values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=visa.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Category B visa filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Category B Visa: Selection timeout after 10 seconds")
                initial_failed_fields.append("Category B Visa")
            except Exception as e:
                daman_logger.error(f"❌ Category B Visa: Selection failed - {e}")
                initial_failed_fields.append("Category B Visa")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category B Visa: {e}")
            initial_failed_fields.append("Category B Visa")
    
        # Select option for 'Plan' - Using extract_tpa with timeout protection
        try:
            plan = str(catB['TPA'].iloc[0])
            daman_logger.debug("Category B Plan :" + plan)
            selector = 'select[name="smeQuotationDTO.categories[1].plan"]'
            field = 'TPA'
            
            try:
                await extract_tpa(self.page, portal_name, region, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ Category B Plan: Failed to extract TPA values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=plan.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Category B Plan filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Category B Plan: Selection timeout after 10 seconds")
                initial_failed_fields.append("Category B Plan")
            except Exception as e:
                daman_logger.error(f"❌ Category B Plan: Selection failed - {e}")
                initial_failed_fields.append("Category B Plan")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category B Plan: {e}")
            initial_failed_fields.append("Category B Plan")
        
        # Select option for 'Salary Band' with timeout protection
        try:
            success = await self.select_option_with_error_handling(region, tpa, network, "Salary Band", salary_B, 'select[name="smeQuotationDTO.categories[1].salaryBand"]', portal_name)
            if success:
                initial_successful_fields += 1
                daman_logger.debug("✅ Category B Salary Band filled")
            else:
                initial_failed_fields.append("Category B Salary Band")
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category B Salary Band: {e}")
            initial_failed_fields.append("Category B Salary Band")

        # Select option for 'network UAE' with timeout protection
        try:
            networkUAE = str(catB['Network'].iloc[0])
            daman_logger.debug("Category B Network UAE Value:" + networkUAE)
            selector = 'select[name="smeQuotationDTO.categories[1].benefits.networkUAE"]'
            field = 'Network'
            
            try:
                await extract_network(self.page, portal_name, region, tpa, field, selector)
            except Exception as extract_error:
                daman_logger.warning(f"⚠️ Category B Network UAE: Failed to extract network values - {extract_error}")
            
            try:
                await asyncio.wait_for(
                    self.page.select_option(selector, value=networkUAE.strip()),
                    timeout=10
                )
                await asyncio.sleep(MAX_SLEEP)
                daman_logger.debug("✅ Category B network UAE filled")
                initial_successful_fields += 1
            except asyncio.TimeoutError:
                daman_logger.error("⏰ Category B Network UAE: Selection timeout after 10 seconds")
                initial_failed_fields.append("Category B Network UAE")
            except Exception as e:
                daman_logger.error(f"❌ Category B Network UAE: Selection failed - {e}")
                initial_failed_fields.append("Category B Network UAE")
                
        except Exception as e:
            daman_logger.error(f"❌ Exception while processing Category B Network UAE: {e}")
            initial_failed_fields.append("Category B Network UAE")
        
        # Log initial fields summary
        daman_logger.info(f"📊 Initial fields processing summary: {initial_successful_fields}/6 successful")
        if initial_failed_fields:
            daman_logger.warning(f"⚠️ Failed initial fields: {', '.join(initial_failed_fields)}")
        
        #---------------------------------------------------------------------------#
        
        # Click Customized Benefits
        await self.page.wait_for_selector('//*[@id="sme-benefit-1"]/a/span', timeout=5000)
        await self.page.click('//*[@id="sme-benefit-1"]/a/span')
        await asyncio.sleep(10)
        daman_logger.debug("Clicked Customized Benefits")

        # try:
        #     await asyncio.sleep(10)
        #     await screenshot_and_compare(self.page, "daman", "DAMAN_INSURANCE_5")
        #     await asyncio.sleep(MAX_SLEEP)
        # except Exception as e:
        #     daman_logger.error(f"An error occurred while taking screenshot: {e}")

        fields_to_fill = [
            ('//*[@id="smeQuotationDTO.categories[1].benefits.annualLimit"]', str(catB['Annual Limit'].iloc[0]), "Annual Limit"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.territorialLimit"]', str(catB['Territory'].iloc[0]), "Territorial Limit"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.nonNetwork"]', str(catB['Reimbursement'].iloc[0]), "Non Network"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.pcDeductible"]', str(catB['Deductable'].iloc[0]), "PC Deductible"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.pcCopay"]', str(catB['Diagnostic/Lab Copay'].iloc[0]), "PC Copay"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.pcOutOfPocket"]', str(catB['Consultation Limit'].iloc[0]), "PC Out of Pocket"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.pharmacyLimit"]', str(catB['Limit of Phamacy'].iloc[0]), "Pharmacy Limit"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.pharmacyCoverage"]', str(catB['Pharmacy'].iloc[0]), "Pharmacy Coverage"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.dentalCoverage"]', str(catB['Dental Copay'].iloc[0]), "Dental Coverage"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.dentalLimit"]', str(catB['Dental'].iloc[0]), "Dental Limit"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.opticalCoverage"]', str(catB['Optical CO'].iloc[0]), "Optical Coverage"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.opticalLimit"]', str(catB['Optical'].iloc[0]), "Optical Limit"),
            ('//*[@id="smeQuotationDTO.categories[1].benefits.ipMat"]', str(catB['Maternity - Married Females'].iloc[0]), "IP Mat"),
        ]

        # Process remaining fields with resilient handling
        loop_successful_fields = 0
        loop_failed_fields = []
        total_fields = len(fields_to_fill)
        
        for xpath, value, field_name in fields_to_fill:
            try:
                daman_logger.debug(f"Processing field: {field_name}")
                
                success = await self.select_option_with_error_handling(region, tpa, network, field_name, value, xpath, portal_name)
                
                if success:
                    loop_successful_fields += 1
                    daman_logger.debug(f"✅ {field_name} filled successfully")
                else:
                    loop_failed_fields.append(field_name)
                    daman_logger.warning(f"⚠️ {field_name} failed to fill (XPath: {xpath})")
                    
            except Exception as e:
                loop_failed_fields.append(field_name)
                daman_logger.error(f"❌ Exception while processing {field_name}: {e}")
                # Continue with next field instead of failing the entire process
                continue

        # Log comprehensive summary
        total_successful = initial_successful_fields + loop_successful_fields
        total_attempted = 6 + total_fields  # 6 initial fields + dynamic fields
        all_failed_fields = initial_failed_fields + loop_failed_fields
        
        daman_logger.info(f"📈 Category B Processing Complete:")
        daman_logger.info(f"   • Total fields processed: {total_attempted}")
        daman_logger.info(f"   • Successful fields: {total_successful}")
        daman_logger.info(f"   • Failed fields: {len(all_failed_fields)}")
        
        if all_failed_fields:
            daman_logger.warning(f"⚠️ Failed fields list: {', '.join(all_failed_fields)}")
        else:
            daman_logger.info("🎉 All fields processed successfully!")

        #---------------------------------------------------------------------#
        
        # Click Save button with timeout protection
        try:
            await asyncio.wait_for(
                self.page.wait_for_selector('//*[@id="sme_plan_benefits_wrap_1"]/div/div[2]/input[3]', timeout=5000),
                timeout=10
            )
            await asyncio.wait_for(
                self.page.click('//*[@id="sme_plan_benefits_wrap_1"]/div/div[2]/input[3]'),
                timeout=10
            )
            await asyncio.sleep(10)
            daman_logger.debug("✅ Clicked Save Button")
        except asyncio.TimeoutError:
            daman_logger.error("⏰ Save Button: Click timeout after 10 seconds")
        except Exception as e:
            daman_logger.error(f"❌ Save Button: Click failed - {e}")
        
        daman_logger.info("📋 Category B Processing Completed")
        print('Category B Completed')
        
        # Return success if at least some fields were processed successfully
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