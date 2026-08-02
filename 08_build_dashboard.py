import os
import shutil
import html as html_lib

import pandas as pd


DASHBOARD_DIR = "outputs/dashboard"
ASSET_DIR = os.path.join(DASHBOARD_DIR, "assets")

os.makedirs(DASHBOARD_DIR, exist_ok=True)
os.makedirs(ASSET_DIR, exist_ok=True)


FIGURES = {
    "manhattan_drive_network": "outputs/figures/manhattan_drive_network.png",
    "high_flow_edges_map": "outputs/figures/high_flow_edges_map.png",
    "top20_key_nodes_bar": "outputs/figures/top20_key_nodes_bar.png",
    "key_nodes_map": "outputs/figures/key_nodes_map.png",
    "vulnerability_od_reachability": "outputs/figures/vulnerability_od_reachability.png",
    "vulnerability_avg_delay": "outputs/figures/vulnerability_avg_delay.png",
    "vulnerability_lcc_ratio": "outputs/figures/vulnerability_lcc_ratio.png",
}

TABLE_KEY_NODES = "outputs/tables/top_key_nodes_with_streets.csv"
TABLE_VULNERABILITY = "outputs/tables/vulnerability_results_summary.csv"
TABLE_OD = "data/processed/od_nodes.csv"
TABLE_TAXI = "data/processed/green_manhattan_all.csv"


