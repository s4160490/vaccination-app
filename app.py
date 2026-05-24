from flask import Flask, render_template, request, jsonify
from database import get_db, init_db
import os

app = Flask(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────

def db_stats():
    db = get_db()
    stats = {}
    stats['country_count']  = db.execute("SELECT COUNT(*) FROM countries").fetchone()[0]
    stats['year_min']       = db.execute("SELECT MIN(year) FROM vaccination_data").fetchone()[0]
    stats['year_max']       = db.execute("SELECT MAX(year) FROM vaccination_data").fetchone()[0]
    stats['disease_count']  = db.execute("SELECT COUNT(*) FROM disease_types").fetchone()[0]
    stats['total_vacc_records'] = db.execute("SELECT COUNT(*) FROM vaccination_data").fetchone()[0]
    stats['total_cases']    = db.execute("SELECT SUM(cases) FROM disease_data").fetchone()[0]
    db.close()
    return stats

# ── Level 1A – Landing Page ───────────────────────────────────────────────────

@app.route('/')
def landing():
    db = get_db()
    s = db_stats()

    # Fact 1: timeframe
    fact_timeframe = f"{s['year_min']} – {s['year_max']}"

    # Fact 2: countries tracked
    fact_countries = f"{s['country_count']:,}"

    # Fact 3: total vaccine records
    fact_records = f"{s['total_vacc_records']:,}"

    # Fact 4: list of diseases
    diseases = [r['name'] for r in db.execute("SELECT name FROM disease_types ORDER BY name").fetchall()]

    # Hero stat: average global vaccination coverage (latest year)
    avg_cov = db.execute("""
        SELECT ROUND(AVG(coverage_pct), 1) as avg
        FROM vaccination_data
        WHERE year = (SELECT MAX(year) FROM vaccination_data)
    """).fetchone()['avg']

    # Regional herd immunity snapshot (latest year, MCV2)
    regional = db.execute("""
        SELECT r.name as region,
               ROUND(AVG(v.coverage_pct),1) as avg_cov
        FROM vaccination_data v
        JOIN countries c ON v.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN antigens a ON v.antigen_id = a.id
        WHERE a.code='MCV2' AND v.year=(SELECT MAX(year) FROM vaccination_data)
        GROUP BY r.name
        ORDER BY avg_cov DESC
    """).fetchall()

    db.close()
    return render_template('landing.html',
        fact_timeframe=fact_timeframe,
        fact_countries=fact_countries,
        fact_records=fact_records,
        diseases=diseases,
        avg_cov=avg_cov,
        regional=regional,
        total_cases=f"{s['total_cases']:,}"
    )

# ── Level 1B – Mission Statement ─────────────────────────────────────────────

@app.route('/mission')
def mission():
    db = get_db()
    personas  = db.execute("SELECT * FROM personas").fetchall()
    team      = db.execute("SELECT * FROM team_members").fetchall()
    db.close()
    return render_template('mission.html', personas=personas, team=team)

# ── Level 2A – Vaccination Rates by Country/Region ───────────────────────────

@app.route('/vaccination')
def vaccination():
    db = get_db()
    regions  = [r['name'] for r in db.execute("SELECT name FROM regions ORDER BY name").fetchall()]
    countries= [r['name'] for r in db.execute("SELECT name FROM countries ORDER BY name").fetchall()]
    antigens = db.execute("SELECT code, full_name FROM antigens ORDER BY code").fetchall()
    years    = list(range(2023, 1999, -1))

    # defaults
    sel_antigen = request.args.get('antigen', 'MCV2')
    sel_year    = int(request.args.get('year', 2022))
    sel_region  = request.args.get('region', '')
    sel_country = request.args.get('country', '')

    # Table 1: countries meeting ≥ 90% target
    q1 = """
        SELECT c.name as country, r.name as region,
               ROUND(v.coverage_pct,1) as coverage,
               ROUND(v.coverage_pct / v.target_pct * 100, 1) as pct_of_target,
               v.target_pct
        FROM vaccination_data v
        JOIN countries c ON v.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN antigens a ON v.antigen_id = a.id
        WHERE a.code=? AND v.year=?
          AND v.coverage_pct >= v.target_pct
    """
    params1 = [sel_antigen, sel_year]
    if sel_region:
        q1 += " AND r.name=?"
        params1.append(sel_region)
    if sel_country:
        q1 += " AND c.name=?"
        params1.append(sel_country)
    q1 += " ORDER BY v.coverage_pct DESC"
    table1 = db.execute(q1, params1).fetchall()

    # Table 2: per region, count of countries meeting 90%
    q2 = """
        SELECT r.name as region,
               COUNT(*) as countries_met,
               ROUND(AVG(v.coverage_pct),1) as avg_coverage
        FROM vaccination_data v
        JOIN countries c ON v.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN antigens a ON v.antigen_id = a.id
        WHERE a.code=? AND v.year=? AND v.coverage_pct >= v.target_pct
        GROUP BY r.name
        ORDER BY countries_met DESC
    """
    table2 = db.execute(q2, [sel_antigen, sel_year]).fetchall()

    db.close()
    return render_template('vaccination.html',
        regions=regions, countries=countries, antigens=antigens, years=years,
        sel_antigen=sel_antigen, sel_year=sel_year,
        sel_region=sel_region, sel_country=sel_country,
        table1=table1, table2=table2
    )

# ── Level 2B – Infection by Economic Status ───────────────────────────────────

@app.route('/infection')
def infection():
    db = get_db()
    phases   = [r['name'] for r in db.execute("SELECT name FROM economic_phases ORDER BY name").fetchall()]
    diseases = [r['name'] for r in db.execute("SELECT name FROM disease_types ORDER BY name").fetchall()]
    years    = list(range(2023, 1999, -1))

    sel_phase   = request.args.get('phase', 'Developing')
    sel_disease = request.args.get('disease', 'Measles')
    sel_year    = int(request.args.get('year', 2022))
    sort_col    = request.args.get('sort', 'cases_per_100k')
    sort_dir    = request.args.get('dir', 'DESC')

    allowed_sorts = ['country', 'cases_per_100k', 'cases']
    if sort_col not in allowed_sorts:
        sort_col = 'cases_per_100k'
    if sort_dir not in ('ASC', 'DESC'):
        sort_dir = 'DESC'

    # Main table: country-level infection by economic phase
    table = db.execute(f"""
        SELECT c.name as country,
               ep.name as economic_phase,
               d.name as disease,
               dd.year,
               dd.cases,
               dd.cases_per_100k
        FROM disease_data dd
        JOIN countries c ON dd.country_id = c.id
        JOIN economic_phases ep ON c.economic_phase_id = ep.id
        JOIN disease_types d ON dd.disease_id = d.id
        WHERE ep.name=? AND d.name=? AND dd.year=?
        ORDER BY {sort_col} {sort_dir}
    """, [sel_phase, sel_disease, sel_year]).fetchall()

    # Summary: total cases per economic phase
    summary = db.execute("""
        SELECT ep.name as economic_phase,
               SUM(dd.cases) as total_cases,
               ROUND(AVG(dd.cases_per_100k),2) as avg_rate
        FROM disease_data dd
        JOIN countries c ON dd.country_id = c.id
        JOIN economic_phases ep ON c.economic_phase_id = ep.id
        JOIN disease_types d ON dd.disease_id = d.id
        WHERE d.name=? AND dd.year=?
        GROUP BY ep.name
        ORDER BY total_cases DESC
    """, [sel_disease, sel_year]).fetchall()

    db.close()
    return render_template('infection.html',
        phases=phases, diseases=diseases, years=years,
        sel_phase=sel_phase, sel_disease=sel_disease, sel_year=sel_year,
        sort_col=sort_col, sort_dir=sort_dir,
        table=table, summary=summary
    )

# ── Level 3A – Top Improvers ──────────────────────────────────────────────────

@app.route('/top-improvers')
def top_improvers():
    db = get_db()
    antigens = db.execute("SELECT code, full_name FROM antigens ORDER BY code").fetchall()
    years    = list(range(2023, 2000, -1))

    sel_antigen   = request.args.get('antigen', 'MCV2')
    sel_start     = int(request.args.get('start_year', 2010))
    sel_end       = int(request.args.get('end_year', 2022))
    sel_n         = int(request.args.get('top_n', 10))

    if sel_start >= sel_end:
        sel_start = sel_end - 1

    results = db.execute("""
        WITH start_cov AS (
            SELECT v.country_id,
                   AVG(v.coverage_pct) as cov
            FROM vaccination_data v
            JOIN antigens a ON v.antigen_id = a.id
            WHERE a.code = ? AND v.year = ?
            GROUP BY v.country_id
        ),
        end_cov AS (
            SELECT v.country_id,
                   AVG(v.coverage_pct) as cov
            FROM vaccination_data v
            JOIN antigens a ON v.antigen_id = a.id
            WHERE a.code = ? AND v.year = ?
            GROUP BY v.country_id
        )
        SELECT c.name as country,
               r.name as region,
               ep.name as economic_phase,
               ROUND(s.cov, 1) as start_coverage,
               ROUND(e.cov, 1) as end_coverage,
               ROUND(e.cov - s.cov, 2) as improvement,
               ROUND(((e.cov - s.cov) / NULLIF(s.cov, 0)) * 100, 1) as pct_change
        FROM start_cov s
        JOIN end_cov e ON s.country_id = e.country_id
        JOIN countries c ON s.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN economic_phases ep ON c.economic_phase_id = ep.id
        WHERE e.cov > s.cov
        ORDER BY improvement DESC
        LIMIT ?
    """, [sel_antigen, sel_start, sel_antigen, sel_end, sel_n]).fetchall()

    # global average improvement for context
    global_avg = db.execute("""
        WITH start_cov AS (
            SELECT v.country_id, AVG(v.coverage_pct) as cov
            FROM vaccination_data v JOIN antigens a ON v.antigen_id=a.id
            WHERE a.code=? AND v.year=? GROUP BY v.country_id
        ),
        end_cov AS (
            SELECT v.country_id, AVG(v.coverage_pct) as cov
            FROM vaccination_data v JOIN antigens a ON v.antigen_id=a.id
            WHERE a.code=? AND v.year=? GROUP BY v.country_id
        )
        SELECT ROUND(AVG(e.cov - s.cov), 2) as avg_improvement
        FROM start_cov s JOIN end_cov e ON s.country_id=e.country_id
    """, [sel_antigen, sel_start, sel_antigen, sel_end]).fetchone()

    db.close()
    return render_template('top_improvers.html',
        antigens=antigens, years=years,
        sel_antigen=sel_antigen, sel_start=sel_start,
        sel_end=sel_end, sel_n=sel_n,
        results=results,
        global_avg=global_avg['avg_improvement'] if global_avg else 0
    )

# ── Level 3B – Above Average Infection Rate ───────────────────────────────────

@app.route('/above-average')
def above_average():
    db = get_db()
    diseases = [r['name'] for r in db.execute("SELECT name FROM disease_types ORDER BY name").fetchall()]
    years    = list(range(2023, 1999, -1))

    sel_disease = request.args.get('disease', 'Measles')
    sel_year    = int(request.args.get('year', 2022))

    # Global average infection rate
    global_row = db.execute("""
        SELECT ROUND(AVG(dd.cases_per_100k), 4) as global_rate,
               SUM(dd.cases) as global_cases
        FROM disease_data dd
        JOIN disease_types d ON dd.disease_id = d.id
        WHERE d.name = ? AND dd.year = ?
    """, [sel_disease, sel_year]).fetchone()

    global_rate  = global_row['global_rate']  or 0
    global_cases = global_row['global_cases'] or 0

    # Countries exceeding global average
    above = db.execute("""
        SELECT c.name as country,
               r.name as region,
               ep.name as economic_phase,
               dd.cases_per_100k,
               dd.cases,
               ROUND(dd.cases_per_100k - ?, 4) as excess_rate,
               ROUND((dd.cases_per_100k / NULLIF(?, 0) - 1) * 100, 1) as pct_above_avg
        FROM disease_data dd
        JOIN disease_types d ON dd.disease_id = d.id
        JOIN countries c ON dd.country_id = c.id
        JOIN regions r ON c.region_id = r.id
        JOIN economic_phases ep ON c.economic_phase_id = ep.id
        WHERE d.name = ? AND dd.year = ?
          AND dd.cases_per_100k > ?
        ORDER BY dd.cases_per_100k DESC
    """, [global_rate, global_rate, sel_disease, sel_year, global_rate]).fetchall()

    # Breakdown of above-average countries by economic phase
    phase_breakdown = db.execute("""
        SELECT ep.name as economic_phase,
               COUNT(*) as country_count,
               ROUND(AVG(dd.cases_per_100k), 2) as avg_rate
        FROM disease_data dd
        JOIN disease_types d ON dd.disease_id = d.id
        JOIN countries c ON dd.country_id = c.id
        JOIN economic_phases ep ON c.economic_phase_id = ep.id
        WHERE d.name = ? AND dd.year = ?
          AND dd.cases_per_100k > ?
        GROUP BY ep.name
        ORDER BY avg_rate DESC
    """, [sel_disease, sel_year, global_rate]).fetchall()

    db.close()
    return render_template('above_average.html',
        diseases=diseases, years=years,
        sel_disease=sel_disease, sel_year=sel_year,
        global_rate=global_rate, global_cases=global_cases,
        above=above, phase_breakdown=phase_breakdown
    )

# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if not os.path.exists('vaccination.db'):
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
