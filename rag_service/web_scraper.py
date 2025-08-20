import argparse
import os
import re
import time
import unicodedata
from pathlib import Path
from typing import Iterable, List, Optional, Set, Tuple, Dict

import requests
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://www.mp.pl/pacjent/leki/"
MEDICINE_PATH_FRAGMENT = "/pacjent/leki/lek/"
DATA_DIR = Path(__file__).resolve().parent / "data"


# ----------------------------- HTTP -----------------------------

def fetch_html(url: str, timeout: int = 20) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/126.0 Safari/537.36"
        )
    }
    resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.text


def absolute_url(href: str) -> Optional[str]:
    if not href:
        return None
    if href.startswith(("http://", "https://")):
        return href
    if href.startswith("/"):
        return f"https://www.mp.pl{href}"
    if href.startswith("./"):
        return BASE_URL.rstrip("/") + href[1:]
    if href.startswith("#") or ":" in href:
        return None
    return BASE_URL.rstrip("/") + "/" + href


# --------------------------- Discovery --------------------------

def discover_letter_pages(index_html: str) -> List[str]:
    soup = BeautifulSoup(index_html, "html.parser")
    candidate_urls: Set[str] = set()
    for a in soup.find_all("a"):
        href = a.get("href")
        url = absolute_url(href)
        if not url:
            continue
        if "/pacjent/leki/" in url and MEDICINE_PATH_FRAGMENT not in url:
            candidate_urls.add(url.split("#")[0])
    candidate_urls.add(BASE_URL)
    prioritized = [u for u in candidate_urls if any(x in u for x in ["letter", "litera", "-od-a-do-z", "/leki/"])]
    return sorted(set(prioritized))


def extract_medicine_links(listing_html: str) -> List[str]:
    soup = BeautifulSoup(listing_html, "html.parser")
    links: Set[str] = set()
    for ul in soup.select("ul.list-unstyled.drug-list"):
        for a in ul.find_all("a", href=True):
            url = absolute_url(a["href"])
            if url and MEDICINE_PATH_FRAGMENT in url:
                links.add(url)
    if not links:
        for a in soup.find_all("a", href=True):
            url = absolute_url(a["href"])
            if url and MEDICINE_PATH_FRAGMENT in url:
                links.add(url)
    return sorted(links)


# --------------------------- Utilities --------------------------

def slugify(filename: str) -> str:
    normalized = unicodedata.normalize("NFKD", filename)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = re.sub(r"[^A-Za-z0-9\-_. ]+", "", ascii_only).strip()
    cleaned = re.sub(r"[\s]+", "_", cleaned)
    cleaned = cleaned.strip("._")
    return cleaned or "medicine"


def clean_text(s: str) -> str:
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\s+\n", "\n", s)
    return s.strip()


# ---------------------- Structure-aware parsing -----------------

def extract_main_container(soup: BeautifulSoup) -> Tag:
    cont = soup.select_one("div.drug-description")
    if cont:
        return cont
    for sel in ["article", "div.article-content", "div#content", "main", "div.content"]:
        found = soup.select_one(sel)
        if found:
            return found
    return soup.body or soup


def _norm(s: str) -> str:
    """Lowercase, strip, collapse spaces, remove diacritics."""
    if s is None:
        return ""
    s = s.replace("\xa0", " ").strip()
    s = re.sub(r"\s+", " ", s)
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.lower()


def _canon_key(s: str) -> str:
    """Map various header spellings/typos to canonical keys."""
    s = _norm(s).rstrip(":")
    # handle common variants / typos
    s = s.replace("refudacji", "refundacji")   # site typo
    if "nazwa" in s:
        return "nazwa preparatu"
    if s.startswith("postac") or "dawka" in s or "opakowanie" in s:
        return "postać; dawka; opakowanie"
    if "producent" in s:
        return "producent"
    if "cena 100" in s or (s.startswith("cena") and "refund" not in s):
        return "cena 100%"
    if "refundac" in s:
        return "cena po refundacji"
    return s  # fallback


