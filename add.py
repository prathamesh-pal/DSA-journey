#!/usr/bin/env python3
"""
add.py - create a solution file for a LeetCode question and update the README.

Usage:
    python add.py 15 python
    python add.py 15 cpp
    python add.py 15 cpp --no-open   (skip opening the file)

No third-party packages needed (standard library only).
"""
import html
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
from datetime import date
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).parent
SOLUTIONS = ROOT / "solutions"
INDEX_FILE = ROOT / "index.json"
README = ROOT / "README.md"
START, END = "<!-- PROGRESS:START -->", "<!-- PROGRESS:END -->"

API = "https://leetcode.com/graphql"

# our name -> (file extension, LeetCode snippet slug, comment prefix)
LANGS = {
    "python": ("py", "python3", "#"),
    "cpp": ("cpp", "cpp", "//"),
}


# ---------- LeetCode fetching ----------
def gql(query, variables):
    body = json.dumps({"query": query, "variables": variables}).encode()
    req = urllib.request.Request(
        API,
        data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://leetcode.com",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)["data"]


def find_slug(number):
    q = """
    query ($filters: QuestionListFilterInput) {
      problemsetQuestionList: questionList(
        categorySlug: "", limit: 50, skip: 0, filters: $filters
      ) {
        questions: data { frontendQuestionId: questionFrontendId titleSlug }
      }
    }"""
    data = gql(q, {"filters": {"searchKeywords": str(number)}})
    for item in data["problemsetQuestionList"]["questions"]:
        if item["frontendQuestionId"] == str(number):
            return item["titleSlug"]
    raise SystemExit(f"Could not find LeetCode question #{number}.")


def fetch_question(slug):
    q = """
    query ($titleSlug: String!) {
      question(titleSlug: $titleSlug) {
        questionFrontendId title difficulty isPaidOnly content
        topicTags { name slug }
        codeSnippets { langSlug code }
      }
    }"""
    return gql(q, {"titleSlug": slug})["question"]


# ---------- helpers ----------
class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []

    def handle_data(self, d):
        self.out.append(d)

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "p", "li", "pre", "ul", "ol"):
            self.out.append("\n")

    def handle_endtag(self, tag):
        if tag in ("p", "li", "pre", "ul", "ol"):
            self.out.append("\n")


def html_to_text(raw):
    p = _Text()
    p.feed(raw or "")
    text = html.unescape("".join(p.out)).replace("\xa0", " ")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def snake(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def build_file(q, lang, description):
    ext, snippet_slug, c = LANGS[lang]
    num = int(q["questionFrontendId"])
    topics = ", ".join(t["name"] for t in q["topicTags"]) or "Uncategorized"

    header = [
        f"{num}. {q['title']}",
        f"Difficulty: {q['difficulty']}",
        f"Topics: {topics}",
        f"Link: https://leetcode.com/problems/{slugify(q['title'])}/",
        "",
        *description.splitlines(),
        "",
        "--- My notes ---",
        "Approach:",
        "Time complexity:",
        "Space complexity:",
        "What I got wrong / to revisit:",
    ]
    block = "\n".join(f"{c} {line}".rstrip() for line in header)

    starter = next(
        (s["code"] for s in q["codeSnippets"] or [] if s["langSlug"] == snippet_slug),
        None,
    )
    if starter is None:
        starter = "class Solution:\n    pass\n" if lang == "python" else "class Solution {};\n"

    if lang == "python":
        starter = starter.rstrip()
        if starter.endswith(":"):  # LeetCode's stub has an empty body
            starter += "\n        pass"
        starter = "from typing import List, Optional\n\n\n" + starter
    else:
        starter = "#include <bits/stdc++.h>\nusing namespace std;\n\n" + starter

    return block + "\n\n" + starter.rstrip() + "\n"


# ---------- index + README ----------
def load_index():
    try:
        data = json.loads(INDEX_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}  # missing or empty/corrupt index.json: start fresh


def render_readme_table(index):
    rows = sorted(index.values(), key=lambda e: e["number"])
    lines = [
        f"**Solved: {len(rows)}**  "
        f"(Easy {sum(r['difficulty']=='Easy' for r in rows)} / "
        f"Medium {sum(r['difficulty']=='Medium' for r in rows)} / "
        f"Hard {sum(r['difficulty']=='Hard' for r in rows)})",
        "",
        "| # | Title | Difficulty | Topic | Solutions | Date |",
        "|---|-------|------------|-------|-----------|------|",
    ]
    for r in rows:
        sols = " · ".join(f"[{l}]({p})" for l, p in sorted(r["files"].items()))
        lines.append(
            f"| {r['number']} | {r['title']} | {r['difficulty']} | "
            f"{r['topic']} | {sols} | {r['date']} |"
        )
    return "\n".join(lines)


def update_readme(index):
    table = f"{START}\n{render_readme_table(index)}\n{END}"
    if README.exists():
        text = README.read_text()
    else:
        text = "# DSA Journey\n\nMy LeetCode progress, tracked automatically.\n\n"
    if START in text and END in text:
        text = re.sub(
            re.escape(START) + r".*?" + re.escape(END), lambda m: table, text, flags=re.S
        )
    else:
        text = text.rstrip() + "\n\n" + table + "\n"
    README.write_text(text)


def open_file(path):
    """Open in VS Code if installed, otherwise the system default app."""
    try:
        code = shutil.which("code")
        if code:
            subprocess.Popen([code, str(ROOT), "-g", str(path)], shell=(os.name == "nt"))
        elif sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        print(f"(Could not auto-open the file: {e})")


# ---------- main ----------
def main():
    args = [a for a in sys.argv[1:] if a != "--no-open"]
    no_open = "--no-open" in sys.argv
    if len(args) != 2 or args[1].lower() not in LANGS or not args[0].isdigit():
        raise SystemExit("Usage: python add.py <question_number> <python|cpp> [--no-open]")
    number, lang = int(args[0]), args[1].lower()

    slug = find_slug(number)
    q = fetch_question(slug)

    if q["isPaidOnly"] or not q["content"]:
        print("Note: this question is premium, so no description is available.")
        description = "(Premium question - description not available.)"
    else:
        description = html_to_text(q["content"])

    topic_tag = q["topicTags"][0]["slug"] if q["topicTags"] else "uncategorized"
    ext = LANGS[lang][0]
    folder = SOLUTIONS / topic_tag
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{number:04d}_{snake(q['title'])}.{ext}"

    if path.exists():
        # keep your work, but still make sure it is registered in the index/README
        print(f"Already exists: {path.relative_to(ROOT)} (not overwriting)")
    else:
        path.write_text(build_file(q, lang, description), encoding="utf-8")

    index = load_index()
    entry = index.setdefault(
        str(number),
        {
            "number": number,
            "title": q["title"],
            "difficulty": q["difficulty"],
            "topic": q["topicTags"][0]["name"] if q["topicTags"] else "Uncategorized",
            "topics": [{"name": t["name"], "slug": t["slug"]} for t in q["topicTags"]]
            or [{"name": "Uncategorized", "slug": "uncategorized"}],
            "files": {},
            "date": date.today().isoformat(),
        },
    )
    entry["files"][lang] = path.relative_to(ROOT).as_posix()
    INDEX_FILE.write_text(json.dumps(index, indent=2))
    update_readme(index)

    print(f"Ready: {path.relative_to(ROOT)}")
    print("README.md updated.")
    if not no_open:
        open_file(path)


if __name__ == "__main__":
    main()