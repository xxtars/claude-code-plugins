#!/usr/bin/env python3
"""Convert a Distill-style transformer-circuits HTML page to a clean LaTeX PDF."""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


def fetch_rendered_html(url: str, out_path: Path) -> None:
    """Use headless Chrome to dump the JS-rendered DOM."""
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    subprocess.run(
        [chrome, "--headless", "--disable-gpu", "--virtual-time-budget=15000",
         "--dump-dom", url],
        stdout=out_path.open("wb"), stderr=subprocess.DEVNULL, check=True,
    )


def download_image(src: str, base_url: str, images_dir: Path) -> str | None:
    """Download an image, return the local filename relative to LaTeX root."""
    if src.startswith("data:"):
        # Inline data URI — extract and save
        m = re.match(r"data:image/(\w+);base64,(.*)", src)
        if not m:
            return None
        import base64
        ext, data = m.group(1), m.group(2)
        h = hashlib.md5(data.encode()).hexdigest()[:12]
        name = f"{h}.{ext}"
        path = images_dir / name
        if not path.exists():
            path.write_bytes(base64.b64decode(data))
        return f"images/{name}"
    full_url = urljoin(base_url, src)
    parsed = urlparse(full_url)
    ext = os.path.splitext(parsed.path)[1] or ".png"
    h = hashlib.md5(full_url.encode()).hexdigest()[:12]
    name = f"{h}{ext}"
    path = images_dir / name
    if not path.exists():
        try:
            r = requests.get(full_url, timeout=30)
            r.raise_for_status()
            path.write_bytes(r.content)
        except Exception as e:
            print(f"  ! failed image {full_url}: {e}", file=sys.stderr)
            return None
    return f"images/{name}"


UNICODE_TEXT_FIXES = {
    "−": "-", "–": "--", "—": "---",
    "‘": "`", "’": "'", "“": "``", "”": "''",
    "…": "...",
    " ": " ", " ": " ", "​": "",
    "•": "*",
    "†": r"\dag{}", "‡": r"\ddag{}",
    "§": r"\S{}",
}

UNICODE_MACRO_FIXES = {
    "×": r"\ensuremath{\times}", "·": r"\ensuremath{\cdot}",
    "→": r"\ensuremath{\rightarrow}", "←": r"\ensuremath{\leftarrow}",
    "↔": r"\ensuremath{\leftrightarrow}", "⇒": r"\ensuremath{\Rightarrow}",
    "≤": r"\ensuremath{\leq}", "≥": r"\ensuremath{\geq}",
    "≠": r"\ensuremath{\neq}", "≈": r"\ensuremath{\approx}",
    "±": r"\ensuremath{\pm}", "∞": r"\ensuremath{\infty}",
    "α": r"\ensuremath{\alpha}", "β": r"\ensuremath{\beta}",
    "γ": r"\ensuremath{\gamma}", "δ": r"\ensuremath{\delta}",
    "λ": r"\ensuremath{\lambda}", "σ": r"\ensuremath{\sigma}",
    "θ": r"\ensuremath{\theta}", "ε": r"\ensuremath{\epsilon}",
    "π": r"\ensuremath{\pi}", "μ": r"\ensuremath{\mu}",
    "Σ": r"\ensuremath{\Sigma}", "Δ": r"\ensuremath{\Delta}",
    "Λ": r"\ensuremath{\Lambda}", "Θ": r"\ensuremath{\Theta}",
    "Φ": r"\ensuremath{\Phi}", "Ψ": r"\ensuremath{\Psi}",
    "Ω": r"\ensuremath{\Omega}",
}


def escape_tex(s: str) -> str:
    """Escape LaTeX special characters and tame Unicode."""
    for k, v in UNICODE_TEXT_FIXES.items():
        s = s.replace(k, v)
    replacements = [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"), ("%", r"\%"), ("$", r"\$"),
        ("#", r"\#"), ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
        ("<", r"\textless{}"), (">", r"\textgreater{}"),
    ]
    s = s.replace("\\", "\x00")
    for k, v in replacements[1:]:
        s = s.replace(k, v)
    s = s.replace("\x00", r"\textbackslash{}")
    for k, v in UNICODE_MACRO_FIXES.items():
        s = s.replace(k, v)
    # Final fallback: any remaining non-ASCII gets stripped (LaTeX without unicode pkg can't render)
    s = "".join(c if ord(c) < 128 else "?" for c in s)
    return s


