import pandas as pd
from database import fetch_data


def analyze_by_timestamp():
    """按时间戳分析消息数量，并将时间转换为北京时间（UTC+8）"""
    query = """
    SELECT
        DATE_FORMAT(CONVERT_TZ(timestamp, '+00:00', '+08:00'), '%Y-%m-%d %H:00:00') AS timestamp,
        COUNT(*) AS count
    FROM
        messages
    GROUP BY
        DATE_FORMAT(CONVERT_TZ(timestamp, '+00:00', '+08:00'), '%Y-%m-%d %H:00:00')
    ORDER BY
        timestamp;
    """

    # 获取数据
    df = fetch_data(query)

    # 生成结果格式
    time_series = []
    for index, row in df.iterrows():
        time_series.append({
            "timestamp": row["timestamp"],
            "count": float(row["count"])
        })

    # 返回符合要求的结构
    return {"time_series": time_series}


def analyze_user_behavior():
    """获取用户行为数据并生成分析报告"""
    # SQL 查询，联表 `users` 表获取 `username`
    query = """
        SELECT m.sender_id AS user_id, u.username, m.timestamp, m.content AS message 
        FROM messages m
        JOIN users u ON m.sender_id = u.id 
    """
    df = fetch_data(query)

    # 检查数据是否为空
    if df is None or df.empty:
        print("No data retrieved from the database.")
        return {"user_behavior": []}

    # 打印数据，检查格式
    print(df.head())

    # 转换时间格式
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors='coerce')

    # 处理时间为空的数据
    df = df.dropna(subset=["timestamp"])

    # 先 localize 为 UTC，然后转换为北京时间
    df["beijing_time"] = df["timestamp"].dt.tz_localize('UTC').dt.tz_convert('Asia/Shanghai')

    # 统计每小时的用户活跃度
    df.set_index("beijing_time", inplace=True)
    user_activity = df.groupby([pd.Grouper(freq='H'), 'user_id']).size().unstack(fill_value=0)

    # 计算每个用户最活跃的时间段
    user_active_period = user_activity.idxmax(axis=0)

    # 计算每个用户的消息总数
    user_message_count = df.groupby('user_id').size()

    # 获取用户 ID 和用户名的映射
    user_id_to_name = df.set_index("user_id")["username"].to_dict()

    # 生成用户行为分析报告
    user_behavior_report = []
    for user_id in user_message_count.index:
        user_behavior_report.append({
            "user_id": user_id,
            "username": user_id_to_name.get(user_id, "未知用户"),
            "message_count": int(user_message_count[user_id]),  # 确保是 int 类型
            "active_period": str(user_active_period[user_id]) if not pd.isna(user_active_period[user_id]) else "无数据"
        })

    return {"user_behavior": user_behavior_report}
