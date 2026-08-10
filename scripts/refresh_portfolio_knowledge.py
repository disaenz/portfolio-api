#!/usr/bin/env python3
"""Build the AI portfolio context from the deployed site and Dropbox resume.

The refresh is operator-run, so chat requests remain fast and do not scrape
Dropbox or call OpenAI for every visitor.
"""

from __future__ import annotations

import asyncio
import hashlib
import io
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from pypdf import PdfReader

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from database import AsyncSessionLocal  # noqa: E402
from repositories.portfolio_knowledge_repository import (  # noqa: E402
    get_current_source_hash,
    save_knowledge,
)

SITE_URL = os.getenv("PORTFOLIO_SITE_URL", "https://daniel-saenz.com")
RESUME_URL = os.getenv("PORTFOLIO_RESUME_URL")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TIMEOUT_SECONDS = 30
MAX_SCRIPT_BYTES = 2_000_000
LOCAL_REFERENCE_PATH = Path(__file__).resolve().parents[1] / "data" / "portfolio_knowledge.json"

OUTPUT_SHAPE = {
    "summary": "string",
    "about": {"bio": ["string"], "personal_interests": ["string"], "resume_link": "string"},
    "experience": [{"company": "string", "role": "string", "location": "string", "start": "string", "end": "string", "responsibilities": ["string"]}],
    "education": [{"institution": "string", "degree": "string", "years": "string", "gpa": "string or omit"}],
    "certifications": ["string"],
    "skills": {"category_name": ["string"]},
    "languages": ["string"],
    "projects": [{"name": "string", "description": "string", "role": "string", "impact": "string", "features": ["string"], "tech_stack": ["string"]}],
}


def show_progress(step: int, total: int, message: str) -> None:
    """Render a simple dependency-free progress bar for the operator."""
    width = 24
    completed = round(width * step / total)
    bar = "#" * completed + "-" * (width - completed)
    percent = round(100 * step / total)
    print(f"[{bar}] {percent:>3}%  {message}", flush=True)


def download(url: str) -> requests.Response:
    response = requests.get(url, timeout=TIMEOUT_SECONDS, headers={"User-Agent": "portfolio-knowledge-refresh/1.0"})
    response.raise_for_status()
    return response


def is_trusted_dropbox_url(url: str) -> bool:
    """Allow only HTTPS URLs hosted by Dropbox, never a matching URL path."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    return parsed.scheme == "https" and (host == "dropbox.com" or host.endswith(".dropbox.com"))


def dropbox_download_url(url: str) -> str:
    """Turn a public Dropbox share URL into a direct-download URL."""
    if not is_trusted_dropbox_url(url):
        raise ValueError("Resume URL must use an HTTPS Dropbox host")

    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    query["dl"] = ["1"]
    return urlunparse(parsed._replace(query=urlencode(query, doseq=True)))


def read_site(site_url: str) -> tuple[str, str | None]:
    html = download(site_url).text
    soup = BeautifulSoup(html, "html.parser")
    resume_url = RESUME_URL
    for link in soup.find_all("a", href=True):
        href = urljoin(site_url, link["href"])
        label = link.get_text(" ", strip=True).lower()
        if is_trusted_dropbox_url(href) and ("resume" in label or ".pdf" in href.lower()):
            resume_url = href
            break

    # Vite SPAs put their copy in same-origin JavaScript assets. Including those
    # makes this work with the hosted client-rendered site as well as static HTML.
    asset_text = []
    site_host = urlparse(site_url).netloc
    for script in soup.find_all("script", src=True):
        asset_url = urljoin(site_url, script["src"])
        if urlparse(asset_url).netloc != site_host:
            continue
        try:
            asset_text.append(download(asset_url).text[:MAX_SCRIPT_BYTES])
        except requests.RequestException as error:
            print(f"Warning: could not read site asset {asset_url}: {error}", file=sys.stderr)

    combined_assets = "\n\n".join(asset_text)
    if not resume_url:
        # The resume link in this React/Vite site is compiled into an asset,
        # rather than present in the initial HTML response.
        for match in re.finditer(r"https?://[^\"'\\ ]*dropbox\.com[^\"'\\ ]*", combined_assets):
            candidate = match.group(0).replace("\\u0026", "&")
            if is_trusted_dropbox_url(candidate) and ".pdf" in candidate.lower():
                resume_url = candidate
                break

    return "\n\n".join([soup.get_text(" ", strip=True), combined_assets]), resume_url


def read_resume(resume_url: str | None) -> str:
    if not resume_url:
        return ""
    response = download(dropbox_download_url(resume_url))
    reader = PdfReader(io.BytesIO(response.content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def build_knowledge(site_text: str, resume_text: str, resume_url: str | None) -> dict:
    client = OpenAI()
    prompt = f"""Create a factual JSON knowledge document for a portfolio Q&A assistant.