def walk_node(node, ctx) -> str:
    """Recursively convert a DOM node to LaTeX."""
    if isinstance(node, NavigableString):
        text = str(node)
        # Collapse runs of whitespace, but keep one space
        if not text.strip():
            return " " if text else ""
        return escape_tex(text)

    if not isinstance(node, Tag):
        return ""

    name = node.name.lower()

    # Skip rendering of these
    if name in {"script", "style", "noscript", "head", "meta", "link",
                "d-bibliography", "d-byline", "d-front-matter",
                "d-citation-list", "d-footnote-list", "d-appendix-section-list"}:
        return ""

    # TOC and chrome to drop
    cls = " ".join(node.get("class", []))
    nid = node.get("id", "")
    if nid in {"toc-sidebar", "appendix-toc-sidebar"}:
        return ""
    if "comment" in cls and node.find_parent("d-appendix"):
        # keep — substantive
        pass

    # Math
    if name == "d-math":
        latex = node.get_text()
        # block attribute means display math
        if node.has_attr("block") or "\\\\" in latex:
            return f"\\[{latex}\\]\n"
        return f"\\({latex}\\)"

    # Citations
    if name == "d-cite":
        key = node.get("key", "").strip()
        if not key:
            return ""
        keys = ",".join(k.strip() for k in key.split(","))
        return f"\\cite{{{keys}}}"

    # Footnotes
    if name == "d-footnote":
        inner = "".join(walk_node(c, ctx) for c in node.children).strip()
        return f"\\footnote{{{inner}}}"

    # Headings: distill uses h1 as title, h2 as section, h3 as subsection, h4 as subsubsection
    if name in {"h1", "h2", "h3", "h4"}:
        inner = "".join(walk_node(c, ctx) for c in node.children).strip()
        if not inner:
            return ""
        if name == "h1":
            return ""
        cmd = {"h2": "section", "h3": "subsection", "h4": "subsubsection"}[name]
        # Anthropic style: unnumbered + addcontentsline
        slug = re.sub(r"[^a-z0-9]+", "-", inner.lower()).strip("-")[:40]
        return (
            f"\n\\{cmd}*{{{inner}}}\\label{{sec:{slug}}}\n"
            f"\\addcontentsline{{toc}}{{{cmd}}}{{{inner}}}\n"
        )

    # Paragraphs
    if name == "p":
        inner = "".join(walk_node(c, ctx) for c in node.children).strip()
        if not inner:
            return ""
        return f"\n{inner}\n"

    # Lists
    if name in {"ul", "ol"}:
        env = "itemize" if name == "ul" else "enumerate"
        items = []
        for li in node.find_all("li", recursive=False):
            inner = "".join(walk_node(c, ctx) for c in li.children).strip()
            items.append(f"  \\item {inner}")
        if not items:
            return ""
        return f"\n\\begin{{{env}}}\n" + "\n".join(items) + f"\n\\end{{{env}}}\n"

    if name == "li":
        # Handled by ul/ol; if encountered alone, render inline
        return "".join(walk_node(c, ctx) for c in node.children)

    # Figures
    if name == "figure" or (name == "div" and "gdoc-image" in cls):
        return render_figure(node, ctx)

    # Images outside a figure
    if name == "img":
        src = node.get("src", "")
        local = download_image(src, ctx["base_url"], ctx["images_dir"])
        if not local:
            return ""
        return f"\n\\begin{{center}}\\includegraphics[max width=\\linewidth]{{{local}}}\\end{{center}}\n"

    # Tables
    if name == "table":
        return render_table(node, ctx)

    # Bold/italic/code
    if name in {"strong", "b"}:
        inner = "".join(walk_node(c, ctx) for c in node.children)
        return f"\\textbf{{{inner}}}"
    if name in {"em", "i"}:
        inner = "".join(walk_node(c, ctx) for c in node.children)
        return f"\\textit{{{inner}}}"
    if name == "code":
        inner = node.get_text()
        # Use \texttt with escaping for safety
        return f"\\texttt{{{escape_tex(inner)}}}"
    if name == "pre":
        inner = node.get_text()
        # verbatim, but escape just in case
        return f"\n\\begin{{verbatim}}\n{inner}\n\\end{{verbatim}}\n"

    # Links
    if name == "a":
        href = node.get("href", "")
        inner = "".join(walk_node(c, ctx) for c in node.children).strip()
        if href.startswith("#"):
            return inner  # internal anchor, just keep text
        if not href:
            return inner
        return f"\\href{{{href}}}{{{inner}}}"

    # Line break
    if name == "br":
        return "\\\\\n"
    if name == "hr":
        return "\n\\medskip\\hrule\\medskip\n"

    # Span / div / generic — recurse
    if name in {"span", "div", "section", "article", "main", "header", "footer",
                "d-article", "d-appendix", "d-title", "d-abstract"}:
        return "".join(walk_node(c, ctx) for c in node.children)

    # SVG: skip (would need rasterization)
    if name == "svg":
        return ""

    # Unknown: recurse children
    return "".join(walk_node(c, ctx) for c in node.children)


