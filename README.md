# Snipping Tool Clone

A feature-rich desktop screen capture application built with Python and PyQt6. This tool provides a modern user interface that replicates the core functionality of the native Windows Snipping Tool, complete with automatic dark and light theme support based on system preferences.

## Download
You can download the latest compiled executable for Windows here:
[Download Snipping Tool v1.0.0](https://github.com/polkboban/snippingtool/releases/latest)

*Note: Extract the .zip file and run SnippingTool.exe. No installation required!*

## Features

* **Capture Modes:**
    * **Rectangle Mode:** Click and drag to capture a specific rectangular area.
    * **Free-form Mode:** Draw an arbitrary shape to capture custom areas.
    * **Window Mode:** Automatically highlight and capture specific application windows using Windows APIs.
    * **Fullscreen Mode:** Capture the entire screen immediately.
* **Capture Delay:** Set a timer for 3, 5, or 10 seconds before the capture begins.
* **Preview Dialog:** Review your captured snip in a dedicated preview window before saving or copying.
* **Quick Actions:** Save the capture as a PNG file or copy it directly to your system clipboard.
* **System Theming:** Automatically adapts to Windows light or dark mode settings.

## Prerequisites

* Python 3.x
* Required Python packages:
    * `PyQt6`
    * `Pillow`
    * `pywin32`

## Installation

1. Clone the repository to your local machine.
2. Install the required dependencies using pip:
    ```bash
    pip install PyQt6 Pillow pywin32
    ```

## Usage

Run the main application script:

```bash
python main.py