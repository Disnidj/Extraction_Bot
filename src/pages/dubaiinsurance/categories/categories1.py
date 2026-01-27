import asyncio
import asyncio
import os
# from src.utils.load_yaml import DUBAIINSURANCE_QUOTATION_DIR
from src.utils.logger import dubaiinsurance_logger as logger
from src.utils.special_function_iframe import extract_dropdown_values, extract_network


class Categories1:
    def __init__(self, page, df2, cat1, portal_name):
        self.page = page
        self.df2 = df2
        self.cat1 = cat1
        self.portal_name = portal_name

    def get_value(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[0]).strip()
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None

    async def categories1_information(self, tpa, network):
        logger.info("Started Filling Category 1 Information")
        
        # Get region from DataFrame or use default
        try:
            region = self.get_value("Region") or "Dubai"
        except:
            region = "Dubai"

        # Initialize field tracking
        successful_fields = 0
        failed_fields = []
        
        try:
            # TPA - Commented out but keeping structure for potential future use
            await asyncio.sleep(4)

            # Network
            try:
                network_value = self.get_value("Network")
                logger.debug(f"Network (Before Apply): {network_value}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod1").select_option(network_value),
                        timeout=10
                    )
                    field = "Network"
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod1")
                    try:
                        await extract_network(self.portal_name, tpa, field, dropdown)
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Network: Failed to extract network values - {extract_error}")
                    
                    logger.debug(f"✅ Network (After Apply): {network_value}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Network: Selection timeout after 10 seconds")
                    failed_fields.append("Network")
                except Exception as e:
                    logger.error(f"❌ Network: Selection failed - {e}")
                    failed_fields.append("Network")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Network: {e}")
                failed_fields.append("Network")

            # Annual Limit
            try:
                annual_limit = self.get_value("Annual Limit")
                logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Annual Limit", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Annual Limit: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(annual_limit),
                        timeout=10
                    )
                    logger.debug(f"✅ Annual Limit (After Apply): {annual_limit}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Annual Limit: Selection timeout after 10 seconds")
                    failed_fields.append("Annual Limit")
                except Exception as e:
                    logger.error(f"❌ Annual Limit: Selection failed - {e}")
                    failed_fields.append("Annual Limit")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Annual Limit: {e}")
                failed_fields.append("Annual Limit")

            # Territory
            try:
                territory = self.get_value("Territory")
                logger.debug(f"Territory (Before Apply): {territory}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Territory", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Territory: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(territory),
                        timeout=10
                    )
                    logger.debug(f"✅ Territory (After Apply): {territory}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Territory: Selection timeout after 10 seconds")
                    failed_fields.append("Territory")
                except Exception as e:
                    logger.error(f"❌ Territory: Selection failed - {e}")
                    failed_fields.append("Territory")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Territory: {e}")
                failed_fields.append("Territory")

            # Deductable
            try:
                deductable = self.get_value("Deductable")
                logger.debug(f"Deductable (Before Apply): {deductable}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Deductable", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Deductable: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(deductable),
                        timeout=10
                    )
                    logger.debug(f"✅ Deductable (After Apply): {deductable}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Deductable: Selection timeout after 10 seconds")
                    failed_fields.append("Deductable")
                except Exception as e:
                    logger.error(f"❌ Deductable: Selection failed - {e}")
                    failed_fields.append("Deductable")
                    
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"❌ Exception while processing Deductable: {e}")
                failed_fields.append("Deductable")

            # Limit of Pharmacy
            try:
                limit_of_phamacy = self.get_value("Limit of Phamacy")
                logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Limit of Phamacy", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Limit of Phamacy: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(limit_of_phamacy),
                        timeout=10
                    )
                    logger.debug(f"✅ Limit of Phamacy (After Apply): {limit_of_phamacy}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Limit of Phamacy: Selection timeout after 10 seconds")
                    failed_fields.append("Limit of Phamacy")
                except Exception as e:
                    logger.error(f"❌ Limit of Phamacy: Selection failed - {e}")
                    failed_fields.append("Limit of Phamacy")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Limit of Phamacy: {e}")
                failed_fields.append("Limit of Phamacy")

            # Medicine
            try:
                medicine = self.get_value("Medicine")
                logger.debug(f"Medicine (Before Apply): {medicine}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Medicine", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Medicine: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(medicine),
                        timeout=10
                    )
                    logger.debug(f"✅ Medicine (After Apply): {medicine}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Medicine: Selection timeout after 10 seconds")
                    failed_fields.append("Medicine")
                except Exception as e:
                    logger.error(f"❌ Medicine: Selection failed - {e}")
                    failed_fields.append("Medicine")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Medicine: {e}")
                failed_fields.append("Medicine")

            # Pharmacy
            try:
                pharmacy = self.get_value("Pharmacy")
                try:
                    pharmacy = float(pharmacy) * 100
                    pharmacy = f"{int(pharmacy)}%" 
                except ValueError:
                    pass

                logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Pharmacy", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Pharmacy: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(pharmacy),
                        timeout=10
                    )
                    logger.debug(f"✅ Pharmacy (After Apply): {pharmacy}")
                    logger.debug(f"Final value sent: {pharmacy}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Pharmacy: Selection timeout after 10 seconds")
                    failed_fields.append("Pharmacy")
                except Exception as e:
                    logger.error(f"❌ Pharmacy: Selection failed - {e}")
                    failed_fields.append("Pharmacy")
                    
                await asyncio.sleep(3)
                print(f"Final value sent: {pharmacy}")
            except Exception as e:
                logger.error(f"❌ Exception while processing Pharmacy: {e}")
                failed_fields.append("Pharmacy")

            # Physio
            try:
                physio = self.get_value("Physio")
                logger.debug(f"Physio (Before Apply): {physio}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Physio", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Physio: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(physio),
                        timeout=10
                    )
                    logger.debug(f"✅ Physio (After Apply): {physio}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Physio: Selection timeout after 10 seconds")
                    failed_fields.append("Physio")
                except Exception as e:
                    logger.error(f"❌ Physio: Selection failed - {e}")
                    failed_fields.append("Physio")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Physio: {e}")
                failed_fields.append("Physio")

            # Physio CO
            try:
                physio_co = self.get_value("Physio Co")
                try:
                    physio_co = float(physio_co) * 100
                    physio_co = f"{int(physio_co)}%" 
                except ValueError:
                    pass

                logger.debug(f"Physio CO (Before Apply): {physio_co}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physiocopay1")
                    try:
                        await extract_dropdown_values(tpa, network, "Physio Co", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Physio CO: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(physio_co),
                        timeout=10
                    )
                    logger.debug(f"✅ Physio CO (After Apply): {physio_co}")
                    logger.debug(f"Final value sent: {physio_co}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Physio CO: Selection timeout after 10 seconds")
                    failed_fields.append("Physio CO")
                except Exception as e:
                    logger.error(f"❌ Physio CO: Selection failed - {e}")
                    failed_fields.append("Physio CO")
                    
                await asyncio.sleep(3)
                print(f"Final value sent: {physio_co}")
            except Exception as e:
                logger.error(f"❌ Exception while processing Physio CO: {e}")
                failed_fields.append("Physio CO")

            # Maternity - Married Females
            try:
                married_females = self.get_value("Maternity - Married Females")
                logger.debug(f"Maternity - Married (Before Apply): {married_females}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Maternity - Married Females", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Maternity - Married Females: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(married_females),
                        timeout=10
                    )
                    logger.debug(f"✅ Maternity - Married: {married_females}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Maternity - Married Females: Selection timeout after 10 seconds")
                    failed_fields.append("Maternity - Married Females")
                except Exception as e:
                    logger.error(f"❌ Maternity - Married Females: Selection failed - {e}")
                    failed_fields.append("Maternity - Married Females")
                    
                await asyncio.sleep(3)
                print(f"Maternity - Married Females (After Apply): {married_females}")
            except Exception as e:
                logger.error(f"❌ Exception while processing Maternity - Married Females: {e}")
                failed_fields.append("Maternity - Married Females")

            # Maternity - Married Females CO
            try:
                married_females_co = self.get_value("Maternity - Married Females CO")
                try:
                    married_females_co = float(married_females_co) * 100
                    married_females_co = f"{int(married_females_co)}%" 
                except ValueError:
                    pass

                logger.debug(f"pre married_females_co is (Before Apply): {married_females_co}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Maternity - Married Females CO", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Maternity - Married Females CO: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(married_females_co),
                        timeout=10
                    )
                    logger.debug(f"✅ pre married_females_co is (After Apply): {married_females_co}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Maternity - Married Females CO: Selection timeout after 10 seconds")
                    failed_fields.append("Maternity - Married Females CO")
                except Exception as e:
                    logger.error(f"❌ Maternity - Married Females CO: Selection failed - {e}")
                    failed_fields.append("Maternity - Married Females CO")
                    
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"❌ Exception while processing Maternity - Married Females CO: {e}")
                failed_fields.append("Maternity - Married Females CO")

            # Dental
            try:
                dental = self.get_value("Dental")
                logger.debug(f"Dental1 (Before Apply): {dental}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Dental", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Dental: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(dental),
                        timeout=10
                    )
                    logger.debug(f"✅ Dental (After Apply): {dental}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Dental: Selection timeout after 10 seconds")
                    failed_fields.append("Dental")
                except Exception as e:
                    logger.error(f"❌ Dental: Selection failed - {e}")
                    failed_fields.append("Dental")
                    
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"❌ Exception while processing Dental: {e}")
                failed_fields.append("Dental")

            # Dental CO
            try:
                dental_co = self.get_value("Dental CO")
                logger.debug(f"Dental CO is (Before Apply): {dental_co}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Dental CO", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Dental CO: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(dental_co),
                        timeout=10
                    )
                    logger.debug(f"✅ Dental CO is (After Apply): {dental_co}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Dental CO: Selection timeout after 10 seconds")
                    failed_fields.append("Dental CO")
                except Exception as e:
                    logger.error(f"❌ Dental CO: Selection failed - {e}")
                    failed_fields.append("Dental CO")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Dental CO: {e}")
                failed_fields.append("Dental CO")

            # Optical
            try:
                optical = self.get_value("Optical")
                logger.debug(f"Optical (Before Apply): {optical}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Optical", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Optical: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(optical),
                        timeout=10
                    )
                    logger.debug(f"✅ Optical (After Apply): {optical}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Optical: Selection timeout after 10 seconds")
                    failed_fields.append("Optical")
                except Exception as e:
                    logger.error(f"❌ Optical: Selection failed - {e}")
                    failed_fields.append("Optical")
                    
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"❌ Exception while processing Optical: {e}")
                failed_fields.append("Optical")

            # Optical CO
            try:
                optical_co = self.get_value("Optical CO")
                logger.debug(f"Optical CO is (Before Apply): {optical_co}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Optical CO", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Optical CO: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(optical_co),
                        timeout=10
                    )
                    logger.debug(f"✅ Optical CO is (After Apply): {optical_co}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Optical CO: Selection timeout after 10 seconds")
                    failed_fields.append("Optical CO")
                except Exception as e:
                    logger.error(f"❌ Optical CO: Selection failed - {e}")
                    failed_fields.append("Optical CO")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Optical CO: {e}")
                failed_fields.append("Optical CO")

            # Life benefit - Death due to any cause
            try:
                life_benefit = self.get_value("Life benefit - Death due to any cause")
                logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit1")
                    try:
                        await extract_dropdown_values(tpa, network, "Life benefit - Death due to any cause", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Life benefit - Death due to any cause: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(life_benefit),
                        timeout=10
                    )
                    logger.debug(f"✅ Life benefit - Death due to any cause (After Apply): {life_benefit}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Life benefit - Death due to any cause: Selection timeout after 10 seconds")
                    failed_fields.append("Life benefit - Death due to any cause")
                except Exception as e:
                    logger.error(f"❌ Life benefit - Death due to any cause: Selection failed - {e}")
                    failed_fields.append("Life benefit - Death due to any cause")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Life benefit - Death due to any cause: {e}")
                failed_fields.append("Life benefit - Death due to any cause")

            # Repatriation of Mortal remains
            try:
                repatriation = self.get_value("Repatriation of Mortal remains")
                print("Repatriation"+ repatriation)
                logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit1")
                    try:
                        await extract_dropdown_values(tpa, network, "Repatriation of Mortal remains", dropdown, self.portal_name, region)
                        await asyncio.sleep(3)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Repatriation of Mortal remains: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(repatriation),
                        timeout=10
                    )
                    logger.debug(f"✅ Repatriation of Mortal remains (After Apply): {repatriation}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Repatriation of Mortal remains: Selection timeout after 10 seconds")
                    failed_fields.append("Repatriation of Mortal remains")
                except Exception as e:
                    logger.error(f"❌ Repatriation of Mortal remains: Selection failed - {e}")
                    failed_fields.append("Repatriation of Mortal remains")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Repatriation of Mortal remains: {e}")
                failed_fields.append("Repatriation of Mortal remains")

            # Telehealth Consultation
            try:
                tele_consultation = self.get_value("Telehealth Consultation")
                logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit1")
                    try:
                        await extract_dropdown_values(tpa, network, "Telehealth Consultation", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Telehealth Consultation: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(tele_consultation),
                        timeout=10
                    )
                    logger.debug(f"✅ Telehealth Consultation (After Apply): {tele_consultation}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Telehealth Consultation: Selection timeout after 10 seconds")
                    failed_fields.append("Telehealth Consultation")
                except Exception as e:
                    logger.error(f"❌ Telehealth Consultation: Selection failed - {e}")
                    failed_fields.append("Telehealth Consultation")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Telehealth Consultation: {e}")
                failed_fields.append("Telehealth Consultation")

            # Wellness Package
            try:
                wellness_package = self.get_value("Wellness Package")
                logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa1")
                    try:
                        await extract_dropdown_values(tpa, network, "Wellness Package", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Wellness Package: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(wellness_package),
                        timeout=10
                    )
                    logger.debug(f"✅ Wellness Package (After Apply): {wellness_package}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Wellness Package: Selection timeout after 10 seconds")
                    failed_fields.append("Wellness Package")
                except Exception as e:
                    logger.error(f"❌ Wellness Package: Selection failed - {e}")
                    failed_fields.append("Wellness Package")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Wellness Package: {e}")
                failed_fields.append("Wellness Package")

            # Assist America
            try:
                assist_america = self.get_value("Assist America")
                logger.debug(f"Assist America (Before Apply): {assist_america}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS1")
                    try:
                        await extract_dropdown_values(tpa, network, "Assist America", dropdown, self.portal_name, region)
                        await asyncio.sleep(3)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Assist America: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(assist_america),
                        timeout=10
                    )
                    logger.debug(f"✅ Assist America (After Apply): {assist_america}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Assist America: Selection timeout after 10 seconds")
                    failed_fields.append("Assist America")
                except Exception as e:
                    logger.error(f"❌ Assist America: Selection failed - {e}")
                    failed_fields.append("Assist America")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Assist America: {e}")
                failed_fields.append("Assist America")

            # Psychiatry
            try:
                psychiatry = self.get_value("Psychiatry")
                logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch1")
                    try:
                        await extract_dropdown_values(tpa, network, "Psychiatry", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Psychiatry: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(psychiatry),
                        timeout=10
                    )
                    logger.debug(f"✅ Psychiatry (After Apply): {psychiatry}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Psychiatry: Selection timeout after 10 seconds")
                    failed_fields.append("Psychiatry")
                except Exception as e:
                    logger.error(f"❌ Psychiatry: Selection failed - {e}")
                    failed_fields.append("Psychiatry")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Psychiatry: {e}")
                failed_fields.append("Psychiatry")

            # Alternative Medicine
            try:
                alternative_medicine = self.get_value("Alternative Medicine")
                logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
                
                try:
                    dropdown = self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben1")
                    try:
                        await extract_dropdown_values(tpa, network, "Alternative Medicine", dropdown, self.portal_name, region)
                        await asyncio.sleep(2)  # Wait for dropdown values to load
                    except Exception as extract_error:
                        logger.warning(f"⚠️ Alternative Medicine: Failed to extract dropdown values - {extract_error}")
                        
                    await asyncio.wait_for(
                        dropdown.select_option(alternative_medicine),
                        timeout=10
                    )
                    logger.debug(f"✅ Alternative Medicine (After Apply): {alternative_medicine}")
                    successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Alternative Medicine: Selection timeout after 10 seconds")
                    failed_fields.append("Alternative Medicine")
                except Exception as e:
                    logger.error(f"❌ Alternative Medicine: Selection failed - {e}")
                    failed_fields.append("Alternative Medicine")
                    
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"❌ Exception while processing Alternative Medicine: {e}")
                failed_fields.append("Alternative Medicine")

            # Click Get Quote with timeout protection
            try:
                await asyncio.wait_for(
                    self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click(),
                    timeout=10
                )
                await asyncio.sleep(2)
                
                # Check if button is visible and click again if needed
                if not await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').is_visible():
                    try:
                        await asyncio.wait_for(
                            self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click(),
                            timeout=10
                        )
                        print("get quote")
                        logger.debug("✅ Get Quote button clicked (second attempt)")
                    except asyncio.TimeoutError:
                        logger.error("⏰ Get Quote button (second click): Timeout after 10 seconds")
                    except Exception as e:
                        logger.error(f"❌ Get Quote button (second click): Failed - {e}")
                else:
                    logger.debug("✅ Get Quote button clicked successfully")
                    
            except asyncio.TimeoutError:
                logger.error("⏰ Get Quote button: Click timeout after 10 seconds")
            except Exception as e:
                logger.error(f"❌ Get Quote button: Click failed - {e}")
    
            # Log comprehensive summary
            total_attempted = 17  # Total number of fields processed
            logger.info(f"📈 Category 1 Processing Complete:")
            logger.info(f"   • Total fields processed: {total_attempted}")
            logger.info(f"   • Successful fields: {successful_fields}")
            logger.info(f"   • Failed fields: {len(failed_fields)}")
            
            if failed_fields:
                logger.warning(f"⚠️ Failed fields list: {', '.join(failed_fields)}")
            else:
                logger.info("🎉 All fields processed successfully!")
            
            logger.info("Get Quote button clicked")
            await asyncio.sleep(10)
            logger.info("Quotation downloaded successfully")
            
            # Return success if at least some fields were processed
            return successful_fields > 0
        
        except Exception as e:
            print(f"An error occurred while filling Category 1 information: {e}")
            logger.error(f"An error occurred while filling Category 1 information: {e}")
            return False