def render_figure(node, ctx) -> str:
    """Render a <figure> or .gdoc-image div as a LaTeX figure."""
    img = node.find("img")
    if not img:
        return ""
    src = img.get("src", "")
    local = download_image(src, ctx["base_url"], ctx["images_dir"])
    if not local:
        return ""
    cap_el = node.find("figcaption")
    caption = ""
    if cap_el:
        caption = "".join(walk_node(c, ctx) for c in cap_el.children).strip()
    if caption:
        return (
            f"\n\\begin{{figure}}[htbp]\n\\centering\n"
            f"\\includegraphics[max width=\\linewidth]{{{local}}}\n"
            f"\\caption{{{caption}}}\n\\end{{figure}}\n"
        )
    return (
        f"\n\\begin{{figure}}[htbp]\n\\centering\n"
        f"\\includegraphics[max width=\\linewidth]{{{local}}}\n\\end{{figure}}\n"
    )


def render_table(node, ctx) -> str:
    """Render an HTML table as a LaTeX tabular."""
    rows = []
    max_cols = 0
    for tr in node.find_all("tr"):
        cells = []
        for cell in tr.find_all(["td", "th"]):
            inner = "".join(walk_node(c, ctx) for c in cell.children).strip()
            # Strip newlines from cells
            inner = re.sub(r"\s+", " ", inner)
            cells.append(inner)
        if cells:
            rows.append(cells)
            max_cols = max(max_cols, len(cells))
    if not rows:
        return ""
    spec = "|" + "p{3cm}|" * max_cols
    out = ["\n\\begin{center}", f"\\begin{{tabular}}{{{spec}}}", "\\hline"]
    for r in rows:
        # Pad short rows
        while len(r) < max_cols:
            r.append("")
        out.append(" & ".join(r) + " \\\\ \\hline")
    out += ["\\end{tabular}", "\\end{center}\n"]
    return "\n".join(out)


def extract_metadata(soup) -> dict:
    """Pull title, authors, affiliations from d-byline / d-title."""
    meta = {"title": "", "authors": [], "affiliations": [], "date": ""}
    title_el = soup.find("d-title") or soup.find("title")
    if title_el:
        h1 = title_el.find("h1") if title_el.name == "d-title" else None
        if h1:
            meta["title"] = h1.get_text(strip=True)
        else:
            meta["title"] = title_el.get_text(strip=True)
    byline = soup.find("d-byline")
    if byline:
        text = byline.get_text("\n", strip=True)
        # Heuristic: lines starting with capitals are author lines
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            low = line.lower()
            if low in {"authors", "affiliations", "published"}:
                continue
            if any(c.isdigit() for c in line) and ("2024" in line or "2025" in line or "2026" in line):
                meta["date"] = line
            else:
                # Could be authors or affiliation
                meta.setdefault("byline_lines", []).append(line)
    return meta


