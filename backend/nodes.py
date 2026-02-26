from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from models import model
from database import get_order_full_context,create_request
from schema import UserIntent

def assistant_node(state):
    last_msg = state["messages"][-1].content
    intent = model.with_structured_output(UserIntent).invoke(last_msg)
    
    order_id = intent.order_id or state.get("order_id")
    order_status, request_status = get_order_full_context(order_id)

    if order_status == "Cancelled":
        msg = f"Admin approved! Order {order_id} is CANCELLED." if request_status == "approved" else f"Order {order_id} is already CANCELLED."
        return {"messages": [AIMessage(content=msg)], "order_id": order_id}

    if order_status == "Delivered":
        return {"messages": [AIMessage(content=f"Order {order_id} was DELIVERED. Cannot cancel.")], "order_id": order_id}

    if order_status == "Pending":
        if request_status == "pending":
            msg = f"Order {order_id} is waiting for Admin. Please wait."
            return {"messages": [AIMessage(content=msg)], "order_id": order_id}
        
        if request_status == "refused":
            msg = f"Your request to cancel Order {order_id} was REJECTED by Admin. Your order is still being processed."
            return {"messages": [AIMessage(content=msg)], "order_id": order_id}

        elif intent.wants_to_cancel or intent.is_confirming:
            create_request(order_id, "Cancel Order")
            msg = f"Request sent for Order {order_id}! Please wait for Admin approval."
            
        elif intent.is_declining:
            msg = f"Okay, I won't cancel order {order_id}. Is there anything else I can help with?"
            
        else:
            msg = f"Order {order_id} is PENDING. Want to cancel? (Yes/No)"
        
        return {"messages": [AIMessage(content=msg)], "order_id": order_id}

    return {"messages": [AIMessage(content="Please provide a valid Order ID (ABC/XYZ).")]}