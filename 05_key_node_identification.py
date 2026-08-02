import os
import pandas as pd
import osmnx as ox
import networkx as nx
from sklearn.preprocessing import MinMaxScaler

GRAPH_PATH = "data/graph/manhattan_drive.graphml"
NODE_FLOW_PATH = "data/processed/node_flow.csv"

OUT_DIR = "outputs/tables"
OUT_PATH = os.path.join(OUT_DIR, "top_key_nodes.csv")

os.makedirs(OUT_DIR, exist_ok=True)


def convert_node_id_series(series, graph):
    """
    保证 CSV 中的节点 ID 类型和 GraphML 中的节点 ID 类型一致。
    """
    sample_node = next(iter(graph.nodes))
    if isinstance(sample_node, str):
        return series.astype(str)
    else:
        return series.astype(int)


def build_simple_digraph(G):
    """
    将 OSMnx 的 MultiDiGraph 转换成 DiGraph。
    如果两个节点之间有多条边，保留 travel_time 最小的那条边。
    """
    H = nx.DiGraph()

    for n, attrs in G.nodes(data=True):
        H.add_node(n, **attrs)

    for u, v, key, attrs in G.edges(keys=True, data=True):
        travel_time = attrs.get("travel_time", attrs.get("length", 1.0))
        length = attrs.get("length", 1.0)

        try:
            travel_time = float(travel_time)
        except Exception:
            travel_time = 1.0

        try:
            length = float(length)
        except Exception:
            length = 1.0

        if H.has_edge(u, v):
            old_time = H[u][v].get("travel_time", float("inf"))
            if travel_time < old_time:
                H[u][v].update({
                    "travel_time": travel_time,
                    "length": length
                })
        else:
            H.add_edge(
                u,
                v,
                travel_time=travel_time,
                length=length
            )

    return H


print("正在读取 Manhattan 路网...")
G = ox.load_graphml(GRAPH_PATH)

print("原始路网节点数量：", G.number_of_nodes())
print("原始路网边数量：", G.number_of_edges())

print("正在转换为简单有向图...")
H = build_simple_digraph(G)

print("简单图节点数量：", H.number_of_nodes())
print("简单图边数量：", H.number_of_edges())

print("正在读取节点流量数据...")
flow_df = pd.read_csv(NODE_FLOW_PATH)
flow_df["node"] = convert_node_id_series(flow_df["node"], G)

flow_dict = dict(zip(flow_df["node"], flow_df["flow"]))

print("正在计算度中心性...")
degree_centrality = nx.degree_centrality(H)

print("正在计算 PageRank...")
# 注意：PageRank 的 weight 越大代表连接越强。
# travel_time 越大反而代表成本越高，所以这里额外构造 inv_time。
for u, v, attrs in H.edges(data=True):
    t = attrs.get("travel_time", 1.0)
    try:
        t = float(t)
    except Exception:
        t = 1.0
    attrs["inv_time"] = 1.0 / max(t, 0.1)

pagerank = nx.pagerank(H, weight="inv_time")

print("正在近似计算介数中心性...")
node_count = H.number_of_nodes()

# k 越大越准确，但越慢。
# 你的图有 4669 个节点，k=1000 对课程设计已经足够。
k_sample = min(1000, node_count)

betweenness = nx.betweenness_centrality(
    H,
    k=k_sample,
    normalized=True,
    weight="travel_time",
    seed=42
)

print("正在整合指标...")

records = []

for n, attrs in G.nodes(data=True):
    records.append({
        "node": n,
        "x": attrs.get("x"),
        "y": attrs.get("y"),
        "street_count": attrs.get("street_count"),
        "flow": flow_dict.get(n, 0.0),
        "degree_centrality": degree_centrality.get(n, 0.0),
        "betweenness": betweenness.get(n, 0.0),
        "pagerank": pagerank.get(n, 0.0)
    })

result = pd.DataFrame(records)

# 防止全部为 0 时 MinMaxScaler 报异常
cols = ["flow", "degree_centrality", "betweenness", "pagerank"]

scaler = MinMaxScaler()
result[[
    "flow_norm",
    "degree_norm",
    "betweenness_norm",
    "pagerank_norm"
]] = scaler.fit_transform(result[cols])

# 综合关键节点得分
result["key_score"] = (
    0.4 * result["flow_norm"] +
    0.4 * result["betweenness_norm"] +
    0.1 * result["degree_norm"] +
    0.1 * result["pagerank_norm"]
)

result = result.sort_values("key_score", ascending=False).reset_index(drop=True)

result.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("关键节点识别完成")
print("结果已保存到：", OUT_PATH)

print("Top 30 关键节点：")
print(result.head(30)[[
    "node",
    "flow",
    "betweenness",
    "degree_centrality",
    "pagerank",
    "key_score",
    "x",
    "y"
]])