def build_tex(soup, ctx, meta) -> str:
    """Build the full LaTeX document using the NeurIPS 2024 template (Anthropic style)."""
    body = walk_node(soup.find("d-article"), ctx)
    appendix = soup.find("d-appendix")
    appendix_tex = walk_node(appendix, ctx) if appendix else ""

    # Authors block — handle the transformer-circuits structure with
    # <div class="authors"><div>row1<br>row2<br>row3</div></div>
    author_rows = []
    affiliation = ""
    authors_div = soup.find("div", class_="authors")
    if authors_div:
        # Get the inner div (skip the h3 "Authors")
        for sub in authors_div.find_all("div"):
            # Split on <br>
            html = str(sub).replace("\n", "")
            # Walk children, accumulate text between br tags
            row_buf = ""
            for c in sub.children:
                if isinstance(c, Tag) and c.name == "br":
                    if row_buf.strip():
                        author_rows.append(row_buf.strip())
                    row_buf = ""
                elif isinstance(c, NavigableString):
                    row_buf += str(c)
                else:
                    row_buf += c.get_text("", strip=False)
            if row_buf.strip():
                author_rows.append(row_buf.strip())
            break  # only first inner div
    aff_div = soup.find("div", class_="affiliations")
    if aff_div:
        # Take the first non-h3 text content
        for sub in aff_div.find_all("div"):
            t = sub.get_text(" ", strip=True)
            if t:
                affiliation = t
                break

    title = escape_tex(meta["title"]) if meta["title"] else "Untitled"
    if author_rows:
        # Flatten all rows into a single list of names, then regroup into
        # rows of 4 (Anthropic NeurIPS style — keeps each line short enough
        # to fit the column width without overflowing).
        all_names = []
        for r in author_rows:
            for n in r.split(","):
                n = n.strip()
                if n:
                    all_names.append(n)
        # Convert trailing footnote markers (*, †, ‡) to a single \textsuperscript{...}
        def fmt(name: str) -> str:
            m = re.match(r"^(.*?)([*†‡§]+)$", name)
            if m:
                stem, markers = m.group(1).rstrip(), m.group(2)
                stem_tex = escape_tex(stem)
                # Map each marker char to its LaTeX form
                mtex = ""
                for ch in markers:
                    mtex += {"*": "*", "†": r"\dag", "‡": r"\ddag", "§": r"\S"}.get(ch, ch)
                return f"{stem_tex}\\textsuperscript{{{mtex}}}"
            return escape_tex(name)
        names_tex = [fmt(n) for n in all_names]
        per_row = 4
        rows_tex = []
        for i in range(0, len(names_tex), per_row):
            row = " \\quad ".join(names_tex[i:i+per_row])
            # First row gets bold from NeurIPS \author{}; subsequent rows need \bfseries
            if i > 0:
                row = r"\bfseries " + row
            rows_tex.append(row)
        authors_tex = " \\\\\n".join(rows_tex)
        if affiliation:
            authors_tex += f" \\\\[1.2ex]\n\\mdseries {escape_tex(affiliation)}"
    else:
        authors_tex = "Authors"

    # Web URL footnote
    web_url = ctx.get("base_url", "")
    web_note = ""
    if web_url:
        today = datetime.date.today().isoformat()
        web_note = (
            f"\\footnote{{\\textbf{{Unofficial archival LaTeX rendering}} "
            f"(compiled {today}) of the article originally published at "
            f"\\href{{{web_url}}}{{{web_url}}}, which we recommend for improved interactivity. "
            f"This PDF is not produced or endorsed by the original authors.}}"
        )

    preamble = r"""\documentclass{article}
\usepackage[T1]{fontenc}
\PassOptionsToPackage{numbers,square}{natbib}
\usepackage[final]{neurips_2024}

\usepackage{graphicx}
\usepackage{float}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue,citecolor=blue]{hyperref}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{listings}
\usepackage{microtype}
\usepackage{enumitem}
\setlist{nosep,leftmargin=*}
\usepackage[export]{adjustbox}

\lstset{
  basicstyle=\ttfamily\small,
  breaklines=true,
  columns=fullflexible,
  keepspaces=true,
}

\providecommand{\R}{\mathbb{R}}
\providecommand{\E}{\mathbb{E}}
\providecommand{\N}{\mathbb{N}}
\providecommand{\Z}{\mathbb{Z}}
"""
    title_block = f"""
\\title{{{title}}}
\\author{{{authors_tex}}}

\\begin{{document}}
\\setlength{{\\textfloatsep}}{{10pt plus 2pt minus 4pt}}
\\setlength{{\\floatsep}}{{8pt plus 2pt minus 4pt}}
\\setlength{{\\intextsep}}{{8pt plus 2pt minus 4pt}}
\\setlength{{\\abovecaptionskip}}{{6pt}}
\\setlength{{\\belowcaptionskip}}{{2pt}}

\\maketitle
"""

    # Abstract section: try to extract from first paragraphs before any h2
    abstract_tex = ""
    article = soup.find("d-article")
    if article:
        abs_paras = []
        for child in article.children:
            if isinstance(child, Tag) and child.name in {"h2", "h3"}:
                break
            if isinstance(child, Tag) and child.name == "p":
                abs_paras.append("".join(walk_node(c, ctx) for c in child.children).strip())
        if abs_paras:
            abstract_tex = (
                "\\begin{abstract}\n"
                + " ".join(abs_paras)
                + web_note
                + "\n\\end{abstract}\n\n"
            )

    # Strip abstract paragraphs from body so they don't appear twice
    if abstract_tex and article:
        # Re-walk article but skip leading <p> nodes before first heading
        body = walk_article_without_abstract(article, ctx)

    end = r"""
\bibliographystyle{plainnat}
\bibliography{bibliography}
\end{document}
"""

    return (
        preamble + title_block + abstract_tex + body
        + ("\n\\appendix\n" + appendix_tex if appendix_tex.strip() else "")
        + end
    )


