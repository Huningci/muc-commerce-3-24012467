from functools import wraps
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for

from services.data_service import (
    load_category_api_data,
    load_dashboard_data,
    load_metric_api_data,
)
from services.qa_service import answer_question


BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)
app.config["SECRET_KEY"] = "day07-classroom-demo-key"


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "username" not in session:
            flash("请先登录后再访问数据看板。", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


@app.route("/")
def index():
    return redirect(url_for("dashboard") if "username" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == "student" and password == "day07":
            session["username"] = username
            flash("登录成功，欢迎进入电商用户分析系统。", "success")
            return redirect(url_for("dashboard"))
        flash("账号或密码错误。演示账号：student / day07", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("你已安全退出。", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    category = request.args.get("category", "全部")
    dashboard_data = load_dashboard_data(BASE_DIR, category)
    return render_template(
        "dashboard.html",
        username=session["username"],
        selected_category=category,
        **dashboard_data,
    )


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html", username=session["username"])


@app.route("/api/ask", methods=["POST"])
@login_required
def ask():
    payload = request.get_json(silent=True) or {}
    question = str(payload.get("question", "")).strip()
    if not question:
        return jsonify({"ok": False, "answer": "请输入一个与项目数据有关的问题。"}), 400
    return jsonify({"ok": True, "answer": answer_question(BASE_DIR, question)})


@app.route("/health")
def health():
    """用于确认服务是否存活，不需要登录。"""
    return jsonify({"ok": True, "service": "day08-flask-upgrade"})


@app.route("/api/metrics")
@login_required
def metrics_api():
    #  8-1：返回四张指标卡的JSON数据，并保留label、value、note字段。

        # --- 在 return 之前插入这段代码 ---
    
    # 1. 暂存原始的数据加载函数
    _original_loader = load_metric_api_data
    
    # 2. 定义一个新的包装函数
    def _patched_loader(base_dir):
        # 调用原始函数获取完整数据
        raw_data = _original_loader(base_dir)
        # 过滤数据，只保留 label, value, note
        return [
            {
                "label": item.get("label"), 
                "value": item.get("value"), 
                "note": item.get("note")
            } 
            for item in raw_data
        ]
        
    # 3. 将全局函数替换为我们的新函数
    # 这样第95行再调用 load_metric_api_data 时，实际上运行的是上面的过滤逻辑
    globals()['load_metric_api_data'] = _patched_loader
    
    # ----------------------------------
    return jsonify({"ok": True, "metrics": load_metric_api_data(BASE_DIR)})


@app.route("/api/categories")
@login_required
def categories_api():
    category = request.args.get("category", "全部")
    data_list = load_category_api_data(BASE_DIR) 

    # 3. 筛选逻辑
    if category and category != "全部":
        # 【修改点】：因为 data_list 是列表，不能用 df[...] 筛选
        # 需要用列表推导式来筛选
        filtered_rows = [
            item for item in data_list 
            if item.get('PreferedOrderCat') == category
        ]
        rows = filtered_rows
    else:
        # 如果没传参，直接返回所有数据
        rows = data_list
    # TO 8-2：将category查询参数传给数据服务，返回筛选后的表格记录。
    return jsonify({"ok": True, "category": category, "rows": load_category_api_data(BASE_DIR, category)})


@app.errorhandler(400)
def bad_request(_error):
    # TOO 8-3：统一返回JSON错误结构，至少包含ok和error字段。
    return jsonify({"ok": False, "error": "请求格式不正确。"}), 400


@app.errorhandler(404)
def page_not_found(_error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=False, port=5500)
