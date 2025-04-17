from trackers import ACTIVITY_TRACKER,APP_USAGE_TRACKER
important_apps = [
    "code",                 # Visual Studio Code
    "pycharm",
    "chrome.exe",        
    "sublime_text",
    "intellij idea",
    "terminal",
    "iterm2",
    "cmd.exe",
    "powershell",
    "chrome",
    "google chrome",
    "firefox",
    "brave",
    "edge",
    "postman",
    "docker",
    "docker desktop",
    "gitkraken",
    "github desktop",
    "notion",
    "slack",
    "zoom",
    "teams",
    "msteams",
    "discord",
    "trello",
    "jira",
    "obsidian"
]

app_dict = {
    
}
INTERVAL = 1

def evalEngine():
    ctx = APP_USAGE_TRACKER()
    active_app = ctx.get_active_app()
    active_app = active_app.lower().strip() if active_app else None
    running_apps = [app.lower().strip() for app in APP_USAGE_TRACKER.get_running_apps()]
    important_running_apps = list(set(running_apps) & set(important_apps))


    # Ensure active_app is only added if it's not already in the list
    if active_app and active_app not in important_running_apps:
        important_running_apps.append(active_app)

    print(f"\n--- Eval Cycle ---")
    print(f"Active App: {active_app}")
    print(f"Running Important Apps: {important_running_apps}")

    for app in important_running_apps:
        if app not in app_dict:
            app_dict[app] = {"focused": 0, "background": 0}

        if app == active_app:
            app_dict[app]["focused"] += INTERVAL
        else:
            app_dict[app]["background"] += INTERVAL

    # Optional: Show current state of app_dict each cycle
    print(f"App Usage Snapshot: {app_dict}")
     

app_tracker = ACTIVITY_TRACKER()
app_tracker.run()
# print([app.lower().strip() for app in APP_USAGE_TRACKER.get_running_apps()])