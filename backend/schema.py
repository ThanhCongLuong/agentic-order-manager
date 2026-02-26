from pydantic import BaseModel, Field
from typing import Optional

class UserIntent(BaseModel):
    order_id: Optional[str] = Field(None, description="The order ID if mentioned (e.g., ABC, XYZ)")
    
    is_confirming: bool = Field(
        False, 
        description="True ONLY if the user says 'Yes', 'Sure', 'Confirm', 'Do it', or 'Okay' to proceed with a cancellation."
    )
    
    is_declining: bool = Field(
        False, 
        description="True ONLY if the user says 'No', 'Stop', 'Don't do it', or 'I changed my mind' to STOP the cancellation process."
    )
    
    wants_to_cancel: bool = Field(
        False, 
        description="True if the user explicitly asks to cancel an order (e.g., 'I want to cancel', 'cancel for me'). This is different from confirming/declining."
    )
