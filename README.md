# 📂 File Butler

> An AI-powered directory organizer that channels your inner sloth by doing the tedious file sorting for you. Built for Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady Submission 🦥.

## 🦥 The Problem
Manually sorting cluttered directories like your `Downloads` or `Desktop` folder file-by-file is exhausting and repetitive. Sloths know how to conserve energy, so why should you do the heavy lifting? **File Butler** analyzes your directory structure and intelligently categorizes your files in one click.

---

## 🚀 How It Works
1. **Scans Target Directory:** Inspects loose files and subfolders while safely ignoring hidden files.
2. **AI Taxonomy Planning:** Sends a lightweight JSON map of your directory structure to an open-weight model (`openai/gpt-oss-20b`) via the **Groq API**.
3. **Safe Execution & Safeguards:** 
   - Proposes a clean categorization structure.
   - Includes a **Dry-Run Mode** (`--dry-run`) to preview changes safely.
   - Requires human-in-the-loop interactive confirmation before moving files.
   - Gracefully handles edge cases like already-organized folders, file permission errors, and name collisions.
4. **Audit Trail:** Automatically records all actions into `file_butler.log`.

---

## 💡 Why Open Innovation Matters for File Butler
- **Zero Heavy Infrastructure:** By leveraging open-weight models through Groq's high-performance cloud inference, File Butler runs instantly without needing a local GPU or heavy compute setup.
- **Cost Efficiency & Free Tier Viability:** Using an efficient open-weight model keeps API costs virtually nonexistent, allowing developers to run automation pipelines comfortably within free developer tier limits.
- **No Vendor Lock-In:** The open-weight approach ensures portability and flexibility, avoiding proprietary ecosystem lock-in.

---

## 🛠️ Quick Start

### 1. Clone & Setup Environment
```bash
git clone [https://github.com/YOUR-USERNAME/file-butler.git](https://github.com/YOUR-USERNAME/file-butler.git)
cd file-butler

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### 2. Configure Your API Key

Set your Groq API key as an environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key_here"

```

### 3. Run File Butler

* **Preview changes (Dry-Run):**
```bash
python file_butler.py test_dir --dry-run

```


* **Run live organization:**
```bash
python file_butler.py test_dir


```

---
