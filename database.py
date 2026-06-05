"""
database.py — SQLite veritabanı arayüzü.
Tüm DB işlemleri bu tek dosyada toplanmıştır.
"""

import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"


@contextmanager
def _connect():
    """Context manager: bağlantı aç, kapat."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Schema
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """Veritabanı tablolarını oluşturur (yoksa)."""
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS jobs (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                url              TEXT    UNIQUE,
                title            TEXT,
                company          TEXT,
                location         TEXT,
                description      TEXT,
                extracted_skills TEXT,
                experience_years INTEGER,
                seniority_level  TEXT,
                search_profile   TEXT,
                date_scraped     DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS loadouts (
                name          TEXT PRIMARY KEY,
                query_rows    TEXT,
                must_include  TEXT,
                must_exclude  TEXT,
                country       TEXT,
                city          TEXT,
                limit_jobs    INTEGER,
                delay_seconds REAL
            );
            CREATE TABLE IF NOT EXISTS api_settings (
                id             INTEGER PRIMARY KEY CHECK (id = 1),
                provider       TEXT DEFAULT 'spacy',
                api_key        TEXT DEFAULT '',
                model_name     TEXT DEFAULT ''
            );
        """)
        try:
            conn.execute("ALTER TABLE loadouts ADD COLUMN must_have TEXT DEFAULT ''")
            conn.execute("ALTER TABLE loadouts ADD COLUMN or_have TEXT DEFAULT ''")
            conn.execute("ALTER TABLE loadouts ADD COLUMN not_have TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE loadouts ADD COLUMN auto_scan BOOLEAN DEFAULT 0")
            conn.execute("ALTER TABLE loadouts ADD COLUMN auto_scan_interval INTEGER DEFAULT 60")
            conn.execute("ALTER TABLE loadouts ADD COLUMN last_scan_time DATETIME DEFAULT NULL")
        except sqlite3.OperationalError:
            pass
        try:
            conn.execute("ALTER TABLE loadouts ADD COLUMN title_must_include TEXT DEFAULT ''")
            conn.execute("ALTER TABLE loadouts ADD COLUMN title_must_exclude TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass
            
        conn.execute("""
            CREATE TABLE IF NOT EXISTS skill_categories (
                skill TEXT PRIMARY KEY,
                category TEXT
            )
        """)
        
        # Initialize api_settings if empty
        conn.execute("INSERT OR IGNORE INTO api_settings (id, provider, api_key, model_name) VALUES (1, 'spacy', '', '')")

# ─────────────────────────────────────────────────────────────────────────────
# Skill Categories
# ─────────────────────────────────────────────────────────────────────────────

def get_skill_category(skill: str) -> str:
    with _connect() as conn:
        row = conn.execute("SELECT category FROM skill_categories WHERE skill = ?", (skill,)).fetchone()
        if row:
            return row["category"]
        return None

def save_skill_category(skill: str, category: str):
    with _connect() as conn:
        conn.execute("INSERT OR REPLACE INTO skill_categories (skill, category) VALUES (?, ?)", (skill, category))


# ─────────────────────────────────────────────────────────────────────────────
# API Settings
# ─────────────────────────────────────────────────────────────────────────────

def get_api_settings() -> dict:
    with _connect() as conn:
        row = conn.execute("SELECT provider, api_key, model_name FROM api_settings WHERE id = 1").fetchone()
        if row:
            return dict(row)
        return {"provider": "spacy", "api_key": "", "model_name": ""}

def update_api_settings(provider: str, api_key: str, model_name: str) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE api_settings SET provider = ?, api_key = ?, model_name = ? WHERE id = 1",
            (provider, api_key, model_name)
        )

# ─────────────────────────────────────────────────────────────────────────────
# Loadout CRUD
# ─────────────────────────────────────────────────────────────────────────────

def save_loadout_config(name: str, config: dict) -> None:
    """Loadout profilini kaydeder veya günceller (UPSERT)."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO loadouts
                (name, query_rows, must_have, or_have, not_have, must_include, must_exclude, country, city, limit_jobs, delay_seconds, auto_scan, auto_scan_interval, title_must_include, title_must_exclude)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                "[]", # Deprecated query_rows
                config.get("must_have", ""),
                config.get("or_have", ""),
                config.get("not_have", ""),
                config.get("must_include", ""),
                config.get("must_exclude", ""),
                config.get("country", "Worldwide"),
                config.get("city", "Hepsi"),
                config.get("limit_jobs", 20),
                config.get("delay_seconds", 2.0),
                int(config.get("auto_scan", 0)),
                config.get("auto_scan_interval", 60),
                config.get("title_must_include", ""),
                config.get("title_must_exclude", ""),
            ),
        )


def get_loadout_config(name: str) -> dict | None:
    """Belirtilen loadout'un konfigürasyonunu döner, yoksa None."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM loadouts WHERE name = ?", (name,)).fetchone()
    if not row:
        return None
    cfg = dict(row)
    # Legacy migration: if must_have is empty and query_rows exists, migrate
    query_rows = json.loads(cfg["query_rows"]) if cfg.get("query_rows") else []
    if not cfg.get("must_have") and query_rows:
        cfg["must_have"] = ",".join([r.get("keyword","") for r in query_rows if r.get("keyword")])
    return cfg


