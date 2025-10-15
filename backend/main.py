#!/usr/bin/env python3
"""
SuccessFactors Scraper - Main Entry Point
Simple script to test SuccessFactors login functionality
"""

import os
from successfactors_scraper import SuccessFactorsScraper
from dotenv import load_dotenv

def main():
    """Main function to run the SuccessFactors scraper"""
    # Load environment variables
    load_dotenv()
    
    # Check if credentials are configured
    if not all([os.getenv('SF_COMPANY_ID'), os.getenv('SF_USERNAME'), os.getenv('SF_PASSWORD')]):
        print("❌ Missing credentials in .env file")
        print("Please configure SF_COMPANY_ID, SF_USERNAME, and SF_PASSWORD")
        return
    
    print("🚀 Starting SuccessFactors login...")
    
    try:
        with SuccessFactorsScraper() as scraper:
            # Navigate to SuccessFactors
            if scraper.navigate_to_login():
                print("✅ Navigated to SuccessFactors")
                
                # Attempt login
                if scraper.login():
                    print("🎉 Login successful!")
                    
                    # Get current page info
                    page_info = scraper.get_current_page_info()
                    print(f"📄 Current page: {page_info.get('page_type', 'unknown')}")
                    print(f"🔗 URL: {page_info.get('url', 'unknown')}")
                    
                    # Take screenshot
                    screenshot = scraper.take_screenshot("login_success.png")
                    print(f"📸 Screenshot: {screenshot}")
                    
                    print("✅ Ready for automation!")
                    
                    # Extract data from SuccessFactors APIs
                    print("\n🔍 Starting data extraction...")
                    extractor = scraper.extract_data()
                    
                    if extractor:
                        # Extract permission groups data
                        print("📋 Fetching permission groups...")
                        groups = extractor.get_permission_groups()
                        
                        if groups:
                            print(f"✅ Found {len(groups)} permission groups")
                            
                            # Extract all data (groups + details)
                            print("📊 Extracting complete data...")
                            all_data = extractor.extract_all_data()
                            
                            # Save to file
                            filename = extractor.save_data_to_file(all_data)
                            if filename:
                                print(f"💾 Data saved to: {filename}")
                            
                            print("🎊 Data extraction completed!")
                            
                            # Extract roles data from UI
                            print("\n🔍 Starting roles extraction...")
                            roles_data = scraper.extract_roles_data()
                            
                            if roles_data:
                                print(f"✅ Found {len(roles_data)} roles")
                                
                                # Fetch permissions for each role
                                print("🔍 Fetching permissions for each role...")
                                roles_with_permissions = 0
                                
                                for role in roles_data:
                                    role_id = role.get('id')
                                    if role_id:
                                        try:
                                            permissions = scraper.fetch_role_permissions(role_id)
                                            if permissions:
                                                role['permissions'] = permissions
                                                roles_with_permissions += 1
                                                print(f"✅ Fetched permissions for role {role_id}")
                                            else:
                                                role['permissions'] = {}
                                                print(f"❌ Failed to fetch permissions for role {role_id}")
                                        except Exception as e:
                                            print(f"💥 Error fetching permissions for role {role_id}: {str(e)}")
                                            role['permissions'] = {}
                                    else:
                                        role['permissions'] = {}
                                
                                print(f"🎊 Permissions fetched for {roles_with_permissions}/{len(roles_data)} roles")
                                
                                # Save roles data to file
                                import json
                                roles_filename = "roles_data.json"
                                with open(roles_filename, 'w', encoding='utf-8') as f:
                                    json.dump({
                                        "roles": roles_data,
                                        "summary": {
                                            "total_roles": len(roles_data),
                                            "roles_with_permissions": roles_with_permissions
                                        }
                                    }, f, indent=2, ensure_ascii=False)
                                
                                print(f"💾 Roles data saved to: {roles_filename}")
                                print("🎊 Roles extraction completed!")
                            else:
                                print("❌ Failed to extract roles data")
                        
                        else:
                            print("❌ Failed to fetch permission groups")
                    else:
                        print("❌ Failed to create data extractor")
                    
                else:
                    print("❌ Login failed!")
                    scraper.take_screenshot("login_failed.png")
            else:
                print("❌ Failed to navigate to SuccessFactors")
                
    except Exception as e:
        print(f"💥 Error: {str(e)}")

if __name__ == "__main__":
    main()
