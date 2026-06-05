import streamlit as st
import pdfplumber

from nlp_extractor import SkillExtractor
from analyzer import analyze_skills
import database as db

def _render_profile_selector(all_profiles: list) -> list:
    st.subheader("📂 Kıyaslanacak Profil(ler)i Seçin")
    st.markdown("CV'nizin pazar verileriyle kıyaslanması için hedef profil(ler)i seçin.")
    selected = []
    
    if not all_profiles:
        st.info("Henüz profil yok.")
        return []

    cols = st.columns(2)
    for i, p in enumerate(sorted(all_profiles)):
        count = db.get_job_count_by_profile(p)
        with cols[i % 2]:
            if st.checkbox(f"**{p}** ({count} ilan)", key=f"cv_chk_{p}"):
                selected.append(p)
                
    return selected


def _render_cv_upload_and_analysis(db_jobs: list):
    """CV yükleme + NLP analizi bölümü."""
    st.markdown("---")
    uploaded = st.file_uploader("CV'nizi Yükleyin (Sadece PDF)", type=["pdf"])
    if uploaded is None:
        return

    with pdfplumber.open(uploaded) as pdf:
        cv_text = "".join(
            (p.extract_text() or "") + "\n" for p in pdf.pages
        )

    if not cv_text.strip():
        st.error("PDF'den metin okunamadı. Resim tabanlı olmayan bir CV yükleyin.")
        return

    with st.spinner("CV NLP ile analiz ediliyor…"):
        extractor = SkillExtractor()
        cv_skills = extractor.extract_skills(cv_text)

    if not cv_skills:
        st.warning("CV'nizde teknik bir yetenek tespit edilemedi.")
        return

    st.success(f"CV'nizden **{len(cv_skills)} yetenek** başarıyla çıkarıldı!")

    if not db_jobs:
        st.warning("Seçilen profillerde hiç ilan yok. Kıyaslama yapılamıyor.")
        return

    job_skills_list = []
    for j in db_jobs:
        if j.get("extracted_skills"):
            job_skills_list.append(j["extracted_skills"])

    freqs, _ = analyze_skills(job_skills_list)
    if not freqs:
        st.warning("Seçilen profillerden yetenek çıkarılamadı.")
        return

    top_20 = [s for s, _ in freqs.most_common(20)]

    cv_skills_set  = set(cv_skills)
    top_20_set     = set(top_20)

    matches = cv_skills_set.intersection(top_20_set)
    missing = top_20_set - cv_skills_set
    extra   = cv_skills_set - top_20_set

    st.markdown("---")
    st.subheader("💡 Yapay Zeka Kariyer Analizi")

    c_match, c_miss, c_ext = st.columns(3)
    with c_match:
        st.success(f"✅ **Eşleşenler ({len(matches)}/20)**\n\n" + ", ".join(matches) if matches else "Eşleşme yok.")
    with c_miss:
        st.error(f"❌ **Eksikler ({len(missing)})**\n\n" + ", ".join(missing) if missing else "Eksik yok, mükemmel!")
    with c_ext:
        st.info(f"➕ **CV'nizdeki Ekstralar ({len(extra)})**\n\n" + ", ".join(extra) if extra else "Ekstra yetenek yok.")

    st.markdown("---")
    st.markdown("### 🚀 CV Geliştirme Önerileri")
    if missing:
        st.markdown(
            "Seçtiğiniz pazar profillerine göre en çok istenen ama **sizde bulunmayan** anahtar kelimeler şunlar:\n\n"
            + "".join([f"- **{m}**\n" for m in missing]) +
            "\n👉 *Eğer bu yeteneklere sahipseniz, CV'nize mutlaka ekleyin. Sahip değilseniz öğrenmeye öncelik verin.*"
        )
    else:
        st.success("Tebrikler! Pazardaki Top 20 yeteneğin tümü CV'nizde yer alıyor.")


def render_cv_tab(all_profiles: list):
    """
    CV Analizi sekmesinin ana render fonksiyonu.
    """
    st.markdown("Mevcut CV'nizi PDF olarak yükleyip, oluşturduğunuz profillerin **pazar standartları** ile kıyaslayın.")

    selected_profiles = _render_profile_selector(all_profiles)

    if not selected_profiles:
        st.warning("Devam etmek için lütfen yukarıdan en az 1 profil seçin.")
        return

    # Seçilen profillerin ilanlarını birleştir
    db_jobs = []
    for p in selected_profiles:
        db_jobs.extend(db.get_jobs_by_profile(p))

    st.info(f"Seçilen profillerden toplam **{len(db_jobs)} ilan** verisiyle kıyaslama yapılacak.")

    _render_cv_upload_and_analysis(db_jobs)