def get_all_loadout_configs() -> dict:
    """Tüm loadout konfigürasyonlarını {name: config} sözlüğü olarak döner."""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM loadouts").fetchall()
    result = {}
    for row in rows:
        cfg = dict(row)
        query_rows = json.loads(cfg["query_rows"]) if cfg.get("query_rows") else []
        if not cfg.get("must_have") and query_rows:
            cfg["must_have"] = ",".join([r.get("keyword","") for r in query_rows if r.get("keyword")])
        result[cfg["name"]] = cfg
    return result


def delete_loadout(name: str) -> None:
    """Loadout profilini ve ilgili tüm ilanları siler."""
    with _connect() as conn:
        conn.execute("DELETE FROM loadouts WHERE name = ?", (name,))
        conn.execute("DELETE FROM jobs WHERE search_profile = ?", (name,))

def clear_jobs_for_profile(name: str) -> None:
    """Sadece profile ait ilanları siler, profil ayarlarını silmez."""
    with _connect() as conn:
        conn.execute("DELETE FROM jobs WHERE search_profile = ?", (name,))

def delete_jobs_by_urls(urls: list[str]) -> None:
    """Belirtilen URL listesindeki ilanları siler."""
    if not urls:
        return
    with _connect() as conn:
        placeholders = ",".join(["?"] * len(urls))
        conn.execute(f"DELETE FROM jobs WHERE url IN ({placeholders})", tuple(urls))

def update_last_scan_time(name: str) -> None:
    """Oto-tarama sonrası son tarama vaktini günceller."""
    with _connect() as conn:
        conn.execute("UPDATE loadouts SET last_scan_time = CURRENT_TIMESTAMP WHERE name = ?", (name,))

def toggle_auto_scan(name: str, is_active: bool) -> None:
    """Belirtilen profil için oto-taramayı açar veya kapatır."""
    val = 1 if is_active else 0
    with _connect() as conn:
        conn.execute("UPDATE loadouts SET auto_scan = ? WHERE name = ?", (val, name))

def update_auto_scan_interval(name: str, interval: int) -> None:
    """Oto-tarama çalışma sıklığını (dakika) günceller."""
    with _connect() as conn:
        conn.execute("UPDATE loadouts SET auto_scan_interval = ? WHERE name = ?", (interval, name))

def update_bot_params(name: str, limit_jobs: int, delay_seconds: float) -> None:
    """Oto-tarama bot limitlerini (limit_jobs, delay_seconds) günceller."""
    with _connect() as conn:
        conn.execute("UPDATE loadouts SET limit_jobs = ?, delay_seconds = ? WHERE name = ?", (limit_jobs, delay_seconds, name))


# ─────────────────────────────────────────────────────────────────────────────
# Jobs CRUD
# ─────────────────────────────────────────────────────────────────────────────

def save_job(job: dict, profile: str) -> None:
    """İlanı DB'ye kaydeder; URL zaten varsa sessizce atlar (IGNORE)."""
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO jobs
                (url, title, company, location, description,
                 extracted_skills, experience_years, seniority_level, search_profile)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.get("url"),
                job.get("title"),
                job.get("company"),
                job.get("location", "Worldwide"),
                job.get("description"),
                ",".join(job.get("extracted_skills", [])),
                job.get("experience_years"),
                job.get("seniority_level"),
                profile,
            ),
        )


def get_jobs_by_profile(profile: str) -> list[dict]:
    """Belirtilen profile ait tüm ilanları liste olarak döner."""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM jobs WHERE search_profile = ?", (profile,)).fetchall()
    return [_parse_job(dict(row)) for row in rows]


def get_all_jobs() -> list[dict]:
    """Veritabanındaki tüm ilanları döner."""
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM jobs").fetchall()
    return [_parse_job(dict(row)) for row in rows]


def get_job_count_by_profile(profile: str) -> int:
    """Bir profile ait ilan sayısını döner."""
    with _connect() as conn:
        result = conn.execute(
            "SELECT COUNT(*) FROM jobs WHERE search_profile = ?", (profile,)
        ).fetchone()
    return result[0] if result else 0


# ─────────────────────────────────────────────────────────────────────────────
# Profil listeleme
# ─────────────────────────────────────────────────────────────────────────────

def get_all_profiles() -> list[str]:
    """
    Hem loadouts hem de jobs tablolarındaki tüm profil isimlerini
    birleştirip sıralı liste olarak döner.
    """
    profiles: set[str] = set()
    with _connect() as conn:
        for row in conn.execute("SELECT name FROM loadouts").fetchall():
            if row[0]:
                profiles.add(row[0])
        for row in conn.execute("SELECT DISTINCT search_profile FROM jobs").fetchall():
            if row[0]:
                profiles.add(row[0])
    return sorted(profiles)


# ─────────────────────────────────────────────────────────────────────────────
# Dahili yardımcılar
# ─────────────────────────────────────────────────────────────────────────────

def _parse_job(job: dict) -> dict:
    """extracted_skills alanını string'den listeye çevirir."""
    job["extracted_skills"] = (
        job["extracted_skills"].split(",") if job.get("extracted_skills") else []
    )
    return job
