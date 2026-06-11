from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel

# define required fields for validation
REQUIRED_FIELDS = ["source_id", "job_title", "company", "description"]

# define Pydantic model for job listing
class JobListing(BaseModel):
    source_id: str
    job_title: str
    company: str
    description: str

# functions to load HTML into Beautiful Soup
def load_html(html_file: Path) -> BeautifulSoup:
    return BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")

# helper functions to extract data from HTML
def extract_data(soup: BeautifulSoup, value: str) -> str:
    tag = soup.find(attrs={"data-automation": value})
    return tag.get_text(strip=True) if tag else ""

# helper function to extract meta content
def get_meta_content(soup: BeautifulSoup, property: str) -> str:
    tag = soup.find("meta", property=property)
    return tag["content"] if tag and tag.get("content") else ""

# helper function to extract job description
def extract_description(soup: BeautifulSoup) -> str:
    tag = soup.find(attrs={"data-automation": "jobAdDetails"})
    return " ".join(tag.get_text(separator=" ").split()) if tag else ""

# main functions to process HTML and save as JSON
def parse_job(soup: BeautifulSoup) -> dict:
    url = get_meta_content(soup, "og:url")
    return {
        "source_id": url.rstrip("/").split("/")[-1],
        "job_title": extract_data(soup, "job-detail-title"),
        "company": extract_data(soup, "advertiser-name"),
        "description": extract_description(soup),
    }

# validation function to check for missing fields
def validate_job(job_data: dict, filename: str) -> bool:
    missing = [f for f in REQUIRED_FIELDS if not job_data.get(f)]
    [print(f"⚠️ Missing {f} in: {filename}") for f in missing]
    return not missing

# main function to process all HTML files in bronze and save as JSON in silver
def process_all_html(bronze_dir: Path, silver_dir: Path) -> None:
    silver_dir.mkdir(parents=True, exist_ok=True)

    html_files = list(bronze_dir.glob("*.html"))
    if not bronze_dir.exists() or not html_files:
        print("No HTML files found in bronze, skipping.")
        return

    total, processed, skipped = len(html_files), 0, 0
    print("🥈 Silver:")

    for html_file in html_files:
        try:
            job_data = parse_job(load_html(html_file))
            if not validate_job(job_data, html_file.name):
                skipped += 1
                continue
            job = JobListing(**job_data)
            output_path = silver_dir / html_file.with_suffix(".json").name
            output_path.write_text(job.model_dump_json(indent=2), encoding="utf-8")
            print(f"✅ Processed: {html_file.name}")
            processed += 1
        except Exception as e:
            print(f"⚠️ Error: {html_file.name} — {e}")
            skipped += 1

    print(f"\n📊 Silver Summary: Total: {total} | Processed: {processed} | Skipped: {skipped}")

# test code to verify parsing logic
if __name__ == "__main__":
    test_file = Path("data/1_bronze/your_file.html")
    soup = load_html(test_file)
    job_data = parse_job(soup)
    for key, value in job_data.items():
        print(f"=== {key} ===", str(value)[:200])