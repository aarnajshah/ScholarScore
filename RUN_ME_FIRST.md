# Run ScholarScore in VS Code

## Windows (Aarna)
Open the **ScholarScore 1.0** folder in VS Code. Then choose **Terminal → New Terminal**.

Run these commands one at a time:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Open the new `.env` file and replace `PASTE_YOUR_KEY_HERE` with Aarna's College Scorecard API key.

Then run:

```powershell
.\.venv\Scripts\python.exe app.py
```

Open the local address shown by Flask, normally `http://127.0.0.1:5000`.

This method intentionally does not require `source` or PowerShell activation.

## Mac
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Put the College Scorecard API key into `.env`, then:

```bash
python app.py
```

## Important
- Do not upload `.env` to GitHub; it contains the private API key.
- `college_model_demo.py` is included as the original teaching/demo script.
- `model_service.py` is the reusable version connected to the Flask website.
- Internet access is required for live College Scorecard API searches.
