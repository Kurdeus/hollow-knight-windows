# Hollow Knight Editor

A user-friendly desktop application designed to help you view, edit, and modify Hollow Knight save files, including geo, health, and other game attributes.
This tool simplifies the process of editing Hollow Knight save files, making it easy to customize your gameplay experience.

![Hollow Knight Editor Screenshot](https://github.com/Kurdeus/hollow-knight-windows/blob/main/screenshot/app.jpg?raw=true)

## Features

- **Simple Interface**: Easy-to-use JSON editor for modifying save files
- **Cross-Platform Support**: Works with both PC and mobile save files
- **Version Checking**: Automatically checks for updates on startup
- **Backup Support**: Create backups before making changes to prevent data loss

## Guide to Transferring Save Files Between PC and Mobile

Hollow Knight supports up to 4 save slots, named `user1.dat`, `user2.dat`, `user3.dat`, and `user4.dat`. If you have a save file in one slot, you can rename it to use it in a different slot.

**Note:** To transfer or create save files, ensure you have played the game at least until the first rest bench to trigger a save.

### Save File Locations:
- **PC Version:** Save files are located at:  
  `%USERPROFILE%\AppData\LocalLow\Team Cherry\Hollow Knight\`
- **Android Version:** Save files can be found at:  
  `/Android/data/com.TeamCherry.HollowKnight/files/`

You can transfer your save files between PC and mobile by copying the aforementioned files.

**Important for Android Users:** The `/Android/Data` directory is protected, and normal access or modification of files within it is restricted. To access this directory, consider using apps like ZArchive or X-plore.

## How to Use the Editor

1. **Backup First:** Always create a backup of your save file to prevent data loss in case of corruption.
2. **Open Save File:** Click the "Open Save File" button to load your save file into the editor. The contents will be displayed in a readable JSON format.
3. **Edit Data:** Browse through the data (health, geo, etc.) and modify values as needed.
4. **Save Changes:** Use "Save Changes" to overwrite the original file, or "Save As" to create a new file.
5. **Enjoy:** Load your game and enjoy the changes you've made!

## Keyboard Shortcuts

- **Ctrl+O**: Open save file
- **Ctrl+S**: Save changes
- **Ctrl+Shift+S**: Save as new file

## Getting Updates

The application automatically checks for updates when launched. You can also manually check for updates using the "Check for Updates" button in the Help menu.

## Download

You can download the latest version of the Hollow Knight Editor from the [official GitHub releases page](https://github.com/Kurdeus/hollow-knight-windows/releases).
