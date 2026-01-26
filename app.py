from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from db_config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

app = Flask(__name__)
app.secret_key = "1a8309ad37ffde4ba90bed9784c99948"

# ---------------- Database Connection ----------------
def get_db_connection():
    return mysql.connector.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB
    )

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT * FROM users WHERE username=%s AND password=%s",
            (username, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid login!")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) AS total FROM projects_import")
    total_projects = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS ongoing FROM projects_import WHERE status='Ongoing'")
    ongoing_projects = cur.fetchone()["ongoing"]

    cur.execute("SELECT COUNT(*) AS completed FROM projects_import WHERE status='Closed'")
    completed_projects = cur.fetchone()["completed"]

    cur.close()
    conn.close()

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        ongoing_projects=ongoing_projects,
        completed_projects=completed_projects
    )

# ---------------- SEARCH / VIEW PROJECTS ----------------
@app.route("/projects", methods=["GET", "POST"])
def search():
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # ---------------- Financial Year Dropdown ----------------
    cur.execute("""
        SELECT MIN(YEAR(mou_start_date)) AS min_year,
               MAX(YEAR(mou_end_date)) AS max_year
        FROM projects_import
        WHERE mou_start_date IS NOT NULL
    """)
    row = cur.fetchone()
    min_year = row["min_year"] or datetime.now().year
    max_year = row["max_year"] or datetime.now().year
    financial_years = [f"{y}-{y+1}" for y in range(min_year, max_year + 1)]

    # ---------------- Base Query ----------------
    query = "SELECT * FROM projects_import WHERE 1=1"
    params = []
    selected_fy = ""

    # ---------------- Dashboard Status Filter ----------------
    status_from_dashboard = request.args.get("status")
    if status_from_dashboard:
        query += " AND status=%s"
        params.append(status_from_dashboard)

    # ---------------- Search Filters (ONLY when POST) ----------------
    if request.method == "POST":
        project_year = request.form.get("project_initiated_year", "").strip()
        thematic = request.form.get("thematic", "").strip()
        erp_code = request.form.get("erp_code", "").strip()
        selected_fy = request.form.get("financial_year", "").strip()

        if project_year:
            query += " AND project_initiated_year=%s"
            params.append(project_year)

        if thematic:
            query += " AND thematic LIKE %s"
            params.append(f"%{thematic}%")

        if erp_code:
            query += " AND erp_code LIKE %s"
            params.append(f"%{erp_code}%")

        if selected_fy:
            fy_start, fy_end = map(int, selected_fy.split("-"))
            fy_start_date = datetime(fy_start, 4, 1).date()
            fy_end_date = datetime(fy_end, 3, 31).date()

            query += """
                AND mou_start_date <= %s
                AND (mou_end_date IS NULL OR mou_end_date >= %s)
            """
            params.extend([fy_end_date, fy_start_date])

    # ---------------- Execute ----------------
    cur.execute(query, params)
    results = cur.fetchall()

    # ---------------- Financial Year Display ----------------
    for row in results:
        start = row["mou_start_date"]
        if start:
            fy_year = start.year if start.month >= 4 else start.year - 1
            row["financial_year"] = f"{fy_year}-{fy_year + 1}"
        else:
            row["financial_year"] = "-"

    cur.close()
    conn.close()

    return render_template(
        "search.html",
        results=results,
        financial_years=financial_years,
        selected_fy=selected_fy,
        from_dashboard=bool(status_from_dashboard)
    )

# ---------------- ADD PROJECT ----------------
@app.route("/add_project", methods=["GET", "POST"])
def add_project():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = (
            request.form.get("erp_code"),
            request.form.get("project_name"),
            request.form.get("project_initiated_year"),
            request.form.get("thematic"),
            request.form.get("ro"),
            request.form.get("mou_start_date") or None,
            request.form.get("mou_end_date") or None,
            request.form.get("donor"),
            request.form.get("budget_2024"),
            request.form.get("total_budget_inr"),
            request.form.get("status"),
            request.form.get("state"),
            request.form.get("districts"),
            request.form.get("block"),
            request.form.get("location"),
            request.form.get("rural_urban")
        )

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO projects_import
            (erp_code, project_name, project_initiated_year, thematic, ro,
             mou_start_date, mou_end_date, donor, budget_2024,
             total_budget_inr, status, state, districts, block,
             location, rural_urban)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, data)
        conn.commit()
        cur.close()
        conn.close()

        flash("Project added successfully!")
        return redirect(url_for("dashboard"))

    return render_template("add_project.html")

# ---------------- EDIT PROJECT ----------------
@app.route("/edit_project/<int:id>", methods=["GET", "POST"])
def edit_project(id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM projects_import WHERE id=%s", (id,))
    project = cur.fetchone()

    if request.method == "POST":
        data = (
            request.form.get("erp_code"),
            request.form.get("project_name"),
            request.form.get("project_initiated_year"),
            request.form.get("thematic"),
            request.form.get("ro"),
            request.form.get("mou_start_date") or None,
            request.form.get("mou_end_date") or None,
            request.form.get("donor"),
            request.form.get("budget_2024"),
            request.form.get("total_budget_inr"),
            request.form.get("status"),
            request.form.get("state"),
            request.form.get("districts"),
            request.form.get("block"),
            request.form.get("location"),
            request.form.get("rural_urban"),
            id
        )

        cur.execute("""
            UPDATE projects_import SET
            erp_code=%s, project_name=%s, project_initiated_year=%s,
            thematic=%s, ro=%s, mou_start_date=%s, mou_end_date=%s,
            donor=%s, budget_2024=%s, total_budget_inr=%s,
            status=%s, state=%s, districts=%s, block=%s,
            location=%s, rural_urban=%s
            WHERE id=%s
        """, data)

        conn.commit()
        cur.close()
        conn.close()

        flash("Project updated successfully!")
        return redirect(url_for("search"))

    cur.close()
    conn.close()
    return render_template("edit_project.html", project=project)

# ---------------- DELETE PROJECT ----------------
@app.route("/delete_project/<int:id>")
def delete_project(id):
    if "username" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects_import WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()

    flash("Project deleted successfully!")
    return redirect(url_for("search"))

# ---------------- Projects by Date ----------------
@app.route("/projects_by_date", methods=["GET", "POST"])
def projects_by_date():
    if "username" not in session:
        return redirect(url_for("login"))

    projects_ongoing = []
    projects_closed = []
    selected_date = ""

    if request.method == "POST":
        selected_date = request.form.get("selected_date")
        if selected_date:
            selected_date_obj = datetime.strptime(selected_date, "%Y-%m-%d").date()
            conn = get_db_connection()
            cur = conn.cursor(dictionary=True)

            # Ongoing projects: status 'Ongoing' + MOU date filter
            cur.execute("""
                SELECT * FROM projects_import
                WHERE status='Ongoing'
                  AND mou_start_date <= %s
                  AND (mou_end_date IS NULL OR mou_end_date >= %s)
                ORDER BY mou_start_date
            """, (selected_date_obj, selected_date_obj))
            projects_ongoing = cur.fetchall()

            # Closed projects: status 'Closed' + MOU end date before selected date
            cur.execute("""
                SELECT * FROM projects_import
                WHERE status='Closed'
                  AND mou_end_date IS NOT NULL
                  AND mou_end_date <= %s
                ORDER BY mou_end_date
            """, (selected_date_obj,))
            projects_closed = cur.fetchall()

            cur.close()
            conn.close()

    return render_template(
        "projects_by_date.html",
        projects_ongoing=projects_ongoing,
        projects_closed=projects_closed,
        selected_date=selected_date
    )

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
