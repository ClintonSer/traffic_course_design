import os
import pandas as pd
import osmnx as ox

GRAPH_PATH = "data/graph/manhattan_drive.graphml"
TAXI_PATH = "data/processed/green_manhattan_all.csv"
OUT_PATH = "data/processed/od_nodes.csv"

os.makedirs("data/processed", exist_ok=True)

print("正在读取曼哈顿出租车数据...")
df = pd.read_csv(TAXI_PATH)

print("出租车记录数量：", len(df))

print("正在读取 Manhattan OSM 路网...")
G = ox.load_graphml(GRAPH_PATH)

print("路网节点数量：", G.number_of_nodes())
print("路网边数量：", G.number_of_edges())

# 注意：
# 你的 graphml 已经投影到了 UTM 坐标系；
# 但出租车 GPS 是经纬度 WGS84。
# 为避免坐标系不一致，这里重新将路网转换回经纬度用于 nearest_nodes。
print("正在将路网转换回经纬度坐标系...")
G_latlon = ox.project_graph(G, to_crs="EPSG:4326")

print("正在匹配上车点到最近路网节点...")
pickup_nodes = ox.distance.nearest_nodes(
    G_latlon,
    X=df["pickup_lon"].values,
    Y=df["pickup_lat"].values
)

print("正在匹配下车点到最近路网节点...")
dropoff_nodes = ox.distance.nearest_nodes(
    G_latlon,
    X=df["dropoff_lon"].values,
    Y=df["dropoff_lat"].values
)

df["origin_node"] = pickup_nodes
df["dest_node"] = dropoff_nodes

# 删除起点和终点匹配到同一个节点的记录
df = df[df["origin_node"] != df["dest_node"]].copy()

print("删除同节点 OD 后记录数量：", len(df))

print("正在聚合 OD 节点对...")

od = (
    df.groupby(["origin_node", "dest_node"])
    .size()
    .reset_index(name="trips")
)

od = od.sort_values("trips", ascending=False).reset_index(drop=True)

od.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("OD 节点对数量：", len(od))
print("前 20 个高频 OD：")
print(od.head(20))
print("已保存到：", OUT_PATH)