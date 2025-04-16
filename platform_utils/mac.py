from AppKit import NSWorkspace

def get_focused_app():
    try:
        active_app  = NSWorkspace.sharedWorkspace().activeApplication()['NSApplicationName']
        return active_app.lower()
    except Exception as e:
        print(f"[macOS] Focused app error: {e}")
        return None
    
    
    