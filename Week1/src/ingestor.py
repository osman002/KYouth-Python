from pathlib import Path
import email
from email.message import Message

def load_mhtml(mhtml_file: Path) -> Message:
    with open(mhtml_file, "rb") as f:
        return email.message_from_bytes(f.read())

def extract_html(msg: Message) -> str:
    for part in msg.walk():
        if part.get_content_type() == "text/html":
            payload = part.get_payload(decode=True)
            return payload.decode("utf-8")
    return ""

def ingest_all_mhtml(source_dir: Path, bronze_dir: Path) -> None:
    bronze_dir.mkdir(parents=True, exist_ok=True)

    # Check for .mhtml files before processing
    if not source_dir.exists() or not list(source_dir.glob("*.mhtml")):
        print("No source files found, skipping.")
        return

    # create variables to track progress
    mhtml_files = list(source_dir.glob("*.mhtml"))
    total = len(mhtml_files)
    extracted = 0
    failed = 0

    print("🥉 Bronze:")

    # process each .mhtml file
    for mhtml_file in mhtml_files:
        msg = load_mhtml(mhtml_file)
        html = extract_html(msg)

        # handle case where no HTML content is found
        if not html:
            print(f"⚠️ No HTML content found in: {mhtml_file.name}")
            failed += 1
            continue

        # save extracted HTML to bronze directory
        output_path = bronze_dir / mhtml_file.with_suffix(".html").name
        output_path.write_text(html, encoding="utf-8")
        print(f"✅ Extracted: {mhtml_file.name}")
        extracted += 1

    # print summary
    print(f"\n📊 Bronze Summary: Total: {total} | Extracted: {extracted} | Failed: {failed}")