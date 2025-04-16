Cloud Explorer
==============
Modification for [rclone](https://rclone.org/) command line tool with GUI.

Supports Linux and Windows.

Table of contents
-------------------
*   [Features](https://github.com/Communist02/agile#features)
*   [Sample screenshots](https://github.com/Communist02/agile#sample-screenshots)
*   [Build instructions](https://github.com/Communist02/agile#build-instructions)

Features
--------
*   Allows to browse and modify any rclone remote, including encrypted ones
*   Uses same configuration file as rclone, no extra configuration required
*   Lists files hierarchically with file name, size and modify date
*   All rclone commands are executed asynchronously, no freezing GUI
*   File hierarchy is lazily cached in memory, for faster traversal of folders
*   Allows to upload, download, create new folders, rename or delete files and folders
*   Allows to calculate size of remote
*   Drag & drop support for dragging files from local file explorer for uploading
*   Mount and unmount folders on Linux and Windows (for Windows requires [winfsp](http://www.secfs.net/winfsp/))
*   Optionally minimizes to tray
*   Supports merging remotes into one remote with configuration settings(where files will upload after drag and drop or paste etc.)
*   Supports creating servers for your remotes, if you don't have one.
*   Multiple themes for all platforms

Sample screenshots
-------------------
**main_screen** 
<p align="center">
<img src="https://github.com/user-attachments/assets/712ba579-4fc7-44b5-85c8-77789b2d9b0d" width="100%" />

**remote_screens**
<p align="center">
<img src="https://github.com/user-attachments/assets/f7987752-be9a-4af7-aaf7-a65365de339f" width="100%" />

**remote_options**
<p align="center">
<img src="https://github.com/user-attachments/assets/8bb680de-2fa5-45e0-a47f-12821dc82643" width="100%" />

**file_options**
<p align="center">
<img src="https://github.com/user-attachments/assets/fb47b52e-6acb-4f5c-a439-dabd7d725b9d" width="100%" />

**serve_options**
<p align="center">
<img src="https://github.com/user-attachments/assets/b7d7527e-e45c-4e04-b22b-2bed4bf2760b" width="100%" />

**style_options**
<p align="center">
<img src="https://github.com/user-attachments/assets/d8768886-e29e-4ccf-844d-40b01f73bbb2" width="100%" />

Build Instructions
-------------------
### Linux
1.  Install dependencies for your particular distribution:

### Windows
1. Install everything from requirements.txt
2. Install rclone.exe from https://rclone.org/
2. Run main.py in IDE (Vs code, Pycharm, etc.)
