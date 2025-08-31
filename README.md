# PyGame Shmup Tutorial Implementation

A shoot-'em-up game built with Pygame as a learning project.

This code is my implementation of the fantastic ["Shmup" tutorial series](https://www.youtube.com/playlist?list=PLsk-HSGFjnaH5yghzu7PcOzm9NhsW0Urw) by [KidsCanCode](https://github.com/kidscancode).

The original tutorial code and structure can be found in their [pygame_tutorials](https://github.com/kidscancode/pygame_tutorials) repository.

## How to Run

1.  Ensure you have Python 3 installed.
2.  Clone this repository.
3.  Navigate to the project directory in your terminal.
4.  (Optional but recommended) Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
5.  Install the required dependency:
    ```bash
    pip install -r requirements.txt
    ```
6.  Run the game:
    ```bash
    python Shmup.py
    ```

## Building a Standalone Executable (Windows)

This game can be packaged into a standalone application using [PyInstaller](https://pyinstaller.org/).

1.  Install PyInstaller inside your virtual environment:
    ```bash
    pip install pyinstaller
    ```

2.  Run one of the following build commands from the project's root directory:

    **Option 1: Create a Distribution Folder (Recommended for testing)**
    *Easier to debug if necessary, as all files are in one folder.*
    ```bash
    pyinstaller --onedir --windowed --add-data "img;img" --add-data "snd;snd" --icon=game_icon.ico Shmup.py
    ```
    *The executable (`Shmup.exe`) and all required game files will be created in the `dist/Shmup/` directory. You can distribute the entire `dist/Shmup` folder.*

    **Option 2: Create a Single Executable File**
    *Creates a single, portable `.exe` file for distribution.*
    ```bash
    pyinstaller --onefile --windowed --add-data "img;img" --add-data "snd;snd" --icon=game_icon.ico Shmup.py
    ```
    *A single executable file (`Shmup.exe`) will be created in the `dist/` directory.*

*Note: The `dist/` and `build/` directories, along with any `.spec` file, are excluded from this repository by the `.gitignore` file.*

## Controls
*   **Arrow Keys:** Move your ship
*   **Spacebar:** Fire lasers
*   **Close Button (X):** Quit the game

## Credits & Licensing

- **Tutorial:** [KidsCanCode](https://www.youtube.com/c/Kidscancode)
- **Music:** "Frozen Jam" by tgfcoder (<https://twitter.com/tgfcoder>) licensed under CC-BY-3 (<http://creativecommons.org/licenses/by/3.0/>)
- **Art Assets & Jingles:** From [Kenney.nl](https://kenney.nl/assets) (Public Domain)
- **Sound Effects (`Explosion1.wav`, `Explosion2.wav`, `Laser_Shoot2.wav`)**: Created by [WilliamGoosen](https://github.com/WilliamGoosen) using [Bfxr](https://www.bfxr.net/).
- **Code:** This specific implementation is by [WilliamGoosen](https://github.com/WilliamGoosen), based on the KidsCanCode tutorial.
- **This Project:** Licensed under the MIT License.