"""
config.py — Uygulama genelinde kullanılan sabitler.
Ülke/şehir haritaları burada tanımlıdır.
"""

COUNTRY_MAP = {
    "Dünya Geneli (Worldwide)": "Worldwide",
    "Türkiye": "Turkey",
    "Amerika Birleşik Devletleri": "United States",
    "Almanya": "Germany",
    "İngiltere": "United Kingdom",
    "Hollanda": "Netherlands",
    "Avrupa Birliği (Europe)": "Europe",
    "Kanada": "Canada",
}

REVERSE_COUNTRY_MAP = {v: k for k, v in COUNTRY_MAP.items()}

CITY_MAP = {
    "Dünya Geneli (Worldwide)": ["Hepsi"],
    "Türkiye": ["Hepsi", "Istanbul", "Ankara", "Izmir"],
    "Amerika Birleşik Devletleri": ["Hepsi", "San Francisco", "New York", "Seattle", "Austin", "Remote"],
    "Almanya": ["Hepsi", "Berlin", "Munich", "Frankfurt", "Hamburg", "Remote"],
    "İngiltere": ["Hepsi", "London", "Manchester", "Cambridge", "Remote"],
    "Hollanda": ["Hepsi", "Amsterdam", "Rotterdam", "Eindhoven", "Remote"],
    "Avrupa Birliği (Europe)": ["Hepsi"],
    "Kanada": ["Hepsi", "Toronto", "Vancouver", "Montreal", "Remote"],
}

SEEN_JOBS_FILE = "seen_jobs.json"