STYLE_CSS = """
<style>
    :root {
        --bg: #f3f7fb;
        --panel: #ffffff;
        --panel-soft: #f8fafc;
        --text-main: #0f172a;
        --text-sub: #64748b;
        --text-light: #94a3b8;
        --blue: #2563eb;
        --blue-dark: #1e40af;
        --cyan: #06b6d4;
        --green: #10b981;
        --orange: #f59e0b;
        --red: #ef4444;
        --border: #e2e8f0;
        --shadow-sm: 0 4px 14px rgba(15, 23, 42, 0.05);
        --shadow-md: 0 14px 34px rgba(15, 23, 42, 0.08);
        --radius-lg: 22px;
        --radius-md: 16px;
    }

    * {
        box-sizing: border-box;
    }

    html {
        scroll-behavior: smooth;
    }

    body {
        margin: 0;
        font-family: "Microsoft YaHei", "微软雅黑", "Segoe UI", Arial, sans-serif;
        background:
            radial-gradient(circle at top left, rgba(59, 130, 246, 0.12), transparent 34%),
            radial-gradient(circle at top right, rgba(6, 182, 212, 0.13), transparent 32%),
            var(--bg);
        color: var(--text-main);
    }

    .topbar {
        position: sticky;
        top: 0;
        z-index: 20;
        height: 68px;
        background: rgba(255, 255, 255, 0.88);
        backdrop-filter: blur(18px);
        border-bottom: 1px solid rgba(226, 232, 240, 0.9);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 46px;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 19px;
        font-weight: 800;
        letter-spacing: 0.2px;
        color: var(--text-main);
    }

    .brand::before {
        content: "";
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--blue), var(--cyan));
        box-shadow: 0 0 0 6px rgba(37, 99, 235, 0.12);
    }

    .nav a {
        margin-left: 26px;
        text-decoration: none;
        color: #475569;
        font-size: 14px;
        font-weight: 600;
        transition: 0.2s ease;
    }

    .nav a:hover {
        color: var(--blue);
    }

    .hero {
        position: relative;
        overflow: hidden;
        color: white;
        padding: 74px 46px 68px 46px;
        background:
            linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 64, 175, 0.95) 58%, rgba(6, 182, 212, 0.88) 100%);
    }

    .hero::before {
        content: "";
        position: absolute;
        width: 360px;
        height: 360px;
        right: -90px;
        top: -130px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.13);
    }

    .hero::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        left: 54%;
        bottom: -150px;
        border-radius: 50%;
        background: rgba(14, 165, 233, 0.22);
    }

    .hero-inner {
        position: relative;
        z-index: 2;
        max-width: 1220px;
        margin: 0 auto;
    }

    .hero-kicker {
        display: inline-block;
        margin-bottom: 18px;
        padding: 7px 13px;
        border-radius: 999px;
        color: #dbeafe;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.16);
        font-size: 13px;
        letter-spacing: 0.4px;
    }

    .hero h1 {
        margin: 0 0 18px 0;
        max-width: 920px;
        font-size: 38px;
        line-height: 1.34;
        letter-spacing: 0.4px;
        font-weight: 800;
    }

    .hero p {
        max-width: 900px;
        margin: 0 0 26px 0;
        font-size: 16px;
        line-height: 1.95;
        opacity: 0.93;
    }

    .tag {
        display: inline-flex;
        align-items: center;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(255, 255, 255, 0.14);
        color: #eff6ff;
        font-size: 13px;
        font-weight: 700;
        margin-right: 10px;
        margin-bottom: 8px;
        border: 1px solid rgba(255, 255, 255, 0.18);
    }

    .container {
        max-width: 1260px;
        margin: 0 auto;
        padding: 38px 30px 68px 30px;
    }

    section {
        margin-bottom: 42px;
    }

    .section-title {
        position: relative;
        font-size: 25px;
        font-weight: 800;
        margin: 0 0 12px 0;
        color: var(--text-main);
        letter-spacing: 0.2px;
    }

    .section-title::before {
        content: "";
        display: inline-block;
        width: 6px;
        height: 22px;
        margin-right: 10px;
        border-radius: 999px;
        vertical-align: -4px;
        background: linear-gradient(180deg, var(--blue), var(--cyan));
    }

    .section-subtitle {
        margin: 0 0 20px 16px;
        color: var(--text-sub);
        font-size: 14px;
        line-height: 1.8;
    }

    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        background: rgba(255, 255, 255, 0.92);
        border-radius: var(--radius-lg);
        padding: 24px 24px 22px 24px;
        border: 1px solid rgba(226, 232, 240, 0.9);
        box-shadow: var(--shadow-sm);
        transition: 0.25s ease;
    }

    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
    }

    .kpi-card::after {
        content: "";
        position: absolute;
        right: -42px;
        top: -42px;
        width: 110px;
        height: 110px;
        border-radius: 50%;
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(6, 182, 212, 0.1));
    }

    .kpi-label {
        position: relative;
        z-index: 1;
        font-size: 14px;
        color: var(--text-sub);
        margin-bottom: 10px;
    }

    .kpi-value {
        position: relative;
        z-index: 1;
        font-size: 31px;
        font-weight: 850;
        color: var(--blue-dark);
        letter-spacing: -0.5px;
    }

    .kpi-note {
        position: relative;
        z-index: 1;
        margin-top: 9px;
        font-size: 12px;
        color: var(--text-light);
        line-height: 1.6;
    }

    .process {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 14px;
    }

    .process-step {
        position: relative;
        background: white;
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 18px 12px;
        text-align: center;
        font-size: 14px;
        font-weight: 800;
        color: var(--blue-dark);
        box-shadow: var(--shadow-sm);
    }

    .process-step::after {
        content: "→";
        position: absolute;
        right: -13px;
        top: 50%;
        transform: translateY(-50%);
        color: var(--blue);
        font-weight: 900;
    }

    .process-step:last-child::after {
        display: none;
    }

    .grid-2 {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
    }

    .grid-3 {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
    }

    .card {
        background: rgba(255, 255, 255, 0.95);
        border-radius: var(--radius-lg);
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: var(--shadow-sm);
        overflow: hidden;
        transition: 0.25s ease;
    }

    .card:hover {
        box-shadow: var(--shadow-md);
    }

    .card-head {
        padding: 22px 24px 10px 24px;
        border-bottom: 1px solid rgba(241, 245, 249, 0.95);
        background: linear-gradient(180deg, #ffffff, #fbfdff);
    }

    .card-title {
        font-size: 18px;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 6px;
    }

    .card-desc {
        font-size: 13px;
        color: var(--text-sub);
        line-height: 1.7;
    }

    .image-box {
        width: 100%;
        height: 460px;
        padding: 18px 20px 24px 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background:
            linear-gradient(45deg, #f8fafc 25%, transparent 25%),
            linear-gradient(-45deg, #f8fafc 25%, transparent 25%),
            linear-gradient(45deg, transparent 75%, #f8fafc 75%),
            linear-gradient(-45deg, transparent 75%, #f8fafc 75%);
        background-size: 22px 22px;
        background-position: 0 0, 0 11px, 11px -11px, -11px 0;
    }

    .image-box.tall {
        height: 560px;
    }

    .image-box.wide {
        height: 390px;
    }

    .image-box.compact {
        height: 330px;
    }

    .image-box img {
        max-width: 100%;
        max-height: 100%;
        object-fit: contain;
        border-radius: 14px;
        background: white;
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.06);
    }

    .table-card {
        padding: 24px;
    }

    .table-title {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 14px;
    }

    .table-title-main {
        font-size: 18px;
        font-weight: 800;
        color: var(--text-main);
    }

    .table-title-sub {
        font-size: 13px;
        color: var(--text-light);
    }

    table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        font-size: 13px;
        background: white;
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
    }

    th {
        background: #eff6ff;
        color: #1e3a8a;
        text-align: left;
        padding: 13px 12px;
        border-bottom: 1px solid #dbeafe;
        white-space: nowrap;
        font-weight: 800;
    }

    td {
        padding: 12px 12px;
        border-bottom: 1px solid #eef2f7;
        color: #334155;
        vertical-align: top;
        line-height: 1.65;
    }

    tbody tr:nth-child(even) td {
        background: #fbfdff;
    }

    tr:hover td {
        background: #f1f7ff;
    }

    tr:last-child td {
        border-bottom: none;
    }

    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 22px;
    }

    .analysis-card {
        background: white;
        border-radius: var(--radius-lg);
        padding: 24px 24px 22px 24px;
        border: 1px solid rgba(226, 232, 240, 0.95);
        box-shadow: var(--shadow-sm);
    }

    .analysis-icon {
        width: 42px;
        height: 42px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 14px;
        color: white;
        font-weight: 900;
        background: linear-gradient(135deg, var(--blue), var(--cyan));
    }

    .analysis-card h3 {
        margin: 0 0 10px 0;
        font-size: 17px;
        color: var(--text-main);
    }

    .analysis-card p {
        margin: 0;
        color: var(--text-sub);
        font-size: 14px;
        line-height: 1.85;
    }

    .missing {
        color: var(--text-light);
        border: 1px dashed #cbd5e1;
        border-radius: 14px;
        padding: 34px;
        width: 100%;
        text-align: center;
        background: rgba(255, 255, 255, 0.72);
    }

    .footer {
        text-align: center;
        color: var(--text-light);
        padding: 24px 20px 34px 20px;
        font-size: 13px;
    }

    @media (max-width: 1100px) {
        .kpi-grid,
        .grid-2,
        .grid-3,
        .analysis-grid,
        .process {
            grid-template-columns: 1fr;
        }

        .hero h1 {
            font-size: 30px;
        }

        .topbar {
            padding: 0 22px;
        }

        .nav {
            display: none;
        }

        .process-step::after {
            display: none;
        }

        .image-box,
        .image-box.tall,
        .image-box.wide,
        .image-box.compact {
            height: auto;
            min-height: 300px;
        }
    }
</style>
"""