Use only the supplied source material. Prefer the resume for employment dates and details,
and the website for projects and public-facing descriptions. Do not invent facts. Omit an
unknown optional field. Output JSON only, with this exact broad shape:
{json.dumps(OUTPUT_SHAPE)}

Site source:
{site_text[:350_000]}

Resume source:
{resume_text[:300_000]}

The public resume URL is: {resume_url or ''}
"""
    response = client.responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=12_000,
        text={"format": {"type": "json_object"}},
    )
    knowledge = json.loads(response.output_text)
    if not isinstance(knowledge, dict):
        raise ValueError("OpenAI did not return a JSON object for portfolio knowledge")

    # Keep the same top-level contract as the former portfolio_knowledge.json,
    # even when a source does not contain a particular category.
    knowledge.setdefault("summary", "")
    knowledge.setdefault("about", {})
    knowledge["about"].setdefault("bio", [])
    knowledge["about"].setdefault("personal_interests", [])
    knowledge["about"].setdefault("resume_link", resume_url or "")
    for key in ("experience", "education", "certifications", "languages", "projects"):
        knowledge.setdefault(key, [])
    knowledge.setdefault("skills", {})
    return knowledge


async def refresh(*, write_local_reference: bool) -> dict[str, str]:
    total_steps = 5
    show_progress(1, total_steps, "Reading the deployed portfolio site...")
    site_text, discovered_resume_url = read_site(SITE_URL)

    show_progress(2, total_steps, "Downloading and extracting the Dropbox resume...")
    resume_text = read_resume(discovered_resume_url)

    source_hash = hashlib.sha256((site_text + resume_text).encode("utf-8")).hexdigest()
    show_progress(3, total_steps, "Checking whether the source material changed...")
    async with AsyncSessionLocal() as db:
        if await get_current_source_hash(db) == source_hash:
            show_progress(5, total_steps, "No source changes found; OpenAI generation skipped.")
            return {"status": "unchanged", "source_hash": source_hash}

    show_progress(3, total_steps, f"Generating portfolio knowledge with {MODEL}...")
    knowledge = build_knowledge(site_text, resume_text, discovered_resume_url)

    show_progress(4, total_steps, "Saving portfolio knowledge to PostgreSQL...")
    async with AsyncSessionLocal() as db:
        await save_knowledge(
            db,
            content=knowledge,
            source_site_url=SITE_URL,
            source_resume_url=discovered_resume_url,
            source_hash=source_hash,
        )

    if write_local_reference:
        show_progress(5, total_steps, "Writing the local reference file...")
        LOCAL_REFERENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOCAL_REFERENCE_PATH.write_text(
            json.dumps(knowledge, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
    else:
        show_progress(5, total_steps, "Refresh completed.")

    print("Portfolio knowledge refreshed in PostgreSQL.")
    if write_local_reference:
        print(f"Local reference written to {LOCAL_REFERENCE_PATH}.")
        print(json.dumps(knowledge, indent=2, ensure_ascii=False))
    return {"status": "refreshed", "source_hash": source_hash}


async def main() -> None:
    await refresh(write_local_reference=True)


if __name__ == "__main__":
    asyncio.run(main())
