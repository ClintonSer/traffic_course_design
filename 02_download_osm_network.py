import os
import osmnx as ox

# 输出路径
GRAPH_DIR = "data/graph"
FIG_DIR = "outputs/figures"

GRAPH_PATH = os.path.join(GRAPH_DIR, "manhattan_drive.graphml")
FIG_PATH = os.path.join(FIG_DIR, "manhattan_drive_network.png")

os.makedirs(GRAPH_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

# 显示 OSMnx 日志，方便观察下载进度
ox.settings.log_console = True
ox.settings.use_cache = True

# 研究区域
PLACE = "Manhattan, New York City, New York, USA"

print("正在下载 Manhattan 机动车路网...")

# 下载机动车可行驶道路
G = ox.graph_from_place(
    PLACE,
    network_type="drive",
    simplify=True,
    retain_all=False,
    truncate_by_edge=True
)

print("原始路网下载完成")
print("节点数量：", G.number_of_nodes())
print("边数量：", G.number_of_edges())

print("正在投影路网...")

# 投影到适合纽约的平面坐标系，单位为米
G_proj = ox.project_graph(G)

print("正在添加道路速度和通行时间...")

# 添加速度，单位 km/h
G_proj = ox.add_edge_speeds(G_proj)

# 添加通行时间，单位秒
G_proj = ox.add_edge_travel_times(G_proj)

print("正在保存 GraphML 文件...")

ox.save_graphml(G_proj, GRAPH_PATH)

print("正在保存路网图片...")

fig, ax = ox.plot_graph(
    G_proj,
    node_size=0,
    edge_linewidth=0.5,
    bgcolor="white",
    save=True,
    filepath=FIG_PATH,
    show=False,
    close=True
)

print("Manhattan 路网处理完成")
print("路网文件保存到：", GRAPH_PATH)
print("路网图片保存到：", FIG_PATH)
print("投影后节点数量：", G_proj.number_of_nodes())
print("投影后边数量：", G_proj.number_of_edges())