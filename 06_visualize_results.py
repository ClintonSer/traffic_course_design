import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
import matplotlib.pyplot as plt

GRAPH_PATH = "data/graph/manhattan_drive.graphml"
KEY_NODE_PATH = "outputs/tables/top_key_nodes.csv"
EDGE_FLOW_PATH = "data/processed/edge_flow.csv"

OUT_TABLE_DIR = "outputs/tables"
OUT_FIG_DIR = "outputs/figures"

KEY_NODE_WITH_STREET_OUT = os.path.join(
    OUT_TABLE_DIR,
    "top_key_nodes_with_streets.csv"
)

BAR_FIG_OUT = os.path.join(
    OUT_FIG_DIR,
    "top20_key_nodes_bar.png"
)

KEY_NODE_MAP_OUT = os.path.join(
    OUT_FIG_DIR,
    "key_nodes_map.png"
)

EDGE_FLOW_MAP_OUT = os.path.join(
    OUT_FIG_DIR,
    "high_flow_edges_map.png"
)

os.makedirs(OUT_TABLE_DIR, exist_ok=True)
os.makedirs(OUT_FIG_DIR, exist_ok=True)


def normalize_name(value):
    """
    OSM 的道路名有时是字符串，有时是列表，有时为空。
    这里统一转成可读字符串。
    """
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join([str(v) for v in value])
    return str(value)


def get_node_neighbor_streets(G, node):
    """
    根据节点相邻边，提取该节点附近道路名称。
    """
    street_names = set()
    highway_types = set()

    # 出边
    if node in G:
        for _, v, key, attrs in G.out_edges(node, keys=True, data=True):
            name = normalize_name(attrs.get("name", ""))
            highway = normalize_name(attrs.get("highway", ""))

            if name:
                street_names.add(name)
            if highway:
                highway_types.add(highway)

        # 入边
        for u, _, key, attrs in G.in_edges(node, keys=True, data=True):
            name = normalize_name(attrs.get("name", ""))
            highway = normalize_name(attrs.get("highway", ""))

            if name:
                street_names.add(name)
            if highway:
                highway_types.add(highway)

    street_text = "; ".join(sorted(street_names))
    highway_text = "; ".join(sorted(highway_types))

    return street_text, highway_text


def convert_node_id_series(series, graph):
    """
    保证 CSV 中节点 ID 类型和图中的节点 ID 类型一致。
    """
    sample_node = next(iter(graph.nodes))
    if isinstance(sample_node, str):
        return series.astype(str)
    else:
        return series.astype(int)


print("正在读取路网...")
G = ox.load_graphml(GRAPH_PATH)

print("正在读取关键节点结果...")
key_df = pd.read_csv(KEY_NODE_PATH)
key_df["node"] = convert_node_id_series(key_df["node"], G)

print("正在为关键节点补充相邻道路名称...")
street_list = []
highway_list = []

for node in key_df["node"]:
    streets, highways = get_node_neighbor_streets(G, node)
    street_list.append(streets)
    highway_list.append(highways)

key_df["nearby_streets"] = street_list
key_df["nearby_highway_types"] = highway_list

key_df.to_csv(KEY_NODE_WITH_STREET_OUT, index=False, encoding="utf-8-sig")

print("已保存带道路名的关键节点表：", KEY_NODE_WITH_STREET_OUT)

# ============================================================
# 图 1：Top 20 关键节点综合得分柱状图
# ============================================================

print("正在绘制 Top 20 关键节点柱状图...")

top20 = key_df.head(20).copy()
top20["node_label"] = top20["node"].astype(str)

plt.figure(figsize=(12, 7))
plt.barh(top20["node_label"], top20["key_score"])
plt.gca().invert_yaxis()
plt.xlabel("Key Score")
plt.ylabel("Node ID")
plt.title("Top 20 Key Nodes by Comprehensive Score")
plt.tight_layout()
plt.savefig(BAR_FIG_OUT, dpi=300)
plt.close()