def _cell_text(td: Tag) -> str:
    """Extract readable text from a td, preferring .div-cell; keep semicolons/linebreaks."""
    target = td.select_one(".div-cell") or td
    
    # Special handling for refundacja column - extract only the price links
    # Check if this is a refundacja column by looking at data-title or checking for tooltip-lek links
    is_refundacja = (
        "refundacji" in str(td.get("data-title", "")).lower() or
        "refudacji" in str(td.get("data-title", "")).lower() or
        target.find("a", class_="tooltip-lek") is not None
    )
    
    if is_refundacja:
        # Look for tooltip-lek links which contain the actual prices
        price_links = target.find_all("a", class_="tooltip-lek")
        if price_links:
            prices = []
            for link in price_links:
                # Get the text content of the link (the price)
                price_text = link.get_text(separator=" ", strip=True)
                if price_text:
                    # Clean up the price text - remove extra whitespace and newlines
                    price_text = re.sub(r'\s+', ' ', price_text).strip()
                    # Only keep the price part (before any additional text)
                    if 'zł' in price_text:
                        # Extract just the price and currency
                        price_match = re.search(r'([\d,]+)\s*zł', price_text)
                        if price_match:
                            prices.append(f"{price_match.group(1)} zł")
                        else:
                            prices.append(price_text)
                    else:
                        prices.append(price_text)
            if prices:
                return "; ".join(prices)
    
    # Preserve line breaks between inline blocks; collapse excessive spaces
    text = target.get_text(separator="\n", strip=True)
    text = text.replace("\xa0", " ")
    # compact multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def parse_table_responsive(container: Tag) -> Dict[str, object]:
    """
    Parse the .table-responsive grid into:
      { "headers": [canon...], "rows": [ {canon_col: value, ...}, ... ] }
    Robust to: .table-postaci, div-cell wrappers, data-title, typos.
    """
    out = {"headers": [], "rows": []}
    wrap = container.select_one(".table-responsive")
    if not wrap:
        return out

    table = wrap.select_one("table")  # class may be 'table-postaci'
    if not table:
        return out

    # 1) headers from thead if present
    headers_raw: List[str] = []
    thead = table.find("thead")
    if thead:
        ths = thead.find_all(["th", "td"])
        headers_raw = [th.get_text(" ", strip=True) for th in ths]

    headers_canon = [_canon_key(h) for h in headers_raw] if headers_raw else []

    # 2) rows from tbody
    tbody = table.find("tbody") or table
    for tr in tbody.find_all("tr"):
        tds = tr.find_all("td")
        if not tds:
            continue

        row: Dict[str, str] = {}
        for idx, td in enumerate(tds):
            # prefer header by index; else use data-title for that cell
            key = ""
            if idx < len(headers_canon) and headers_canon[idx]:
                key = headers_canon[idx]
            else:
                key = _canon_key(td.get("data-title", ""))

            val = _cell_text(td)
            if not key:
                # still try data-title
                key = _canon_key(td.get("data-title", "")) or f"col_{idx}"

            # merge if duplicate keys (rare): join with newline
            if key in row and val:
                row[key] = (row[key] + "\n" + val).strip()
            else:
                row[key] = val

        out["rows"].append(row)

    # Ensure canonical header order for rendering later
    canon_cols = [
        "nazwa preparatu",
        "postać; dawka; opakowanie",
        "producent",
        "cena 100%",
        "cena po refundacji",
    ]
    # Build final headers list: keep canonical first, then any extras we saw
    seen_extra = [k for r in out["rows"] for k in r.keys() if k not in canon_cols]
    extras_ordered = []
    for k in seen_extra:
        if k not in extras_ordered:
            extras_ordered.append(k)
    out["headers"] = canon_cols + extras_ordered
    return out


def _md_escape_pipes(s: str) -> str:
    return s.replace("|", r"\|")


