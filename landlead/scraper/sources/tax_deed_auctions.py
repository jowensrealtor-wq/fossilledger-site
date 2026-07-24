"""Tax-deed / tax-lien auction notice scraper.

County treasurer / sheriff-sale and tax-deed auction postings are public notice
pages. Layouts vary wildly by county, so this scraper is a *resilient generic
HTML harvester*: it pulls the notice page and extracts anything that looks like
a parcel/APN reference plus surrounding context (sale date, amount owed). It is
intentionally conservative — it never guesses a lead into existence without an
APN-like token.

For a JS-rendered auction portal, set the county's auction entry to use
Playwright by adding `render_js: true`; if Playwright isn't installed the
scraper logs a skip rather than crashing (see COMPLIANCE.md — we don't try to
force our way past anything).
"""
from __future__ import annotations

import re
from typing import Iterable

from bs4 import BeautifulSoup

from scraper.base import BaseScraper

# Common parcel/APN token shapes across Eastern US counties: 3-6 dash/dot/space
# separated numeric segments, each 2-6 digits (segments can be 5+ digits, e.g.
# the sub-parcel '00450'), so we must not cap segment width too low.
APN_TOKEN = re.compile(r"\b\d{2,6}(?:[-\.\s]\d{2,6}){2,5}\b")
MONEY_RE = re.compile(r"\$\s?[\d,]+(?:\.\d{2})?")
# Sale dates: slash form (08/12/2026) or month-name form. We deliberately do NOT
# accept a dash-only numeric date here, because dash dates collide with the
# dash-formatted parcel numbers on the same line; the parcel span is removed
# before this runs anyway (see fetch()).
DATE_RE = re.compile(r"\b(?:\d{1,2}/\d{1,2}/\d{2,4}|"
                     r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b", re.I)


class TaxDeedAuctionScraper(BaseScraper):
    source = "tax_deed_auctions"

    def __init__(self, county_cfg: dict):
        super().__init__(county_cfg)
        cfg = (county_cfg.get("sources") or {}).get("tax_deed_auctions") or {}
        self.url = cfg.get("url")
        self.render_js = bool(cfg.get("render_js"))

    def _get_html(self) -> str:
        if self.render_js:
            return self._get_html_playwright()
        resp = self.get(self.url)
        if resp is None or resp.status_code != 200:
            raise RuntimeError(f"Auction page returned "
                               f"{getattr(resp, 'status_code', 'n/a')}")
        return resp.text

    def _get_html_playwright(self) -> str:
        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:
            raise PermissionError(
                "render_js requested but Playwright is not installed; skipping "
                f"({exc}). `pip install playwright && playwright install chromium`."
            )
        if not self._robots_ok(self.url):
            raise PermissionError(f"robots.txt disallows {self.url}")
        self._throttle(self.url)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=self.settings.USER_AGENT)
            page.goto(self.url, timeout=self.settings.TIMEOUT_SECONDS * 1000)
            page.wait_for_load_state("networkidle")
            html = page.content()
            browser.close()
        return html

    def fetch(self) -> Iterable[dict]:
        if not self.url:
            raise ValueError(f"No tax_deed_auctions.url configured for {self.county}")

        html = self._get_html()
        soup = BeautifulSoup(html, "lxml")

        out: list[dict] = []
        seen: set[str] = set()

        # Prefer structured rows (tables / list items) so context stays with APN.
        blocks = soup.find_all(["tr", "li", "div", "p"])
        for block in blocks:
            text = " ".join(block.get_text(" ", strip=True).split())
            if not text:
                continue
            apn_match = APN_TOKEN.search(text)
            if not apn_match:
                continue
            apn = apn_match.group(0).strip()
            key = re.sub(r"[-\.\s]", "", apn)
            if key in seen:
                continue
            seen.add(key)
            # Strip the APN span so a dash-formatted parcel can't be misread as a
            # date/amount, then look for the sale date and amount in what's left.
            remainder = text.replace(apn, " ")
            money = MONEY_RE.search(remainder)
            date = DATE_RE.search(remainder)
            amount = None
            if money:
                try:
                    amount = float(money.group(0).replace("$", "").replace(",", "").strip())
                except ValueError:
                    amount = None
            out.append({
                "apn": apn,
                "tax_delinquent": True,
                "tax_delinquent_amount": amount,
                "sale_date": date.group(0) if date else None,
                "context": text[:400],
            })
        return out
