"""
pages/sidebar.py — Sidebar UI: Profil yönetimi + Arama ayarları.
render_sidebar() çağrıldığında sidebar'ı çizer ve arama parametrelerini döner.
"""

import streamlit as st
import database as db
from config import COUNTRY_MAP, REVERSE_COUNTRY_MAP, CITY_MAP
from utils.scrape_runner import build_query_string


def _init_session_defaults():
    defaults = {
        "must_have": "developer",
        "or_have": "",
        "not_have": "",
        "must_include": "",
        "must_exclude": "",
        "title_must_include": "",
        "title_must_exclude": "",
        "country_key": "Dünya Geneli (Worldwide)",
        "city_key": "Hepsi",
        "loadout_name_input": "",
        "selected_loadout": None,
        "limit_jobs": 20,
        "delay_seconds": 2.0,
        "auto_scan": False,
        "auto_scan_interval": 1, # Hours
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _load_loadout(name: str, all_configs: dict):
    """Seçilen loadout ayarlarını session state'e yükler."""
    cfg = all_configs.get(name)
    if not cfg:
        return
        
    st.session_state.must_have = cfg.get("must_have", "")
    st.session_state.or_have = cfg.get("or_have", "")
    st.session_state.not_have = cfg.get("not_have", "")

    st.session_state.must_include = cfg.get("must_include", "")
    st.session_state.must_exclude = cfg.get("must_exclude", "")
    st.session_state.title_must_include = cfg.get("title_must_include", "")
    st.session_state.title_must_exclude = cfg.get("title_must_exclude", "")
    st.session_state.country_key = REVERSE_COUNTRY_MAP.get(cfg.get("country", "Worldwide"), "Dünya Geneli (Worldwide)")
    st.session_state.city_key = cfg.get("city", "Hepsi")
    st.session_state.loadout_name_input = name
    st.session_state.selected_loadout = name
    st.session_state.limit_jobs = cfg.get("limit_jobs", 20)
    st.session_state.delay_seconds = float(cfg.get("delay_seconds", 2.0))
    st.session_state.auto_scan = bool(cfg.get("auto_scan", 0))
    st.session_state.auto_scan_interval = cfg.get("auto_scan_interval", 1)


def _render_profile_manager(all_configs: dict):
    """Profil listesi: selectbox ile yükle."""
    st.sidebar.header("📂 Profil (Loadout) Yükle")
    
    # Ana ekrandan "Ayarları Düzenle" butonuna tıklandıysa:
    if st.session_state.get("trigger_load_profile"):
        _load_loadout(st.session_state.trigger_load_profile, all_configs)
        st.session_state.trigger_load_profile = None

    if not all_configs:
        st.sidebar.info("Henüz kayıtlı profil yok. Aşağıdan oluşturun.")
        return

    profile_options = ["-- Yeni Profil (Boş) --"]
    profile_mapping = {}
    for name in sorted(all_configs.keys()):
        count = db.get_job_count_by_profile(name)
        label = f"{name} ({count} ilan)"
        profile_options.append(label)
        profile_mapping[label] = name

    idx = 0
    if st.session_state.selected_loadout:
        for i, lbl in enumerate(profile_options):
            if lbl != "-- Yeni Profil (Boş) --" and profile_mapping[lbl] == st.session_state.selected_loadout:
                idx = i
                break
                
    selected_label = st.sidebar.selectbox("Kayıtlı Profili Seç", profile_options, index=idx)
    
    if selected_label != "-- Yeni Profil (Boş) --":
        actual_name = profile_mapping[selected_label]
        if actual_name != st.session_state.selected_loadout:
            _load_loadout(actual_name, all_configs)
            st.rerun()
    else:
        if st.session_state.selected_loadout is not None:
            st.session_state.selected_loadout = None
            st.session_state.loadout_name_input = ""
            st.session_state.must_have = "developer"
            st.session_state.or_have = ""
            st.session_state.not_have = ""
            st.session_state.must_include = ""
            st.session_state.must_exclude = ""
            st.session_state.title_must_include = ""
            st.session_state.title_must_exclude = ""
            st.rerun()
    st.sidebar.markdown("---")


def _render_search_settings() -> tuple:
    """Arama ayarları (keyword, filtre, konum). Döner: (location, linkedin_country, selected_city)."""
    st.sidebar.header("🔍 Arama Ayarları (LinkedIn)")
    st.sidebar.markdown("Kelimeleri **virgülle** ayırarak yazın.")

    st.sidebar.text_input("🟢 Kesinlikle Olmalı (AND)", key="must_have", placeholder="örn: developer, python")
    st.sidebar.text_input("🔵 Şunlardan Biri Olmalı (OR)", key="or_have", placeholder="örn: junior, entry")
    st.sidebar.text_input("🔴 Kesinlikle Olmasın (NOT)", key="not_have", placeholder="örn: senior, lead")

    st.sidebar.markdown("---")

    st.sidebar.subheader("📌 BAŞLIK İçi Metin Filtreleri")
    st.sidebar.text_input("Başlık Şunları İÇERSİN", key="title_must_include", placeholder="örn: kimya, mühendis")
    st.sidebar.text_input("Başlık Şunları İÇERMESİN", key="title_must_exclude", placeholder="örn: asistan, stajyer")

    st.sidebar.subheader("📌 İLAN İçi Metin Filtreleri")
    st.sidebar.text_input("Açıklama Şunları İÇERSİN", key="must_include", placeholder="örn: visa, relocation")
    st.sidebar.text_input("Açıklama Şunları İÇERMESİN", key="must_exclude", placeholder="örn: part-time, clearance")
    st.sidebar.markdown("---")

    st.sidebar.subheader("🌍 Konum Ayarı")
    selected_country_tr = st.sidebar.selectbox("Ülke / Bölge", list(COUNTRY_MAP.keys()), key="country_key")
    cities = CITY_MAP[selected_country_tr]
    if st.session_state.city_key not in cities:
        st.session_state.city_key = "Hepsi"
    selected_city = (
        st.sidebar.selectbox("Şehir (veya Remote)", cities, key="city_key")
        if len(cities) > 1 else "Hepsi"
    )
    if len(cities) == 1:
        st.session_state.city_key = "Hepsi"

    linkedin_country = COUNTRY_MAP[selected_country_tr]
    location = (
        linkedin_country if linkedin_country in ("Worldwide", "Europe")
        else (linkedin_country if selected_city == "Hepsi" else f"{selected_city}, {linkedin_country}")
    )

    return location, linkedin_country, selected_city


def _render_save_profile(linkedin_country: str, selected_city: str):
    """Profil kaydetme formu."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("💾 Ayarları Profile Kaydet")
    
    st.sidebar.text_input(
        "Profil Adı", key="loadout_name_input", placeholder="Örn: Frontend-TR"
    )
    if st.sidebar.button("✔️ Ayarları Kaydet / Güncelle"):
        name = st.session_state.loadout_name_input.strip()
        if name:
            db.save_loadout_config(name, {
                "must_have": st.session_state.must_have,
                "or_have": st.session_state.or_have,
                "not_have": st.session_state.not_have,
                "must_include": st.session_state.must_include,
                "must_exclude": st.session_state.must_exclude,
                "title_must_include": st.session_state.title_must_include,
                "title_must_exclude": st.session_state.title_must_exclude,
                "country": linkedin_country,
                "city": selected_city,
                "limit_jobs": st.session_state.limit_jobs,
                "delay_seconds": st.session_state.delay_seconds,
                "auto_scan": st.session_state.auto_scan,
                "auto_scan_interval": st.session_state.auto_scan_interval,
            })
            st.session_state.selected_loadout = name
            st.sidebar.success(f"🎉 '{name}' başarıyla kaydedildi!")
            st.rerun()
        else:
            st.sidebar.error("Lütfen bir isim girin!")


def _render_api_settings():
    """Yapay Zeka API Ayarlarını (LLM) yönetir."""
    st.sidebar.markdown("---")
    st.sidebar.header("🧠 Yapay Zeka & API Ayarları")
    
    current_settings = db.get_api_settings()
    
    provider_options = ["spacy", "ollama", "google-genai", "openai"]
    provider_labels = {
        "spacy": "Standart Kelime Eşleştirme (Eski)",
        "ollama": "Ollama (Yerel/Offline - Ücretsiz)",
        "google-genai": "Google Gemini API (Ücretsiz)",
        "openai": "OpenAI / DeepSeek API (Ücretli/Key)"
    }
    
    idx = 0
    if current_settings["provider"] in provider_options:
        idx = provider_options.index(current_settings["provider"])
        
    selected_provider_label = st.sidebar.selectbox(
        "Yetenek Çıkarma Motoru", 
        [provider_labels[p] for p in provider_options],
        index=idx
    )
    selected_provider = provider_options[[provider_labels[p] for p in provider_options].index(selected_provider_label)]
    
    api_key = current_settings["api_key"]
    model_name = current_settings["model_name"]
    
    if selected_provider in ["google-genai", "openai"]:
        api_key = st.sidebar.text_input("API Anahtarı (Zorunlu)", value=api_key, type="password")
        model_name = st.sidebar.text_input(
            "Model Adı", 
            value=model_name, 
            placeholder="örn: gemini-2.5-flash veya deepseek-chat"
        )
    elif selected_provider == "ollama":
        model_name = st.sidebar.text_input(
            "Ollama Model Adı", 
            value=model_name if model_name else "llama3", 
            placeholder="örn: llama3 veya deepseek-r1"
        )
        st.sidebar.info("Ollama'nın arka planda (localhost:11434) çalıştığından emin olun.")
        
    if st.sidebar.button("💾 API Ayarlarını Kaydet"):
        db.update_api_settings(selected_provider, api_key, model_name)
        st.sidebar.success("Yapay zeka motoru ayarları güncellendi!")

def render_sidebar() -> dict:
    """
    Tüm sidebar'ı çizer.
    Döner: parametre dict.
    """
    _init_session_defaults()
    all_configs = db.get_all_loadout_configs()

    _render_profile_manager(all_configs)
    location, linkedin_country, selected_city = _render_search_settings()
    _render_save_profile(linkedin_country, selected_city)
    _render_api_settings()

    final_query = build_query_string(st.session_state.must_have, st.session_state.or_have, st.session_state.not_have)

    return {
        "final_query": final_query,
        "location": location,
        "must_include": st.session_state.must_include,
        "must_exclude": st.session_state.must_exclude,
        "title_must_include": st.session_state.title_must_include,
        "title_must_exclude": st.session_state.title_must_exclude,
        "active_profile": st.session_state.loadout_name_input.strip(),
        "linkedin_country": linkedin_country,
        "selected_city": selected_city,
    }
