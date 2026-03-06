from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from models import model
from database import get_order_full_context,create_request
from schema import UserIntent

def assistant_node(state):
    last_msg = state["messages"][-1].content
    intent = model.with_structured_output(UserIntent).invoke(last_msg)
    
    order_id = intent.order_id or state.get("order_id")
    if not order_id:
        return {"messages": [AIMessage(content="Please provide a valid Order ID to proceed (e.g., ABC, XYZ).")]}

    order_status, request_status = get_order_full_context(order_id)

    if order_status == "Cancelled":
        msg = f"Order {order_id} is already CANCELLED."
        return {"messages": [AIMessage(content=msg)], "order_id": order_id}

    if order_status == "Delivered":
        return {"messages": [AIMessage(content=f"Order {order_id} was DELIVERED. Cancellation is no longer possible.")], "order_id": order_id}

    if order_status == "Pending":
        if request_status == "pending":
            msg = f"A cancellation request for Order {order_id} is already awaiting Admin approval. Please wait."
        
        elif request_status == "refused":
            msg = f"Your previous request for Order {order_id} was rejected by Admin. Your order remains active."
            if intent.wants_to_cancel:
                msg += " If you have a specific reason to re-apply, please contact support."
        
        elif intent.is_confirming or intent.wants_to_cancel:
            create_request(order_id, "Cancel Order")
            msg = f"I've submitted a cancellation request for Order {order_id}. Admin will review it shortly."
            
        elif intent.is_declining:
            msg = f"Understood. I will not cancel Order {order_id}. How else can I assist you?"
            
        else:
            msg = f"Order {order_id} is currently PENDING. Would you like to request a cancellation? (Yes/No)"
        
        return {"messages": [AIMessage(content=msg)], "order_id": order_id}

    return {"messages": [AIMessage(content=f"Order {order_id} is in status: {order_status}. Please contact support for more details.")], "order_id": order_id}