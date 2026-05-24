=======================================================
  VaxInsight — Preventable Infectious Diseases App
  COSC3107 | COSC3108 — Studio Project 2025
=======================================================

HOW TO RUN
----------
1. Install Flask:
   pip install flask

2. Run the app:
   python app.py

3. Open in browser:
   http://localhost:5000

PAGES
-----
  /                → Level 1A  — Dashboard (Landing Page)
  /mission         → Level 1B  — Mission Statement & Personas
  /vaccination     → Level 2A  — Vaccination Rates by Country/Region
  /infection       → Level 2B  — Infection Data by Economic Status
  /top-improvers   → Level 3A  — Countries with Biggest Improvement
  /above-average   → Level 3B  — Countries with Above-Average Infection Rate

DATABASE
--------
The file vaccination.db is a sample SQLite database with:
  - 50 countries across 12 regions
  - 4 economic phases (Developed, Developing, Economy in Transition, Least Developed)
  - 8 antigens (MCV1, MCV2, DTP1, DTP3, BCG, POL3, HepB3, RCV1)
  - 7 disease types (Measles, Rubella, Diphtheria, Pertussis, Polio, Hepatitis B, Tuberculosis)
  - Data from year 2000 to 2023

To replace with real data:
  - Edit database.py to match your real schema
  - Update the SQL queries in app.py accordingly

FILE STRUCTURE
--------------
  app.py                     ← Flask routes (all 6 pages)
  database.py                ← Database init + sample data
  vaccination.db             ← SQLite database (auto-generated)
  static/
    style.css                ← All styles
    app.js                   ← Progress bar animations
  templates/
    base.html                ← Shared layout + sidebar nav
    landing.html             ← Level 1A
    mission.html             ← Level 1B
    vaccination.html         ← Level 2A
    infection.html           ← Level 2B
    top_improvers.html       ← Level 3A
    above_average.html       ← Level 3B
