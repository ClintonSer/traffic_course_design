import os
import time
from collections import defaultdict

import pandas as pd
import osmnx as ox
import networkx as nx

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, **kwargs):
        return x


GRAPH_PATH = "data/graph/manhattan_drive.graphml"
OD_PATH = "data/processed/od_nodes.csv"

NODE_FLOW_OUT = "data/processed/node_flow.csv"
EDGE_FLOW_OUT = "data/processed/edge_flow.csv"
FAILED_OD_OUT = "data/processed/failed_od.csv"

os.makedirs("data/processed", exist_ok=True)

# 是否只测试前 N 条 OD
# 第一次可以设置为 5000，确认代码能跑；
# 正式实验改成 None，表示使用全部 OD。
TEST_LIMIT = None
# TEST_LIMIT = 5000


def convert_node_id_series(series, graph):
    """
    保证 od_nodes.csv 里的节点 ID 类型和 GraphML 里的节点 ID 类型一致。
    有些 OSMnx 版本读入 GraphML 后节点是 int，有些可能是 str。
    """
    sample_node = next(iter(graph.nodes))
    if isinstance(sample_node, str):
        return series.astype(str)
    else:
        return series.astype(int)


def get_best_edge_key_and_attrs(G, u, v):
    """
    MultiDiGraph 中 u-v 之间可能有多条平行边。
    这里选 travel_time 最小的一条边作为流量加载对象。
    """
    edge_dict = G.get_edge_data(u, v)

    if edge_dict is None:
        return None, None

    best_key = None
    best_attrs = None
    best_time = float("inf")

    for key, attrs in edge_dict.items():
        travel_time = attrs.get("travel_time", attrs.get("length", 1.0))

        try:
            travel_time = float(travel_time)
        except Exception:
            travel_time = 1.0

        if travel_time < best_time:
            best_time = travel_time
            best_key = key
            best_attrs = attrs

    return best_key, best_attrs


def get_edge_attr_float(attrs, name, default=0.0):
    value = attrs.get(name, default)
    try:
        return float(value)
    except Exception:
        return default


print("正在读取 Manhattan 路网...")
G = ox.load_graphml(GRAPH_PATH)

print("路网节点数量：", G.number_of_nodes())
print("路网边数量：", G.number_of_edges())

print("正在读取 OD 节点对...")
od = pd.read_csv(OD_PATH)

if TEST_LIMIT is not None:
    od = od.head(TEST_LIMIT).copy()
    print(f"当前为测试模式，仅使用前 {TEST_LIMIT} 个 OD 节点对")
else:
    print("当前为正式模式，使用全部 OD 节点对")

# 保证节点 ID 类型一致
od["origin_node"] = convert_node_id_series(od["origin_node"], G)
od["dest_node"] = convert_node_id_series(od["dest_node"], G)

# trips 转成数值
od["trips"] = pd.to_numeric(od["trips"], errors="coerce").fillna(0)

# 删除不在路网中的 OD
graph_nodes = set(G.nodes)
before = len(od)

od = od[
    od["origin_node"].isin(graph_nodes) &
    od["dest_node"].isin(graph_nodes) &
    (od["origin_node"] != od["dest_node"]) &
    (od["trips"] > 0)
].copy()

after = len(od)
print("OD 节点对原始数量：", before)
print("有效 OD 节点对数量：", after)

# 按起点分组
origin_groups = list(od.groupby("origin_node"))
print("唯一出发节点数量：", len(origin_groups))

node_flow = defaultdict(float)
edge_flow = defaultdict(float)
failed_records = []

start_time = time.time()

print("开始进行最短路径流量加载...")

for origin, group in tqdm(origin_groups, total=len(origin_groups)):
    try:
        # 对每个 origin 只计算一次到所有节点的最短路径
        paths = nx.single_source_dijkstra_path(
            G,
            source=origin,
            weight="travel_time"
        )
    except Exception as e:
        for row in group.itertuples(index=False):
            failed_records.append({
                "origin_node": row.origin_node,
                "dest_node": row.dest_node,
                "trips": row.trips,
                "reason": f"source_failed: {e}"
            })
        continue

    for row in group.itertuples(index=False):
        dest = row.dest_node
        w = float(row.trips)

        if dest not in paths:
            failed_records.append({
                "origin_node": row.origin_node,
                "dest_node": row.dest_node,
                "trips": row.trips,
                "reason": "no_path"
            })
            continue

        path = paths[dest]

        if len(path) < 2:
            continue

        # 节点流量加载
        for n in path:
            node_flow[n] += w

        # 边流量加载
        for u, v in zip(path[:-1], path[1:]):
            key, attrs = get_best_edge_key_and_attrs(G, u, v)

            if key is None:
                failed_records.append({
                    "origin_node": row.origin_node,
                    "dest_node": row.dest_node,
                    "trips": row.trips,
                    "reason": f"edge_missing: {u}->{v}"
                })
                continue

            edge_flow[(u, v, key)] += w


elapsed = time.time() - start_time

print("流量加载完成")
print("耗时秒数：", round(elapsed, 2))

print("正在整理节点流量结果...")

node_records = []

for n, flow in node_flow.items():
    attrs = G.nodes[n]
    node_records.append({
        "node": n,
        "flow": flow,
        "x": attrs.get("x"),
        "y": attrs.get("y"),
        "street_count": attrs.get("street_count", None)
    })

node_flow_df = pd.DataFrame(node_records)
node_flow_df = node_flow_df.sort_values("flow", ascending=False).reset_index(drop=True)

print("正在整理边流量结果...")

edge_records = []

for (u, v, key), flow in edge_flow.items():
    attrs = G.get_edge_data(u, v, key)

    if attrs is None:
        attrs = {}

    edge_records.append({
        "u": u,
        "v": v,
        "key": key,
        "flow": flow,
        "length": get_edge_attr_float(attrs, "length", 0.0),
        "travel_time": get_edge_attr_float(attrs, "travel_time", 0.0),
        "highway": attrs.get("highway", ""),
        "name": attrs.get("name", "")
    })

edge_flow_df = pd.DataFrame(edge_records)
edge_flow_df = edge_flow_df.sort_values("flow", ascending=False).reset_index(drop=True)

failed_df = pd.DataFrame(failed_records)

node_flow_df.to_csv(NODE_FLOW_OUT, index=False, encoding="utf-8-sig")
edge_flow_df.to_csv(EDGE_FLOW_OUT, index=False, encoding="utf-8-sig")
failed_df.to_csv(FAILED_OD_OUT, index=False, encoding="utf-8-sig")

print("节点流量结果已保存到：", NODE_FLOW_OUT)
print("边流量结果已保存到：", EDGE_FLOW_OUT)
print("失败 OD 记录已保存到：", FAILED_OD_OUT)

print("节点流量 Top 20：")
print(node_flow_df.head(20))

print("边流量 Top 20：")
print(edge_flow_df.head(20))

print("失败 OD 数量：", len(failed_df))