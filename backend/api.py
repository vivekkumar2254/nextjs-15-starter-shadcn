"""
FastAPI Service for SuccessFactors Data Extraction
Provides endpoints to extract permission groups and roles data
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import logging
from successfactors_scraper import SuccessFactorsScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SuccessFactors Scraper API", version="1.0.0")

class Credentials(BaseModel):
    username: str
    password: str
    company_name: str  # This maps to company_id
    page: int = 1
    page_size: int = 50

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "SuccessFactors Scraper API", "version": "1.0.0"}

@app.post("/permission-groups")
async def get_permission_groups(credentials: Credentials):
    """
    Extract permission groups data from SuccessFactors
    """
    try:
        logger.info("Starting permission groups extraction")

        with SuccessFactorsScraper(
            username=credentials.username,
            password=credentials.password,
            company_id=credentials.company_name
        ) as scraper:
            # Navigate and login
            if not scraper.navigate_to_login():
                raise HTTPException(status_code=400, detail="Failed to navigate to SuccessFactors")

            if not scraper.login():
                raise HTTPException(status_code=401, detail="Login failed")

            # Extract data
            extractor = scraper.extract_data()
            if not extractor:
                raise HTTPException(status_code=500, detail="Failed to create data extractor")

            # Get permission groups
            groups = extractor.get_permission_groups()
            if not groups:
                raise HTTPException(status_code=404, detail="No permission groups found")

            # Extract all data
            all_data = extractor.extract_all_data()

            logger.info(f"Successfully extracted {len(groups)} permission groups")
            return {
                "status": "success",
                "permission_groups": groups,
                "complete_data": all_data
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting permission groups: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/roles-data")
async def get_roles_data(credentials: Credentials):
    """
    Extract roles data with permissions from SuccessFactors
    Supports pagination with page and page_size parameters
    """
    try:
        logger.info(f"Starting roles data extraction (page {credentials.page}, size {credentials.page_size})")

        with SuccessFactorsScraper(
            username=credentials.username,
            password=credentials.password,
            company_id=credentials.company_name
        ) as scraper:
            # Navigate and login
            if not scraper.navigate_to_login():
                raise HTTPException(status_code=400, detail="Failed to navigate to SuccessFactors")

            if not scraper.login():
                raise HTTPException(status_code=401, detail="Login failed")

            # Extract roles data
            all_roles_data = scraper.extract_roles_data()
            if not all_roles_data:
                raise HTTPException(status_code=404, detail="No roles data found")

            # Apply pagination
            total_roles = len(all_roles_data)
            start_idx = (credentials.page - 1) * credentials.page_size
            end_idx = start_idx + credentials.page_size
            
            if start_idx >= total_roles:
                paginated_roles = []
            else:
                paginated_roles = all_roles_data[start_idx:end_idx]

            # Fetch permissions for each role in the paginated results
            roles_with_permissions = 0
            for role in paginated_roles:
                role_id = role.get('id')
                if role_id:
                    try:
                        permissions = scraper.fetch_role_permissions(role_id)
                        if permissions:
                            role['permissions'] = permissions
                            roles_with_permissions += 1
                        else:
                            role['permissions'] = {}
                    except Exception as e:
                        logger.warning(f"Error fetching permissions for role {role_id}: {str(e)}")
                        role['permissions'] = {}
                else:
                    role['permissions'] = {}

            # Calculate pagination metadata
            total_pages = (total_roles + credentials.page_size - 1) // credentials.page_size
            
            logger.info(f"Successfully extracted {len(paginated_roles)} roles (page {credentials.page}/{total_pages}) with {roles_with_permissions} having permissions")
            return {
                "status": "success",
                "roles": paginated_roles,
                "pagination": {
                    "page": credentials.page,
                    "page_size": credentials.page_size,
                    "total_roles": total_roles,
                    "total_pages": total_pages,
                    "has_next": credentials.page < total_pages,
                    "has_prev": credentials.page > 1
                },
                "summary": {
                    "roles_returned": len(paginated_roles),
                    "roles_with_permissions": roles_with_permissions
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting roles data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
