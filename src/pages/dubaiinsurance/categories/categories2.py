import asyncio
import asyncio
import os
# from src.utils.load_yaml import DUBAIINSURANCE_QUOTATION_DIR
from src.utils.logger import dubaiinsurance_logger as logger

class Categories2:
    def __init__(self, page, df2, cat2):
        self.page = page
        self.df2 = df2

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
        
    def get_value_catB(self, column_name):
        try:
            # Fetch value from the specific column and convert to string
            return str(self.df2[column_name].values[1]).strip()
        except KeyError:
            print(f"KeyError: '{column_name}' column not found in DataFrame.")
            logger.error(f"KeyError: '{column_name}' column not found in DataFrame.")
            return None
        except IndexError:
            print(f"IndexError: No data found in column '{column_name}'.")
            logger.error(f"IndexError: No data found in column '{column_name}'.")
            return None

    async def categories2_information(self):

        logger.info("Started Filling Category 1 Information")

        # Initialize field tracking
        cat1_successful_fields = 0
        cat1_failed_fields = []

        try:
            # TPA
            try:
                tpa = self.get_value("TPA")
                logger.debug(f"TPA (Before Apply): {tpa}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_tpaben21").select_option(tpa),
                        timeout=10
                    )
                    logger.debug(f"✅ TPA (After Apply): {tpa}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ TPA: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("TPA")
                except Exception as e:
                    logger.error(f"❌ TPA: Selection failed - {e}")
                    cat1_failed_fields.append("TPA")
                    
                await asyncio.sleep(4)
            except Exception as e:
                logger.error(f"❌ Exception while processing TPA: {e}")
                cat1_failed_fields.append("TPA")
            
            # Network
            try:
                network = self.get_value("Network")
                logger.debug(f"Network (Before Apply): {network}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod21").select_option(network),
                        timeout=10
                    )
                    logger.debug(f"✅ Network (After Apply): {network}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Network: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Network")
                except Exception as e:
                    logger.error(f"❌ Network: Selection failed - {e}")
                    cat1_failed_fields.append("Network")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Network: {e}")
                cat1_failed_fields.append("Network")

            # Annual Limit
            try:
                annual_limit = self.get_value("Annual Limit")
                logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben21").select_option(annual_limit),
                        timeout=10
                    )
                    logger.debug(f"✅ Annual Limit (After Apply): {annual_limit}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Annual Limit: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Annual Limit")
                except Exception as e:
                    logger.error(f"❌ Annual Limit: Selection failed - {e}")
                    cat1_failed_fields.append("Annual Limit")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Annual Limit: {e}")
                cat1_failed_fields.append("Annual Limit")

            # Territory
            try:
                territory = self.get_value("Territory")
                logger.debug(f"Territory (Before Apply): {territory}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben21").select_option(territory),
                        timeout=10
                    )
                    logger.debug(f"✅ Territory (After Apply): {territory}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Territory: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Territory")
                except Exception as e:
                    logger.error(f"❌ Territory: Selection failed - {e}")
                    cat1_failed_fields.append("Territory")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Territory: {e}")
                cat1_failed_fields.append("Territory")

            # Deductable
            try:
                deductable = self.get_value("Deductable")
                logger.debug(f"Deductable (Before Apply): {deductable}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben21").select_option(deductable),
                        timeout=10
                    )
                    logger.debug(f"✅ Deductable (After Apply): {deductable}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Deductable: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Deductable")
                except Exception as e:
                    logger.error(f"❌ Deductable: Selection failed - {e}")
                    cat1_failed_fields.append("Deductable")
                    
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"❌ Exception while processing Deductable: {e}")
                cat1_failed_fields.append("Deductable")
            # Network - Defualt
            # op_co_insurance = self.get_value("Op Co Insurance")
            # print(op_co_insurance)
            # await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_copayben21").select_option(op_co_insurance)
            # await asyncio.sleep(3)
            # print(op_co_insurance)

            # Limit of Pharmacy
            try:
                limit_of_phamacy = self.get_value("Limit of Phamacy")
                logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben21").select_option(limit_of_phamacy),
                        timeout=10
                    )
                    logger.debug(f"✅ Limit of Phamacy (After Apply): {limit_of_phamacy}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Limit of Phamacy: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Limit of Phamacy")
                except Exception as e:
                    logger.error(f"❌ Limit of Phamacy: Selection failed - {e}")
                    cat1_failed_fields.append("Limit of Phamacy")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Limit of Phamacy: {e}")
                cat1_failed_fields.append("Limit of Phamacy")

            # Medicine
            try:
                medicine = self.get_value("Medicine")
                logger.debug(f"Medicine (Before Apply): {medicine}")
                
                try:
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben21").select_option(medicine),
                        timeout=10
                    )
                    logger.debug(f"✅ Medicine (After Apply): {medicine}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Medicine: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Medicine")
                except Exception as e:
                    logger.error(f"❌ Medicine: Selection failed - {e}")
                    cat1_failed_fields.append("Medicine")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Medicine: {e}")
                cat1_failed_fields.append("Medicine")

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
                    await asyncio.wait_for(
                        self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben21").select_option(pharmacy),
                        timeout=10
                    )
                    logger.debug(f"✅ Pharmacy (After Apply): {pharmacy}")
                    cat1_successful_fields += 1
                except asyncio.TimeoutError:
                    logger.error("⏰ Pharmacy: Selection timeout after 10 seconds")
                    cat1_failed_fields.append("Pharmacy")
                except Exception as e:
                    logger.error(f"❌ Pharmacy: Selection failed - {e}")
                    cat1_failed_fields.append("Pharmacy")
                    
                await asyncio.sleep(3)
            except Exception as e:
                logger.error(f"❌ Exception while processing Pharmacy: {e}")
                cat1_failed_fields.append("Pharmacy")

            # Physio
            physio = self.get_value("Physio")
            logger.debug(f"Physio (Before Apply): {physio}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben21").select_option(physio)
            logger.debug(f"Physio (After Apply): {physio}")
            await asyncio.sleep(3)

            # Physio CO
            physio_co = self.get_value("Physio Co")
            try:
                physio_co = float(physio_co) * 100
                physio_co = f"{int(physio_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Physio CO (Before Apply): {physio_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physiocopay21").select_option(physio_co)
            logger.debug(f"Physio CO (After Apply): {physio_co}")
            await asyncio.sleep(3)
            print(f"Final value sent: {physio_co}")

            # Maternity - Married Females
            married_females = self.get_value("Maternity - Married Females")
            logger.debug(f"Maternity - Married Females (Before Apply): {married_females}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben21").select_option(married_females)
            logger.debug(f"Maternity - Married Females (After Apply): {married_females}")
            await asyncio.sleep(3)

            # Maternity - Married Females CO
            married_females_co = self.get_value("Maternity - Married Females CO")
            try:
                married_females_co = float(married_females_co) * 100
                married_females_co = f"{int(married_females_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Maternity - Married Females CO (Before Apply): {married_females_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben21").select_option(married_females_co)
            logger.debug(f"Maternity - Married Females CO (After Apply): {married_females_co}")
            await asyncio.sleep(3)
            print(f"married_females_co is : {married_females_co}")

            # Dental
            dental = self.get_value("Dental")
            logger.debug(f"Dental (Before Apply): {dental}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben21").select_option(dental)
            logger.debug(f"Dental (After Apply): {dental}")
            await asyncio.sleep(1)

            # Dental CO
            dental_co = self.get_value("Dental CO")
            try:
                dental_co = float(dental_co) * 100
                dental_co = f"{int(dental_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Dental CO (Before Apply): {dental_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben21").select_option(dental_co)
            logger.debug(f"Dental CO (After Apply): {dental_co}")
            await asyncio.sleep(3)
            print(f"Denatal CO is : {dental_co}")

            # Optical
            optical = self.get_value("Optical")
            logger.debug(f"Optical (Before Apply): {optical}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben21").select_option(optical)
            logger.debug(f"Optical (After Apply): {optical}")
            await asyncio.sleep(1)

            # Optical CO
            optical_co = self.get_value("Optical CO")
            try:
                optical_co = float(optical_co) * 100
                optical_co = f"{int(optical_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Optical CO (Before Apply): {optical_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben21").select_option(optical_co)
            logger.debug(f"Optical CO (After Apply): {optical_co}")
            await asyncio.sleep(3)
            print(f"Optical CO is : {optical_co}")

            # Life benefit - Death due to any cause
            life_benefit = self.get_value("Life benefit - Death due to any cause")
            logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit21").select_option(life_benefit)             
            logger.debug(f"Life benefit - Death due to any cause (After Apply): {life_benefit}")
            await asyncio.sleep(1)

            # Repatriation of Mortal remains
            repatriation = self.get_value("Repatriation of Mortal remains")
            logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
            print("Repatriation"+ repatriation)
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit21").select_option(repatriation)           
            logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation}")
            await asyncio.sleep(1)

            # Telehealth Consultation
        
            tele_consultation = self.get_value("Telehealth Consultation")
            logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit21").select_option(tele_consultation)          
            logger.debug(f"Telehealth Consultation (After Apply): {tele_consultation}")
            await asyncio.sleep(1)
        
                

            # Wellness Package
            wellness_package = self.get_value("Wellness Package")
            logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa21").select_option(wellness_package)          
            logger.debug(f"Wellness Package (After Apply): {wellness_package}")
            await asyncio.sleep(0.5)

            # Assist America
            assist_america = self.get_value("Assist America")
            logger.debug(f"Assist America (Before Apply): {assist_america}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS21").select_option(assist_america)          
            logger.debug(f"Assist America (After Apply): {assist_america}")
            await asyncio.sleep(0.5)

            # Psychiatry
            psychiatry = self.get_value("Psychiatry")
            logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch21").select_option(psychiatry)          
            logger.debug(f"Psychiatry (After Apply): {psychiatry}")
            await asyncio.sleep(0.5)

            # Alternative Medicine
            alternative_medicine = self.get_value("Alternative Medicine")
            logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben21").select_option(alternative_medicine)          
            logger.debug(f"Alternative Medicine (After Apply): {alternative_medicine}")
            await asyncio.sleep(0.5)


        #       ------------------------CAT B------------------------------
            logger.info("Started Filling Category 2 Information")

            # Network
            network = self.get_value_catB("Network")
            logger.debug(f"Network (Before Apply): {network}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Prod22").select_option(network)
            logger.debug(f"Network (After Apply): {network}")
            await asyncio.sleep(3)

            # Annual Limit
            annual_limit = self.get_value_catB("Annual Limit")
            logger.debug(f"Annual Limit (Before Apply): {annual_limit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_AnnualLimitben22").select_option(annual_limit)
            logger.debug(f"Annual Limit (After Apply): {annual_limit}")
            await asyncio.sleep(3)

            # Territory
            territory = self.get_value_catB("Territory")
            logger.debug(f"Territory (Before Apply): {territory}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TerritorialCoverELCben22").select_option(territory)
            logger.debug(f"Territory (After Apply): {territory}")
            await asyncio.sleep(3)

            # Deductable
            deductable = self.get_value_catB("Deductable")
            logger.debug(f"Deductable (Before Apply): {deductable}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_dedben22").select_option(deductable)
            logger.debug(f"Deductable (After Apply): {deductable}")
            await asyncio.sleep(5)

            # Network - Defualt
            # op_co_insurance = self.get_value_catB("Op Co Insurance")
            # print(op_co_insurance)
            # await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_copayben22").select_option(op_co_insurance)
            # await asyncio.sleep(3)
            # print(op_co_insurance)

            # Limit of Phamacy
            limit_of_phamacy = self.get_value_catB("Limit of Phamacy")
            logger.debug(f"Limit of Phamacy (Before Apply): {limit_of_phamacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHLimitben22").select_option(limit_of_phamacy)
            logger.debug(f"Limit of Phamacy (After Apply): {limit_of_phamacy}")
            await asyncio.sleep(3)

            # Medicine
            medicine = self.get_value_catB("Medicine")
            logger.debug(f"Medicine (Before Apply): {medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MedTypeben22").select_option(medicine)
            logger.debug(f"Medicine (After Apply): {medicine}")
            await asyncio.sleep(3)

            # Pharmacy
            pharmacy = self.get_value_catB("Pharmacy")
            try:
                pharmacy = float(pharmacy) * 100
                pharmacy = f"{int(pharmacy)}%" 
            except ValueError:
                pass
            logger.debug(f"Pharmacy (Before Apply): {pharmacy}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_PHCopayben22").select_option(pharmacy)
            logger.debug(f"Pharmacy (After Apply): {pharmacy}")
            await asyncio.sleep(3)
            print(f"Final value sent: {pharmacy}")

            # Physio
            physio = self.get_value_catB("Physio")
            logger.debug(f"Physio (Before Apply): {physio}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physioben22").select_option(physio)
            logger.debug(f"Physio (After Apply): {physio}")
            await asyncio.sleep(3)

            # Physio CO
            physio_co = self.get_value_catB("Physio Co")
            try:
                physio_co = float(physio_co) * 100
                physio_co = f"{int(physio_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Physio CO (Before Apply): {physio_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Physiocopay22").select_option(physio_co)
            logger.debug(f"Physio CO (After Apply): {physio_co}")
            await asyncio.sleep(3)
            print(f"Final value sent: {physio_co}")

            # Maternity - Married Females
            married_females = self.get_value_catB("Maternity - Married Females")
            logger.debug(f"Maternity - Married Females (Before Apply): {married_females}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Matben22").select_option(married_females)
            logger.debug(f"Maternity - Married Females (After Apply): {married_females}")
            await asyncio.sleep(3)

            # Maternity - Married Females CO
            married_females_co = self.get_value_catB("Maternity - Married Females CO")
            try:
                married_females_co = float(married_females_co) * 100
                married_females_co = f"{int(married_females_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Maternity - Married Females CO (Before Apply): {married_females_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_MatCopayben22").select_option(married_females_co)
            logger.debug(f"Maternity - Married Females CO (After Apply): {married_females_co}")
            await asyncio.sleep(3)
            print(f"married_females_co is : {married_females_co}")

            # Dental
            dental = self.get_value_catB("Dental")
            logger.debug(f"Dental (Before Apply): {dental}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Dentben22").select_option(dental)
            logger.debug(f"Dental (After Apply): {dental}")
            await asyncio.sleep(1)

            # Dental CO
            dental_co = self.get_value_catB("Dental CO")
            try:
                dental_co = float(dental_co) * 100
                dental_co = f"{int(dental_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Dental CO (Before Apply): {dental_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_DentCopayben22").select_option(dental_co)
            logger.debug(f"Dental CO (After Apply): {dental_co}")
            await asyncio.sleep(3)
            print(f"Denatal CO is : {dental_co}")

            # Optical
            optical = self.get_value_catB("Optical")
            logger.debug(f"Optical (Before Apply): {optical}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_Optben22").select_option(optical)
            logger.debug(f"Optical (After Apply): {optical}")
            await asyncio.sleep(1)

            # Optical CO
            optical_co = self.get_value_catB("Optical CO")
            try:
                optical_co = float(optical_co) * 100
                optical_co = f"{int(optical_co)}%" 
            except ValueError:
                pass
            logger.debug(f"Optical CO (Before Apply): {optical_co}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_OptCopayben22").select_option(optical_co)
            logger.debug(f"Optical CO (After Apply): {optical_co}")
            await asyncio.sleep(3)

            # Life benefit - Death due to any cause
            life_benefit = self.get_value_catB("Life benefit - Death due to any cause")
            logger.debug(f"Life benefit - Death due to any cause (Before Apply): {life_benefit}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_lifeLimit22").select_option(life_benefit)             
            logger.debug(f"Life benefit - Death due to any cause (After Apply): {life_benefit}")
            await asyncio.sleep(3)

            # Repatriation of Mortal remains
            repatriation = self.get_value_catB("Repatriation of Mortal remains")
            logger.debug(f"Repatriation of Mortal remains (Before Apply): {repatriation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_RepatriLimit22").select_option(repatriation)           
            logger.debug(f"Repatriation of Mortal remains (After Apply): {repatriation}")
            await asyncio.sleep(3)

            # Telehealth Consultation
        
            tele_consultation = self.get_value_catB("Telehealth Consultation")
            logger.debug(f"Telehealth Consultation (Before Apply): {tele_consultation}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_TeleLimit22").select_option(tele_consultation)          
            logger.debug(f"Telehealth Consultation (After Apply): {tele_consultation}")
            await asyncio.sleep(3)
        

            # Wellness Package
            wellness_package = self.get_value_catB("Wellness Package")
            logger.debug(f"Wellness Package (Before Apply): {wellness_package}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_WellPa22").select_option(wellness_package)          
            logger.debug(f"Wellness Package (After Apply): {wellness_package}")
            await asyncio.sleep(3)

            # Assist America
            assist_america = self.get_value_catB("Assist America")
            logger.debug(f"Assist America (Before Apply): {assist_america}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_ISOS22").select_option(assist_america)          
            logger.debug(f"Assist America (After Apply): {assist_america}")
            await asyncio.sleep(3)

            # Psychiatry
            psychiatry = self.get_value_catB("Psychiatry")
            logger.debug(f"Psychiatry (Before Apply): {psychiatry}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_psch22").select_option(psychiatry)          
            logger.debug(f"Psychiatry (After Apply): {psychiatry}")
            await asyncio.sleep(3)

            # Alternative Medicine
            alternative_medicine = self.get_value_catB("Alternative Medicine")
            logger.debug(f"Alternative Medicine (Before Apply): {alternative_medicine}")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator("#ddl_alterMedben22").select_option(alternative_medicine)          
            logger.debug(f"Alternative Medicine (After Apply): {alternative_medicine}")
            await asyncio.sleep(3)

            # Click Get Quote
            logger.debug("Clicking Get Quote button (Before Click)")
            await self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click()
            logger.debug("Clicked Get Quote button (After Click)")

            await asyncio.sleep(2)

            if not await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').is_visible():
                logger.debug("Get Quote button not visible, clicking again (Before Click)")
                await self.page.locator("iframe[name=\"content\"]").content_frame.locator('//*[@id="btn_quote"]').click()
                logger.debug("Clicked Get Quote button again (After Click)")
                print("get quote")
    

            # # Download the Quotation
            # download_path = 'D:\\AlgoSpring\\python\\DubaiIns'

            # # Ensure the download directory exists
            # if not os.path.exists(download_path):
            #     os.makedirs(download_path)

            # try:
            #     # Wait for the download to start
            #     async with self.page.expect_download(timeout=120000) as download_info:
            #         # Click the download button
            #         await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').click()

            #         # Wait for the download to complete and save it to the specified path
            #         download = await download_info.value
            #         download_path_full = os.path.join(download_path, "quotation1.pdf")
            #         await download.save_as(download_path_full)
            #         print(f"Downloaded quotation PDF to: {download_path_full}")

            # except asyncio.TimeoutError:
            #     print("Error: Timeout exceeded while waiting for the download.")
            # except Exception as e:
            #     print(f"Unexpected error during download: {e}")

            # await asyncio.sleep(10) 

            # # Download the Quotation
            # download_path = DUBAIINSURANCE_QUOTATION_DIR

            # # Ensure the download directory exists
            # if not os.path.exists(download_path):
            #     os.makedirs(download_path)

            # try:
            #     # Wait for the download to start
            #     async with self.page.expect_download(timeout=120000) as download_info:
            #         # Click the download button
            #         await self.page.locator("iframe[name=\"content\"]").content_frame.locator('#btn_submit').click()

            #         # Wait for the download to complete and save it to the specified path
            #         download = await download_info.value
            #         download_path_full = os.path.join(download_path, "quotation_dubaiinsurance.pdf")
            #         await download.save_as(download_path_full)
            #         print(f"Downloaded quotation PDF to: {download_path_full}")
            #         logger.info(f"Downloaded quotation PDF to: {download_path_full}")

            # except asyncio.TimeoutError:
            #     print("Error: Timeout exceeded while waiting for the download.")
            #     logger.error("Error: Timeout exceeded while waiting for the download.")
            # except Exception as e:
            #     print(f"Unexpected error during download: {e}")
            #     logger.error(f"Unexpected error during download: {e}")

            await asyncio.sleep(10)
            return True
        
        except Exception as e:
            print(f"An error occurred while filling Category 2 information: {e}")
            logger.error(f"An error occurred while filling Category 2 information: {e}")
            return False