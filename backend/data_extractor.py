"""
SuccessFactors Data Extractor
Handles API calls to extract permission groups and related data after login
"""

import re
import json
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import parse_qs, urlparse
import logging

logger = logging.getLogger(__name__)


class SuccessFactorsDataExtractor:
    """
    Extracts data from SuccessFactors APIs after successful login
    """
    
    def __init__(self, scraper):
        """Initialize with the authenticated scraper instance"""
        self.scraper = scraper
        self.driver = scraper.driver
        self.session = requests.Session()
        self.base_url = "https://salesdemo.successfactors.eu"
        
        # Session data extracted from browser
        self.csrf_token = None
        self.session_id = None
        self.cookies = None
        self.headers = {}
        
    def extract_session_data(self) -> bool:
        """
        Extract session tokens and cookies from the authenticated browser session
        """
        try:
            # Get cookies from browser
            browser_cookies = self.driver.get_cookies()
            self.cookies = {cookie['name']: cookie['value'] for cookie in browser_cookies}
            
            # Update requests session with browser cookies
            for cookie in browser_cookies:
                self.session.cookies.set(cookie['name'], cookie['value'])
            
            # Extract CSRF token from page or meta tags
            self.csrf_token = self._extract_csrf_token()
            
            # Extract session ID from script or cookies
            self.session_id = self._extract_session_id()
            
            # Setup default headers
            self._setup_headers()
            
            logger.info("Session data extracted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to extract session data: {str(e)}")
            return False
    
    def _extract_csrf_token(self) -> Optional[str]:
        """Extract CSRF token from the page"""
        try:
            # Try to find CSRF token in meta tags
            csrf_elements = self.driver.find_elements("css selector", "meta[name='_csrf'], meta[name='csrf-token']")
            if csrf_elements:
                return csrf_elements[0].get_attribute("content")
            
            # Try to find in script tags or page source
            page_source = self.driver.page_source
            
            # Look for common CSRF token patterns
            csrf_patterns = [
                r'csrfToken["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'_csrf["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'csrf["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in csrf_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    token = match.group(1)
                    if len(token) > 10:  # Valid tokens are usually longer
                        return token
            
            # Check URL parameters
            current_url = self.driver.current_url
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)
            
            for param_name in ['_s.crb', 'csrf', 'token']:
                if param_name in query_params:
                    return query_params[param_name][0]
            
            logger.warning("CSRF token not found")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting CSRF token: {str(e)}")
            return None
    
    def _extract_session_id(self) -> Optional[str]:
        """Extract session ID from cookies or page"""
        try:
            # Try common session cookie names
            session_cookies = ['JSESSIONID', 'sessionId', 'sid']
            for cookie_name in session_cookies:
                if cookie_name in self.cookies:
                    return self.cookies[cookie_name]
            
            # Try to extract from page source
            page_source = self.driver.page_source
            session_patterns = [
                r'sessionId["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                r'scriptSessionId["\']?\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in session_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    return match.group(1)
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting session ID: {str(e)}")
            return None
    
    def _setup_headers(self):
        """Setup default headers for API requests"""
        current_url = self.driver.current_url
        
        self.headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9,de;q=0.8,fr;q=0.7",
            "content-type": "text/plain",
            "priority": "u=1, i",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-sap-page-info": f"companyId={self.scraper.company_id}&moduleId=ADMIN&pageId=ADMIN&pageQualifier=MANAGE_RBP_GROUP&uiVersion=V12",
            "Referer": current_url
        }
        
        if self.csrf_token:
            self.headers["x-ajax-token"] = self.csrf_token
            self.headers["x-csrf-token"] = self.csrf_token
    
    def get_permission_groups(self) -> Optional[Dict]:
        """
        Fetch permission groups data from the first endpoint
        """
        try:
            if not self.extract_session_data():
                logger.error("Failed to extract session data")
                return None
            
            url = f"{self.base_url}/xi/ajax/remoting/call/plaincall/dgListControllerProxy.getStickyGroupData.dwr"
            
            # Prepare request body based on the provided example
            body_data = [
                "callCount=1",
                f"page={self.driver.current_url}",
                "httpSessionId=",
                f"scriptSessionId={self.session_id or '80A8BD291A8E635A37D57F13E5D1F423722'}",
                "c0-scriptName=dgListControllerProxy",
                "c0-methodName=getStickyGroupData",
                "c0-id=0",
                "c0-param0=string:permission",
                "c0-param1=boolean:true",
                "batchId=4"
            ]
            
            body = "\n".join(body_data)
            
            # Add dynamic headers
            headers = self.headers.copy()
            headers["viewid"] = "/ui/rbp/pages/manage_permission_groups.xhtml"
            headers["x-event-id"] = f"EVENT-PLT-ADMIN_MANAGE_RBP_GROUP-{self._generate_event_id()}"
            headers["x-subaction"] = "0"
            
            logger.info("Fetching permission groups data...")
            
            response = self.session.post(url, data=body, headers=headers)
            
            if response.status_code == 200:
                logger.info("Permission groups data fetched successfully")
                return self._parse_dwr_response(response.text)
            else:
                logger.error(f"Failed to fetch permission groups: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching permission groups: {str(e)}")
            return None
    
    def get_permission_group_details(self, group_id: str) -> Optional[Dict]:
        """
        Fetch detailed data for a specific permission group using the retrieveGroup endpoint
        """
        try:
            logger.info(f"Fetching details for permission group: {group_id}")
            
            url = f"{self.base_url}/xi/ajax/remoting/call/plaincall/dGUpdateControllerProxy.retrieveGroup.dwr"
            
            body_data = [
                "callCount=1",
                f"page={self._get_relative_page_url()}",
                "httpSessionId=",
                f"scriptSessionId={self.session_id or '80A8BD291A8E635A37D57F13E5D1F423722'}",
                "c0-scriptName=dGUpdateControllerProxy",
                "c0-methodName=retrieveGroup",
                "c0-id=0",
                f"c0-param0=number:{group_id}",
                "c0-param1=string:permission",
                "batchId=6"
            ]
            
            body = "\n".join(body_data)
            
            # Add dynamic headers with different event ID
            headers = self.headers.copy()
            headers["viewid"] = "/ui/rbp/pages/manage_permission_groups.xhtml"
            headers["x-event-id"] = f"EVENT-PLT-ADMIN_MANAGE_RBP_GROUP-{self._generate_event_id()}-1"
            headers["x-subaction"] = "0"
            
            response = self.session.post(url, data=body, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Details fetched for group {group_id}")
                return self._parse_dwr_response(response.text)
            else:
                logger.error(f"Failed to fetch group details: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching group details: {str(e)}")
            return None
    
    def get_group_members(self, group_id: str) -> Optional[Dict]:
        """
        Fetch the list of members for a specific permission group
        """
        try:
            logger.info(f"Fetching members for permission group: {group_id}")
            
            url = f"{self.base_url}/xi/ajax/remoting/call/plaincall/dGUpdateControllerProxy.getGroupMembers.dwr"
            
            body_data = [
                "callCount=1",
                f"page={self.driver.current_url}",
                "httpSessionId=",
                f"scriptSessionId={self.session_id or '80A8BD291A8E635A37D57F13E5D1F423722'}",
                "c0-scriptName=dGUpdateControllerProxy",
                "c0-methodName=getGroupMembers",
                "c0-id=0",
                f"c0-param0=number:{group_id}",
                "c0-param1=string:permission",
                "c0-param2=number:0",  # start index
                "c0-param3=number:1000",  # max results, adjust if needed
                "batchId=7"
            ]
            
            body = "\n".join(body_data)
            
            # Add dynamic headers
            headers = self.headers.copy()
            headers["viewid"] = "/ui/rbp/pages/manage_permission_groups.xhtml"
            headers["x-event-id"] = f"EVENT-PLT-ADMIN_MANAGE_RBP_GROUP-{self._generate_event_id()}-2"
            headers["x-subaction"] = "0"
            
            response = self.session.post(url, data=body, headers=headers)
            
            if response.status_code == 200:
                logger.info(f"Members fetched for group {group_id}")
                return self._parse_dwr_response(response.text)
            else:
                logger.error(f"Failed to fetch group members: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching group members: {str(e)}")
            return None
    
    def _parse_dwr_response(self, response_text: str) -> Optional[Dict]:
        """
        Parse DWR (Direct Web Remoting) response format based on actual SuccessFactors structure
        """
        try:
            # Look for the DWR callback line
            lines = response_text.strip().split('\n')
            
            for line in lines:
                if line.startswith('dwr.engine._remoteHandleCallback'):
                    # Extract the JSON data from the callback
                    # Pattern: dwr.engine._remoteHandleCallback('4','0',{JSON_DATA});
                    match = re.search(r"dwr\.engine\._remoteHandleCallback\('[^']*',\s*'[^']*',\s*(.+)\);?$", line)
                    if match:
                        try:
                            json_str = match.group(1)
                            # Parse the JSON data
                            data = json.loads(json_str)
                            
                            # The response structure contains:
                            # - attributes: metadata
                            # - groupList: array of group objects
                            # - totalCount: total number of groups
                            
                            return data
                            
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse JSON from DWR response: {str(e)}")
                            return {"error": "Invalid JSON in DWR response", "raw": json_str}
            
            # If no callback found, return raw response
            logger.warning("No DWR callback found in response")
            return {"error": "No DWR callback found", "raw_response": response_text}
            
        except Exception as e:
            logger.error(f"Error parsing DWR response: {str(e)}")
            return {"error": str(e), "raw_response": response_text}
    
    def _generate_event_id(self) -> str:
        """Generate a unique event ID for requests"""
        import time
        import random
        timestamp = str(int(time.time() * 1000))
        random_part = str(random.randint(100000, 999999))
        return f"or46abe15-20251015071438-{random_part}"
    
    def extract_all_data(self) -> Dict[str, Any]:
        """
        Extract all permission groups and their details
        """
        try:
            logger.info("Starting full data extraction...")
            
            # Get list of permission groups
            groups_response = self.get_permission_groups()
            if not groups_response:
                return {"error": "Failed to fetch permission groups"}
            
            result = {
                "permission_groups_overview": groups_response,
                "group_details": {},
                "summary": {
                    "total_groups": 0,
                    "extracted_details": 0,
                    "failed_extractions": 0
                }
            }
            
            # Extract basic group info
            if 'groupList' in groups_response:
                result["summary"]["total_groups"] = len(groups_response['groupList'])
                
                # Extract group IDs and fetch details for each
                group_ids = self._extract_group_ids(groups_response)
                
                logger.info(f"Found {len(group_ids)} groups, fetching details...")
                
                for i, group_id in enumerate(group_ids, 1):
                    logger.info(f"Fetching details for group {i}/{len(group_ids)}: {group_id}")
                    
                    try:
                        details = self.get_permission_group_details(group_id)
                        if details:
                            result["group_details"][group_id] = details
                            result["summary"]["extracted_details"] += 1
                            
                            # Fetch group members
                            members = self.get_group_members(group_id)
                            if members:
                                result["group_details"][group_id]["members"] = members
                                logger.info(f"Members fetched for group {group_id}")
                            else:
                                logger.warning(f"Failed to get members for group {group_id}")
                        else:
                            result["summary"]["failed_extractions"] += 1
                            logger.warning(f"Failed to get details for group {group_id}")
                    
                    except Exception as e:
                        result["summary"]["failed_extractions"] += 1
                        logger.error(f"Error fetching details for group {group_id}: {str(e)}")
            
            else:
                result["summary"]["total_groups"] = 0
                logger.warning("No groupList found in response")
            
            logger.info(f"Data extraction completed. "
                       f"Total: {result['summary']['total_groups']}, "
                       f"Detailed: {result['summary']['extracted_details']}, "
                       f"Failed: {result['summary']['failed_extractions']}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in full data extraction: {str(e)}")
            return {"error": str(e)}
    
    def _extract_group_ids(self, groups_response: Dict) -> List[str]:
        """
        Extract group IDs from the groups response data
        Based on the actual SuccessFactors response structure
        """
        group_ids = []
        
        try:
            # Check if response has the expected structure
            if isinstance(groups_response, dict) and 'groupList' in groups_response:
                group_list = groups_response['groupList']
                
                for group in group_list:
                    if isinstance(group, dict) and 'groupId' in group:
                        group_ids.append(str(group['groupId']))
            
            logger.info(f"Extracted {len(group_ids)} group IDs: {group_ids}")
            return group_ids
        
        except Exception as e:
            logger.error(f"Error extracting group IDs: {str(e)}")
            return []
    
    def save_data_to_file(self, data: Dict[str, Any], filename: str = "permission_groups_data.json"):
        """Save extracted data to a JSON file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Data saved to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Error saving data to file: {str(e)}")
            return None
    
    def _get_relative_page_url(self) -> str:
        """Get the relative page URL for DWR requests"""
        current_url = self.driver.current_url
        if current_url.startswith(self.base_url):
            return current_url[len(self.base_url):]
        return current_url  # fallback to full URL if not matching
