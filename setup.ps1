param([string]$Username="binit-js",[string]$Name="Binit Kumar Nayak",[string]$Image=".\me.jpg")
$ErrorActionPreference="Stop"
python -m pip install -r requirements.txt
python scripts/dotify.py $Image -o assets/portrait --cols 100 --equalize --detail 0.5 --color
python scripts/radar.py --data assets/skills.json -o assets/radar
python scripts/radar.py --github $Username -o assets/radar-langs --limit 7 --values --curve 0.4 --exclude "shell,makefile,dockerfile,batchfile,procfile"
python scripts/cards.py --user $Username --out assets
Write-Host "Generated profile assets. Review README.md and preview.html."
