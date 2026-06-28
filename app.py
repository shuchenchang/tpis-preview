import ast
import html

import pandas as pd
import streamlit as st

from modules.data_loader import get_data_summary, prepare_master_df, validate_data_files


STATIC_SUMMARY = {
    "rows": 1749,
    "date_min": "2022-12-25",
    "date_max": "2026-06-24",
    "issue_main_count": 18,
}

PREVIEW_NOTICE = "展示範例，非即時分析。"


st.set_page_config(
    page_title="TPIS | Taipei Policy Intelligence Search",
    layout="wide",
)


@st.cache_data(show_spinner=False)
def load_public_data(data_dir="data"):
    try:
        validation = validate_data_files(data_dir)
        if validation.get("missing_files"):
            return None, STATIC_SUMMARY, False

        master_df = prepare_master_df(data_dir)
        summary = get_data_summary(master_df)
        clean_summary = {
            "rows": summary.get("rows") or STATIC_SUMMARY["rows"],
            "date_min": normalize_date(summary.get("date_min")) or STATIC_SUMMARY["date_min"],
            "date_max": normalize_date(summary.get("date_max")) or STATIC_SUMMARY["date_max"],
            "issue_main_count": summary.get("issue_main_count")
            or STATIC_SUMMARY["issue_main_count"],
        }
        return master_df, clean_summary, True
    except Exception:
        return None, STATIC_SUMMARY, False


def normalize_date(value):
    if value is None:
        return None
    return str(value)[:10]


def year_range(summary):
    return f"{str(summary['date_min'])[:4]}–{str(summary['date_max'])[:4]}"


def parse_list_like(value):
    if value is None or pd.isna(value):
        return []
    if isinstance(value, list):
        return value
    text = str(value).strip()
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except Exception:
        pass
    return [part.strip() for part in text.split(",") if part.strip()]


def truncate(text, limit=150):
    text = "" if text is None or pd.isna(text) else str(text)
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "..."


def calculate_search_results(master_df, query="北士科", top_n=5):
    if master_df is None or master_df.empty:
        return []

    df = master_df.copy()
    fields = {
        "title_doc": 5,
        "summary": 4,
        "search_summary": 4,
        "keywords": 3,
        "issue_main": 2,
        "issue_sub": 2,
        "text": 1,
    }
    df["search_score"] = 0
    for col, weight in fields.items():
        if col in df.columns:
            hit = df[col].fillna("").astype(str).str.contains(query, case=False, na=False)
            df["search_score"] += hit.astype(int) * weight

    if "date_doc" in df.columns:
        df["date_sort"] = pd.to_datetime(df["date_doc"], errors="coerce")
    else:
        df["date_sort"] = pd.NaT

    results = (
        df[df["search_score"] > 0]
        .sort_values(["search_score", "date_sort"], ascending=[False, False])
        .head(top_n)
    )
    return results.to_dict("records")


def issue_counts(master_df, column, top_n=10):
    if master_df is None or column not in master_df.columns:
        return pd.DataFrame(columns=["議題", "筆數", "占比"])

    rows = []
    for value in master_df[column].dropna():
        items = parse_list_like(value) if column == "issue_sub" else [value]
        for item in items:
            item = str(item).strip()
            if item:
                rows.append(item)

    if not rows:
        return pd.DataFrame(columns=["議題", "筆數", "占比"])

    counts = pd.Series(rows).value_counts().head(top_n)
    total = len(rows)
    return pd.DataFrame(
        {
            "議題": counts.index,
            "筆數": counts.values,
            "占比": [f"{value / total:.1%}" for value in counts.values],
        }
    )


def monthly_attention(master_df):
    if master_df is None or "date_doc" not in master_df.columns or "issue_main" not in master_df.columns:
        return pd.DataFrame(columns=["月份", "主議題", "筆數"])

    df = master_df.copy()
    df["month"] = pd.to_datetime(df["date_doc"], errors="coerce").dt.to_period("M").astype(str)
    grouped = (
        df.dropna(subset=["month", "issue_main"])
        .groupby(["month", "issue_main"])
        .size()
        .reset_index(name="筆數")
        .sort_values(["month", "筆數"], ascending=[False, False])
    )
    grouped = grouped.rename(columns={"month": "月份", "issue_main": "主議題"})
    return grouped