def render_price_table(table_data: Dict[str, object]) -> str:
    rows = table_data.get("rows", [])
    if not rows:
        return ""

    # We will render only the canonical 5 columns (others can be appended if needed)
    cols = [
        "nazwa preparatu",
        "postać; dawka; opakowanie",
        "producent",
        "cena 100%",
        "cena po refundacji",
    ]
    header = " | ".join([c.title() if c != "postać; dawka; opakowanie" else "Postać; dawka; opakowanie" for c in cols])

    lines = []
    for r in rows:
        line_vals = []
        for c in cols:
            val = r.get(c, "")
            # Clean up the value for markdown table
            if val:
                # Replace newlines with semicolons for better readability in markdown tables
                val = val.replace("\n", "; ")
                # Clean up multiple semicolons and spaces
                val = re.sub(r';+', ';', val)
                val = re.sub(r'\s+', ' ', val).strip()
                val = val.strip('; ')
            # Escape pipes for markdown
            val = _md_escape_pipes(val)
            line_vals.append(val)
        lines.append(" | ".join(line_vals))

    return header + "\n" + "\n".join(lines) + "\n\n"


def h1_title(soup: BeautifulSoup, parsed_name: str) -> str:
    h1 = soup.find("h1")
    if h1:
        t = clean_text(h1.get_text(" ", strip=True))
        if t and len(t) <= 120:
            return t
    return parsed_name or "Lek (brak nazwy)"


def render_unique_list(items: List[str]) -> str:
    seen = set()
    out = []
    for it in items:
        it = it.strip()
        if not it or it in seen:
            continue
        seen.add(it)
        out.append(f"- {it}")
    return "\n".join(out) + ("\n\n" if out else "")


def convert_article_to_markdown(soup: BeautifulSoup, source_url: str) -> Tuple[str, str]:
    container = extract_main_container(soup)

    # parse full variants table
    table = parse_table_responsive(container)

    # derive title
    first_name = ""
    if table.get("rows"):
        r0 = table["rows"][0]
        first_name = r0.get("nazwa preparatu") or r0.get("nazwa") or ""
    title = h1_title(soup, first_name)

    md_parts: List[str] = [f"# {title}\n\n", f"Źródło: {source_url}\n\n"]

    # ## Zestawienie preparatów -> full variations table
    price_table_md = render_price_table(table)
    if price_table_md:
        md_parts.append("## Zestawienie preparatów\n\n")
        md_parts.append(price_table_md)

    # ## Postać -> unique list of "Postać; dawka; opakowanie"
    if table.get("rows"):
        postac_list = [r.get("postać; dawka; opakowanie") or r.get("postac; dawka; opakowanie") or r.get("postać") or r.get("postac") or ""
                       for r in table["rows"]]
        postac_md = render_unique_list([p for p in postac_list if p])
        if postac_md.strip():
            md_parts.append("## Postać\n\n")
            md_parts.append(postac_md)

    # ## Refundacja -> per-variant bullets (variant → refund price)
    if table.get("rows"):
        refund_lines = []
        for r in table["rows"]:
            variant = r.get("postać; dawka; opakowanie") or r.get("postac; dawka; opakowanie") or r.get("postać") or r.get("postac") or ""
            refund = r.get("cena po refundacji") or r.get("refundacja") or ""
            if refund:
                label = variant or (r.get("nazwa preparatu") or "")
                refund_lines.append(f"- {label}: {refund}")
        if refund_lines:
            md_parts.append("## Refundacja\n\n")
            md_parts.append("\n".join(refund_lines) + "\n\n")

    # Other content sections: each <h2> + nearest .item-content
    for h2 in container.find_all("h2"):
        heading = clean_text(h2.get_text(" ", strip=True))
        # skip the "Inne preparaty..." here; handle later
        if re.search(r"inne\s+preparaty", heading, flags=re.I):
            continue

        # find nearest item-content following this h2
        content_div = None
        nxt = h2
        for _ in range(6):
            nxt = nxt.next_sibling
            if not nxt:
                break
            if isinstance(nxt, Tag):
                if nxt.name == "div" and "item-content" in (nxt.get("class") or []):
                    content_div = nxt
                    break
                inner = nxt.select_one("div.item-content")
                if inner:
                    content_div = inner
                    break
        if not content_div:
            content_div = h2.find_next("div", class_="item-content")

        body = clean_text(content_div.get_text("\n", strip=True)) if content_div else ""
        if heading:
            md_parts.append(f"## {heading}\n\n")
            if body:
                md_parts.append(body + "\n\n")

    # Inne preparaty … (links)
    other_h2 = None
    for h2 in container.find_all("h2"):
        if re.search(r"inne\s+preparaty", h2.get_text(" ", strip=True), flags=re.I):
            other_h2 = h2
            break
    if other_h2:
        plist = other_h2.find_next("p", class_="other-drugs")
        links = []
        if plist:
            for a in plist.find_all("a", href=True):
                txt = clean_text(a.get_text(" ", strip=True))
                url = absolute_url(a["href"])
                if txt and url:
                    links.append(f"- [{txt}]({url})")
        if links:
            md_parts.append("## " + clean_text(other_h2.get_text(" ", strip=True)) + "\n\n")
            md_parts.append("\n".join(links) + "\n\n")

    markdown = "".join(md_parts).strip() + "\n"
    return title, markdown


