from pathlib import Path
import pandas as pd

def _read_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, encoding="utf-8-sig")

def load_dashboard_data(base_dir: Path, selected_category: str = "全部") -> dict:
    data_dir = base_dir / "data"
    metrics_df = _read_csv(data_dir / "overall_metrics.csv")
    category_df = _read_csv(data_dir / "category_analysis.csv")
    segment_df = _read_csv(data_dir / "segment_analysis.csv")

    metric_map = dict(zip(metrics_df["指标"], metrics_df["数值"]))

    # --- TODO 2-1: 补齐指标卡 ---
    # 1. 获取基础数值
    total_users = int(metric_map["用户数"])
    churn_users = int(metric_map["流失人数"])
    
    # 2. 计算总体流失率 (流失人数 / 用户数 * 100)，保留1位小数
    churn_rate_val = (churn_users / total_users * 100) if total_users > 0 else 0
    
    # 3. 获取平均订单数 (假设 metric_map 中有该字段，转为浮点数保留2位)
    avg_orders_val = float(metric_map.get("平均订单数", 0))

    metrics = [
        {"label": "总用户数", "value": f"{total_users:,}", "note": "人"},
        {"label": "流失用户", "value": f"{churn_users:,}", "note": "人"},
        # 新增的两项：
        {"label": "总体流失率", "value": f"{churn_rate_val:.1f}%", "note": ""},
        {"label": "平均订单数", "value": f"{avg_orders_val:.2f}", "note": "单"},
    ]

    categories = ["全部", *category_df["PreferedOrderCat"].tolist()]
    table_df = category_df.copy()

    # TODO 3-1: 选择具体品类后筛选 table_df (此处保持原样，逻辑在后续步骤)
    if selected_category != "全部":
        table_df = table_df[table_df["PreferedOrderCat"] == selected_category]

    table_df = table_df.rename(
        columns={
            "PreferedOrderCat": "偏好品类",
            "用户数": "用户数",
            "流失率": "流失率",
            "平均订单数": "平均订单数",
        }
    )[["偏好品类", "用户数", "流失率", "平均订单数"]]

    # 格式化表格中的百分比和数值显示
    table_df["流失率"] = table_df["流失率"].map(lambda value: f"{value:.1%}")
    table_df["平均订单数"] = table_df["平均订单数"].map(lambda value: f"{value:.2f}")

    # --- TODO 2-2: 生成数据观察 ---
    # 找出流失率最高的生命周期阶段
    # 注意：此时 segment_df 还是原始数据（未重命名），列名通常是英文或原始中文
    # 假设 segment_df 中有一列叫 "阶段" (或类似名称) 和 "流失率"
    
    # 安全获取最高流失率的索引
    max_idx = segment_df["流失率"].idxmax()
    max_row = segment_df.loc[max_idx]
    
    # 提取阶段名称（请确保 "阶段" 是 CSV 中的真实列名，如果是 "LifecycleStage" 请自行替换）
    stage_name = max_row.get("阶段", "未知阶段") 
    max_rate = max_row["流失率"] * 100  # 转换为百分数数值
    
    insight = f"数据显示，【{stage_name}】阶段的流失风险最高，流失率达到 {max_rate:.1f}%，需重点关注。"
    chart_path_2 = "static/images/03_ordered_line.png"

    return {
        "metrics": metrics,
        "categories": categories,
        "category_rows": table_df.to_dict("records"),
        "insight": insight,
        "chart_path_2":chart_path_2
    }