def walk_article_without_abstract(article, ctx) -> str:
    """Walk d-article skipping the leading <p> nodes (which became the abstract)."""
    out = []
    seen_heading = False
    for child in article.children:
        if not seen_heading:
            if isinstance(child, Tag) and child.name in {"h2", "h3"}:
                seen_heading = True
            elif isinstance(child, Tag) and child.name == "p":
                continue  # skip — already in abstract
        out.append(walk_node(child, ctx))
    return "".join(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("url")
    p.add_argument("--out", default="/tmp/nla-pdf")
    args = p.parse_args()

    work = Path(args.out)
    work.mkdir(exist_ok=True)
    images_dir = work / "images"
    images_dir.mkdir(exist_ok=True)

    html_path = work / "rendered.html"
    if not html_path.exists():
        print(f"Dumping {args.url} ...", file=sys.stderr)
        fetch_rendered_html(args.url, html_path)

    soup = BeautifulSoup(html_path.read_text(), "lxml")
    base_url = args.url if args.url.endswith("/") else args.url + "/"
    base_url = base_url.split("#")[0]

    ctx = {"base_url": base_url, "images_dir": images_dir}
    meta = extract_metadata(soup)
    print(f"Title: {meta['title']}", file=sys.stderr)

    tex = build_tex(soup, ctx, meta)
    # Cleanup pass: strip stray \\ lines and collapse blank runs
    tex = re.sub(r"(?m)^\s*\\\\\s*$\n?", "", tex)
    tex = re.sub(r"\n{3,}", "\n\n", tex)
    # Remove \\ immediately before a sectioning command
    tex = re.sub(r"\\\\\s*(\n+\\(?:section|subsection|subsubsection))", r"\1", tex)
    tex_path = work / "paper.tex"
    tex_path.write_text(tex)

    # Copy bibliography if available
    bib_url = urljoin(base_url, "bibliography.bib")
    try:
        r = requests.get(bib_url, timeout=15)
        if r.ok:
            (work / "bibliography.bib").write_bytes(r.content)
    except Exception as e:
        print(f"  ! bibliography fetch: {e}", file=sys.stderr)

    print(f"Wrote {tex_path} ({tex_path.stat().st_size} bytes)", file=sys.stderr)
    print(f"Images: {len(list(images_dir.iterdir()))}", file=sys.stderr)


if __name__ == "__main__":
    main()