print("Top 20 关键节点柱状图已保存：", BAR_FIG_OUT)

# ============================================================
# 准备路网 GeoDataFrame
# ============================================================

print("正在转换路网为 GeoDataFrame...")
nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)

# ============================================================
# 图 2：关键节点空间分布图
# ============================================================

print("正在绘制关键节点空间分布图...")

top_key = key_df.head(30).copy()

# 根据节点 ID 选出对应节点几何
top_key_nodes_gdf = nodes_gdf.loc[top_key["node"]].copy()
top_key_nodes_gdf["key_score"] = top_key.set_index("node")["key_score"]
top_key_nodes_gdf["flow"] = top_key.set_index("node")["flow"]

plt.figure(figsize=(10, 12))
ax = plt.gca()

edges_gdf.plot(
    ax=ax,
    linewidth=0.4,
    color="lightgray"
)

top_key_nodes_gdf.plot(
    ax=ax,
    markersize=top_key_nodes_gdf["key_score"] * 300,
    color="red",
    alpha=0.8
)

plt.title("Spatial Distribution of Top 30 Key Nodes")
plt.axis("off")
plt.tight_layout()
plt.savefig(KEY_NODE_MAP_OUT, dpi=300)
plt.close()

print("关键节点空间分布图已保存：", KEY_NODE_MAP_OUT)

# ============================================================
# 图 3：高流量道路空间分布图
# ============================================================

print("正在读取边流量结果...")
edge_flow = pd.read_csv(EDGE_FLOW_PATH)

# 为了稳健匹配，统一构造字符串 key
edge_flow["edge_id"] = (
    edge_flow["u"].astype(str) + "_" +
    edge_flow["v"].astype(str) + "_" +
    edge_flow["key"].astype(str)
)

edges_reset = edges_gdf.reset_index().copy()
edges_reset["edge_id"] = (
    edges_reset["u"].astype(str) + "_" +
    edges_reset["v"].astype(str) + "_" +
    edges_reset["key"].astype(str)
)

edges_with_flow = edges_reset.merge(
    edge_flow[["edge_id", "flow"]],
    on="edge_id",
    how="left"
)

edges_with_flow["flow"] = edges_with_flow["flow"].fillna(0)

# 选取流量最高的前 5% 道路
threshold = edges_with_flow["flow"].quantile(0.95)
high_flow_edges = edges_with_flow[edges_with_flow["flow"] >= threshold].copy()

# 线宽归一化
if high_flow_edges["flow"].max() > high_flow_edges["flow"].min():
    high_flow_edges["linewidth"] = (
        0.5 +
        4.5 *
        (high_flow_edges["flow"] - high_flow_edges["flow"].min()) /
        (high_flow_edges["flow"].max() - high_flow_edges["flow"].min())
    )
else:
    high_flow_edges["linewidth"] = 2.0

high_flow_edges = gpd.GeoDataFrame(
    high_flow_edges,
    geometry="geometry",
    crs=edges_gdf.crs
)

print("正在绘制高流量道路空间分布图...")

plt.figure(figsize=(10, 12))
ax = plt.gca()

edges_gdf.plot(
    ax=ax,
    linewidth=0.3,
    color="lightgray"
)

high_flow_edges.plot(
    ax=ax,
    linewidth=high_flow_edges["linewidth"],
    color="blue",
    alpha=0.8
)

plt.title("High Flow Road Segments in Manhattan")
plt.axis("off")
plt.tight_layout()
plt.savefig(EDGE_FLOW_MAP_OUT, dpi=300)
plt.close()

print("高流量道路空间分布图已保存：", EDGE_FLOW_MAP_OUT)

print("全部可视化完成。")

print("输出文件：")
print(KEY_NODE_WITH_STREET_OUT)
print(BAR_FIG_OUT)
print(KEY_NODE_MAP_OUT)
print(EDGE_FLOW_MAP_OUT)