import streamlit as st
import database as db
import pandas as pd
from analyzer import analyze_skills, analyze_categories
from utils.scrape_runner import run_scrape_for_profile
from utils.charts import (
    make_seniority_pie, make_radar_chart, make_bar_chart,
    make_wordcloud, make_heatmap, make_network_html
)
import streamlit.components.v1 as components

def _render_results(freqs, co_occurrences, seniorities, experience_years):
    """Analiz sonuçlarını grafik olarak gösterir."""
    st.markdown("---")
    st.subheader("👨‍💼 Kıdem ve Tecrübe Dağılımı")
    col_sen1, col_sen2 = st.columns(2)
    with col_sen1:
        st.plotly_chart(make_seniority_pie(seniorities), use_container_width=True)
    with col_sen2:
        if experience_years:
            avg = sum(experience_years) / len(experience_years)
            st.metric("Ortalama İstenen Tecrübe", f"{avg:.1f} Yıl")
        else:
            st.metric("Ortalama İstenen Tecrübe", "Veri Yok")
        st.markdown("Bu veriler ilan metinlerindeki tecrübe kalıplarından (Regex) otomatik çekilmiştir.")

    st.markdown("---")
    st.subheader("🕸️ Yetenek Kategorizasyonu (Pazar Karakteristiği)")
    cat_freqs = analyze_categories(freqs)
    radar = make_radar_chart(cat_freqs)
    if radar:
        st.plotly_chart(radar, use_container_width=True)

    st.markdown("---")
    top_skills = [s for s, _ in freqs.most_common(20)]
    top_counts = [c for _, c in freqs.most_common(20)]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 En Çok İstenen 20 Yetenek")
        st.plotly_chart(make_bar_chart(top_skills, top_counts), use_container_width=True)
    with col2:
        st.subheader("☁️ Yetenek Bulutu")
        st.pyplot(make_wordcloud(dict(freqs)))

    st.markdown("---")
    st.subheader("🔥 Yetenek Eşleşme Analizi")
    t1, t2 = st.tabs(["Isı Haritası", "Ağ Haritası"])
    with t1:
        st.plotly_chart(make_heatmap(top_skills, freqs, co_occurrences), use_container_width=True)
    with t2:
        html_content = make_network_html(top_skills, freqs, co_occurrences)
        components.html(html_content, height=470)


