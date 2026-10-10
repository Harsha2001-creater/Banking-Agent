from langchain_core.tools import tool
from src.db.database import get_db_connection

@tool
def create_service_request(user_id: str, request_type: str, details: str) -> str:
    """
    Creates a new customer service request ticket.
    Use this when a user wants to report an issue, dispute a charge, order a new card, or request help.
    """
    print(f"\n[System: 🛑 Agent is attempting to create a {request_type} ticket for {user_id}]")
    print(f"[System: Details parsed by AI: {details}]")
    
    # Human-in-the-Loop (HITL) Check
    approval = input("\n⚠️ Do you approve this database action? (y/n): ")
    
    if approval.strip().lower() != 'y':
        print("[System: Action aborted by user.]")
        return f"The human user declined to open the ticket for {user_id}. Ask them if they need anything else."
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO service_requests (user_id, request_type, details, status)
                    VALUES (%s, %s, %s, 'OPEN')
                    RETURNING request_id
                    """,
                    (user_id, request_type, details)
                )
                
                new_request_id = cursor.fetchone()['request_id']
                conn.commit()
                
                return f"Successfully created service request ticket #{new_request_id} for user {user_id}."
    except Exception as e:
        return f"System error creating service request: {str(e)}"