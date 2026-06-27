import streamlit as st

from modules.data_loader import get_data_summary, prepare_master_df, validate_data_files


STATIC_SUMMARY = {
    "rows": 1749,
    "date_min": "2022-12-25",
    "date_max": "2026-06-24",
    "issue_main_count": 18,
}


st.set_page_config(
    page_title="TPIS | Taipei Policy Intelligence Search",
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


def format_year_range(date_min, date_max):
    return f"{str(date_min)[:4]}–{str(date_max)[:4]}"


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
                radial-gradient(circle at top left, rgba(37, 99, 235, 0.10), transparent 30rem),
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

        button[kind="secondary"]:disabled {
            color: #FFFFFF !important;
            background: var(--primary) !important;
            border-color: var(--primary) !important;
            opacity: 0.85 !important;
        }

        .brand-chip {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            background: rgba(255, 255, 255, 0.78);
            color: var(--muted);
            font-size: 0.88rem;
            margin-bottom: 1rem;
        }

        .hero {
            padding: 4.6rem 0 2.4rem;
            text-align: center;
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
            margin: 1.25rem auto 0;
            font-size: clamp(1.35rem, 4.2vw, 2.4rem);
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
            max-width: 760px;
            margin: 1.4rem auto 0;
            color: #374151;
            font-size: 1.05rem;
            line-height: 1.85;
        }

        .cta-row {
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-top: 1.5rem;
        }

        .cta {
            display: inline-flex;
            border-radius: 999px;
            padding: 0.7rem 1rem;
            background: var(--primary);
            color: #FFFFFF;
            font-weight: 680;
            box-shadow: 0 16px 36px rgba(37, 99, 235, 0.22);
        }

        .cta-note {
            display: inline-flex;
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.7rem 1rem;
            background: rgba(255, 255, 255, 0.78);
            color: var(--muted);
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
            max-width: 760px;
            color: var(--muted);
            font-size: 1.02rem;
            line-height: 1.75;
            margin-bottom: 1.3rem;
        }

        .kpi-card,
        .feature-card,
        .preview-card,
        .timeline-card,
        .coverage-card,
        .roadmap-card,
        .footer {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.92);
            box-shadow: 0 18px 50px rgba(17, 24, 39, 0.05);
        }

        .kpi-card {
            padding: 1rem;
            min-height: 7.4rem;
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

        .feature-card,
        .preview-card,
        .coverage-card,
        .roadmap-card {
            padding: 1.05rem;
            min-height: 100%;
        }

        .feature-card h3,
        .preview-card h3,
        .coverage-card h3,
        .roadmap-card h3 {
            font-size: 1.12rem;
            line-height: 1.35;
            margin: 0 0 0.25rem;
            color: var(--text);
        }

        .feature-card .cn,
        .roadmap-card .version {
            color: var(--primary);
            font-size: 0.92rem;
            font-weight: 680;
            margin-bottom: 0.6rem;
        }

        .feature-card p,
        .preview-card p,
        .coverage-card p,
        .roadmap-card p {
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
            padding: 0.9rem;
            background: #FFFFFF;
            margin-bottom: 0.75rem;
        }

        .result-card strong {
            display: block;
            font-size: 1rem;
            margin: 0.18rem 0 0.35rem;
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

            .cta-row {
                justify-content: flex-start;
            }

            .timeline-card {
                grid-template-columns: 1fr;
            }

            .kpi-card,
            .feature-card,
            .preview-card,
            .coverage-card,
            .roadmap-card {
                padding: 0.95rem;
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


def feature_card(title, cn_title, body):
    st.markdown(
        f"""
        <div class="feature-card">
            <h3>{title}</h3>
            <div class="cn">{cn_title}</div>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(date, title, summary, issue):
    st.markdown(
        f"""
        <div class="result-card">
            <div class="muted">{date} · {issue}</div>
            <strong>{title}</strong>
            <p>{summary}</p>
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


def roadmap_card(version, title, body):
    st.markdown(
        f"""
        <div class="roadmap-card">
            <div class="version">{version}</div>
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def preview_label():
    st.markdown(
        '<div class="preview-label">示意內容，非即時查詢結果</div>',
        unsafe_allow_html=True,
    )


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
year_range = format_year_range(summary["date_min"], summary["date_max"])
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
        st.success("已讀取本機資料摘要")
    else:
        st.info("使用 Preview 預設資料摘要")

    st.caption("Showcase only. No live search. No AI analysis.")


tabs = st.tabs(
    [
        "Overview",
        "Capabilities",
        "Data Coverage",
        "Preview",
        "Roadmap",
    ]
)


with tabs[0]:
    st.markdown(
        """
        <section class="hero">
            <div class="brand-chip">Version 0.1 Preview · Static Showcase</div>
            <h1>TPIS</h1>
            <div class="subtitle">Taipei Policy Intelligence Search</div>
            <div class="zh">臺北市政策智慧分析平台</div>
            <div class="copy">
                讓政策資料變得可以探索、比較與理解。TPIS 整合臺北市政府公開政策文本，
                建立可支援政策搜尋、時間軸分析、政策演進比較與攻防簡報的智慧資料平台。
                本頁為 v0.1 Preview，暫未開放即時搜尋與 AI 分析功能。
            </div>
            <div class="cta-row">
                <span class="cta">Explore the Preview</span>
                <span class="cta-note">Static showcase · no live query</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        kpi_card(f"{summary['rows']:,}", "公開文件")
    with k2:
        kpi_card(f"{summary['issue_main_count']}", "政策主題")
    with k3:
        kpi_card(year_range, "資料期間")
    with k4:
        kpi_card("v0.1", "Preview")

    st.markdown(" ")
    st.info("本版本是 Showcase / Preview，不是正式測試版；不提供即時搜尋、不連接 AI 分析服務。")
    footer()


with tabs[1]:
    st.markdown('<div class="section-kicker">Capabilities</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">政策資料的探索、脈絡與證據層</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        TPIS 的設計目標，是把分散的公開文本整理成可追蹤、可比較、可回溯來源的政策資料介面。
        v0.1 先展示產品方向，功能尚未對外開放。
        </div>
        """,
        unsafe_allow_html=True,
    )

    row1 = st.columns(3)
    with row1[0]:
        feature_card(
            "Policy Search",
            "政策搜尋",
            "快速探索臺北市公開政策文本，掌握特定議題的相關文件與脈絡。",
        )
    with row1[1]:
        feature_card(
            "Timeline",
            "政策時間軸",
            "依時間整理政策事件，看見一項政策如何被提出、擴充、調整與執行。",
        )
    with row1[2]:
        feature_card(
            "Policy Evolution",
            "政策演進分析",
            "比較不同時間點的政策說法，辨識延續、擴充、轉向或潛在不一致。",
        )

    row2 = st.columns(3)
    with row2[0]:
        feature_card(
            "Briefing Assistant",
            "攻防簡報助理",
            "根據公開資料整理可追問方向、政策依據與風險提醒。",
        )
    with row2[1]:
        feature_card(
            "Attention Dashboard",
            "政策熱度儀表板",
            "觀察不同月份的政策主題變化，辨識上升與下降議題。",
        )
    with row2[2]:
        feature_card(
            "Evidence-first Output",
            "證據優先輸出",
            "所有分析都以公開文本與資料來源為基礎，避免無根據推論。",
        )

    footer()


with tabs[2]:
    st.markdown('<div class="section-kicker">Data Coverage</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">以公開市政文本建立政策資料層</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        v0.1 展示資料範圍與 metadata 設計。若本機資料可讀取，頁面會使用實際摘要；
        若資料讀取失敗，仍會使用預設靜態數字顯示。
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class="coverage-card">
                <h3>資料來源與範圍</h3>
                <p>
                    <strong>資料來源：</strong>臺北市政府公開文本<br>
                    <strong>文件類型：</strong>市長新聞稿與相關市政文本<br>
                    <strong>資料期間：</strong>{summary['date_min']} 至 {summary['date_max']}<br>
                    <strong>文件數：</strong>{summary['rows']:,} 筆<br>
                    <strong>政策主題：</strong>{summary['issue_main_count']} 類
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="coverage-card">
                <h3>AI metadata 欄位</h3>
                <p>每筆文本可搭配結構化欄位，支援後續搜尋、分類、比較與摘要。</p>
                <div class="badge-wrap">
                    <span class="badge">主議題</span>
                    <span class="badge">次議題</span>
                    <span class="badge">摘要</span>
                    <span class="badge">搜尋摘要</span>
                    <span class="badge">政策狀態</span>
                    <span class="badge">發話意圖</span>
                    <span class="badge">人物</span>
                    <span class="badge">組織</span>
                    <span class="badge">地點</span>
                    <span class="badge">關鍵字</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Preview 資料提醒"):
        st.markdown(
            """
            - 本頁不執行即時查詢。
            - Preview 內容僅展示未來介面與輸出樣式。
            - 正式測試版將補上資料來源、查詢紀錄與可驗證的引用脈絡。
            """
        )

    footer()


with tabs[3]:
    st.markdown('<div class="section-kicker">Preview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">靜態模擬展示區</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        以下展示未來可能的輸出樣式。所有內容皆為示意，不代表即時查詢結果。
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("A. Policy Search Preview")
    st.caption("模擬搜尋關鍵字：北士科")
    preview_label()
    result_card(
        "2024-02-21",
        "北士科產業聚落與智慧城市應用說明",
        "市政文本示意整理：北士科被描述為科技產業、城市治理與公共服務整合的重要場域。",
        "產業發展",
    )
    result_card(
        "2024-09-12",
        "北士科開發進度與公共利益說明",
        "市政文本示意整理：回應外界關注，聚焦用地規劃、招商進度與市民公共利益。",
        "都市發展",
    )
    result_card(
        "2025-03-18",
        "北士科智慧治理與 AI 應用展示",
        "市政文本示意整理：將北士科連結智慧交通、醫療科技與創新應用場景。",
        "智慧城市",
    )

    st.subheader("B. Timeline Preview")
    st.caption("主題：敬老卡")
    preview_label()
    timeline_card(
        "2023-03-10",
        "說明敬老卡點數使用方向",
        "政策說明",
        "強調福利延續與使用彈性，作為高齡友善服務的一部分。",
    )
    timeline_card(
        "2024-05-22",
        "回應敬老卡適用場域討論",
        "持續調整",
        "從既有福利工具延伸到跨局處場域盤點與服務設計。",
    )
    timeline_card(
        "2025-01-15",
        "整理長者交通與休閒支持措施",
        "擴充說明",
        "將單一補助敘事擴展為高齡友善城市服務的一環。",
    )

    st.subheader("C. Briefing Preview")
    st.caption("主題：北士科 AI 政績")
    preview_label()
    b1, b2, b3 = st.columns(3)
    with b1:
        simple_card(
            "資料庫顯示了什麼",
            "北士科常與產業發展、智慧城市、AI 應用場域等敘事連結。政策分析應進一步檢視具體投資、服務落地與公開進度。",
        )
    with b2:
        simple_card(
            "可追問方向",
            "AI 相關成果是已落地服務、試辦計畫，或政策願景？是否有明確績效指標、期程與可驗證資料？",
        )
    with b3:
        simple_card(
            "風險提醒",
            "若只引用單一文本，可能高估政策成果。應搭配原始資料、預算、執行進度與外部資料交叉驗證。",
        )

    footer()


with tabs[4]:
    st.markdown('<div class="section-kicker">Roadmap</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">從 Showcase 到 Beta 的開放節奏</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="section-copy">
        TPIS 會先完成展示與資料層驗證，再逐步開放搜尋、時間軸與 AI 分析能力。
        </div>
        """,
        unsafe_allow_html=True,
    )

    r1 = st.columns(2)
    with r1[0]:
        roadmap_card("v0.1 Preview", "靜態展示頁", "建立產品敘事、資料範圍與模擬輸出樣式。")
    with r1[1]:
        roadmap_card("v0.2 Search Preview", "開放政策搜尋展示", "提供基本關鍵字搜尋與可讀的政策文本結果卡片。")

    r2 = st.columns(2)
    with r2[0]:
        roadmap_card("v0.3 Timeline Preview", "開放政策時間軸", "針對單一政策主題建立時間序列與政策狀態變化。")
    with r2[1]:
        roadmap_card(
            "v0.4 AI Analysis Preview",
            "開放 AI 問答與政策演進分析",
            "加入以證據為基礎的問答、比較與簡報輔助輸出。",
        )

    roadmap_card(
        "v1.0 Beta",
        "完整測試版",
        "整合搜尋、時間軸、政策演進、儀表板與來源追蹤，進入可控測試階段。",
    )

    st.info("Streamlit Cloud 部署 v0.1 Preview 不需要設定任何 API key。")
    footer()
