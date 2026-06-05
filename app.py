"""
app.py — Job Scrater ana giriş noktası.
Yalnızca sayfa yapılandırması, modül çağrıları ve sekme düzeni burada.
"""

import sys
import os

# Proje kök dizinini her zaman sys.path'e ekle
_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

import streamlit as st
import database as db
from ui.sidebar import render_sidebar
from ui.tab_profiles import render_profiles_tab
from ui.tab_cv import render_cv_tab

# ─── Sayfa Yapılandırması ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Job Scrater",
    page_icon="🎯",
    layout="wide",
)

# ─── Veritabanı ───────────────────────────────────────────────────────────────
db.init_db()

# ─── Arka Plan İşçisi ─────────────────────────────────────────────────────────
from utils.auto_scanner import start_auto_scanner
start_auto_scanner()

# ─── Başlık ───────────────────────────────────────────────────────────────────
st.title("🎯 Job Scrater")
st.markdown("LinkedIn verilerini analiz ederek pazar trendlerini okuyun ve CV'nizin eksiklerini bulun.")

# ─── Sidebar ──────────────────────────────────────────────────────────────────
_ = render_sidebar()

# ─── Sekmeler ─────────────────────────────────────────────────────────────────
tab_profiles, tab_cv = st.tabs(["🗂️ Arama Profilleri ve Veri Toplama", "📄 CV Analizi ve Kıyaslama"])

with tab_profiles:
    render_profiles_tab()

with tab_cv:
    all_profiles = db.get_all_profiles()
    render_cv_tab(all_profiles)
