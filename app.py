import argparse
import json
import os
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit


def inspect(text):
    headings = []
    links = []
    fence = None
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.lstrip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker[0]
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence:
            continue
        heading = re.match(r"^ {0,3}(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if heading:
            headings.append(
                {"level": len(heading[1]), "text": heading[2], "line": number}
            )
        for match in re.finditer(
            r'!?\[[^\]]*\]\((<[^>]+>|[^\s)]+)(?:\s+"[^"]*")?\)', line
        ):
            links.append({"target": match[1].strip("<>"), "line": number})
    return {"headings": headings, "links": links}


def index(root, search=None):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Choose an existing directory.")
    documents = []
    broken = []
    errors = []

    def failed(error):
        errors.append({"path": str(error.filename), "error": str(error)})

    for directory, dirs, files in os.walk(root, followlinks=False, onerror=failed):
        dirs[:] = sorted(
            d
            for d in dirs
            if d not in {".git", "node_modules", ".venv"}
            and not (Path(directory) / d).is_symlink()
        )
        for name in sorted(files):
            path = Path(directory) / name
            if path.suffix.lower() != ".md" or path.is_symlink():
                continue
            relative = path.relative_to(root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError) as e:
                errors.append({"path": relative, "error": str(e)})
                continue
            report = inspect(text)
            if (
                search is None
                or search.casefold() in text.casefold()
                or search.casefold() in relative.casefold()
            ):
                documents.append({"path": relative, **report})
            for link in report["links"]:
                url = urlsplit(link["target"])
                if url.scheme or url.netloc or not url.path:
                    continue
                target = (
                    (root / unquote(url.path.lstrip("/")))
                    if url.path.startswith("/")
                    else path.parent / unquote(url.path)
                )
                resolved = target.resolve()
                reason = (
                    "outside workspace"
                    if not resolved.is_relative_to(root)
                    else "missing target" if not resolved.exists() else None
                )
                if reason:
                    broken.append({"document": relative, **link, "reason": reason})
    return {"documents": documents, "broken_links": broken, "errors": errors}


def main():
    p = argparse.ArgumentParser(
        description="Index Markdown headings and find missing local link targets."
    )
    p.add_argument("directory")
    p.add_argument("--search")
    p.add_argument("--check", action="store_true")
    a = p.parse_args()
    try:
        report = index(a.directory, a.search)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if report["errors"] or (a.check and report["broken_links"]):
            p.exit(1)
    except (OSError, ValueError) as e:
        p.exit(2, f"Error: {e}\n")


if __name__ == "__main__":
    main()
