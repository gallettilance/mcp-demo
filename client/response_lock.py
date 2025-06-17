# response_store.py
import threading

_response_data = {
    "agent_response": [],
    "display_log": [],
    "status": "idle",
    "error": None
}
_response_lock = threading.Lock()

def reset():
    with _response_lock:
        _response_data["agent_response"] = []
        _response_data["display_log"] = []
        _response_data["status"] = "running"
        _response_data["error"] = None

def append_response(event):
    with _response_lock:
        _response_data["agent_response"].append(event)

def log_display(msg):
    with _response_lock:
        _response_data["display_log"].append(msg)

def set_done():
    with _response_lock:
        _response_data["status"] = "done"

def set_error(err):
    with _response_lock:
        _response_data["status"] = "error"
        _response_data["error"] = str(err)

def get_response():
    with _response_lock:
        return dict(_response_data)
