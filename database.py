import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'vaccination.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS regions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS economic_phases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS countries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            region_id INTEGER,
            economic_phase_id INTEGER,
            population INTEGER,
            FOREIGN KEY (region_id) REFERENCES regions(id),
            FOREIGN KEY (economic_phase_id) REFERENCES economic_phases(id)
        );

        CREATE TABLE IF NOT EXISTS antigens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vaccination_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            antigen_id INTEGER,
            year INTEGER,
            coverage_pct REAL,
            target_pct REAL DEFAULT 90,
            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (antigen_id) REFERENCES antigens(id)
        );

        CREATE TABLE IF NOT EXISTS disease_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS disease_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_id INTEGER,
            disease_id INTEGER,
            year INTEGER,
            cases INTEGER,
            cases_per_100k REAL,
            FOREIGN KEY (country_id) REFERENCES countries(id),
            FOREIGN KEY (disease_id) REFERENCES disease_types(id)
        );

        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            student_number TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS personas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            age INTEGER,
            description TEXT NOT NULL,
            goals TEXT NOT NULL,
            frustrations TEXT NOT NULL
        );
    """)

    # Regions
    regions = [
        'Western Europe', 'Eastern Europe', 'North America', 'South America',
        'Sub-Saharan Africa', 'North Africa', 'South Asia', 'East Asia',
        'Southeast Asia', 'Middle East', 'Oceania', 'Central Asia'
    ]
    for r in regions:
        cur.execute("INSERT OR IGNORE INTO regions (name) VALUES (?)", (r,))

    # Economic phases
    phases = ['Developed', 'Developing', 'Economy in Transition', 'Least Developed']
    for p in phases:
        cur.execute("INSERT OR IGNORE INTO economic_phases (name) VALUES (?)", (p,))

    # Countries
    countries_data = [
        ('Australia', 'Oceania', 'Developed', 25687041),
        ('Belgium', 'Western Europe', 'Developed', 11555997),
        ('Brazil', 'South America', 'Developing', 215313498),
        ('Canada', 'North America', 'Developed', 38645670),
        ('China', 'East Asia', 'Developing', 1412600000),
        ('Colombia', 'South America', 'Developing', 51874024),
        ('Egypt', 'North Africa', 'Developing', 103476161),
        ('Ethiopia', 'Sub-Saharan Africa', 'Least Developed', 117876227),
        ('France', 'Western Europe', 'Developed', 68042591),
        ('Germany', 'Western Europe', 'Developed', 84270625),
        ('Ghana', 'Sub-Saharan Africa', 'Developing', 32395450),
        ('India', 'South Asia', 'Developing', 1417173173),
        ('Indonesia', 'Southeast Asia', 'Developing', 277534122),
        ('Iran', 'Middle East', 'Developing', 87923432),
        ('Italy', 'Western Europe', 'Developed', 60360000),
        ('Japan', 'East Asia', 'Developed', 125700000),
        ('Kazakhstan', 'Central Asia', 'Economy in Transition', 19196000),
        ('Kenya', 'Sub-Saharan Africa', 'Developing', 55864655),
        ('Mali', 'Sub-Saharan Africa', 'Least Developed', 22414000),
        ('Mexico', 'North America', 'Developing', 128972439),
        ('Mozambique', 'Sub-Saharan Africa', 'Least Developed', 32163000),
        ('Myanmar', 'Southeast Asia', 'Least Developed', 54179000),
        ('Nepal', 'South Asia', 'Least Developed', 29674920),
        ('Netherlands', 'Western Europe', 'Developed', 17590672),
        ('Nigeria', 'Sub-Saharan Africa', 'Developing', 218541000),
        ('Pakistan', 'South Asia', 'Developing', 231402117),
        ('Philippines', 'Southeast Asia', 'Developing', 113880328),
        ('Poland', 'Eastern Europe', 'Economy in Transition', 37654247),
        ('Romania', 'Eastern Europe', 'Economy in Transition', 19237691),
        ('Russia', 'Eastern Europe', 'Economy in Transition', 145478097),
        ('South Africa', 'Sub-Saharan Africa', 'Developing', 60756135),
        ('South Korea', 'East Asia', 'Developed', 51745000),
        ('Spain', 'Western Europe', 'Developed', 47431256),
        ('Sudan', 'North Africa', 'Least Developed', 44909353),
        ('Sweden', 'Western Europe', 'Developed', 10452326),
        ('Switzerland', 'Western Europe', 'Developed', 8738791),
        ('Tanzania', 'Sub-Saharan Africa', 'Least Developed', 63298550),
        ('Thailand', 'Southeast Asia', 'Developing', 71601103),
        ('Turkey', 'Middle East', 'Economy in Transition', 84680273),
        ('Uganda', 'Sub-Saharan Africa', 'Developing', 47123531),
        ('Ukraine', 'Eastern Europe', 'Economy in Transition', 43531422),
        ('United Kingdom', 'Western Europe', 'Developed', 67026292),
        ('United States', 'North America', 'Developed', 331893745),
        ('Uzbekistan', 'Central Asia', 'Economy in Transition', 35300000),
        ('Vietnam', 'Southeast Asia', 'Developing', 97468029),
        ('Afghanistan', 'South Asia', 'Least Developed', 40099462),
        ('Chad', 'Sub-Saharan Africa', 'Least Developed', 17414000),
        ('Bolivia', 'South America', 'Developing', 12080000),
        ('Peru', 'South America', 'Developing', 33035304),
        ('Argentina', 'South America', 'Developing', 46044703),
    ]

    region_map = {r[0]: cur.execute("SELECT id FROM regions WHERE name=?", (r[0],)).fetchone()[0]
                  for r in [(reg,) for reg in regions]}
    phase_map = {p[0]: cur.execute("SELECT id FROM economic_phases WHERE name=?", (p[0],)).fetchone()[0]
                 for p in [(ph,) for ph in phases]}

    for name, region, phase, pop in countries_data:
        cur.execute("INSERT OR IGNORE INTO countries (name, region_id, economic_phase_id, population) VALUES (?,?,?,?)",
                    (name, region_map[region], phase_map[phase], pop))

    # Antigens
    antigens = [
        ('MCV1', 'Measles-Containing Vaccine 1st Dose'),
        ('MCV2', 'Measles-Containing Vaccine 2nd Dose'),
        ('DTP1', 'Diphtheria-Tetanus-Pertussis 1st Dose'),
        ('DTP3', 'Diphtheria-Tetanus-Pertussis 3rd Dose'),
        ('BCG', 'Bacillus Calmette-Guérin (Tuberculosis)'),
        ('POL3', 'Polio 3rd Dose'),
        ('HepB3', 'Hepatitis B 3rd Dose'),
        ('RCV1', 'Rubella-Containing Vaccine 1st Dose'),
    ]
    for code, fname in antigens:
        cur.execute("INSERT OR IGNORE INTO antigens (code, full_name) VALUES (?,?)", (code, fname))

    # Disease types
    diseases = ['Measles', 'Rubella', 'Diphtheria', 'Pertussis', 'Polio', 'Hepatitis B', 'Tuberculosis']
    for d in diseases:
        cur.execute("INSERT OR IGNORE INTO disease_types (name) VALUES (?)", (d,))

    conn.commit()

    # Generate vaccination data
    import random
    random.seed(42)

    all_countries = cur.execute("SELECT id, name, economic_phase_id FROM countries").fetchall()
    all_antigens = cur.execute("SELECT id FROM antigens").fetchall()
    phase_ids = cur.execute("SELECT id, name FROM economic_phases").fetchall()
    phase_id_map = {r['name']: r['id'] for r in phase_ids}

    base_coverage = {
        'Developed': (88, 99),
        'Developing': (60, 90),
        'Economy in Transition': (72, 94),
        'Least Developed': (40, 75),
    }
    phase_name_map = {r['id']: r['name'] for r in phase_ids}

    for country in all_countries:
        pname = phase_name_map[country['economic_phase_id']]
        lo, hi = base_coverage[pname]
        for antigen in all_antigens:
            base = random.uniform(lo, hi)
            for year in range(2000, 2024):
                trend = (year - 2000) * random.uniform(-0.1, 0.5)
                cov = min(99.9, max(5.0, base + trend + random.uniform(-3, 3)))
                cur.execute(
                    "INSERT INTO vaccination_data (country_id, antigen_id, year, coverage_pct, target_pct) VALUES (?,?,?,?,90)",
                    (country['id'], antigen['id'], year, round(cov, 1))
                )

    # Generate disease data
    all_diseases = cur.execute("SELECT id, name FROM disease_types").fetchall()
    disease_base = {
        'Measles': {'Developed': (0.01, 0.5), 'Developing': (0.5, 8.0), 'Economy in Transition': (0.1, 2.0), 'Least Developed': (3.0, 15.0)},
        'Rubella': {'Developed': (0.01, 0.3), 'Developing': (0.2, 5.0), 'Economy in Transition': (0.1, 1.5), 'Least Developed': (1.0, 8.0)},
        'Diphtheria': {'Developed': (0.001, 0.05), 'Developing': (0.05, 1.0), 'Economy in Transition': (0.01, 0.3), 'Least Developed': (0.2, 3.0)},
        'Pertussis': {'Developed': (0.5, 5.0), 'Developing': (1.0, 10.0), 'Economy in Transition': (0.5, 4.0), 'Least Developed': (2.0, 20.0)},
        'Polio': {'Developed': (0.0, 0.01), 'Developing': (0.0, 0.5), 'Economy in Transition': (0.0, 0.1), 'Least Developed': (0.0, 1.0)},
        'Hepatitis B': {'Developed': (0.5, 3.0), 'Developing': (2.0, 15.0), 'Economy in Transition': (1.0, 8.0), 'Least Developed': (5.0, 25.0)},
        'Tuberculosis': {'Developed': (2.0, 10.0), 'Developing': (50.0, 300.0), 'Economy in Transition': (20.0, 80.0), 'Least Developed': (100.0, 500.0)},
    }

    for country in all_countries:
        pname = phase_name_map[country['economic_phase_id']]
        pop = cur.execute("SELECT population FROM countries WHERE id=?", (country['id'],)).fetchone()[0]
        for disease in all_diseases:
            dname = disease['name']
            lo, hi = disease_base[dname][pname]
            base_rate = random.uniform(lo, hi)
            for year in range(2000, 2024):
                trend = (year - 2000) * random.uniform(-0.05, 0.02)
                rate = max(0.0, base_rate + trend + random.uniform(-lo*0.3, lo*0.3))
                cases = int(rate * pop / 100000)
                cur.execute(
                    "INSERT INTO disease_data (country_id, disease_id, year, cases, cases_per_100k) VALUES (?,?,?,?,?)",
                    (country['id'], disease['id'], year, cases, round(rate, 2))
                )

    # Team members
    team = [
        ('Nguyen Van An', 'S12345678'),
        ('Tran Thi Bich', 'S12345679'),
        ('Le Minh Cuong', 'S12345680'),
        ('Pham Thi Dung', 'S12345681'),
    ]
    for name, snum in team:
        cur.execute("INSERT OR IGNORE INTO team_members (name, student_number) VALUES (?,?)", (name, snum))

    # Personas
    personas = [
        ('Dr. Sarah Mitchell', 'Public Health Researcher', 42,
         'A senior epidemiologist at a national health institute who analyses global vaccination trends to inform policy decisions.',
         'Access detailed country-level vaccination data; compare regional herd immunity; identify at-risk populations.',
         'Data buried in spreadsheets; lack of filtering by antigen type; no year-on-year comparison.'),
        ('James Okonkwo', 'Policy Maker', 55,
         'A government health minister in a developing nation seeking evidence to support vaccine funding proposals.',
         'Understand economic-status breakdown of infection rates; quick high-level summaries; clear visualisations.',
         'Overly technical language; no economic-phase grouping; too many clicks to reach key statistics.'),
        ('Amara Singh', 'Undergraduate Student', 21,
         'A public-health student researching the relationship between vaccination coverage and disease incidence for a thesis.',
         'Find historical trends; explore data by disease type and region; download findings for academic use.',
         'No clear data source citation; hard to find specific years; no summary statistics.'),
        ('Carlos Fernandez', 'Journalist', 34,
         'A health journalist writing an article on global vaccine equity and countries leading vaccination improvement.',
         'Quickly find top-performing and worst-performing countries; see infection rates vs vaccination coverage.',
         'Raw numbers without context; no visual snapshots; slow page loads when browsing large datasets.'),
    ]
    for name, role, age, desc, goals, frust in personas:
        cur.execute(
            "INSERT OR IGNORE INTO personas (name, role, age, description, goals, frustrations) VALUES (?,?,?,?,?,?)",
            (name, role, age, desc, goals, frust)
        )

    conn.commit()
    conn.close()
    print("Database initialised successfully.")

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
