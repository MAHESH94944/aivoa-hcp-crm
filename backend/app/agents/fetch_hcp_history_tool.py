import math
from sqlalchemy.orm import Session
from app import models
from typing import List, Dict, Any, Optional
from datetime import date

def fetch_hcp_history_tool(
    db: Session,
    hcp_name: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    page: int = 1,
    page_size: int = 10
) -> Dict[str, Any]:
    """
    Retrieves a paginated and filtered list of interaction records for an HCP
    using advanced search criteria.

    This tool does NOT use an LLM.

    Args:
        db: The SQLAlchemy database session.
        hcp_name: The partial or full name of the HCP to search for (case-insensitive).
        start_date: Optional start date for the filter range.
        end_date: Optional end date for the filter range.
        page: The page number to retrieve.
        page_size: The number of records per page.

    Returns:
        A dictionary containing the list of interactions and pagination metadata.
    """
    if not hcp_name:
        return {"status": "error", "message": "HCP name must be provided."}

    try:
        # Start building the base query
        query = db.query(models.HCPInteraction)

        # 1. Advanced Feature: Fuzzy Name Matching (case-insensitive)
        query = query.filter(models.HCPInteraction.hcp_name.ilike(f"%{hcp_name}%"))

        # 2. Advanced Feature: Date Range Filtering
        if start_date:
            query = query.filter(models.HCPInteraction.date >= start_date)
        if end_date:
            query = query.filter(models.HCPInteraction.date <= end_date)

        # 3. Advanced Feature: Smart Pagination
        # First, get the total count of records that match the filters
        total_records = query.count()
        if total_records == 0:
            return {
                "status": "success",
                "message": f"No interactions found for '{hcp_name}'.",
                "data": [],
                "pagination": {
                    "total_records": 0, "current_page": 1, "page_size": page_size, "total_pages": 0
                }
            }
        
        # Then, apply ordering, offset, and limit to get just the current page's data
        interactions = (
            query
            .order_by(models.HCPInteraction.date.desc(), models.HCPInteraction.time.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

        # Calculate total pages
        total_pages = math.ceil(total_records / page_size)

        return {
            "status": "success",
            "data": interactions,
            "pagination": {
                "total_records": total_records,
                "current_page": page,
                "page_size": page_size,
                "total_pages": total_pages
            }
        }

    except Exception as e:
        return {"status": "error", "message": f"A database error occurred: {str(e)}"}