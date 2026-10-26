import json
import os
import shutil
import logging
from pathlib import Path
from groq import Groq

# Setup logging configuration
logging.basicConfig(
    filename="file_butler.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Initialize Groq client
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please run: export GROQ_API_KEY='your_key'")

client = Groq(api_key=api_key)

def scan_directory(dir_path: Path):
    """Scans target directory and checks for loose files."""
    items = []
    loose_files_found = False
    
    for item in dir_path.iterdir():
        if item.name.startswith("."):
            continue
        
        is_file = item.is_file()
        if is_file:
            loose_files_found = True
            
        items.append({
            "name": item.name,
            "type": "folder" if item.is_dir() else "file",
            "extension": item.suffix if is_file else ""
        })
    return items, loose_files_found

def get_organization_plan(items):
    """Sends file tree to Groq API using openai/gpt-oss-20b for taxonomic categorization."""
    prompt = f"""
You are an expert file organizer for an app called File Butler. Analyze the following list of files and folders inside a user's directory:
{json.dumps(items, indent=2)}

Propose a clean, logical folder structure (e.g., 'Documents', 'Images', 'Videos', 'Financials') to categorize these items.
Return ONLY a raw JSON object (no markdown, no backticks, no explanatory text) mapping each item name to its destination folder name.

Example schema:
{{
  "invoice_2024.pdf": "Documents/Financials",
  "vacation_photo.png": "Images"
}}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    raw_text = response.choices[0].message.content.strip()
    
    if raw_text.startswith("```"):
        raw_text = raw_text.split("\n", 1)[1]
    if raw_text.endswith("```"):
        raw_text = raw_text.rsplit("\n", 1)[0]
    
    return json.loads(raw_text.strip())

def organize_directory(target_dir_str: str, dry_run: bool = False):
    target_dir = Path(target_dir_str).resolve()
    
    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Error: Path '{target_dir_str}' is not a valid directory.")
        return

    print(f"📂 [File Butler] Scanning directory: {target_dir}")
    items, loose_files_found = scan_directory(target_dir)

    if not items:
        print("Directory is empty. Nothing to organize.")
        return

    if not loose_files_found:
        print("✨ Directory is already organized! No loose files found in the root directory.")
        return

    print("🤖 Requesting organization plan from open-weight model via Groq...")
    try:
        plan = get_organization_plan(items)
    except Exception as e:
        print(f"Failed to get or parse plan from Groq API: {e}")
        return

    print("\n📋 Proposed Organization Plan:")
    for item, folder in plan.items():
        print(f"  • {item}  -->  {folder}/")

    if dry_run:
        print("\n🔍 Dry-run mode active. No files were moved.")
        return

    # Interactive Confirmation
    confirmation = input("\nDo you want to execute this plan? (y/n): ").strip().lower()
    if confirmation != 'y':
        print("❌ Organization cancelled by user.")
        return

    print("\n📦 Executing Organization Plan:")
    moved_count = 0
    errors = []

    for item_name, category_folder in plan.items():
        src_path = target_dir / item_name

        if not src_path.exists():
            err_msg = "Source item not found"
            errors.append((item_name, err_msg))
            logging.warning(f"Skipped {item_name}: {err_msg}")
            continue

        dest_folder = target_dir / category_folder

        try:
            dest_folder.mkdir(parents=True, exist_ok=True)
            dest_path = dest_folder / item_name

            if dest_path.exists() and dest_path != src_path:
                stem = src_path.stem
                suffix = src_path.suffix
                dest_path = dest_folder / f"{stem}_copy{suffix}"

            shutil.move(str(src_path), str(dest_path))
            print(f"  ✓ Moved: {item_name}  -->  {category_folder}/")
            logging.info(f"Successfully moved {item_name} to {category_folder}/")
            moved_count += 1

        except PermissionError:
            err_msg = "Permission denied / file in use"
            errors.append((item_name, err_msg))
            logging.error(f"Failed {item_name}: {err_msg}")
        except Exception as err:
            errors.append((item_name, str(err)))
            logging.error(f"Failed {item_name}: {str(err)}")

    # Summary Report
    print("\n" + "=" * 40)
    print(f"🎉 File Butler Complete! Successfully moved: {moved_count} items.")
    logging.info(f"Run summary: {moved_count} items moved, {len(errors)} errors.")
    if errors:
        print(f"⚠️  Skipped {len(errors)} items due to errors:")
        for item, reason in errors:
            print(f"  - {item}: {reason}")
    print("📝 Audit log saved to 'file_butler.log'")

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="File Butler: AI-Powered Directory Organizer")
    parser.add_argument("directory", nargs="?", default="test_dir", help="Target directory to organize")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    
    args = parser.parse_args()
    organize_directory(args.directory, dry_run=args.dry_run)