def recent_attention_cards(master_df):
    trend = monthly_attention(master_df)
    if trend.empty:
        return [], []

    months = sorted(trend["月份"].unique())
    latest_month = months[-1]
    recent_months = months[-3:]
    latest = trend[trend["月份"] == latest_month].head(5)
    recent = (
        trend[trend["月份"].isin(recent_months)]
        .groupby("主議題")["筆數"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
    )
    latest_items = [f"{row['主議題']}（{row['筆數']}）" for _, row in latest.iterrows()]
    recent_items = [f"{topic}（{count}）" for topic, count in recent.items()]
    return latest_items, recent_items


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
                linear-gradient(180deg, #FFFFFF 0%, var(--background) 45%, #FFFFFF 100%);
            color: var(--text);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 2.5rem;
        }

        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.94);
            border-right: 1px solid var(--border);
        }

        .hero {
            padding: 3.8rem 0 2rem;
        }

        .brand-chip,
        .preview-label {
            display: inline-flex;
            border-radius: 999px;
            padding: 0.35rem 0.75rem;
            font-size: 0.88rem;
            margin-bottom: 1rem;
        }

        .brand-chip {
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.82);
            color: var(--muted);
        }

        .preview-label {
            color: #92400E;
            background: #FFFBEB;
            border: 1px solid #FDE68A;
        }

        .hero h1 {
            margin: 0;
            font-size: clamp(3.6rem, 15vw, 8rem);
            line-height: 0.95;
            letter-spacing: 0;
            color: var(--text);
            font-weight: 780;
        }

        .hero .subtitle {
            margin-top: 1rem;
            font-size: clamp(1.3rem, 4vw, 2.25rem);
            line-height: 1.25;
            color: var(--text);
            font-weight: 650;
        }

        .hero .zh {
            margin-top: 0.55rem;
            font-size: clamp(1.05rem, 3vw, 1.4rem);
            color: var(--muted);
            font-weight: 520;
        }

        .hero .copy,
        .section-copy {
            max-width: 820px;
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

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 1.35rem 0 1.6rem;
        }

        .kpi-card,
        .module-card,
        .result-card,
        .preview-card,
        .timeline-card,
        .answer-card,
        .status-card,
        .briefing-card,
        .footer {
            border: 1px solid var(--border);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
            box-shadow: 0 18px 50px rgba(17, 24, 39, 0.05);
        }

        .kpi-card {
            padding: 1rem;
            min-width: 0;
        }

        .kpi-value {
            color: var(--text);
            font-size: clamp(1.4rem, 4vw, 2.05rem);
            line-height: 1.1;
            font-weight: 760;
            white-space: normal;
            overflow-wrap: break-word;
            word-break: normal;
        }

        .kpi-label,
        .muted {
            color: var(--muted);
            line-height: 1.55;
        }

        .module-card,
        .result-card,
        .preview-card,
        .answer-card,
        .status-card,
        .briefing-card {
            padding: 1.05rem;
            min-height: 100%;
        }

        .module-card h3,
        .result-card h3,
        .preview-card h3,
        .answer-card h3,
        .status-card h3,
        .briefing-card h3 {
            font-size: 1.12rem;
            line-height: 1.35;
            margin: 0 0 0.35rem;
            color: var(--text);
        }

        .module-card .eyebrow {
            color: var(--primary);
            font-size: 0.9rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }

        .module-card p,
        .result-card p,
        .preview-card p,
        .answer-card p,
        .status-card p,
        .briefing-card p {
            color: #4B5563;
            line-height: 1.68;
            margin: 0;
            overflow-wrap: break-word;
            word-break: normal;
        }

        .result-card {
            margin: 1rem 0;
        }

        .result-title {
            font-size: clamp(1.18rem, 3.6vw, 1.55rem);
            line-height: 1.35;
            font-weight: 720;
            margin: 0.3rem 0 0.55rem;
            color: var(--text);
        }

        .source-url {
            margin-top: 0.8rem;
            color: var(--primary);
            font-size: 0.9rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
        }

        .answer-card {
            margin: 0.85rem 0;
        }

        .answer-label {
            color: var(--primary);
            font-weight: 760;
            font-size: 0.92rem;
            letter-spacing: 0.02em;
            margin-bottom: 0.35rem;
        }

        .status-card {
            text-align: left;
        }

        .status-mark {
            color: var(--primary);
            font-size: 1.35rem;
            font-weight: 760;
            margin-bottom: 0.2rem;
            white-space: normal;
            word-break: normal;
            overflow-wrap: break-word;
        }

        .status-value {
            font-size: 1.05rem;
            color: var(--text);
            font-weight: 700;
            margin-bottom: 0.35rem;
        }

        .briefing-card {
            margin-bottom: 0.85rem;
        }

        .badge-wrap {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.85rem;
        }

        .badge {
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 0.35rem 0.7rem;
            background: #FFFFFF;
            color: #374151;
            font-size: 0.9rem;
        }

        .timeline-list {
            position: relative;
            margin: 1rem 0;
        }

        .timeline-item {
            display: grid;
            grid-template-columns: 2.2rem 1fr;
            gap: 1rem;
            margin-bottom: 0;
        }

        .timeline-marker {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .timeline-dot {
            width: 0.82rem;
            height: 0.82rem;
            border-radius: 999px;
            background: #FFFFFF;
            border: 2px solid #9CA3AF;
            margin-top: 1.1rem;
            box-sizing: content-box;
        }

        .timeline-line {
            width: 2px;
            flex: 1;
            min-height: 7.8rem;
            background: var(--border);
            margin-top: 0.45rem;
        }

        .timeline-card {
            padding: 1.05rem 1.1rem;
            margin-bottom: 1rem;
            background: #F9FAFB;
            border-color: #E5E7EB;
            box-shadow: 0 10px 30px rgba(17, 24, 39, 0.04);
        }

        .timeline-date {
            color: #6B7280;
            font-weight: 740;
            font-size: 0.92rem;
            margin-bottom: 0.35rem;
        }

        .timeline-card h4 {
            margin: 0 0 0.25rem;
            font-size: 1.06rem;
            line-height: 1.45;
        }

        .timeline-card p {
            margin: 0.18rem 0;
            color: #4B5563;
            line-height: 1.6;
            word-break: normal;
            overflow-wrap: break-word;
        }

        .compact-table {
            border: 1px solid var(--border);
            border-radius: 8px;
            overflow: hidden;
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

        @media (max-width: 760px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
                padding-top: 1.25rem;
            }

            .hero {
                padding: 2.2rem 0 1.4rem;
            }

            .kpi-grid {
                grid-template-columns: 1fr;
                gap: 0.65rem;
            }

            .kpi-card {
                display: block;
            }

            .kpi-value {
                font-size: 1.4rem;
                text-align: left;
            }

            .kpi-label {
                margin-bottom: 0.3rem;
            }

            .timeline-card {
                margin-bottom: 0.7rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def kpi_grid(items):
    for label, value in items:
        with st.container(border=True):
            st.caption(label)
            st.markdown(f"### {value}")


def system_workflow():
    steps = [
        "Public Documents",
        "AI Metadata",
        "Policy Database",
        "Search",
        "Analysis",
        "Briefing",
    ]
    st.markdown("## System Workflow")
    for index, step in enumerate(steps):
        with st.container(border=True):
            st.markdown(f"**{step}**")
        if index < len(steps) - 1:
            st.markdown("↓")


def module_card(module, title, body):
    with st.container(border=True):
        st.caption(module)
        st.markdown(f"### {title}")
        st.markdown(body)


def simple_card(title, body):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.markdown(body)


def result_card(item):
    date_value = normalize_date(item.get("date_doc") or item.get("date"))
    title = item.get("title_doc") or item.get("title") or "未命名文件"
    summary = item.get("search_summary") or item.get("summary") or item.get("text") or ""
    issue_main = item.get("issue_main") or "未分類"
    issue_sub = "、".join(parse_list_like(item.get("issue_sub"))) or "未標註"
    keywords = "、".join(parse_list_like(item.get("keywords"))[:4]) or "未標註"
    url = item.get("url") or ""
    score = item.get("search_score", "")

    with st.container(border=True):
        st.caption(date_value)
        st.markdown(f"### {title}")
        st.markdown(truncate(summary, 180))
        st.markdown(
            f"**主議題：** {issue_main}  \n"
            f"**次議題：** {issue_sub}  \n"
            f"**Search Score：** {score}  \n"
            f"**關鍵字：** {keywords}"
        )
        st.caption(f"Source URL：{url}")


def answer_card(label, body):
    with st.container(border=True):
        st.markdown(f"### {label}")
        st.markdown(body)


def timeline_item(date, event, status, change_type, delta, title, url, is_last=False):
    line_html = "" if is_last else '<div class="timeline-line"></div>'
    st.markdown(
        f"""
        <div class="timeline-item">
            <div class="timeline-marker">
                <div class="timeline-dot"></div>
                {line_html}
            </div>
            <div class="timeline-card">
                <div class="timeline-date">{html.escape(date)}</div>
                <h4>{html.escape(event)}</h4>
                <p><strong>政策狀態：</strong>{html.escape(status)}</p>
                <p><strong>Change Type：</strong>{html.escape(change_type)}</p>
                <p><strong>Policy Delta：</strong>{html.escape(delta)}</p>
                <p><strong>來源：</strong>{html.escape(title)}</p>
                <p><strong>URL：</strong>{html.escape(url)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def status_card(mark, title, value, body):
    with st.container(border=True):
        st.markdown(f"### {mark} {title}")
        st.markdown(f"**{value}**")
        st.markdown(body)


def briefing_card(title, body):
    with st.container(border=True):
        st.markdown(f"### {title}")
        st.markdown(body)


def preview_label(text=PREVIEW_NOTICE):
    st.warning(PREVIEW_NOTICE)


def footer():
    st.divider()
    st.caption("TPIS")
    st.caption("Taipei Policy Intelligence Search")
    st.caption("Version 0.2 Colab Results Showcase · 2026")


master_df, summary, loaded_from_data = load_public_data("data")
search_results = calculate_search_results(master_df, "北士科", 5)
main_rank = issue_counts(master_df, "issue_main", 10)
sub_rank = issue_counts(master_df, "issue_sub", 10)
monthly_trend = monthly_attention(master_df)
latest_topics, recent_topics = recent_attention_cards(master_df)
inject_styles()


with st.sidebar:
    st.markdown("## TPIS")
    st.caption("Taipei Policy Intelligence Search")
    st.caption("版本 v0.2")
    st.divider()
    st.metric("公開文件", f"{summary['rows']:,}")
    st.metric("政策主題", f"{summary['issue_main_count']}")
    st.write(f"資料期間：{summary['date_min']} 至 {summary['date_max']}")
    st.divider()
    if loaded_from_data:
        st.success("已讀取公開資料摘要")
    else:
        st.info("使用展示版預設摘要")
    st.caption("Colab 實測成果展示｜公開版不連接 API")


tabs = st.tabs(
    [
        "系統總覽",
        "事實查詢",
        "議題分析",
        "政策演變",
        "政策一致性",
        "攻防分析",
    ]
)


with tabs[0]:
    st.caption("v0.2 Colab Results Showcase")
    st.title("TPIS")
    st.subheader("Taipei Policy Intelligence Search")
    st.markdown(
        "AI-powered policy intelligence platform for structured retrieval, "
        "analysis and briefing of public policy documents."
    )
    preview_label()
    st.markdown("臺北市政策智慧分析平台")
    st.markdown(
        "TPIS 是一個以臺北市公開市政文本為基礎的政策智慧分析原型，"
        "將非結構化政策文本整理為可搜尋、可比較、可追蹤、可攻防的政策資料庫。"
    )
    kpi_grid(
        [
            ("公開文件", f"{summary['rows']:,}"),
            ("政策主題", f"{summary['issue_main_count']}"),
            ("資料期間", f"{summary['date_min']} 至 {summary['date_max']}"),
            ("版本", "v0.2 Colab Results Showcase"),
        ]
    )
    system_workflow()

    st.markdown("### 五大模組成果")
    c1, c2, c3 = st.columns(3)
    with c1:
        module_card("Module 1", "事實查詢", "以關鍵字與政策問題檢索資料庫，整理相關原文、摘要與回答依據。")
    with c2:
        module_card("Module 2", "議題分析", "統計主議題、次議題與月份趨勢，呈現政策注意力分布。")
    with c3:
        module_card("Module 3", "政策演變", "依時間排序同一政策議題，觀察政策狀態與論述重點如何改變。")
    c4, c5 = st.columns(2)
    with c4:
        module_card("Module 4", "政策一致性分析", "比較不同文本之間的立場、承諾、優先順序與理由變化。")
    with c5:
        module_card("Module 5", "攻防分析", "整理政策依據、可追問方向、攻防強度與需要補強的資料。")
    footer()


with tabs[1]:
    st.caption("Module 1")
    st.header("事實查詢")
    st.markdown("快速搜尋公開政策文本，提供可追溯的引用依據。")
    preview_label()

    st.markdown("#### 查詢案例")
    st.markdown("- 查詢詞：**北士科**\n- 問題：**提過北士科？**")

    st.markdown("### A. Fact Search 實測結果")
    for item in search_results[:5]:
        result_card(item)

    st.markdown("### B. GPT Answer 實測結果")
    answer_card(
        "Question",
        "提過北士科？",
    )
    answer_card(
        "Answer",
        "公開文本中多次提到北士科，內容主要集中在產業發展、科技聚落、重大投資、輝達進駐、智慧城市與 AI 應用等政策脈絡。",
    )
    answer_card(
        "Evidence",
        "資料庫可找到北士科相關新聞稿與市政文本，包含產業招商、科技園區發展、就業人口估算、交通影響評估與智慧治理應用等內容。",
    )
    answer_card(
        "Sources",
        "Fact Search 前 5 筆結果顯示，北士科常與 AI、產業聚落、輝達、智慧治理、都市發展與交通規劃共同出現。",
    )
    footer()


with tabs[2]:
    st.caption("Module 2")
    st.header("議題分析")
    st.markdown("自動統計政策議題分類、關注重點與議題分布。")
    preview_label()

    st.markdown("### 1. 主議題排行榜")
    st.dataframe(main_rank, use_container_width=True, hide_index=True)

    st.markdown("### 2. 次議題排行榜")
    st.dataframe(sub_rank, use_container_width=True, hide_index=True)

    st.markdown("### 3. 每月議題趨勢")
    if not monthly_trend.empty:
        compact_trend = monthly_trend.head(20)
        st.dataframe(compact_trend, use_container_width=True, hide_index=True)
    else:
        st.info("目前沒有可顯示的月份趨勢資料。")

    st.markdown("### 4. 政策注意力儀表板")
    d1, d2 = st.columns(2)
    with d1:
        simple_card("最近月份熱門議題", "、".join(latest_topics) if latest_topics else "目前沒有資料")
    with d2:
        simple_card("近三個月熱門議題", "、".join(recent_topics) if recent_topics else "目前沒有資料")
    footer()


with tabs[3]:
    st.caption("Module 3")
    st.header("政策演變")
    st.markdown("依時間軸整理政策發展歷程，觀察重要調整與演變。")
    preview_label()
 
    st.markdown("#### 主題：敬老卡")
    timeline_item(
        "2026-06-22",
        "敬老卡 600 點上路與重陽禮金時程說明",
        "政策擴充",
        "Benefit Expansion",
        "每月點數由 480 點提高至 600 點，並規劃新增生活消費通路與點數累積機制。",
        "宣布敬老福利再升級 敬老卡600點7月上路、重陽禮金9月發放",
        "https://www.gov.taipei/",
    )
    timeline_item(
        "2026-06-10",
        "關懷獨居長者並說明敬老措施",
        "政策延伸",
        "Service Integration",
        "敬老卡點數提高與志工關懷、高齡照顧據點等長者支持措施共同納入高齡友善政策敘事。",
        "「陪伴不缺席」關懷獨居長者 蔣萬安號召全民加入志工行列",
        "https://www.gov.taipei/",
    )
    timeline_item(
        "2025-10-29",
        "市政總質詢回應敬老點數使用範圍",
        "滾動評估",
        "Scope Review",
        "除提高點數外，進一步評估合作場域、累積機制與使用誘因。",
        "赴議會報告追加預算及總預算案",
        "https://www.gov.taipei/",
    )
    timeline_item(
        "2025-03-05",
        "高齡友善與長者福利措施納入市政討論",
        "政策延伸",
        "Framing Shift",
        "敬老卡從交通補助延伸到高齡友善、生活支持與社會參與政策。",
        "臺北市政府市政會議紀錄",
        "https://www.gov.taipei/",

    )
    simple_card(
        "整體時間軸觀察",
        "敬老卡政策從既有交通與場館使用補助，逐步擴充到點數提高、醫療與生活消費場域、點數累積與高齡友善城市敘事。政策論述重點由單一福利工具，轉向長者生活支持與城市照顧系統。",
    )
    footer()


with tabs[4]:
    st.caption("Module 4")
    st.header("政策一致性分析")
    st.markdown("比較不同時期政策內容，辨識可能的立場與策略變化。")
    preview_label()
    
    c1, c2 = st.columns(2)
    with c1:
        simple_card("比較對象 A", "早期敬老卡文本：聚焦交通補助、公有場館使用與基本長者福利。")
    with c2:
        simple_card("比較對象 B", "近期敬老卡文本：聚焦 600 點、生活消費通路、點數累積與高齡友善城市。")

    st.markdown("#### 分析面向")
    status_card("✓", "立場", "無明顯改變", "整體立場延續支持長者福利。")
    status_card("△", "承諾", "部分調整", "從維持既有服務，擴充為點數提高與通路增加。")
    status_card("△", "優先順序", "部分調整", "從交通便利轉向生活支持與社會參與。")
    status_card("△", "理由", "新增說明", "從補助工具轉為高齡友善城市治理。")

    st.markdown("#### 輸出結果")
    simple_card("是否存在明顯變化", "有。變化主要是政策範圍擴充，不是立場反轉。")
    simple_card("變化類型", "政策擴充、服務場域擴大、政策敘事升級。")
    simple_card("依據摘要", "近期文本增加 600 點、超商超市藥局農會等生活消費通路，以及第二代敬老卡與點數累積規劃。")
    simple_card("風險提醒", "若只看單一文本，可能忽略政策由交通補助擴展到生活支持的演變；正式分析仍需附上原文與日期。")
    footer()


with tabs[5]:
    st.caption("Module 5")
    st.header("攻防分析")
    st.markdown("根據公開資料整理可引用資訊、可質疑重點與追問方向。")
    preview_label()
   
    st.markdown("#### 批評主題：北士科 AI 政績")
    simple_card("搜尋關鍵字", "北士科、AI、產業發展、輝達、智慧城市")
    briefing_card(
        "🟢 資料顯示",
        "市府公開文本中，北士科經常與 AI、輝達、智慧城市、產業聚落、招商與科技治理等主題共同出現。這些文本呈現市府將北士科放在產業發展與智慧城市敘事中的脈絡，但仍需要進一步檢視哪些內容已落地、哪些仍屬規劃或招商階段。",
    )
    briefing_card(
        "🔴 可質疑",
        "可追問是否已有具體落地成果、是否有明確 KPI、是否已有企業正式進駐與營運數據、交通承載與土地程序是否同步說明、公共利益如何衡量，以及相關敘事是否仍停留在願景包裝而非可驗證政績。",
    )
    briefing_card(
        "🟡 可追問",
        "目前北士科已有多少 AI 相關企業正式進駐？輝達相關投資是否已有明確時程與可公開契約？市府所稱 AI 產業成果，有沒有產值、就業或招商 KPI？交通承載、土地程序與公共設施是否已同步到位？哪些成果已完成，哪些仍只是規劃或招商階段？",
    )
    briefing_card(
        "📄 可引用",
        "可引用市府新聞稿、市政會議資料，以及北士科、AI、輝達、招商、智慧城市相關公開文本。需要補強的資料包括預算、工程進度、KPI、招商成果、正式進駐與營運數據、交通評估、土地程序與公共利益指標。",
    )
    footer()
