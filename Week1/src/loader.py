import sqlite3
import json
from pathlib import Path

def load_all_jsons(silver_dir: Path, gold_dir: Path) -> None:
    gold_dir.mkdir(parents=True, exist_ok=True)
    db_path = gold_dir / "jobs.db"

    # Create SQLite database
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                source_id   TEXT PRIMARY KEY,
                job_title   TEXT NOT NULL,
                company     TEXT NOT NULL,
                description TEXT NOT NULL,
                tech_stack  TEXT
            )
        """)
        # Check for .json files before processing
        json_files = list(silver_dir.glob("*.json"))

        if not silver_dir.exists() or not json_files:
            print("No JSON files found in silver, skipping.")
            return

        # create variables to track progress
        total, loaded, skipped = len(json_files), 0, 0
        print("🥇 Gold:...")

        # process each .json file
        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text(encoding="utf-8"))

                cursor.execute("""
                    INSERT OR IGNORE INTO jobs (source_id, job_title, company, description)
                    VALUES (?, ?, ?, ?)
                """, (
                    data.get("source_id"),
                    data.get("title"),
                    data.get("company"),
                    data.get("description"),
                ))

                if cursor.rowcount == 1:
                    print(f"✅ Inserted: {json_file.name}")
                    loaded += 1
                else:
                    print(f"⏭️ Skipped (duplicate): {json_file.name}")
                    skipped += 1

            except Exception as e:
                print(f"⚠️ Failed: {json_file.name} — {e}")
                skipped += 1

        conn.commit()
        print(f"\n📊 Gold Summary: \nTotal: {total} | Inserted: {loaded} | Skipped: {skipped}")


if __name__ == "__main__":
    load_all_jsons(Path("data/2_silver"), Path("data/3_gold"))