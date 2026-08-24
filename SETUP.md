# Setup

This is the complete starter folder for Binit Kumar Nayak's GitHub profile README system, based on the supplied PDF's architecture and customized with the README information provided in chat.

## 1. Repository

Create a public GitHub repository named exactly `binit-js`.

## 2. Photo

Put your photo at `me.jpg` in the project root.

## 3. Install and generate

```powershell
python -m pip install -r requirements.txt
python scripts/dotify.py me.jpg -o assets/portrait --cols 100 --equalize --detail 0.5 --color
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github binit-js -o assets/radar-langs --limit 7 --values --curve 0.4 --exclude "shell,makefile,dockerfile,batchfile,procfile"
python scripts/cards.py --user binit-js --out assets
```

Or on Windows:

```powershell
.\setup.ps1
```

## 4. Projects

Edit `assets/projects.json` and replace `PROJECT_ONE` through `PROJECT_FOUR` with your actual repository names. Also replace the four links in `README.md`.

## 5. GitHub Actions

Set repository Actions permissions to **Read and write**. Add the `METRICS_TOKEN` repository secret as described by the supplied PDF. The guide specifies a GitHub classic personal access token with `read:user`; add `repo` only when private contribution totals are required.

## 6. First run

Push the repository, open Actions, and manually run Metrics, Contribution Snake, and Charts and Cards once. After that the schedules refresh them automatically.
