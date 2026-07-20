from pathlib import Path
import pandas as pd

def answer_question(base_dir: Path, question: str) -> str:
    data_dir = base_dir / "data"
    # 读取整体指标表
    metrics_df = pd.read_csv(data_dir / "overall_metrics.csv", encoding="utf-8-sig")
    metrics = dict(zip(metrics_df["指标"], metrics_df["数值"]))
    # 读取品类、生命周期分段数据表
    category_df = pd.read_csv(data_dir / "category_analysis.csv", encoding="utf-8-sig")
    segment_df = pd.read_csv(data_dir / "segment_analysis.csv", encoding="utf-8-sig")

    normalized = question.replace(" ", "").lower()

    # 1. 用户规模问答
    if any(word in normalized for word in ["多少用户", "用户数", "总用户"]):
        return f"数据集中共有{int(metrics['用户数'])}名用户。"

    # 2. 流失情况问答
    elif any(word in normalized for word in ["流失率", "流失人数"]):
        total = int(metrics["用户数"])
        churn_num = int(metrics["流失人数"])
        churn_rate = (churn_num / total) * 100 if total > 0 else 0
        return f"平台流失用户共{churn_num}人，整体流失率为{churn_rate:.1f}%。"

    # 3. 偏好品类问答
    elif any(word in normalized for word in ["偏好品类", "哪个品类用户最多"]):
        max_row = category_df.loc[category_df["用户数"].idxmax()]
        cat_name = max_row["PreferedOrderCat"]
        cat_user = max_row["用户数"]
        return f"{cat_name}品类的用户数量最多，总计{cat_user}位用户。"

    # 4. 生命周期风险问答
    elif any(word in normalized for word in ["生命周期", "风险最高", "流失风险"]):
        max_seg = segment_df.loc[segment_df["流失率"].idxmax()]
        seg_name = max_seg["阶段"]
        seg_rate = max_seg["流失率"]
        return f"{seg_name}阶段流失风险最高，该阶段流失率为{seg_rate:.1f}%。"

    # 5. 订单情况问答（均值+中位数）
    elif any(word in normalized for word in ["订单", "平均订单数"]):
        avg_order = float(metrics["平均订单数"])
        mid_order = float(metrics["订单中位数"])
        return f"用户平均订单数为{avg_order:.2f}单，订单数中位数是{mid_order:.2f}单。"

    # 兜底：不支持问题友好提示
    return (
        "基础问答尚未完成。目前可以回答用户总数、流失情况、偏好品类、生命周期风险、订单相关问题，"
        "请换一种更具体的问法。"
    )