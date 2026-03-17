# BosLab Pulsometr

Python 3.14 + pygame-ce + bleak desktop app for Windows 10/11.

## Run

```bash
python -m pip install -r requirements.txt
python main.py
```

## Build `.exe`

PowerShell:

```powershell
./build.ps1
```

Settings are persisted near executable/script:
- `bos_settings.json`
- `bos_record.json`
