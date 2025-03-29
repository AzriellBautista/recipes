import subprocess

# Requires the "Show-ToastNotification.ps1"
PATH_TO_SHOWTOASTNOTIFICATIONPS1 = r".\Show-ToastNotification.ps1"


if __name__ == "__main__":
    # * Example Usage for calling within Python
    subprocess.call([
        "powershell", 
        *("-ExecutionPolicy", "Bypass"), 
        *("-File", PATH_TO_SHOWTOASTNOTIFICATIONPS1),
        *("-templateType", "ToastText02"),
        *("-text1", "Hello world!"),
        *("-text2", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."),
    ])
