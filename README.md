# SpurC++ Editor

## Overview

SpurC++ is a lightweight and beginner-friendly C/C++ code editor built using Python’s tkinter. It offers syntax highlighting, file operations, a compilation console, and a clean retro-style theme inspired by personal customization preferences.

## Motivation

I wanted to create a coding environment that felt personal and unique. Building an editor with a personal theme, inspired by my favorite Football Club, 'Tottenham Hotspur', made the process fun and much more enjoyable. It’s amazing how having a tool that reflects your style can make coding feel more engaging and meaningful. SpurC++ grew out of that motivation—it’s a tool built with simplicity, learning, and personal aesthetics in mind.

## What I Achieved

* Learned how to build a GUI application in Python using `tkinter`
* Implemented syntax highlighting and custom styling from scratch
* Built a functional interface for editing, compiling, and running C/C++ code
* Created an app that I use to learn and write small programs in DSA.  

## Features

* Clean and minimal retro theme with Spurs-inspired color scheme
* Syntax highlighting for C and C++ (keywords, comments, strings, numbers)
* Line number gutter
* Integrated console for compiler feedback
* Compile and run buttons
* Toggleable console
* Status bar showing character count

## Requirements

* Python 3.6 or higher
* Pillow (for icon support, Optional but cool for the aesthetics)
* GCC or G++ compiler in PATH (for compiling C/C++ files). I used MSYS on Windows to provide these tools.
* PyInstaller (for building standalone executables, optional)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/spurcpp-editor.git
   cd spurcpp-editor
   ```

2. Install dependencies:

   ```bash
   pip install pillow (again, optional)
   ```

3. Run the editor:

   ```bash
   python SpurCppEditor.py
   ```

## Building Executable (Windows) - Optional

You can build a standalone .exe using PyInstaller:

```bash
pyinstaller --onefile --windowed --icon=spurslogo.ico SpurCppEditor.py
```

## How I Use It on My PC

I’ve packaged SpurC++ as a Windows .exe file using PyInstaller, with a custom icon. I keep it pinned to my taskbar like any other app. It opens quickly and lets me jump straight into C++ coding without distractions. For me, it’s a comfortable, lightweight environment for focused coding sessions.

## Notes

* Only files up to 10MB are supported.
* Requires gcc or g++ to be installed and added to your system's PATH.
* This editor does not support advanced language features like IntelliSense or debugging.

## Additional Note (For keyboard shortcuts)
If you would be interested in having keyboard shortcuts for the buttons, add the following in the `_bind_events()` method:
```bash
    self.bind("<Control-s>", lambda e: self.save_file()) 
    self.bind("<Control-o>", lambda e: self.open_file())
    self.bind("<Control-r>", lambda e: self.run())
    self.bind("<Control-R>", lambda e: self.compile())
```
You can modify the shortcuts to your convenience.

## License

This project is released under the MIT License.

------

For feedback or suggestions, feel free to open an issue or pull request.
