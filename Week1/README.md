### Project Description

- This project scrapes and structures job listing data from a popular Malaysian job search website to power a resume gap analyzer. The pipeline ingests raw MHTML files, extracts relevant fields, validates and stores them as structured JSON, and loads them into a SQLite database for further analysis.

### Setup Instructions (if any)

1. Clone the repository
2. Create a `.python-version` file with `3.14`
3. Install dependencies:

```bash
uv python install
uv venv

### Usage
Place your `.mhtml` files inside `data/0_source/` before running.

**Run individual stages:**

```bash
python main.py ingest     # extract HTML from MHTML files → data/1_bronze/
python main.py process    # parse and validate HTML → data/2_silver/
python main.py load       # load JSON into SQLite → data/3_gold/jobs.db
python main.py profile    # run data quality metrics on the database
```

**Run full pipeline:**

```bash
python main.py all
```

### Day 1: The Extractor (Medallion & Lakehouses)

- **What We Did:** Setup folder-based Medallion Architecture `(0_source to 3_gold)`. Extracted raw `.mhtml` files to `1_bronze/`.
- **Industry Context:** Modern data platforms often use ***Data Lakes*** to store raw files before transforming them into structured, query-ready data in a ***Data Warehouse**.*
- **Reflection:** Why is it useful to keep the original raw HTML files instead of directly inserting processed data into the database? What problems become easier to debug or recover from?
- **Answer**: Keeping raw HTML lets us re-extract different fields later without re-scraping the source. If our extractor has a bug or we decide to add new fields, we can just reprocess the bronze layer instead of starting from scratch.

### Day 2: Treatment Plant (ETL vs ELT & Scale)

- **What We Did:** Clean HTML `(transform into 2_silver/)` before database load `(load into 3_gold/)` (ETL).
- **Industry Context:** Cloud platforms ***(Snowflake/BigQuery)*** often store raw data first then transform later ***(ELT)***. Enterprise systems use ***Apache Spark*** to process large amounts of data in parallel instead of one file at a time.
- **Reflection:** Why do cloud systems prefer loading raw data first before cleaning it (ELT)? What problems happen when processing files sequentially, and how does distributed processing help?
- **Answer**: Cloud storage is cheap, so it makes sense to store everything raw first and transform only what you need later. Processing files one by one becomes too slow at scale — distributed tools like Spark split the work across many machines so thousands of files can be processed simultaneously instead of waiting for each one to finish.

### Day 3: The Blueprint & The Vault (Storage & Contracts)

- **What We Did:** Used SQLite as Gold "warehouse" layer. Enforced basic data integrity via idempotency during load.
- **Industry Context:** Production systems often separate databases used for day-to-day application operations ***(OLTP)*** from databases optimized for analytics and reporting ***(OLAP)***. Strict Data Contracts help ensure incomplete or corrupted data does not break dashboards, analytics, or downstream systems.
- **Reflection:** What should happen if an important field like `job_title` disappears? Why fail early instead of silently inserting `nulls` into DB? How does `INSERT OR IGNORE` help prevent duplicate records?
- **Answer**: If `job_title` is missing, the record should be skipped entirely — a job listing without a title is essentially unusable for analysis. Failing early surfaces the problem immediately rather than letting bad data silently corrupt the database and break downstream analysis. `INSERT OR IGNORE` prevents duplicates by checking `source_id` as the primary key — if the record already exists, the insert is skipped rather than creating a duplicate row.

### Day 4: The QA Inspector & Orchestrator (Orchestration & DAGs)

- **What We Did:** `main.py` acts as manual orchestrator, `all` command finalizes sequence
- **Industry Context:** Real-world pipelines usually use orchestration tools like ***Airflow***, which automate execution, retries, scheduling, and dependency management.
- **Reflection:** What happens if `processor.py` crashes halfway? How are automated orchestration tools more reliable than manual retries with Python scripts?
- **Answer**: If `processor.py` crashes halfway, some files get processed and some don't — and we have no automatic way to resume from where it stopped. We'd have to manually figure out which files failed and rerun them. Orchestration tools like Airflow track each task's state, automatically retry failed steps, and only rerun what actually failed — making pipelines far more reliable and recoverable at scale.