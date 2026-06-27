import streamlit as st

from modules.data_loader import get_data_summary, prepare_master_df, validate_data_files


STATIC_SUMMARY = {
    "rows": 1749,
    "date_min": "2022-12-25",
    "date_max": "2026-06-24",
    "issue_main_count": 18,
}


st.set_page_config(
    page_title="TPIS Preview | Taipei Policy Intelligence Search",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_data_summary(data_dir="data"):
    try:
        validation = validate_data_files(data_dir)
        if validation.get("missing_files"):
            return STATIC_SUMMARY, False

        master_df = prepare_master_df(data_dir)
        summary = get_data_summary(master_df)
        return {
            "rows": summary.get("rows") or STATIC_SUMMARY["rows"],
            "date_min": summary.get("date_min") or STATIC_SUMMARY["date_min"],
            "date_max": summary.get("date_max") or STATIC_SUMMARY["date_max"],
            "issue_main_count": summary.get("issue_main_count")
            or STATIC_SUMMARY["issue_main_count"],
        }, True
    except Exception:
        return STATIC_SUMMARY, False


def year_range(summary):
    return f"{str(summary['date_min'])[:4]}–{str(summary['date_max'])[:4]}"


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --background: #FAFAFA;
            --text: #111827;
            --muted: #6B7280;
            --primary: #2563EB;
            --card: #FFFFFF;
            --border: #E5E7EB;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 28rem),
                linear-gradient(180deg, #FFFFFF 0%, var(--background) 42%, #FFFFFF 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.92);
            border-right: 1px solid var(--border);
        }

        .hero {
            padding: 4.5rem 0 2.25rem;
            text-align: center;
        }

        .brand-chip {
            display: inline-flex;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            background: rgba(255, 255, 255, 0.82);
            color: var(--muted);
            font-size: 0.88rem;
            margin-bottom: 1rem;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(4rem, 16vw, 8.5rem);
            line-height: 0.92;
            letter-spacing: 0;
            color: var(--text);
            font-weight: 780;
        }

        .hero .subtitle {
            margin: 1.2rem auto 0;
            font-size: clamp(1.35rem, 4.2vw, 2.35rem);
            line-height: 1.25;
            color: var(--text);
            font-weight: 650;
        }

        .hero .zh {
            margin: 0.65rem auto 0;
            font-size: clamp(1.05rem, 3.2vw, 1.45rem);
            color: var(--muted);
            font-weight: 520;
        }

        .hero .copy {
            max-width: 780px;
            margin: 1.35rem auto 0;
            color: #374151;
            font-size: 1.06rem;
            line-height: 1.85;
        }

        .section-kicker {
            color: var(--primary);
            font-size: 0.82rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            font-weight: 750;
            margin-bottom: 0.4rem;
        }

        .section-title {
            font-size: clamp(1.9rem, 5vw, 3rem);
            line-height: 1.12;
            font-weight: 760;
            margin: 0 0 0.8rem;
        }

        .section-copy {
            max-width: 780px;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.75;
            margin-bottom: 1.3rem;
        }

        .kpi-card,
        .module-card,
        .preview-card,
        .flow-card,
        .timeline-card,
        .footer {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 18px 50px rgba(17, 24, 39, 0.05);
        }

        .kpi-card {
            padding: 1rem;
            min-height: 7.25rem;
        }

        .kpi-value {
            color: var(--text);
            font-size: clamp(1.55rem, 6vw, 2.2rem);
            line-height: 1.05;
            font-weight: 760;
            margin-bottom: 0.45rem;
        }

        .kpi-label,
        .muted {
            color: var(--muted);
            line-height: 1.55;
        }

        .module-card,
        .preview-card,
        .flow-card {
            padding: 1.05rem;
            min-height: 100%;
        }

        .module-card h3,
        .preview-card h3,
        .flow-card h3 {
            font-size: 1.12rem;
            line-height: 1.35;
            margin: 0 0 0.3rem;
            color: var(--text);
        }

        .module-card .eyebrow {
            color: var(--primary);
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }

        .module-card p,
        .preview-card p,
        .flow-card p {
            color: #4B5563;
            line-height: 1.68;
            margin: 0;
        }

        .badge-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.9rem;
        }

        .badge {
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            background: #FFFFFF;
            color: #374151;
            font-size: 0.9rem;
        }

        .preview-label {
            display: inline-flex;
            color: #92400E;
            background: #FFFBEB;
            border: 1px solid #FDE68A;
            border-radius: 999px;
            padding: 0.32rem 0.68rem;
            font-size: 0.86rem;
            margin-bottom: 0.85rem;
        }

        .result-card {
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.95rem;
            background: #FFFFFF;
            margin-bottom: 0.75rem;
        }

        .result-card strong {
            display: block;
            font-size: 1.02rem;
            margin: 0.2rem 0 0.35rem;
            color: var(--text);
        }

        .timeline-card {
            display: grid;
            grid-template-columns: minmax(5.5rem, 7.5rem) 1fr;
            gap: 0.85rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
        }

        .timeline-date {
            color: var(--primary);
            font-weight: 740;
        }

        .timeline-card h4 {
            margin: 0 0 0.25rem;
            font-size: 1.02rem;
        }

        .timeline-card p {
            margin: 0.18rem 0;
            color: #4B5563;
            line-height: 1.6;
        }

        .footer {
            padding: 1.25rem;
            text-align: center;
            color: var(--muted);
            margin-top: 2rem;
        }

        .footer strong {
            color: var(--text);
        }

        @media (max-width: 640px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.25rem;
            }

            .hero {
                padding: 2.4rem 0 1.6rem;
                text-align: left;
            }

            .timeline-card {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_card(value, label):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-value">{value}</div>
            <div class="kpi-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def module_card(module, title, body):
    st.markdown(
        f"""
        <div class="module-card">
            <div class="eyebrow">{module}</div>
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def simple_card(title, body):
    st.markdown(
        f"""
        <div class="preview-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(date, title, summary, issue, keywords):
    st.markdown(
        f"""
        <div class="result-card">
            <div class="muted">{date} · {issue}</div>
            <strong>{title}</strong>
            <p>{summary}</p>
            <div class="badge-wrap">
                <span class="badge">{keywords}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def timeline_card(date, event, status, change):
    st.markdown(
        f"""
        <div class="timeline-card">
            <div class="timeline-date">{date}</div>
            <div>
                <h4>{event}</h4>
                <p><strong>政策狀態：</strong>{status}</p>
                <p><strong>政策變化：</strong>{change}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def preview_label(text):
    st.markdown(f'<div class="preview-label">{text}</div>', unsafe_allow_html=True)


def footer():
    st.markdown(
        """
        <div class="footer">
            <strong>TPIS</strong><br>
            Taipei Policy Intelligence Search<br>
            Version 0.1 Preview · 2026
        </div>
        """,
        unsafe_allow_html=True,
    )


summary, loaded_from_data = load_data_summary("data")
inject_styles()


with st.sidebar:
    st.markdown("## TPIS")
    st.caption("Taipei Policy Intelligence Search")
    st.caption("Version 0.1 Preview")
    st.divider()
    st.metric("公開文件", f"{summary['rows']:,}")
    st.metric("政策主題", f"{summary['issue_main_count']}")
    st.write(f"資料期間：{summary['date_min']} 至 {summary['date_max']}")
    st.divider()
    if loaded_from_data:
        st.success("已讀取公開資料摘要")
    else:
        st.info("使用 Preview 預設資料摘要")
    st.caption("Static showcase. No live search. No API connection.")


tabs = st.tabs(
    [
        "Overview",
        "Module 1｜Data Foundation",
        "Module 2｜AI Metadata",
        "Module 3｜Policy Search",
        "Module 4｜Policy QA",
        "Module 5｜Policy Intelligence",
    ]
)


with tabs[0]:
    st.markdown(
        """
        <section class="hero">
            <div class="brand-chip">Version 0.1 Preview · Public Showcase</div>
            <h1>TPIS</h1>
            <div class="subtitle">Taipei Policy Intelligence Search</div>
            <div class="zh">臺北市政策智慧分析平台</div>
            <div class="copy">
                TPIS 是一個以臺北市公開市政文本為基礎的政策智慧分析原型，
                將非結構化政策文本整理為可搜尋、可比較、可追蹤的政策資料庫。
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_card(f"{summary['rows']:,}", "公開文件")
    with c2:
        kpi_card(f"{summary['issue_main_count']}", "政策主題")
    with c3:
        kpi_card(year_range(summary), "資料期間")
    with c4:
        kpi_card("v0.1", "Preview")

    st.markdown("### v0.1 已完成模組")
    m1, m2, m3 = st.columns(3)
    with m1:
        module_card("Module 1", "資料表建置", "建立公開文本資料表，整理文件日期、標題、來源、連結與全文。")
    with m2:
        module_card("Module 2", "AI metadata 標註", "將非結構化文本轉為議題、摘要、狀態、意圖與實體欄位。")
    with m3:
        module_card("Module 3", "政策搜尋原型", "展示以關鍵字探索政策文本與相關摘要的產品流程。")

    m4, m5 = st.columns(2)
    with m4:
        module_card("Module 4", "政策問答原型", "展示以資料依據為核心的問答輸出結構。")
    with m5:
        module_card("Module 5", "政策時間軸與政策智慧分析原型", "展示時間軸、政策演進、熱度儀表板與簡報助理的整合方向。")

    st.info("本公開版不包含核心分析程式、模型指令、憑證、即時搜尋或即時 AI 問答。")
    footer()


with tabs[1]:
    st.markdown('<div class="section-kicker">Module 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data Foundation</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        Module 1 建立政策文本的資料基礎，把公開市政文本整理為可分析的文件資料表。
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card(f"{summary['rows']:,}", "公開文本")
    with c2:
        kpi_card(f"{summary['date_min']} 至 {summary['date_max']}", "資料期間")
    with c3:
        kpi_card("document_table", "核心文件資料表")

    st.markdown("#### 資料來源")
    st.markdown("- 臺北市政府公開文本\n- 市長新聞稿與相關市政資料")

    st.markdown("#### document_table_v01.csv 的角色")
    st.markdown(
        """
        `document_table_v01.csv` 是 TPIS 的文件基礎層，負責保存每筆公開文本的識別碼、
        日期、標題、來源、連結與正文，讓後續 metadata 標註、搜尋與政策分析可以建立在同一份資料基準上。
        """
    )

    st.markdown("#### 欄位示意")
    st.markdown(
        """
        <div class="badge-wrap">
            <span class="badge">doc_id</span>
            <span class="badge">date</span>
            <span class="badge">title</span>
            <span class="badge">url</span>
            <span class="badge">text</span>
            <span class="badge">source_type</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### 流程")
    st.markdown(
        """
        <div class="flow-card">
            <h3>公開文本 → 文件清理 → document_table → 可分析資料庫</h3>
            <p>從分散文本整理為結構化資料表，讓後續搜尋、比較與時間軸分析有穩定的資料底層。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    footer()


with tabs[2]:
    st.markdown('<div class="section-kicker">Module 2</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Metadata</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        Module 2 把非結構化政策文本轉成可搜尋、可比較、可排序的 metadata。
        </div>
        """,
        unsafe_allow_html=True,
    )

    simple_card(
        "ai_analysis_table_v01.csv 的角色",
        "這張資料表保存每筆文本的議題分類、摘要、政策狀態、發話意圖與實體資訊，是政策搜尋與智慧分析的中介層。",
    )

    st.markdown("#### AI 分析欄位")
    st.markdown(
        """
        <div class="badge-wrap">
            <span class="badge">issue_main</span>
            <span class="badge">issue_sub</span>
            <span class="badge">summary</span>
            <span class="badge">search_summary</span>
            <span class="badge">keywords</span>
            <span class="badge">policy_status</span>
            <span class="badge">speech_intent</span>
            <span class="badge">people</span>
            <span class="badge">organizations</span>
            <span class="badge">locations</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### AI metadata preview")
    preview_label("示意內容，非即時查詢結果")
    simple_card(
        "範例議題：北士科",
        "主議題：產業發展／科技政策<br>政策狀態：推動中<br>發話意圖：政績說明／政策宣傳<br>關鍵字：北士科、AI、產業聚落、創新",
    )
    footer()


with tabs[3]:
    st.markdown('<div class="section-kicker">Module 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Policy Search</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        政策搜尋原型展示使用者輸入關鍵字後，系統如何回傳相關文件、摘要、日期、政策議題與關鍵字。
        本頁不提供真正搜尋。
        </div>
        """,
        unsafe_allow_html=True,
    )

    preview_label("示意內容，非即時查詢結果")
    st.markdown("#### 使用者輸入：北士科")
    result_card(
        "2024-02-21",
        "北士科產業聚落與智慧城市應用說明",
        "市政文本示意整理：北士科被描述為科技產業、城市治理與公共服務整合的重要場域。",
        "產業發展",
        "北士科、AI、產業聚落",
    )
    result_card(
        "2024-09-12",
        "北士科開發進度與公共利益說明",
        "市政文本示意整理：回應外界關注，聚焦用地規劃、招商進度與市民公共利益。",
        "都市發展",
        "北士科、招商、公共利益",
    )
    result_card(
        "2025-03-18",
        "北士科智慧治理與 AI 應用展示",
        "市政文本示意整理：將北士科連結智慧交通、醫療科技與創新應用場景。",
        "智慧城市",
        "AI、智慧治理、創新",
    )
    footer()


with tabs[4]:
    st.markdown('<div class="section-kicker">Module 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Policy QA</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        政策問答原型展示未來 AI 回答的資訊架構。本公開版不連 API、不產生即時回答。
        </div>
        """,
        unsafe_allow_html=True,
    )

    preview_label("示意內容，非即時 AI 回答")
    st.markdown("#### 使用者問題")
    st.markdown("> 市府如何說明北士科與 AI 產業發展？")

    st.markdown("#### 系統輸出架構")
    qa_cols = st.columns(2)
    with qa_cols[0]:
        simple_card("1. 直接回答", "市府文本通常將北士科定位為科技產業與智慧城市應用的重要場域，並以 AI、創新與產業聚落作為主要敘事。")
        simple_card("2. 主要依據", "依據示意文本，相關說法集中在招商、智慧治理、公共服務整合與創新應用場景。")
        simple_card("3. 時間脈絡", "早期聚焦開發與招商，中期連結智慧城市，近期逐步納入 AI 應用與產業成果展示。")
    with qa_cols[1]:
        simple_card("4. 可追問問題", "AI 應用是否已有具體服務？是否有可驗證的投資、進駐、就業與市民效益指標？")
        simple_card("5. 資料來源提醒", "正式版本應附上原始文本、日期、標題與來源連結，避免脫離資料依據的推論。")
    footer()


with tabs[5]:
    st.markdown('<div class="section-kicker">Module 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Policy Intelligence</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        Module 5 整合政策時間軸、政策演進分析、政策熱度儀表板與簡報助理，形成政策智慧分析展示層。
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("A. Timeline Preview")
    preview_label("示意內容，非即時查詢結果")
    st.caption("主題：敬老卡")
    timeline_card("2023-03-10", "說明敬老卡點數使用方向", "政策說明", "強調福利延續與使用彈性。")
    timeline_card("2024-05-22", "回應敬老卡適用場域討論", "持續調整", "增加跨局處協調與場域盤點。")
    timeline_card("2025-01-15", "整理長者交通與休閒支持措施", "擴充說明", "從單一補助延伸到高齡友善服務。")

    st.subheader("B. Policy Evolution Preview")
    e1, e2, e3 = st.columns(3)
    with e1:
        simple_card("早期重點", "增加供給")
    with e2:
        simple_card("中期重點", "加速興建")
    with e3:
        simple_card("近期重點", "品質、管理與社區整合")

    st.subheader("C. Attention Dashboard Preview")
    d1, d2, d3 = st.columns(3)
    with d1:
        simple_card("近期熱門議題", "交通、社宅、北士科、AI、市場改建")
    with d2:
        simple_card("上升議題", "AI、產業發展、交通安全")
    with d3:
        simple_card("下降議題", "疫情相關議題")

    st.subheader("D. Briefing Preview")
    b1, b2, b3 = st.columns(3)
    with b1:
        simple_card("資料庫顯示了什麼", "北士科常與產業發展、智慧城市、AI 應用場域等敘事連結。")
    with b2:
        simple_card("可追問方向", "AI 相關成果是已落地服務、試辦計畫，或政策願景？是否有明確績效指標？")
    with b3:
        simple_card("風險提醒", "若只引用單一文本，可能高估政策成果；應搭配預算、進度與外部資料驗證。")

    footer()
