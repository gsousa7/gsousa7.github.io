import os
import re
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(REPO_ROOT, "_data")

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
    experience.append({
        "company": item["title"],
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
    title = item["title"]
    if "," in title:
        area, institution = [p.strip() for p in title.split(",", 1)]
    else:
        area, institution = title, ""
    start, end = parse_range(item["date"])
    education.append({
        "institution": institution,
        "area": area,
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
            {"fontawesome_icon": "award", "placeholder": "@gsousa7", "url": "https://www.credly.com/users/gsousa7"},
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
        "colors": {
            "name": "rgb(58, 90, 64)",
            "headline": "rgb(58, 90, 64)",
            "connections": "rgb(58, 90, 64)",
            "section_titles": "rgb(58, 90, 64)",
            "links": "rgb(58, 90, 64)",
        },
    },
    "locale": {"language": "english"},
    "settings": {
        "current_date": "today",
        "render_command": {"output_folder": "rendercv_output"},
    },
}

with open("Goncalo_Sousa_CV.yaml", "w", encoding="utf-8") as f:
    yaml.dump(cv, f, sort_keys=False, allow_unicode=True, width=1000)

print("wrote Goncalo_Sousa_CV.yaml")
