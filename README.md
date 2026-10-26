# ScholarScore

ScholarScore is a blue-and-white college planning web app prototype for the
Congressional App Challenge. Students create a profile, receive a transparent
0–100 student score, and compare that score with sample college benchmarks.

## What the project teaches

- HTML and CSS frontend design
- JavaScript events, fetch requests, and DOM updates
- Python and Flask backend development
- JSON data files
- APIs and environment variables
- Introductory NLP-style text analysis
- Transparent scoring models
- Responsible AI and data limitations
- Optional Beautiful Soup web-scraping structure

## Important limitation

The current app does **not** calculate a real admission probability. It produces
an educational fit estimate using sample data and a visible weighted formula.
Real admissions decisions depend on institutional priorities, essays,
recommendations, course availability, demographics, intended major, and many
other factors.

## Run the app in VS Code

### 1. Open the folder

Open the `ScholarScore` folder in VS Code.

### 2. Open the terminal

In VS Code, click:

`Terminal` → `New Terminal`

### 3. Create a virtual environment

Mac:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 4. Install the libraries

```bash
pip install -r requirements.txt
```

### 5. Start the website

Mac:

```bash
python3 app.py
```

Windows:

```bash
python app.py
```

### 6. Open the local website

Open this address in a browser:

```text
http://127.0.0.1:5000
```

## Folder structure

```text
ScholarScore/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── data/
│   ├── colleges.json
│   └── sources.txt
├── scrapers/
│   └── sample_scraper.py
├── static/
│   ├── script.js
│   └── style.css
└── templates/
    └── index.html
```

## How the scoring model works

The student score combines:

- Academics: 55%
- Extracurricular involvement: 20%
- Awards and achievements: 10%
- Essay analysis: 15%

The essay feature uses a basic NLP-style approach. It checks word count and
action words such as “built,” “created,” “led,” and “improved.”

The college comparison uses:

- Student score compared with the college benchmark
- GPA alignment
- SAT alignment

Because every formula is visible in `app.py`, Aarna can explain exactly how the
system works during judging.

## Safe API-key setup

Copy `.env.example` and rename it `.env`. Add keys only to `.env`.

Never place real API keys in:

- HTML
- JavaScript
- GitHub
- screenshots
- presentation slides

A future version can connect to the College Scorecard API or Google Custom
Search. The API call should happen in Python, not browser JavaScript, so the
private key is not exposed.

## Suggested next upgrades

1. Add login and saved profiles.
2. Replace sample data with verified College Scorecard data.
3. Add intended-major competitiveness.
4. Add recommendation categories for improvement.
5. Train a small explainable machine-learning model on a legally usable dataset.
6. Add charts showing score breakdowns.
7. Add a source citation to every college statistic.
8. Add accessibility testing and mobile refinements.
