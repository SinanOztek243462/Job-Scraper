"""
utils/charts.py — Tüm grafik üretme fonksiyonları.
Streamlit çağrısı yapmaz, sadece figure nesneleri döner.
"""

import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from pyvis.network import Network


def make_seniority_pie(seniorities: list):
    """Kıdem dağılımı pasta grafiği."""
    import pandas as pd
    df = pd.DataFrame({"Seniority": seniorities})
    fig = px.pie(
        df, names="Seniority", hole=0.4,
        title="İlanlarda Aranan Seviyeler",
        color_discrete_sequence=px.colors.sequential.RdBu,
    )
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="white"))
    return fig


def make_radar_chart(cat_freqs: dict):
    """Yetenek kategorisi radar grafiği."""
    if not cat_freqs:
        return None
    categories = list(cat_freqs.keys())
    values = list(cat_freqs.values())
    categories.append(categories[0])
    values.append(values[0])
    fig = go.Figure(data=go.Scatterpolar(
        r=values, theta=categories, fill="toself", line=dict(color="#00ffcc")
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, max(values) if values else 1])),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
        height=450,
    )
    return fig


def make_bar_chart(top_skills: list, top_counts: list):
    """En çok istenen yetenekler bar grafiği."""
    fig = px.bar(
        x=top_skills, y=top_counts,
        labels={"x": "Yetenek", "y": "İlan Sayısı"},
        color=top_counts,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    return fig


def make_wordcloud(freqs: dict):
    """Yetenek bulutu matplotlib figure döner."""
    wc = WordCloud(width=600, height=450, background_color="#0E1117", colormap="cool")
    wc.generate_from_frequencies(freqs)
    fig, ax = plt.subplots(figsize=(6, 4.5), facecolor="#0E1117")
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    return fig


def make_heatmap(top_skills: list, freqs, co_occurrences: dict):
    """Yetenek eşleşme ısı haritası."""
    top_15 = top_skills[:15]
    z_data = [
        [
            freqs[s1] if s1 == s2 else co_occurrences.get(tuple(sorted([s1, s2])), 0)
            for s2 in top_15
        ]
        for s1 in top_15
    ]
    fig = px.imshow(z_data, x=top_15, y=top_15, color_continuous_scale="RdBu_r", aspect="auto")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white"),
    )
    return fig


def make_network_html(top_skills: list, freqs, co_occurrences: dict, output_file: str = "skill_network.html") -> str:
    """Yetenek ağ haritası HTML döner."""
    net = Network(height="450px", width="100%", bgcolor="#0E1117", font_color="white")
    net.repulsion(node_distance=150, central_gravity=0.2, spring_length=200, spring_strength=0.05, damping=0.09)

    max_freq = freqs[top_skills[0]] if top_skills else 1
    min_freq = freqs[top_skills[-1]] if top_skills else 0

    def _color(val):
        norm = (val - min_freq) / (max_freq - min_freq) if max_freq > min_freq else 1.0
        return f"#{int(255 * (1 - norm)):02x}{int(255 * norm):02x}00"

    for skill in top_skills:
        count = freqs[skill]
        net.add_node(skill, label=skill, title=f"{skill}: {count} ilan", size=count * 3 + 10, color=_color(count))

    for (s1, s2), count in co_occurrences.items():
        if s1 in top_skills and s2 in top_skills and count > 0:
            net.add_edge(s1, s2, value=count, title=f"Birlikte: {count} ilan", color="#555555")

    net.save_graph(output_file)
    with open(output_file, "r", encoding="utf-8") as f:
        return f.read()
