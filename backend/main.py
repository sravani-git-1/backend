from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from odoo import OdooService

app = FastAPI()
odoo = OdooService()


class PartnerRequest(BaseModel):
    action: str
    type: Optional[str] = None
    data: Optional[Dict] = {}
    filters: Optional[Dict] = {}
    update_fields: Optional[Dict] = {}
    confirm: Optional[bool] = False


# =====================================================
# ✅ YOUR ORIGINAL API (UNCHANGED)
# =====================================================
@app.post("/partner")
def handle_partner(request: PartnerRequest):
    try:
        action = request.action.lower()
        partner_type = request.type.lower() if request.type else None

        if action == "create":
            if not request.data:
                raise HTTPException(status_code=400, detail="Missing data")

            if "name" not in request.data:
                raise HTTPException(status_code=400, detail="Field 'name' is required")

            pid = odoo.create_partner_dynamic(partner_type, request.data)

            return {"status": "success", "id": pid}

        elif action == "read":
            result = odoo.get_partner_dynamic(partner_type, request.filters)

            return {"status": "success", "data": result}

        elif action == "update":
            res = odoo.update_partner_dynamic(
                partner_type, request.filters, request.update_fields
            )
            return {"status": "success" if res else "error"}

        elif action == "delete":
            res = odoo.delete_partner_dynamic(
                partner_type, request.filters
            )
            return {"status": "success" if res else "error"}

        else:
            raise HTTPException(status_code=400, detail="Invalid action")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ✅ NEW APIs (ADDED ONLY)
# =====================================================

@app.post("/customers")
def get_customers(request: PartnerRequest):
    try:
        result = odoo.get_customers_only(request.filters)
        return {"type": "customer", "count": len(result), "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vendors")
def get_vendors(request: PartnerRequest):
    try:
        result = odoo.get_vendors_only(request.filters)
        return {"type": "vendor", "count": len(result), "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))