# --------------------------- Persist ----------------------------

def save_markdown(title: str, markdown: str) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = slugify(title) + ".md"
    path = DATA_DIR / filename
    path.write_text(markdown, encoding="utf-8")
    return path


# --------------------------- Orchestration ----------------------

def scrape_all(
    sleep_between_requests: float = 0.5,
    overwrite: bool = False,
    limit: Optional[int] = None,
) -> None:
    print("Fetching index page …")
    index_html = fetch_html(BASE_URL)

    letter_pages = discover_letter_pages(index_html) or [BASE_URL]
    print(f"Discovered {len(letter_pages)} listing pages")

    medicine_links: List[str] = []
    seen: Set[str] = set()
    for i, listing_url in enumerate(letter_pages, start=1):
        try:
            html = fetch_html(listing_url)
            links = extract_medicine_links(html)
            new_links = [u for u in links if u not in seen]
            seen.update(new_links)
            medicine_links.extend(new_links)
            print(f"[{i}/{len(letter_pages)}] {listing_url} → +{len(new_links)} (total {len(medicine_links)})")
            time.sleep(sleep_between_requests)
        except Exception as e:
            print(f"[WARN] Failed to fetch listing {listing_url}: {e}")

    if limit is not None:
        medicine_links = medicine_links[: max(0, int(limit))]

    print(f"Scraping {len(medicine_links)} medicine pages…")

    count = 0
    for idx, url in enumerate(medicine_links, start=1):
        try:
            html = fetch_html(url)
            soup = BeautifulSoup(html, "html.parser")

            # Title for filename; we'll also re-derive inside convert for correctness
            page_h1 = soup.find("h1")
            prelim_title = clean_text(page_h1.get_text(" ", strip=True)) if page_h1 else f"medicine_{idx}"
            filepath = DATA_DIR / (slugify(prelim_title) + ".md")
            if filepath.exists() and not overwrite:
                print(f"[{idx}/{len(medicine_links)}] SKIP exists: {filepath.name}")
                continue

            title, md = convert_article_to_markdown(soup, url)
            saved_path = save_markdown(title, md)
            count += 1
            print(f"[{idx}/{len(medicine_links)}] Saved: {saved_path.name}")
        except Exception as e:
            print(f"[WARN] Failed to process {url}: {e}")
        finally:
            time.sleep(sleep_between_requests)

    print(f"Done. New/updated files: {count}")


def main():
    parser = argparse.ArgumentParser(description="Scrape mp.pl leki and save markdowns to ./data (header-aware)")
    parser.add_argument("--sleep", type=float, default=0.5, help="Seconds to sleep between requests")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .md files")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of medicines to scrape")
    args = parser.parse_args()

    scrape_all(
        sleep_between_requests=args.sleep,
        overwrite=args.overwrite,
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
