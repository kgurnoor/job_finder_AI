import uuid

def create_session():
    """Creates a new session and returns the session ID."""
    session_id = str(uuid.uuid4())
    # In a real application, you might store session data in a database or a more persistent storage.
    # For this example, we'll keep it simple and use a dictionary.
    sessions[session_id] = {"history": []}
    return session_id

def get_context(session_id):
    """Retrieves the conversation history for a given session."""
    if session_id in sessions:
        return sessions[session_id]["history"]
    else:
        return []  # Return empty list, handle the error

def update_context(session_id, user_query, bot_response):
    """Updates the conversation history for a given session."""
    if session_id in sessions:
        sessions[session_id]["history"].append({"role": "user", "content": user_query})
        sessions[session_id]["history"].append({"role": "assistant", "content": bot_response})
    else:
        print(f"Session ID {session_id} not found.") # error Handling
        sessions[session_id] = {"history": [{"role": "user", "content": user_query},
                                           {"role": "assistant", "content": bot_response}]} # added session

#  In-memory storage for sessions.  Use a proper database in production.
sessions = {}