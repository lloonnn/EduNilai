"""
EduNilai — University Tuition Fee Scraper
==========================================
Scrapes undergraduate tuition fees for Malaysian students from:
  - UTM      (public)  : admission.utm.my
  - UM       (public)  : study.um.edu.my (official PDF)
  - APU      (private) : articles.unienrol.com
  - Taylor's (private) : articles.unienrol.com

No fallbacks. If a scrape fails, the script stops and tells you why.
Fix the issue (check the URL, your internet, the page structure) then re-run.

Exports:
  - edunilai_raw_fees.csv   — every individual programme with its fee
  - edunilai_mean_fees.csv  — mean fee per field category per university
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import pdfplumber
import io
import sys

# ─────────────────────────────────────────────────────────────
# FIELD CATEGORY MAPPING
# Keyword → standardised category
# Longer/more specific keywords are matched first (sorted by length)
# To fix a wrong categorisation, add a more specific keyword here
# ─────────────────────────────────────────────────────────────
CATEGORY_MAP = {
    # Engineering (check before "computer science" to catch "computer engineering")
    "biomedical engineering":           "Engineering",
    "chemical engineering":             "Engineering",
    "computer engineering":             "Engineering",
    "civil engineering":                "Engineering",
    "electrical":                       "Engineering",
    "electronic":                       "Engineering",
    "mechatronic":                      "Engineering",
    "mechanical engineering":           "Engineering",
    "petroleum engineering":            "Engineering",
    "engineering":                      "Engineering",

    # Computer Science & IT
    "computer / it":                    "Computer Science & IT",
    "computer science":                 "Computer Science & IT",
    "software engineering":             "Computer Science & IT",
    "information technology":           "Computer Science & IT",
    "data engineering":                 "Computer Science & IT",
    "data science":                     "Computer Science & IT",
    "artificial intelligence":          "Computer Science & IT",
    "cybersecurity":                    "Computer Science & IT",
    "cyber security":                   "Computer Science & IT",
    "multimedia computing":             "Computer Science & IT",
    "information systems":              "Computer Science & IT",
    "computer systems":                 "Computer Science & IT",
    "computer games":                   "Computer Science & IT",
    "cloud engineering":                "Computer Science & IT",
    "internet of things":               "Computer Science & IT",
    "digital forensics":                "Computer Science & IT",

    # Accounting & Finance (before "finance" alone to catch compound names)
    "accounting and finance":           "Accounting & Finance",
    "banking and finance":              "Accounting & Finance",
    "finance and economics":            "Accounting & Finance",
    "actuarial":                        "Accounting & Finance",
    "accounting":                       "Accounting & Finance",
    "finance":                          "Accounting & Finance",

    # Medicine & Health (before "science" to catch "biomedical science")
    "medicine and bachelor of surgery": "Medicine & Health",
    "biomedical science":               "Medicine & Health",
    "pharmaceutical science":           "Medicine & Health",
    "applied health":                   "Medicine & Health",
    "health science":                   "Medicine & Health",
    "mbbs":                             "Medicine & Health",
    "medicine":                         "Medicine & Health",
    "pharmacy":                         "Medicine & Health",
    "nursing":                          "Medicine & Health",
    "dental":                           "Medicine & Health",

    # Architecture & Built Environment
    "quantity surveying":               "Architecture & Built Environment",
    "building surveying":               "Architecture & Built Environment",
    "urban and regional":               "Architecture & Built Environment",
    "real estate":                      "Architecture & Built Environment",
    "interior architecture":            "Architecture & Built Environment",
    "sustainable digital construction": "Architecture & Built Environment",
    "built environment":                "Architecture & Built Environment",
    "architecture":                     "Architecture & Built Environment",

    # Law
    "bachelor of laws":                 "Law",
    "philosophy, politics":             "Law",

    # Education
    "early childhood education":        "Education",
    "teaching english":                 "Education",
    "education":                        "Education",

    # Business (after "accounting" and "finance" to avoid mismatches)
    "business administration":          "Business",
    "business management":              "Business",
    "international business":           "Business",
    "human resource":                   "Business",
    "marketing management":             "Business",
    "marketing":                        "Business",
    "entrepreneurship":                 "Business",
    "economics":                        "Business",
    "hrd":                              "Business",
    "management":                       "Business",

    # Science (after medicine/health to avoid miscategorising biomedical)
    "environmental management":         "Science",
    "environmental studies":            "Science",
    "ecology":                          "Science",
    "biochemistry":                     "Science",
    "microbiology":                     "Science",
    "molecular genetics":               "Science",
    "applied geology":                  "Science",
    "biotechnology":                    "Science",
    "food science":                     "Science",
    "culinology":                       "Science",
    "chemistry":                        "Science",
    "physics":                          "Science",
    "mathematics":                      "Science",
    "statistics":                       "Science",
    "science with education":           "Science",
    "sciences":                         "Science",

    # Social Sciences
    "international relations":          "Social Sciences",
    "international studies":            "Social Sciences",
    "southeast asian":                  "Social Sciences",
    "anthropology":                     "Social Sciences",
    "sociology":                        "Social Sciences",
    "social administration":            "Social Sciences",
    "social science":                   "Social Sciences",
    "geography":                        "Social Sciences",
    "media studies":                    "Social Sciences",
    "history":                          "Social Sciences",
    "psychology":                       "Social Sciences",

    # Arts & Humanities
    "mass communication":               "Arts & Humanities",
    "media and communication":          "Arts & Humanities",
    "performing arts":                  "Arts & Humanities",
    "interactive spatial design":       "Arts & Humanities",
    "fashion design":                   "Arts & Humanities",
    "industrial design":                "Arts & Humanities",
    "creative media":                   "Arts & Humanities",
    "multimedia technology":            "Arts & Humanities",
    "multimedia design":                "Arts & Humanities",
    "animation":                        "Arts & Humanities",
    "digital advertising":              "Arts & Humanities",
    "visual effects":                   "Arts & Humanities",
    "communication":                    "Arts & Humanities",
    "malay":                            "Arts & Humanities",
    "arabic":                           "Arts & Humanities",
    "japanese":                         "Arts & Humanities",
    "chinese language":                 "Arts & Humanities",
    "tamil":                            "Arts & Humanities",
    "english language":                 "Arts & Humanities",
    "french":                           "Arts & Humanities",
    "german":                           "Arts & Humanities",
    "spanish":                          "Arts & Humanities",
    "italian":                          "Arts & Humanities",
    "music":                            "Arts & Humanities",
    "drama":                            "Arts & Humanities",
    "dance":                            "Arts & Humanities",
    "arts":                             "Arts & Humanities",
    "hospitality":                      "Arts & Humanities",
    "tourism":                          "Arts & Humanities",
    "culinary":                         "Arts & Humanities",
    "events management":                "Arts & Humanities",
    "sports":                           "Arts & Humanities",
    "exercise":                         "Arts & Humanities",
    "islamic":                          "Arts & Humanities",
    "shariah":                          "Arts & Humanities",
}


def categorise(programme_name: str) -> str:
    """Assign a programme to a field category using keyword matching."""
    name_lower = programme_name.lower()
    # Sort by keyword length descending so longer/specific keywords match first
    for keyword in sorted(CATEGORY_MAP, key=len, reverse=True):
        if keyword in name_lower:
            return CATEGORY_MAP[keyword]
    return "Other"


def make_df(records: list, university: str, inst_type: str) -> pd.DataFrame:
    """Standardise a list of {programme, fee} dicts into a clean DataFrame."""
    df = pd.DataFrame(records)
    df["university"]     = university
    df["type"]           = inst_type        # "Public" or "Private"
    df["field_category"] = df["programme"].apply(categorise)
    return df[["university", "type", "field_category", "programme", "fee"]]


def abort(msg: str):
    """Stop the script with a clear error message."""
    print(f"\n❌ SCRAPING FAILED: {msg}")
    print("   Fix the issue above and re-run the script.")
    sys.exit(1)


# ═════════════════════════════════════════════════════════════
# 1. UTM — parse the HTML fee table directly
#    URL: https://admission.utm.my/programme-fees-ug-malaysian/
# ═════════════════════════════════════════════════════════════
def scrape_utm() -> pd.DataFrame:
    print("⏳ Scraping UTM...")
    url     = "https://admission.utm.my/programme-fees-ug-malaysian/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        abort(f"UTM returned HTTP {resp.status_code} from {url}")

    soup   = BeautifulSoup(resp.text, "html.parser")
    tables = soup.find_all("table")
    if not tables:
        abort("UTM: no tables found on page — the page structure may have changed")

    records = []
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 4:
                continue
            programme  = cells[0].get_text(strip=True)
            total_text = cells[3].get_text(strip=True).replace(",", "").replace("RM", "").strip()
            try:
                fee = float(total_text)
                # Skip header rows and sanity-check fee range
                if fee > 1000 and programme and "programme" not in programme.lower():
                    records.append({"programme": programme, "fee": fee})
            except ValueError:
                continue

    if not records:
        abort("UTM: tables were found but no valid fee rows could be parsed")

    df = make_df(records, "UTM", "Public")
    print(f"   ✅ UTM: {len(df)} programmes scraped")
    return df


# ═════════════════════════════════════════════════════════════
# 2. UM — download and parse their official PDF fee schedule
#    URL: https://study.um.edu.my/doc/tution-fee/...
# ═════════════════════════════════════════════════════════════
def scrape_um() -> pd.DataFrame:
    print("⏳ Scraping UM (from official PDF)...")
    url     = "https://fpe.um.edu.my/FPE/fee/UG_UPU.20252026_.pdf"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=20)
    if resp.status_code != 200:
        abort(f"UM PDF returned HTTP {resp.status_code} — check if the URL has changed at study.um.edu.my")

    records = []
    with pdfplumber.open(io.BytesIO(resp.content)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                line = line.strip()
                # Each line ends with a fee like "9,700.00" or "15,000.00"
                parts = line.rsplit(" ", 1)
                if len(parts) == 2:
                    programme = parts[0].strip()
                    fee_str   = parts[1].replace(",", "").strip()
                    try:
                        fee = float(fee_str)
                        # UM fees are between 8,000 and 20,000
                        if 7000 <= fee <= 25000 and len(programme) > 5:
                            records.append({"programme": programme, "fee": fee})
                    except ValueError:
                        continue

    if not records:
        abort("UM: PDF was downloaded but no fee rows could be parsed — check the PDF format")

    df = make_df(records, "UM", "Public")
    print(f"   ✅ UM: {len(df)} programmes scraped from PDF")
    return df


# ═════════════════════════════════════════════════════════════
# 3. APU — parse the unienrol.com fee article
#    URL: https://articles.unienrol.com/asia-pacific-university-apu-fees-and-courses/
# ═════════════════════════════════════════════════════════════
def scrape_apu() -> pd.DataFrame:
    print("⏳ Scraping APU...")
    url     = "https://articles.unienrol.com/asia-pacific-university-apu-fees-and-courses/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        abort(f"APU page returned HTTP {resp.status_code} from {url}")

    soup    = BeautifulSoup(resp.text, "html.parser")
    records = _parse_unienrol_tables(soup)

    if not records:
        abort("APU: page loaded but no undergraduate fee rows found — the table structure may have changed")

    df = make_df(records, "APU", "Private")
    print(f"   ✅ APU: {len(df)} undergraduate programmes scraped")
    return df


# ═════════════════════════════════════════════════════════════
# 4. TAYLOR'S — parse the unienrol.com fee article
#    URL: https://articles.unienrol.com/taylors-university-fees-and-courses/
# ═════════════════════════════════════════════════════════════
def scrape_taylors() -> pd.DataFrame:
    print("⏳ Scraping Taylor's University...")
    url     = "https://articles.unienrol.com/taylors-university-fees-and-courses/"
    headers = {"User-Agent": "Mozilla/5.0"}

    resp = requests.get(url, headers=headers, timeout=15)
    if resp.status_code != 200:
        abort(f"Taylor's page returned HTTP {resp.status_code} from {url}")

    soup    = BeautifulSoup(resp.text, "html.parser")
    records = _parse_unienrol_tables(soup)

    if not records:
        abort("Taylor's: page loaded but no undergraduate fee rows found — the table structure may have changed")

    df = make_df(records, "Taylor's", "Private")
    print(f"   ✅ Taylor's: {len(df)} undergraduate programmes scraped")
    return df


def _parse_unienrol_tables(soup: BeautifulSoup) -> list:
    """
    Parse fee tables from unienrol.com article pages.
    Skips Foundation, Diploma, Certificate, and Postgraduate rows automatically.
    Tables on these pages have 3 columns: Course Name | Duration | Total Fees (RM)
    """
    SKIP_KEYWORDS = [
        "foundation", "diploma", "certificate", "master", "phd",
        "msc", "mba", "postgraduate", "advanced diploma", "acca"
    ]

    records = []
    for table in soup.find_all("table"):
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 3:
                continue

            programme = cells[0].get_text(strip=True)
            fee_text  = cells[2].get_text(strip=True).replace(",", "").replace("RM", "").strip()

            # Skip non-degree rows
            if any(kw in programme.lower() for kw in SKIP_KEYWORDS):
                continue

            try:
                fee = float(fee_text)
                # Private university undergraduate fees: roughly RM90k–RM500k
                if 80000 <= fee <= 500000 and programme:
                    records.append({"programme": programme, "fee": fee})
            except ValueError:
                continue

    return records


# ═════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  EduNilai — Tuition Fee Scraper")
    print("=" * 60 + "\n")

    # ── Step 1: Scrape each university into its own DataFrame ──
    df_utm     = scrape_utm()
    df_um      = scrape_um()
    df_apu     = scrape_apu()
    df_taylors = scrape_taylors()

    # ── Step 2: Combine all 4 into one raw DataFrame ──
    df_all = pd.concat([df_utm, df_um, df_apu, df_taylors], ignore_index=True)

    # Drop anything the categoriser could not recognise
    unrecognised = df_all[df_all["field_category"] == "Other"]
    if not unrecognised.empty:
        print(f"\n⚠️  {len(unrecognised)} programmes could not be categorised and were dropped:")
        for _, row in unrecognised.iterrows():
            print(f"   [{row['university']}] {row['programme']}")
    df_all = df_all[df_all["field_category"] != "Other"].copy()

    print(f"\n📋 Combined dataset: {len(df_all)} programmes across 4 universities")

    # ── Step 3: Mean fee per field category per university ──
    #
    # MISSING DATA POLICY:
    # If a university does not offer a field (e.g. APU has no Medicine),
    # its cell is NaN — it is NOT treated as zero.
    # The overall mean and public/private averages are computed
    # only from universities that actually offer that field.
    #
    df_mean = (
        df_all
        .groupby(["field_category", "university"])["fee"]
        .mean()
        .round(2)
        .unstack(level="university")
    )

    # Enforce column order: public universities first, then private
    col_order = [c for c in ["UTM", "UM", "APU", "Taylor's"] if c in df_mean.columns]
    df_mean   = df_mean.reindex(columns=col_order)

    # Summary columns
    df_mean["Overall_Mean_RM"] = df_mean.mean(axis=1).round(2)
    df_mean["Uni_Count"]       = df_mean[col_order].notna().sum(axis=1)

    print("\n📊 Mean Fee by Field Category (RM):")
    print("-" * 70)
    print(df_mean.to_string())

    # ── Step 4: Export ──
    output_path = "C:/Users/koksl/vscfile/EduNilai/data/cost/"
    df_all.to_csv(output_path  + "edunilai_raw_fees.csv",  index=False)
    df_mean.to_csv(output_path + "edunilai_mean_fees.csv")

    print("\n✅ Exported:")
    print("   📁 edunilai_raw_fees.csv   — all individual programmes")
    print("   📁 edunilai_mean_fees.csv  — mean per field per university")
    print("\nDone! 🎉")