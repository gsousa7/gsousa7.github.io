import glob
import os
import re
import shutil
import subprocess

import rendercv_fonts
import typst
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "_data")
OUTPUT_DIR = "rendercv_output"
FINAL_PDF = os.path.join(REPO_ROOT, "assets/files/Goncalo_Sousa_CV.pdf")

# RenderCV/Typst's Font Awesome set has no Credly brand icon (unlike the
# site's own Credly SVG). Tried "hexagon-check" (closest shape to Credly's
# hexagonal badges) and "certificate" (read as a medal/rosette, not a
# credential) — both in this package's map file but only "certificate"
# actually rendered; several other candidates (badge, badge-check, diploma,
# seal) rendered as broken/wrong glyphs too. Rather than settle for the best
# available Font Awesome icon, swap in the site's real Credly SVG after
# render — `rendercv` has no config option for a custom connection image, so
# this patches the generated Typst source directly before the final compile.
CREDLY_PLACEHOLDER_ICON = "id-badge"

MONTHS = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
}


def load(name):
    with open(f"{DATA_DIR}/{name}.yml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_month_year(s):
    s = s.strip().rstrip(".")
    m = re.match(r"([A-Za-z]{3})\.?\s+(\d{4})", s)
    if not m:
        return None
    mon, year = m.groups()
    return f"{year}-{MONTHS[mon[:3].title()]}"


def parse_range(date_str):
    parts = [p.strip() for p in date_str.split("—")]
    start = parse_month_year(parts[0])
    if len(parts) == 1:
        return start, None
    end = "present" if parts[1].strip().lower() == "present" else parse_month_year(parts[1])
    return start, end


def sanitize(text):
    # RenderCV's markdown->Typst pass misreads a mid-sentence " - " as a new
    # bullet start (splitting the highlight in two); an en dash is unambiguous.
    return re.sub(r"(?<=\S) - (?=\S)", " – ", text)


def extract_devicon_titles(description):
    titles = re.findall(r"!\[devicon\]\([^)]*'([^']*)'\)", description)
    titles += re.findall(r"title='([^']*)'", description)
    seen = []
    for t in titles:
        if t not in seen:
            seen.append(t)
    return seen


experience_yml = load("Experience")
skills_yml = load("Skills")
certs_yml = load("Certificates")
edu_yml = load("Education")
projects_yml = load("Projects")
languages_yml = load("Languages")
intro_yml = load("Introduction")

experience = []
for item in experience_yml["contents"]:
    start, end = parse_range(item["date"])
    company = f"[{item['title']}]({item['url']})" if item.get("url") else item["title"]
    experience.append({
        "company": company,
        "position": item["role"],
        "start_date": start,
        "end_date": end,
        "highlights": [sanitize(d) for d in item["description"]],
    })

skills = []
for item in skills_yml["contents"]:
    tools = extract_devicon_titles(item["description"])
    skills.append({"label": item["title"], "details": ", ".join(tools)})

certifications = []
for item in certs_yml["contents"]:
    certifications.append({
        "name": item["title"],
        "date": item["date"],
        "summary": item.get("description"),
    })

education = []
for item in edu_yml["contents"]:
    start, end = parse_range(item["date"])
    institution = f"[{item['title']}]({item['url']})" if item.get("url") else item["title"]
    education.append({
        "institution": institution,
        "area": item.get("role", ""),
        "start_date": start,
        "end_date": end,
        "summary": item.get("description"),
    })

projects = []
for item in projects_yml["contents"]:
    projects.append({
        "name": item["title"],
        "highlights": list(item["description"]),
    })

languages = []
for item in languages_yml["contents"]:
    languages.append({"label": item["title"], "details": item["description"]})

intro_text = intro_yml["contents"][0]["description"].strip()

cv = {
    "cv": {
        "name": "Gonçalo Sousa",
        "headline": "DevOps Engineer",
        "location": "Seixal, Portugal",
        "photo": os.path.join(REPO_ROOT, "assets/img/profile.jpg"),
        "social_networks": [
            {"network": "LinkedIn", "username": "gsousa7"},
            {"network": "GitHub", "username": "gsousa7"},
            {"network": "GitLab", "username": "gsousa7"},
        ],
        "custom_connections": [
            # Icon here is a placeholder, swapped for the real Credly SVG
            # by patch_credly_icon() after rendercv's own render step.
            # No "@" prefix — matches the plain "gsousa7" that social_networks
            # (LinkedIn/GitHub/GitLab) shows automatically, above.
            {"fontawesome_icon": CREDLY_PLACEHOLDER_ICON, "placeholder": "gsousa7", "url": "https://www.credly.com/users/gsousa7"},
        ],
        "sections": {
            "Introduction": [intro_text],
            "Skills": skills,
            "Experience": experience,
            "Certifications": certifications,
            "Education": education,
            "Projects": projects,
            "Languages": languages,
        },
    },
    "design": {
        "theme": "classic",
        "page": {
            # "Last updated in ..." note at the top of page 1 — noise on a
            # CV meant to be printed/downloaded, not tracked over time.
            "show_top_note": False,
        },
        "links": {
            # Small external-link glyph after every hyperlink — including
            # the company/institution links markdown_to_typst renders from
            # the [text](url) syntax embedded in company/institution above,
            # matching the site's own .external-link-icon next to company
            # names — so a reader can tell at a glance which text is a link.
            "show_external_link_icon": True,
        },
        "colors": {
            # Mirrors the site's own two-tone hierarchy (gold for name/
            # badges, green for job title/links), but darker than the
            # site's own --theme3-dark (#A8955A) — that gold reads fine as
            # an icon/border accent on screen, but as small text on a white
            # PDF page it fails contrast (~3:1). This shade keeps the same
            # gold family while clearing WCAG AA (~4.5:1) on white.
            "name": "rgb(140, 115, 50)",
            "headline": "rgb(61, 114, 93)",
            # Gold on connections, and again on section_titles (repeated at
            # every one of the 7 sections down the page), made gold feel
            # like it was everywhere rather than a deliberate accent.
            # Neutral dark (site's own --font-dark) for connections; green
            # for section_titles, matching the headline/links green already
            # in use — gold now appears exactly once, on the name.
            "connections": "rgb(32, 36, 36)",
            "section_titles": "rgb(61, 114, 93)",
            "links": "rgb(61, 114, 93)",
        },
        "typography": {
            "font_size": {
                # Name/headline default to 30pt/10pt (same size as body
                # text) — too big and too flat a hierarchy respectively.
                # Body itself (10pt default) reads a little small in print.
                "body": "11pt",
                "name": "22pt",
                "headline": "13pt",
            },
            "bold": {
                "headline": True,
            },
        },
        "sections": {
            # Duration ("6 months") pushed the date range onto its own
            # second line — the range alone already fits on one line.
            "show_time_spans_in": [],
            # Shaved down from the 1.2em default to reclaim just enough
            # vertical space to keep all 3 Certifications entries together
            # on one page — the 3rd was landing alone at the top of the
            # next page otherwise. (sections.allow_page_break: false looked
            # like the "proper" fix but it's a single global switch — it
            # also forced Experience, which spans 2 pages on its own, to
            # try to fit on one page and broke the layout entirely.)
            "space_between_regular_entries": "1em",
        },
        "section_titles": {
            # "Category" here meant the 7 page sections (Introduction,
            # Skills, Experience, ...), not the rows inside Skills — default
            # 0.5cm above each section title read as too tight between,
            # say, the end of Skills and the "Experience" heading.
            "space_above": "1cm",
        },
        "entries": {
            # Default 4.15cm reserves far more width than the date ranges
            # need, leaving a visible dead gap on the header line. Too
            # narrow and a range wraps to its own line, and the column's
            # justified alignment stretches it into ugly gapped text — this
            # needs to scale with typography.font_size.body (currently
            # 11pt): fits the longest range ("June 2016 – Sept 2017") on
            # one line with room spare. Re-check if body size changes again.
            "date_and_location_width": "4.1cm",
            # short_second_row (default true) squeezes the highlight
            # bullets into the same narrow column as the header line, even
            # though only the header actually needs to share the row with
            # the date — leaves a big dead margin on every bullet line.
            # False lets bullets use the full page width below the header.
            "short_second_row": False,
        },
        "templates": {
            "education_entry": {
                # Default degree_column ("**DEGREE**") still reserves its
                # 1cm width even when no `degree` field is set, pushing
                # every education entry's text over unnecessarily.
                "degree_column": None,
            },
        },
    },
    "locale": {"language": "english"},
    "settings": {
        "current_date": "today",
        "render_command": {"output_folder": "rendercv_output"},
    },
}

def patch_credly_icon(typ_path):
    credly_svg = os.path.join(os.path.dirname(typ_path), "credly.svg")
    shutil.copy(os.path.join(REPO_ROOT, "assets/img/credly.svg"), credly_svg)

    old = f'#connection-with-icon("{CREDLY_PLACEHOLDER_ICON}")[gsousa7]'
    new = '#box[#image("credly.svg", height: 0.9em)] #h(0.05cm) #box[gsousa7]'
    text = open(typ_path, encoding="utf-8").read()
    if old not in text:
        raise RuntimeError(
            "Credly connection pattern not found in generated Typst — "
            "rendercv's connection template may have changed."
        )
    open(typ_path, "w", encoding="utf-8").write(text.replace(old, new))


yaml_path = "Goncalo_Sousa_CV.yaml"
with open(yaml_path, "w", encoding="utf-8") as f:
    yaml.dump(cv, f, sort_keys=False, allow_unicode=True, width=1000)
print(f"wrote {yaml_path}")

subprocess.run(["rendercv", "render", yaml_path], check=True)

typ_files = glob.glob(os.path.join(OUTPUT_DIR, "*.typ"))
if len(typ_files) != 1:
    raise RuntimeError(f"expected exactly one .typ file in {OUTPUT_DIR}, found {typ_files}")
typ_path = typ_files[0]

patch_credly_icon(typ_path)
print(f"patched Credly icon in {typ_path}")

# Plain typst.compile() doesn't know about rendercv's bundled fonts (Source
# Sans 3, Font Awesome, etc.) and silently falls back to whatever Typst
# finds on the system instead — wrong body font and misshapen icons, with
# no error raised. rendercv's own `render` command sets these explicitly
# (rendercv/renderer/pdf_png.py:get_typst_compiler); replicated here since
# recompiling after the Credly patch bypasses that step.
compiler = typst.Compiler(root=OUTPUT_DIR, font_paths=rendercv_fonts.paths_to_font_folders)
# assets/files/ holds nothing else git-tracked (the PDF itself is
# gitignored — see .gitignore), so git never creates the directory on a
# fresh checkout; a clean CI clone would otherwise fail here with
# "No such file or directory".
os.makedirs(os.path.dirname(FINAL_PDF), exist_ok=True)
compiler.compile(input=typ_path, output=FINAL_PDF)
print(f"wrote {FINAL_PDF}")
