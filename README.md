# Sky Fury — Initial Prototype

This repository contains the initial Pygame prototype for "Sky Fury" — a vertical scrolling shooter.

Quick start (Windows + PowerShell + Conda):

1. Create and activate the conda environment:

```powershell
conda create -n sky-fury python=3.10 -y; conda activate sky-fury
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Run the game:

```powershell
python -m src.main
```

Notes:

- This is an initial version. No external art assets are required — the game uses simple drawn placeholders when images are missing.
- `requirements.txt` lists `pygame` as a dependency.
- See `docs/` for design notes and future tasks.
