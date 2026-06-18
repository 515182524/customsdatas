---
name: WeChat
description: macOS WeChat automation - sending messages and images via pyautogui keyboard simulation.
---

# WeChat

macOS WeChat automation - sending messages and images via pyautogui keyboard simulation.

## Features

- Open WeChat (via Spotlight search)
- Search for contacts/groups
- Send text messages
- Send images

## Requirements

- macOS system
- Python 3.x
- WeChat desktop app

## Dependencies

```bash
pip install pyautogui pyperclip pyperclipimg
```

## Usage

```bash
cd scripts

# Send text message
python3 wechat_send.py --name "Contact Name" --message "Message content"

# Send image
python3 wechat_send.py --name "Contact Name" --image_path="/path/to/image.png"

# Send both message and image
python3 wechat_send.py --name "Contact Name" --message "Check this out" --image_path="test.png"
```

## Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `--name` | Yes | Contact or group name |
| `--message` | At least one | Text message to send |
| `--image_path` | At least one | Path to image file |

Note: At least one of `--message` or `--image_path` must be provided.

## How It Works

1. **Open WeChat**: Simulate `Cmd+Space` to open Spotlight, search for "微信" and launch
2. **Search contact**: Simulate `Cmd+F` to open search, paste contact name, press Enter to enter chat
3. **Send message**: Copy text to clipboard, paste and send
4. **Send image**: Copy image to clipboard, paste and send

## Important Notes

- **Accessibility permission** is required for terminal/IDE (System Settings > Privacy & Security > Accessibility)
- WeChat must be logged in
- Contact name must match exactly as shown in WeChat
- Do not operate mouse/keyboard during sending to avoid interference

## File Structure

```
wechat-skill/
├── SKILL.md              # This documentation
├── scripts/
│   └── wechat_send.py    # Main script
```