def render_profiles_tab():
    st.markdown("### 🗂️ Arama Profilleri ve Analiz Merkezi")
    st.markdown("Oluşturduğunuz arama profillerini (loadout) buradan yönetin. Her profil için ayrı ayrı veri toplayabilir, piyasa analizlerini görüntüleyebilir ve topladığınız **ham ilanlara** erişebilirsiniz.")
    
    all_profiles = db.get_all_loadout_configs()
    if not all_profiles:
        st.info("Henüz oluşturulmuş bir arama profiliniz yok. Sol menüden yeni bir profil oluşturun.")
        return
        
    for p in sorted(all_profiles.keys()):
        job_count = db.get_job_count_by_profile(p)
        
        with st.expander(f"📁 Profil: **{p}** ({job_count} İlan)", expanded=False):
            # Üst Butonlar (Düzenle, Tara, Oto-Tara, Temizle, Sil)
            c1, c2, c3, c4, c5 = st.columns([1, 1.2, 1.2, 1.2, 1])
            
            with c1:
                if st.button("✏️ Ayarları Düzenle", key=f"edit_{p}", help="Bu profilin ayarlarını sol menüye yükler."):
                    st.session_state.trigger_load_profile = p
                    st.rerun()
                    
            with c2:
                if st.button("🔁 Tarama Yap", key=f"scan_{p}", help="Ayarlardaki limit kadar ilan çeker."):
                    saved = run_scrape_for_profile(p, show_ui=True)
                    if saved > 0:
                        st.success(f"{saved} yeni ilan kaydedildi!")
                    else:
                        st.warning("Yeni ilan bulunamadı.")
                        
            with c3:
                is_auto = bool(all_profiles[p].get("auto_scan", 0))
                # toggle_auto_scan fonksiyonunu ui değiştikçe tetikleyeceğiz
                new_auto = st.toggle("🤖 Oto-Tarama", value=is_auto, key=f"auto_{p}", help="Arka planda periyodik olarak tarama yapar.")
                if new_auto != is_auto:
                    db.toggle_auto_scan(p, new_auto)
                    st.rerun()
                        
            with c4:
                if st.button("🧹 İlanları Temizle", key=f"clear_{p}", help="Bu profildeki eski ilanları veritabanından siler."):
                    db.clear_jobs_for_profile(p)
                    st.rerun()
                
            with c5:
                if st.button("🗑️ Profili Sil", key=f"del_{p}"):
                    db.delete_loadout(p)
                    st.rerun()
                    
            if is_auto:
                st.info("🤖 **Oto-Tarama Aktif:** Arka plan işçisi (bot) belirlenen ayarlarla otomatik çalışacak.")
                c_int1, c_int2, c_int3 = st.columns(3)
                
                with c_int1:
                    current_interval = int(all_profiles[p].get("auto_scan_interval", 60))
                    new_interval = st.number_input(
                        "Çalışma Aralığı (Dakika)", 
                        min_value=1, max_value=1440, 
                        value=current_interval, 
                        key=f"interval_{p}"
                    )
                    if new_interval != current_interval:
                        db.update_auto_scan_interval(p, new_interval)
                        
                with c_int2:
                    current_limit = int(all_profiles[p].get("limit_jobs", 20))
                    new_limit = st.number_input(
                        "Maksimum İlan Sayısı",
                        min_value=1, max_value=200,
                        value=current_limit,
                        key=f"limit_{p}"
                    )
                    
                with c_int3:
                    current_delay = float(all_profiles[p].get("delay_seconds", 2.0))
                    new_delay = st.number_input(
                        "Gecikme (Sn)",
                        min_value=1.0, max_value=10.0, step=0.5,
                        value=current_delay,
                        key=f"delay_{p}"
                    )
                    
                if new_limit != current_limit or new_delay != current_delay:
                    db.update_bot_params(p, new_limit, new_delay)
                        
            st.markdown("---")
            
            # İç Sekmeler: Analiz vs Ham Veri
            t1, t2 = st.tabs(["📊 Piyasa Analiz Raporu", "📋 Toplanan Ham İlanlar"])
            
            with t1:
                if job_count > 0:
                    c_rep1, c_rep2 = st.columns([1, 1])
                    with c_rep1:
                        if st.button(f"🚀 Raporu Çiz / Güncelle", key=f"graph_{p}"):
                            with st.spinner("Veriler işleniyor..."):
                                jobs = db.get_jobs_by_profile(p)
                                job_skills_list = []
                                seniorities = []
                                experience_years = []
                                for job in jobs:
                                    if job.get("extracted_skills"):
                                        job_skills_list.append(job["extracted_skills"])
                                    seniorities.append(job.get("seniority_level"))
                                    if job.get("experience_years") is not None:
                                        experience_years.append(job.get("experience_years"))

                                freqs, co_occurrences = analyze_skills(job_skills_list)
                                if freqs:
                                    _render_results(freqs, co_occurrences, seniorities, experience_years)
                                else:
                                    st.warning("Yeterli NLP verisi (yetenek kelimesi) bulunamadı.")
                    with c_rep2:
                        if st.button("🔄 Mevcut İlanları LLM ile Yeniden Analiz Et", key=f"reanalyze_{p}"):
                            from nlp_extractor import SkillExtractor
                            extractor = SkillExtractor()
                            jobs = db.get_jobs_by_profile(p)
                            success_count = 0
                            
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i, job in enumerate(jobs):
                                status_text.text(f"İlanlar analiz ediliyor... {i+1} / {len(jobs)} (API Kotası için yavaş ilerler)")
                                result = extractor.extract_skills(job.get("description", ""))
                                skills = result.get("skills", []) if isinstance(result, dict) else result
                                qualifications_text = result.get("qualifications_text", "") if isinstance(result, dict) else ""
                                
                                if skills or qualifications_text:
                                    job["extracted_skills"] = skills
                                    job["qualifications_text"] = qualifications_text
                                    db.save_job(job, p)
                                    success_count += 1
                                progress_bar.progress((i + 1) / len(jobs))
                                
                            status_text.empty()
                            progress_bar.empty()
                            st.success(f"{len(jobs)} ilandan {success_count} tanesi başarıyla yapay zekadan geçirildi. Şimdi 'Raporu Çiz' butonuna basabilirsiniz!")
                            
                    st.markdown("---")
                    
                    # Eğitim Verisi Dışa Aktarma
                    all_jobs = db.get_jobs_by_profile(p)
                    jobs_with_text = [j for j in all_jobs if j.get("qualifications_text")]
                    if jobs_with_text:
                        import json
                        st.subheader("📚 Eğitim Verisi (Training Data)")
                        st.info(f"{len(jobs_with_text)} adet ilandan saf 'Aranan Nitelikler / Qualifications' metinleri çekildi.")
                        
                        export_data = []
                        for j in jobs_with_text:
                            export_data.append({
                                "title": j.get("title", ""),
                                "company": j.get("company", ""),
                                "skills": j.get("extracted_skills", []),
                                "qualifications_text": j.get("qualifications_text", "")
                            })
                            
                        json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
                        st.download_button(
                            label="📥 Eğitim Verisini İndir (.JSON)",
                            data=json_str,
                            file_name=f"{p}_training_data.json",
                            mime="application/json"
                        )
                        
                        with st.expander("Göz At: Çıkarılan Ham Metinler"):
                            for j in jobs_with_text[:5]:
                                st.markdown(f"**{j.get('title')} ({j.get('company')})**")
                                st.write(j.get("qualifications_text"))
                                st.markdown("---")
                            if len(jobs_with_text) > 5:
                                st.write(f"...ve {len(jobs_with_text) - 5} ilan daha.")
                else:
                    st.info("Bu profil için henüz ilan toplanmadı. Yukarıdan 'Manuel Tarama Yap' butonuna basın.")
                    
            with t2:
                if job_count > 0:
                    jobs = db.get_jobs_by_profile(p)
                    if jobs:
                        df = pd.DataFrame(jobs)
                        # Gösterilecek kolonlar
                        show_cols = ["title", "company", "location", "url"]
                        exist_cols = [c for c in show_cols if c in df.columns]
                        
                        if exist_cols:
                            # Sadece seçili kolonları al ve başına 'Sil' kolonu ekle
                            df_display = df[exist_cols].copy()
                            df_display.insert(0, "Sil", False)
                            
                            st.markdown("Aşağıdaki listeden silmek istediğiniz ilanları işaretleyip butona basın.")
                            edited_df = st.data_editor(
                                df_display, 
                                use_container_width=True, 
                                hide_index=True,
                                key=f"editor_{p}",
                                column_config={"url": st.column_config.LinkColumn("İlan Linki")}
                            )
                            
                            # Sil butonu
                            if st.button("🗑️ Seçili İlanları Sil", key=f"delete_selected_{p}"):
                                urls_to_delete = edited_df[edited_df["Sil"] == True]["url"].tolist()
                                if urls_to_delete:
                                    db.delete_jobs_by_urls(urls_to_delete)
                                    st.success(f"{len(urls_to_delete)} ilan başarıyla silindi!")
                                    st.rerun()
                                else:
                                    st.warning("Silinecek ilan seçmediniz.")
                                    
                            st.markdown("---")
                            # CSV İndirme
                            csv = df.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📥 Tüm İlanları CSV Olarak İndir",
                                data=csv,
                                file_name=f"{p}_ilanlar.csv",
                                mime="text/csv",
                                key=f"csv_{p}"
                            )
                else:
                    st.info("Gösterilecek ilan kaydı yok.")
