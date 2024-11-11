import pyautogui
import pygetwindow as gw
import os
import sys
import time
from pynput import keyboard

# Path to the folder containing the reconnect button images
image_folder = 'F:/Visual Code/NordChanger/images'  # Replace with your folder path

# Define a flag to track if PageDown is pressed
pagedown_pressed = False

def list_all_windows():
    """List all current window titles for debugging purposes."""
    print("Available Windows:")
    for window in gw.getAllWindows():
        print(f"- {window.title}")

def is_nordvpn_active():
    """Check if NordVPN is the active window."""
    active_window = gw.getActiveWindow()
    if active_window and 'NordVPN' in active_window.title:
        return True
    return False

def activate_nordvpn_window():
    """
    Activate the NordVPN window directly using pygetwindow.
    Returns True if activation is successful, else False.
    """
    # Attempt exact match first
    nord_windows = gw.getWindowsWithTitle('NordVPN')

    # If no exact match, attempt partial match
    if not nord_windows:
        nord_windows = [window for window in gw.getAllWindows() if 'NordVPN' in window.title]

    if not nord_windows:
        print("NordVPN window not found.")
        list_all_windows()  # For debugging
        return False

    nord_window = nord_windows[0]
    try:
        nord_window.activate()
        time.sleep(1)  # Wait for the window to come to the front
        if is_nordvpn_active():
            print("NordVPN window activated successfully.")
            return True
        else:
            print("NordVPN window found but failed to activate.")
            return False
    except Exception as e:
        print(f"Error activating NordVPN window: {e}")
        return False

def alt_tab_to_nordvpn():
    """
    Fallback method to activate NordVPN using Alt+Tab.
    Attempts to switch windows up to five times.
    On each attempt, presses Alt+Tab the number of times equal to the attempt number.
    Returns True if NordVPN becomes active, else False.
    """
    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        if is_nordvpn_active():
            print("NordVPN window is now active.")
            return True
        else:
            attempts += 1
            print(f"Attempt {attempts}: Switching windows with Alt+Tab {attempts} times...")
            # Hold down Alt
            pyautogui.keyDown('alt')
            # Press Tab 'attempts' times
            for _ in range(attempts):
                pyautogui.press('tab')
                time.sleep(0.1)  # Small delay between tabs
            # Release Alt
            pyautogui.keyUp('alt')
            time.sleep(1)  # Wait for the window to switch

    print("Failed to activate NordVPN window after multiple Alt+Tab attempts.")
    return False

def press_reconnect():
    """Search for the reconnect button and click it if found."""
    # List all image files in the folder
    for image_file in os.listdir(image_folder):
        # Only consider image files (e.g., .png, .jpg, .jpeg)
        if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_file)
            print(f"Trying to locate {image_path}...")

            try:
                # Try to find the reconnect button in the current image
                button_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)

                if button_location:
                    # Move the mouse to the found location and click
                    pyautogui.moveTo(button_location)
                    pyautogui.click()
                    print(f"Reconnect button clicked using {image_file}.")
                    return True  # Stop checking further images and return success
                else:
                    print(f"No match found for {image_file}.")

            except Exception as e:
                print(f"Error processing {image_file}: {e}")
                continue  # Skip to the next image

    print("Reconnect button not found on the screen.")
    return False  # Return failure if no button was found

def check_vpn_status_and_reconnect():
    """Check if NordVPN is active, activate it if not, and press reconnect."""
    if not is_nordvpn_active():
        print("NordVPN is not active. Attempting to activate...")
        # First, try to activate NordVPN directly
        if activate_nordvpn_window():
            if press_reconnect():
                return  # Successfully reconnected, return to main loop
        else:
            # If direct activation fails, fallback to Alt+Tab
            print("Direct activation failed. Trying Alt+Tab method...")
            if alt_tab_to_nordvpn():
                if press_reconnect():
                    return  # Successfully reconnected, return to main loop
            else:
                print("Failed to bring NordVPN to the front. Exiting.")
                sys.exit(1)
    else:
        print("NordVPN is already active.")
        if press_reconnect():
            return  # Successfully reconnected, return to main loop

def on_press(key):
    """Callback function to detect PageDown key press."""
    global pagedown_pressed
    try:
        if key == keyboard.Key.page_down:
            print("PageDown pressed. Exiting loop.")
            pagedown_pressed = True
            return False  # Stop listener
    except AttributeError:
        pass

def main_loop():
    """Main loop that runs every 5 minutes and checks NordVPN."""
    global pagedown_pressed

    # Start the PageDown key listener
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while not pagedown_pressed:
        print("\n=== Checking NordVPN status ===")
        check_vpn_status_and_reconnect()

        if pagedown_pressed:
            print("PageDown detected, exiting...")
            break

        print("Waiting 5 minutes before the next check...")
        time.sleep(300)  # Sleep for 5 minutes (300 seconds)

    listener.stop()
    print("Script terminated gracefully.")

if __name__ == "__main__":
    main_loop()
