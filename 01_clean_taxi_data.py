import os
import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point

RAW_PATH = "data/raw/green_tripdata_2015-12.csv"
OUT_PATH = "data/processed/green_manhattan_all.csv"

os.makedirs("data/processed", exist_ok=True)

usecols = [
    "lpep_pickup_datetime",
    "Lpep_dropoff_datetime",
    "Pickup_longitude",
    "Pickup_latitude",
    "Dropoff_longitude",
    "Dropoff_latitude",
    "Passenger_count",
    "Trip_distance"
]

df = pd.read_csv(RAW_PATH, usecols=usecols)

# 统一字段名
df = df.rename(columns={
    "lpep_pickup_datetime": "pickup_time",
    "Lpep_dropoff_datetime": "dropoff_time",
    "Pickup_longitude": "pickup_lon",
    "Pickup_latitude": "pickup_lat",
    "Dropoff_longitude": "dropoff_lon",
    "Dropoff_latitude": "dropoff_lat",
    "Passenger_count": "passenger_count",
    "Trip_distance": "trip_distance"
})

# 时间字段转换
df["pickup_time"] = pd.to_datetime(df["pickup_time"], errors="coerce")
df["dropoff_time"] = pd.to_datetime(df["dropoff_time"], errors="coerce")

# 删除缺失值
df = df.dropna(subset=[
    "pickup_time", "dropoff_time",
    "pickup_lon", "pickup_lat",
    "dropoff_lon", "dropoff_lat"
])

# 删除 0 坐标
df = df[
    (df["pickup_lon"] != 0) &
    (df["pickup_lat"] != 0) &
    (df["dropoff_lon"] != 0) &
    (df["dropoff_lat"] != 0)
]

# 纽约大致经纬度范围，先做粗过滤，减少后面空间计算量
df = df[
    df["pickup_lon"].between(-74.30, -73.60) &
    df["pickup_lat"].between(40.40, 41.00) &
    df["dropoff_lon"].between(-74.30, -73.60) &
    df["dropoff_lat"].between(40.40, 41.00)
]

# 行程时间，单位分钟
df["duration_min"] = (
    df["dropoff_time"] - df["pickup_time"]
).dt.total_seconds() / 60

# 删除异常行程
df = df[
    (df["trip_distance"] > 0) &
    (df["duration_min"] >= 1) &
    (df["duration_min"] <= 180)
]

# 添加行号，方便空间筛选后找回原始记录
df = df.reset_index(drop=True)
df["row_id"] = df.index

print("基础清洗后数据量：", len(df))

# 获取 Manhattan 边界
manhattan = ox.geocode_to_gdf("Manhattan, New York City, New York, USA")
manhattan = manhattan.to_crs("EPSG:4326")

# 构造 pickup 点
pickup_gdf = gpd.GeoDataFrame(
    df[["row_id"]],
    geometry=gpd.points_from_xy(df["pickup_lon"], df["pickup_lat"]),
    crs="EPSG:4326"
)

# 构造 dropoff 点
dropoff_gdf = gpd.GeoDataFrame(
    df[["row_id"]],
    geometry=gpd.points_from_xy(df["dropoff_lon"], df["dropoff_lat"]),
    crs="EPSG:4326"
)

# 判断上车点是否在 Manhattan 内
pickup_in_manhattan = gpd.sjoin(
    pickup_gdf,
    manhattan[["geometry"]],
    how="inner",
    predicate="within"
)

# 判断下车点是否在 Manhattan 内
dropoff_in_manhattan = gpd.sjoin(
    dropoff_gdf,
    manhattan[["geometry"]],
    how="inner",
    predicate="within"
)

pickup_ids = set(pickup_in_manhattan["row_id"])
dropoff_ids = set(dropoff_in_manhattan["row_id"])

# 起点和终点都在 Manhattan
manhattan_ids = pickup_ids & dropoff_ids

df_manhattan = df[df["row_id"].isin(manhattan_ids)].copy()

# 删除辅助列
df_manhattan = df_manhattan.drop(columns=["row_id"])

# 不抽样，保存全部曼哈顿数据
df_manhattan.to_csv(OUT_PATH, index=False, encoding="utf-8-sig")

print("曼哈顿 OD 数据量：", len(df_manhattan))
print(df_manhattan.head())
print("已保存到：", OUT_PATH)