def safe_text(value):
    if value is None:
        return ""
    if pd.isna(value):
        return ""
    return html_lib.escape(str(value))


def copy_figures():
    copied = {}

    for name, src in FIGURES.items():
        if os.path.exists(src):
            ext = os.path.splitext(src)[1]
            dst_name = f"{name}{ext}"
            dst = os.path.join(ASSET_DIR, dst_name)
            shutil.copyfile(src, dst)
            copied[name] = f"assets/{dst_name}"
        else:
            copied[name] = ""

    return copied


def fmt_num(x, digits=2):
    try:
        if pd.isna(x):
            return "-"
        value = float(x)
        if digits == 0:
            return f"{value:,.0f}"
        return f"{value:,.{digits}f}"
    except Exception:
        return safe_text(x)


def fmt_pct(x, digits=2):
    try:
        if pd.isna(x):
            return "-"
        return f"{float(x) * 100:.{digits}f}%"
    except Exception:
        return safe_text(x)


def build_key_node_table():
    if not os.path.exists(TABLE_KEY_NODES):
        return "<p class='missing'>未找到关键节点结果表。</p>"

    df = pd.read_csv(TABLE_KEY_NODES).head(15)

    rows = []
    for i, row in df.iterrows():
        nearby = row.get("nearby_streets", "")
        if pd.isna(nearby) or str(nearby).strip() == "":
            nearby = "未记录道路名"

        rows.append(f"""
        <tr>
            <td>{i + 1}</td>
            <td>{safe_text(row.get("node", ""))}</td>
            <td>{fmt_num(row.get("flow", 0), 0)}</td>
            <td>{fmt_num(row.get("betweenness", 0), 4)}</td>
            <td>{fmt_num(row.get("key_score", 0), 4)}</td>
            <td>{safe_text(nearby)}</td>
        </tr>
        """)

    return f"""
    <table>
        <thead>
            <tr>
                <th>排名</th>
                <th>节点 ID</th>
                <th>节点流量</th>
                <th>介数中心性</th>
                <th>综合得分</th>
                <th>相邻道路</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def build_vulnerability_table():
    if not os.path.exists(TABLE_VULNERABILITY):
        return "<p class='missing'>未找到脆弱性仿真汇总表。</p>"

    df = pd.read_csv(TABLE_VULNERABILITY)

    show_k = [0, 10, 20, 50, 100]
    df = df[df["k"].isin(show_k)].copy()

    scenario_order = {
        "baseline": 0,
        "key_node_removal": 1,
        "random_node_removal": 2,
        "key_node_degradation": 3,
    }

    df["scenario_order"] = df["scenario"].map(scenario_order).fillna(99)
    df = df.sort_values(["scenario_order", "k"])

    scenario_name = {
        "baseline": "基准场景",
        "key_node_removal": "关键节点失效",
        "random_node_removal": "随机节点失效",
        "key_node_degradation": "关键节点降级",
    }

    rows = []
    for _, row in df.iterrows():
        scenario = scenario_name.get(row.get("scenario", ""), row.get("scenario", ""))

        rows.append(f"""
        <tr>
            <td>{safe_text(scenario)}</td>
            <td>{int(row.get("k", 0))}</td>
            <td>{fmt_pct(row.get("od_reachability", 0))}</td>
            <td>{fmt_pct(row.get("avg_delay_rate", 0))}</td>
            <td>{fmt_num(row.get("weighted_efficiency", 0), 5)}</td>
            <td>{fmt_pct(row.get("largest_component_ratio", 0))}</td>
        </tr>
        """)

    return f"""
    <table>
        <thead>
            <tr>
                <th>场景</th>
                <th>影响节点数</th>
                <th>OD 可达率</th>
                <th>平均绕行率</th>
                <th>加权效率</th>
                <th>最大连通子图比例</th>
            </tr>
        </thead>
        <tbody>
            {''.join(rows)}
        </tbody>
    </table>
    """


def get_basic_stats():
    taxi_count = "-"
    od_count = "-"

    if os.path.exists(TABLE_TAXI):
        try:
            taxi_df = pd.read_csv(TABLE_TAXI, usecols=["pickup_time"])
            taxi_count = f"{len(taxi_df):,}"
        except Exception:
            taxi_df = pd.read_csv(TABLE_TAXI)
            taxi_count = f"{len(taxi_df):,}"

    if os.path.exists(TABLE_OD):
        try:
            od_df = pd.read_csv(TABLE_OD, usecols=["origin_node", "dest_node", "trips"])
            od_count = f"{len(od_df):,}"
        except Exception:
            od_df = pd.read_csv(TABLE_OD)
            od_count = f"{len(od_df):,}"

    return taxi_count, od_count


def image_card(title, desc, img_path, size="normal"):
    if img_path:
        img_html = f'<img src="{img_path}" alt="{safe_text(title)}">'
    else:
        img_html = '<div class="missing">图片文件未找到</div>'

    return f"""
    <div class="card image-card">
        <div class="card-head">
            <div>
                <div class="card-title">{safe_text(title)}</div>
                <div class="card-desc">{safe_text(desc)}</div>
            </div>
        </div>
        <div class="image-box {safe_text(size)}">
            {img_html}
        </div>
    </div>
    """


def build_html():
    figs = copy_figures()
    taxi_count, od_count = get_basic_stats()

    key_table = build_key_node_table()
    vulnerability_table = build_vulnerability_table()

    html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>交通关键节点识别与韧性分析系统</title>
    {STYLE_CSS}
</head>
<body>

<div class="topbar">
    <div class="brand">交通关键节点识别与韧性分析系统</div>
    <div class="nav">
        <a href="#overview">数据概况</a>
        <a href="#process">分析流程</a>
        <a href="#network">路网流量</a>
        <a href="#keynodes">关键节点</a>
        <a href="#vulnerability">韧性仿真</a>
    </div>
</div>

<div class="hero">
    <div class="hero-inner">
        <div class="hero-kicker">Traffic Network Resilience Dashboard</div>
        <h1>面向 Manhattan 区域路网的交通关键节点识别与韧性、脆弱性仿真分析系统</h1>
        <p>
            本系统基于 2015 年 12 月纽约绿牌出租车 GPS 起终点数据与 OpenStreetMap 路网数据，
            完成出租车 OD 构建、路网节点匹配、最短路径流量加载、关键节点综合识别以及节点失效仿真分析。
        </p>
        <div>
            <span class="tag">Green Taxi GPS</span>
            <span class="tag">OpenStreetMap</span>
            <span class="tag">OD Flow Loading</span>
            <span class="tag">Key Node Identification</span>
            <span class="tag">Network Resilience</span>
        </div>
    </div>
</div>

<div class="container">

    <section id="overview">
        <h2 class="section-title">一、数据与模型概况</h2>
        <p class="section-subtitle">
            本部分展示研究区域、出租车 OD 数据规模和路网建模结果。
        </p>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">曼哈顿出租车 OD 记录</div>
                <div class="kpi-value">{taxi_count}</div>
                <div class="kpi-note">起点和终点均位于 Manhattan 行政边界内</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">聚合 OD 节点对</div>
                <div class="kpi-value">{od_count}</div>
                <div class="kpi-note">GPS 点匹配 OSM 路网节点后聚合得到</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">OSM 路网节点</div>
                <div class="kpi-value">4,669</div>
                <div class="kpi-note">Manhattan 机动车路网节点数量</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-label">OSM 路网边</div>
                <div class="kpi-value">9,965</div>
                <div class="kpi-note">有向道路边，包含长度和通行时间属性</div>
            </div>
        </div>
    </section>

    <section id="process">
        <h2 class="section-title">系统分析流程</h2>
        <p class="section-subtitle">
            系统按照“数据处理—路网建模—交通流加载—关键节点识别—韧性仿真”的流程组织。
        </p>

        <div class="process">
            <div class="process-step">出租车 GPS 清洗</div>
            <div class="process-step">OD 节点匹配</div>
            <div class="process-step">最短路径流量加载</div>
            <div class="process-step">关键节点识别</div>
            <div class="process-step">韧性仿真分析</div>
        </div>
    </section>

    <section id="network">
        <h2 class="section-title">二、路网与交通流量可视化</h2>
        <p class="section-subtitle">
            左图展示 Manhattan 机动车路网结构，右图展示基于出租车 OD 最短路径分配得到的高流量道路。
        </p>

        <div class="grid-2">
            {image_card(
                "Manhattan OSM 机动车路网",
                "由 OpenStreetMap 数据构建并投影后的有向机动车道路网络。",
                figs["manhattan_drive_network"],
                size="tall"
            )}
            {image_card(
                "高流量道路空间分布",
                "根据 OD 最短路径流量加载结果，选取流量较高的道路边进行可视化。",
                figs["high_flow_edges_map"],
                size="tall"
            )}
        </div>
    </section>

    <section id="keynodes">
        <h2 class="section-title">三、交通关键节点识别结果</h2>
        <p class="section-subtitle">
            综合考虑节点流量、介数中心性、度中心性和 PageRank 指标，得到 Manhattan 路网关键节点排序。
        </p>

        <div class="grid-2">
            {image_card(
                "Top 20 关键节点综合得分",
                "综合得分越高，表示节点在交通功能和路网结构上越关键。",
                figs["top20_key_nodes_bar"],
                size="wide"
            )}
            {image_card(
                "Top 30 关键节点空间分布",
                "关键节点主要分布在主干道路、快速路出入口和交通走廊附近。",
                figs["key_nodes_map"],
                size="tall"
            )}
        </div>

        <div class="card table-card" style="margin-top: 24px;">
            <div class="table-title">
                <div class="table-title-main">关键节点识别结果表</div>
                <div class="table-title-sub">展示综合得分前 15 个节点</div>
            </div>
            {key_table}
        </div>
    </section>

    <section id="vulnerability">
        <h2 class="section-title">四、脆弱性与韧性仿真分析</h2>
        <p class="section-subtitle">
            本部分比较关键节点失效、随机节点失效和关键节点降级三类场景下的路网性能变化。
        </p>

        <div class="grid-3">
            {image_card(
                "OD 可达率变化",
                "反映扰动后主要出租车 OD 需求是否仍能完成。",
                figs["vulnerability_od_reachability"],
                size="wide"
            )}
            {image_card(
                "平均绕行率变化",
                "反映可达 OD 在扰动后的通行成本增加程度。",
                figs["vulnerability_avg_delay"],
                size="wide"
            )}
            {image_card(
                "最大连通子图比例变化",
                "反映路网结构连通性受破坏程度。",
                figs["vulnerability_lcc_ratio"],
                size="wide"
            )}
        </div>

        <div class="card table-card" style="margin-top: 24px;">
            <div class="table-title">
                <div class="table-title-main">脆弱性仿真汇总结果</div>
                <div class="table-title-sub">选取 k = 0、10、20、50、100 的代表性结果</div>
            </div>
            {vulnerability_table}
        </div>
    </section>

    <section>
        <h2 class="section-title">五、实验结论摘要</h2>
        <p class="section-subtitle">
            根据关键节点识别结果和脆弱性仿真实验，可以得到以下主要结论。
        </p>

        <div class="analysis-grid">
            <div class="analysis-card">
                <div class="analysis-icon">01</div>
                <h3>关键节点具有结构与功能双重属性</h3>
                <p>
                    高综合得分节点通常同时具有较高的出租车流量承载能力和较高的介数中心性，
                    说明这些节点不仅是交通需求集中经过的位置，也是路网结构中的重要中介节点。
                </p>
            </div>

            <div class="analysis-card">
                <div class="analysis-icon">02</div>
                <h3>关键节点失效显著削弱 OD 可达性</h3>
                <p>
                    与随机节点失效相比，关键节点失效会导致 OD 可达率快速下降，
                    说明少数关键交通节点对 Manhattan 区域路网功能具有明显支撑作用。
                </p>
            </div>

            <div class="analysis-card">
                <div class="analysis-icon">03</div>
                <h3>节点降级主要影响通行效率</h3>
                <p>
                    在关键节点降级场景下，路网结构连通性基本保持不变，
                    但平均绕行率持续上升，说明拥堵、限速或事故占道会显著增加出行成本。
                </p>
            </div>
        </div>
    </section>

</div>

<div class="footer">
    面向区域路网的交通关键节点识别与韧性、脆弱性仿真分析系统
</div>

</body>
</html>
"""

    out_path = os.path.join(DASHBOARD_DIR, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print("Dashboard 已生成：", out_path)
    print("请双击打开 outputs/dashboard/index.html 查看页面。")


if __name__ == "__main__":
    build_html()