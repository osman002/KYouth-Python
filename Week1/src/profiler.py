import sqlite3

# simple function to run SQL queries against the SQLite database
def run_sql(db_path, query):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        return cursor.fetchall()
    

def run_data_profile(db_path):

    # check if database exists before running profiLW
    if not db_path.exists():
        print(f"❌ Database not found at {db_path}")
        return
    
    # run SQL queries to gather profiling metrics
    all_data = run_sql(db_path, "SELECT * FROM jobs")
    missing_data_job_title = run_sql(db_path, "SELECT * FROM jobs WHERE job_title IS NULL")
    missing_data_company = run_sql(db_path, "SELECT * FROM jobs WHERE company IS NULL")
    missing_data_description = run_sql(db_path, "SELECT * FROM jobs WHERE description IS NULL")
    average_description_length = int(run_sql(db_path, "SELECT AVG(LENGTH(description)) FROM jobs")[0][0] or 0)
    shortest = run_sql(db_path, "SELECT source_id,job_title, LENGTH(description) FROM jobs ORDER BY LENGTH(description) ASC LIMIT 1")
    longest = run_sql(db_path, "SELECT source_id, job_title, LENGTH(description) FROM jobs ORDER BY LENGTH(description) DESC LIMIT 1")

    # print profiling report
    print(f"--- 🔍 DATA QUALITY REPORT ---")
    print(f"📈 Total Records: {len(all_data)}")
    print(f"❓ Missing Values -> job_title: {len(missing_data_job_title)}, company: {len(missing_data_company)}, description: {len(missing_data_description)}")
    print(f"📝 Avg Description Length: {average_description_length}")
    print(f"⚠️  Shortest Description: {shortest[0][2]} chars")
    print(f"   ↳ source_id: {shortest[0][0]} | job_title: {shortest[0][1]}")
    print(f"⚠️  Longest Description: {longest[0][2]} chars")
    print(f"   ↳ source_id: {longest[0][0]} | job_title: {longest[0][1]}")
