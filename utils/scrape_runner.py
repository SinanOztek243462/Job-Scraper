"""
utils/scrape_runner.py — Tarama + NLP işleme iş mantığı.
UI'dan bağımsız: LinkedIn'den ilan çeker, filtreler, NLP ile işler, DB'ye kaydeder.
"""

import os
import json
import streamlit as st

from scraper import scrape_linkedin_jobs
from nlp_extractor import SkillExtractor
from analyzer import extract_experience
import database as db
from config import SEEN_JOBS_FILE


def build_query_string(must_have: str, or_have: str, not_have: str) -> str:
    """Kullanıcının girdiği kelimeleri mantıksal LinkedIn sorgusuna çevirir."""
    def parse_words(text):
        if not text: return []
        return [w.strip() for w in text.split(",") if w.strip()]

    must_list = parse_words(must_have)
    or_list = parse_words(or_have)
    not_list = parse_words(not_have)

    query_parts = []

    if or_list:
        if len(or_list) > 1:
            query_parts.append("(" + " OR ".join([f'{w}' for w in or_list]) + ")")
        else:
            query_parts.append(f'{or_list[0]}')

    if must_list:
        query_parts.append(" AND ".join([f'{w}' for w in must_list]))

    query_str = " AND ".join(query_parts)

    if not_list:
        not_str = " ".join([f'NOT {w}' for w in not_list])
        if query_str:
            query_str += " " + not_str
        else:
            query_str = not_str

    return query_str


def build_location(country: str, city: str) -> str:
    """Ülke + şehir bilgisinden LinkedIn location string'i üretir."""
    if country in ("Worldwide", "Europe"):
        return country
    return f"{city}, {country}" if city != "Hepsi" else country


def load_seen_urls() -> set:
    """Daha önce görülmüş ilan URL'lerini dosyadan yükler."""
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r", encoding="utf-8") as f:
            try:
                return set(json.load(f))
            except Exception:
                return set()
    return set()


def save_seen_urls(seen: set) -> None:
    """Görülmüş URL setini dosyaya yazar."""
    with open(SEEN_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f)


def apply_filters(jobs: list, must_include: str, must_exclude: str, title_must_include: str = "", title_must_exclude: str = "") -> list:
    """İlan listesini include/exclude filtrelerine göre süzer."""
    inc = [w.strip().lower() for w in must_include.split(",") if w.strip()] if must_include else []
    exc = [w.strip().lower() for w in must_exclude.split(",") if w.strip()] if must_exclude else []
    t_inc = [w.strip().lower() for w in title_must_include.split(",") if w.strip()] if title_must_include else []
    t_exc = [w.strip().lower() for w in title_must_exclude.split(",") if w.strip()] if title_must_exclude else []
    
    result = []
    for job in jobs:
        text = (job.get("title", "") + " " + job.get("description", "")).lower()
        title_text = job.get("title", "").lower()
        
        # Title filters
        if t_inc and not all(w in title_text for w in t_inc):
            continue
        if t_exc and any(w in title_text for w in t_exc):
            continue
            
        # Description (global) filters
        if inc and not all(w in text for w in inc):
            continue
        if exc and any(w in text for w in exc):
            continue
            
        result.append(job)
    return result


def process_and_save_jobs(jobs: list, profile: str, progress_bar=None) -> tuple:
    """
    İlanları NLP ile işler ve DB'ye kaydeder.
    Döner: (job_skills_list, seniorities, experience_years, saved_count)
    """
    extractor = SkillExtractor()
    job_skills_list = []
    seniorities = []
    experience_years = []
    saved_count = 0

    for idx, job in enumerate(jobs):
        result = extractor.extract_skills(job.get("description", ""))
        skills = result.get("skills", []) if isinstance(result, dict) else result
        qualifications_text = result.get("qualifications_text", "") if isinstance(result, dict) else ""
        
        job["extracted_skills"] = skills
        job["qualifications_text"] = qualifications_text

        seniority, min_years = extract_experience(job.get("title", ""), job.get("description", ""))
        job["seniority_level"] = seniority
        job["experience_years"] = min_years

        seniorities.append(seniority)
        if min_years is not None:
            experience_years.append(min_years)

        db.save_job(job, profile)
        saved_count += 1

        if skills:
            job_skills_list.append(skills)

        if progress_bar is not None:
            progress_bar.progress((idx + 1) / len(jobs))

    return job_skills_list, seniorities, experience_years, saved_count


def run_scrape_for_profile(profile: str, show_ui: bool = True) -> int:
    """
    Belirtilen profile ait kayıtlı loadout ayarlarıyla otomatik tarama yapar.
    Döner: kaydedilen ilan sayısı.
    """
    cfg = db.get_loadout_config(profile)
    if not cfg:
        return 0

    query = build_query_string(cfg.get("must_have", ""), cfg.get("or_have", ""), cfg.get("not_have", ""))

    location = build_location(cfg.get("country", "Worldwide"), cfg.get("city", "Hepsi"))
    limit = cfg.get("limit_jobs", 20)
    delay = float(cfg.get("delay_seconds", 2.0))
    must_include = cfg.get("must_include", "")
    must_exclude = cfg.get("must_exclude", "")
    title_must_include = cfg.get("title_must_include", "")
    title_must_exclude = cfg.get("title_must_exclude", "")

    seen_urls = load_seen_urls()

    if show_ui:
        with st.spinner(f"🔁 '{profile}' için tarama yapılıyor..."):
            raw_jobs = scrape_linkedin_jobs(
                query, location=location, limit=limit,
                seen_urls=seen_urls, include_seen=False, delay=delay
            )
    else:
        raw_jobs = scrape_linkedin_jobs(
            query, location=location, limit=limit,
            seen_urls=seen_urls, include_seen=False, delay=delay
        )

    if not raw_jobs:
        return 0

    new_seen = seen_urls.copy()
    for job in raw_jobs:
        new_seen.add(job["url"])
    save_seen_urls(new_seen)

    filtered = apply_filters(raw_jobs, must_include, must_exclude, title_must_include, title_must_exclude)
    _, _, _, saved = process_and_save_jobs(filtered, profile)
    return saved
