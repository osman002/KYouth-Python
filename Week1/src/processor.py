from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel

# Define required fields for validation
REQUIRED_FIELDS = ["source_id", "title", "company", "description"]
class JobListing(BaseModel):
    source_id: str
    url: str
    title: str
    company: str
    location: str = ""
    work_type: str = ""
    classification: str = ""
    rating: str = ""
    description: str

# Functions to load HTML and encode it into a BeautifulSoup object
def load_html(html_file: Path) -> BeautifulSoup:
    return BeautifulSoup(html_file.read_text(encoding="utf-8"), "html.parser")

# Helper functions to extract specific data points from the HTML
def get_text_by_automation(soup: BeautifulSoup, value: str) -> str:
    tag = soup.find(attrs={"data-automation": value})
    return tag.get_text(strip=True) if tag else ""

# Function to extract meta content by property
def get_meta_content(soup: BeautifulSoup, property: str) -> str:
    tag = soup.find("meta", property=property)
    return tag["content"] if tag and tag.get("content") else ""

# Functions to extract rating which have more complex logic
def extract_rating(soup: BeautifulSoup) -> str:
    tag = soup.find(attrs={"data-automation": "company-review"})
    if tag:
        span = tag.find("span", attrs={"aria-hidden": "true"})
        return span.get_text(strip=True) if span else ""
    return ""

# Function to extract job description with proper whitespace handling
def extract_description(soup: BeautifulSoup) -> str:
    tag = soup.find(attrs={"data-automation": "jobAdDetails"})
    return " ".join(tag.get_text(separator=" ").split()) if tag else ""

# Main function to parse job data from BeautifulSoup object
def parse_job(soup: BeautifulSoup) -> dict:
    url = get_meta_content(soup, "og:url")
    return {
        "source_id": url.rstrip("/").split("/")[-1],
        "url": url,
        "title": get_text_by_automation(soup, "job-detail-title"),
        "company": get_text_by_automation(soup, "advertiser-name"),
        "location": get_text_by_automation(soup, "job-detail-location"),
        "work_type": get_text_by_automation(soup, "job-detail-work-type"),
        "classification": get_text_by_automation(soup, "job-detail-classifications"),
        "rating": extract_rating(soup),
        "description": extract_description(soup),
    }

# Function to validate that all required fields are present in the job data
def validate_job(job_data: dict, filename: str) -> bool:
    missing = [f for f in REQUIRED_FIELDS if not job_data.get(f)]
    [print(f"⚠️ Missing {f} in: {filename}") for f in missing]
    return not missing


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


if __name__ == "__main__":
    test_file = Path("data/1_bronze/your_file.html")
    soup = load_html(test_file)
    job_data = parse_job(soup)
    for key, value in job_data.items():
        print(f"=== {key} ===", str(value)[:200])