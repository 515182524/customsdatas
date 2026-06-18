import argparse
import subprocess
from time import sleep
import pyperclip
import pyperclipimg
import pyautogui

# Delay between pyautogui actions (seconds)
pyautogui.PAUSE = 0.05


def open_wechat() -> None:
    """Launch and activate WeChat directly to avoid typing into other apps."""
    subprocess.run(['open', '-a', 'WeChat'], check=False)
    subprocess.run(
        ['osascript', '-e', 'tell application "WeChat" to activate'],
        check=False,
    )


def search_friend(name: str) -> None:
    """
    Search for a contact by name.

    Requires WeChat to be already open.
    Uses Cmd+F to focus search box, types the name, and enters the chat.
    """
    pyautogui.hotkey('command', 'f')
    pyperclip.copy(name)
    pyautogui.hotkey('command', 'v')
    sleep(0.5)
    pyautogui.press('enter')


def send_message(message: str) -> None:
    """
    Send a text message.

    Requires the chat window to be already open (use search_friend first).
    Copies message to clipboard, pastes, and sends.
    """
    pyperclip.copy(message)
    pyautogui.hotkey('command', 'v')
    sleep(0.5)
    pyautogui.press('enter')


def send_image(image_path: str) -> None:
    """
    Send an image file.

    Requires the chat window to be already open (use search_friend first).
    Copies image to clipboard, pastes, and sends.
    """
    # Copy image content to clipboard
    pyperclipimg.copy(image_path)
    pyautogui.hotkey('command', 'v')
    sleep(0.5)
    pyautogui.press('enter')


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Send messages and images via WeChat"
    )
    parser.add_argument(
        '--name',
        type=str,
        required=True,
        help="Contact or group name"
    )
    parser.add_argument(
        '--message',
        type=str,
        required=False,
        help="Text message to send"
    )
    parser.add_argument(
        '--image_path',
        type=str,
        required=False,
        help="Path to image file"
    )
    arguments = vars(parser.parse_args())

    # Validate: at least one of message or image_path must be provided
    if not arguments.get('message') and not arguments.get('image_path'):
        parser.error("At least one of --message or --image_path is required")

    # Step 1: Open WeChat
    open_wechat()
    sleep(1)

    # Step 2: Search for the contact
    search_friend(arguments['name'])
    sleep(1)

    # Step 3: Send message (if provided)
    if arguments.get('message'):
        send_message(arguments['message'])
        sleep(1)

    # Step 4: Send image (if provided)
    if arguments.get('image_path'):
        send_image(arguments['image_path'])
        sleep(1)


if __name__ == "__main__":
    main()
