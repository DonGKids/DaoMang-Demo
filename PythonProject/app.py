# 导茫犬——大学生“扫茫”信息服务平台
# 项目：黑龙江省大学生创新创业训练计划
# 技术：Python Flask + SQLite + 前端页面（内嵌）
# 功能：用户系统、迷茫检测、信息分类、互助论坛、个性化推荐

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

# 初始化应用
app = Flask(__name__)
app.secret_key = "daomangquan_20251021"
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

# ===================== 数据库操作 =====================
def get_db():
    db = sqlite3.connect("daomangquan.db", check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db

# 初始化数据库表
def init_database():
    db = get_db()
    # 用户表
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        student_id TEXT NOT NULL,
        college TEXT,
        major TEXT
    )''')
    # 迷茫检测表
    db.execute('''CREATE TABLE IF NOT EXISTS maze_detect (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # 信息分类表
    db.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )''')
    # 信息内容表
    db.execute('''CREATE TABLE IF NOT EXISTS infos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cate_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )''')
    # 论坛帖子表
    db.execute('''CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    # 插入默认分类
    default_cates = [
        (1, "生活常识", "医保、出行、安全、日常科普"),
        (2, "升学就业", "考研、考公、实习、就业"),
        (3, "法律知识", "劳动权益、兼职安全、合同保护"),
        (4, "创业资讯", "大学生创业政策、项目资源")
    ]
    for c in default_cates:
        if not db.execute("SELECT id FROM categories WHERE id=?", (c[0],)).fetchone():
            db.execute("INSERT INTO categories VALUES (?,?,?)", c)
    db.commit()

# ===================== 前端页面模板（内嵌） =====================
BASE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>导茫犬 - 大学生扫茫平台</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:Microsoft YaHei;}
        body{background:#f5f7fa;}
        .header{background:#4285F4;color:white;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;}
        .nav a{color:white;margin-left:20px;text-decoration:none;}
        .container{max-width:1000px;margin:20px auto;padding:0 20px;}
        .card{background:white;border-radius:8px;padding:24px;margin-bottom:16px;box-shadow:0 2px 10px rgba(0,0,0,0.05);}
        .btn{background:#4285F4;color:white;border:none;padding:10px 20px;border-radius:6px;cursor:pointer;margin-top:10px;}
        input,textarea{width:100%;padding:10px;margin:8px 0;border:1px solid #eee;border-radius:6px;}
        .title{margin-bottom:16px;color:#333;}
    </style>
</head>
<body>
    <div class="header">
        <h2>导茫犬 · 大学生扫茫信息平台</h2>
        <div class="nav">
            <a href="/">首页</a>
            <a href="/info">信息库</a>
            <a href="/forum">论坛</a>
            {% if session.user_id %}
                <a href="/maze">迷茫检测</a>
                <a href="/logout">退出</a>
            {% else %}
                <a href="/login">登录</a>
                <a href="/register">注册</a>
            {% endif %}
        </div>
    </div>
    <div class="container">
        {{ content | safe }}
    </div>
</body>
</html>
'''

# ===================== 页面路由 =====================
@app.route("/")
def index():
    content = """
<div class="card">
    <h2 class="title">欢迎使用导茫犬平台</h2>
    <p>📌 解决大学生信息碎片化、迷茫、信息茧房问题</p>
    <p>📌 提供：迷茫检测 | 分类信息 | 互助论坛 | 个性化推荐</p>
    <p>📌 覆盖：生活、升学、法律、创业四大核心模块</p>
</div>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return jsonify(code=200, msg="登录成功")
        return jsonify(code=400, msg="账号或密码错误")
    content = """
<div class="card">
    <h2 class="title">用户登录</h2>
    <input id="username" placeholder="用户名">
    <input id="password" type="password" placeholder="密码">
    <button class="btn" onclick="login()">登录</button>
</div>
<script>
function login(){
    fetch("/login",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:"username="+document.getElementById("username").value+"&password="+document.getElementById("password").value})
    .then(r=>r.json()).then(d=>{d.code===200?location.href="/":alert(d.msg);})
}
</script>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        try:
            db = get_db()
            db.execute("INSERT INTO users (username,password,student_id,college,major) VALUES (?,?,?,?,?)",
                (request.form["username"], generate_password_hash(request.form["password"]),
                 request.form["student_id"], request.form["college"], request.form["major"]))
            db.commit()
            return jsonify(code=200, msg="注册成功")
        except:
            return jsonify(code=400, msg="用户名已存在")
    content = """
<div class="card">
    <h2 class="title">用户注册</h2>
    <input id="username" placeholder="用户名">
    <input id="password" type="password" placeholder="密码">
    <input id="student_id" placeholder="学号">
    <input id="college" placeholder="学院">
    <input id="major" placeholder="专业">
    <button class="btn" onclick="register()">注册</button>
</div>
<script>
function register(){
    fetch("/register",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:"username="+document.getElementById("username").value+"&password="+document.getElementById("password").value
    +"&student_id="+document.getElementById("student_id").value+"&college="+document.getElementById("college").value
    +"&major="+document.getElementById("major").value})
    .then(r=>r.json()).then(d=>{d.code===200?location.href="/login":alert(d.msg);})
}
</script>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/maze")
def maze():
    if "user_id" not in session: return redirect("/login")
    content = """
<div class="card">
    <h2 class="title">迷茫检测</h2>
    <p>描述你的迷茫（学习/就业/生活/人际），系统将为你个性化推荐信息</p>
    <textarea id="content" rows="6" placeholder="请输入你的困惑..."></textarea>
    <button class="btn" onclick="detect()">提交检测</button>
</div>
<script>
function detect(){
    fetch("/api/maze",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:"content="+document.getElementById("content").value})
    .then(r=>r.json()).then(d=>alert(d.msg));
}
</script>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

@app.route("/info")
def info():
    content = """
<div class="card">
    <h2 class="title">分类信息库</h2>
    <div id="info_list"></div>
</div>
<script>
fetch("/api/info").then(r=>r.json()).then(d=>{
    let html = "";
    d.data.forEach(item=>{
        html += `<div style='padding:12px;border-bottom:1px solid #eee;margin:8px 0'>
            <h3>${item.title}</h3><p>${item.content}</p></div>`;
    });
    document.getElementById("info_list").innerHTML = html;
})
</script>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

@app.route("/forum")
def forum():
    content = """
<div class="card">
    <h2 class="title">互助论坛</h2>
    {% if session.user_id %}
    <input id="title" placeholder="标题">
    <textarea id="content" rows="4" placeholder="分享你的问题或经验"></textarea>
    <button class="btn" onclick="post()">发布帖子</button>
    {% endif %}
    <div id="post_list" style="margin-top:20px;"></div>
</div>
<script>
function load_posts(){
    fetch("/api/posts").then(r=>r.json()).then(d=>{
        let html = "";
        d.data.forEach(p=>{
            html += `<div style='padding:12px;border-bottom:1px solid #eee'>
                <h3>${p.title}</h3><p>${p.content}</p><small>${p.create_time}</small></div>`;
        });
        document.getElementById("post_list").innerHTML = html;
    })
}
function post(){
    fetch("/api/post",{method:"POST",headers:{"Content-Type":"application/x-www-form-urlencoded"},
    body:"title="+document.getElementById("title").value+"&content="+document.getElementById("content").value})
    .then(r=>r.json()).then(d=>{alert(d.msg);load_posts();})
}
load_posts();
</script>
"""
    return render_template_string(BASE_HTML, content=content, session=session)

# ===================== 核心API接口 =====================
@app.route("/api/maze", methods=["POST"])
def api_maze():
    if "user_id" not in session: return jsonify(code=401, msg="请先登录")
    db = get_db()
    db.execute("INSERT INTO maze_detect (user_id,content) VALUES (?,?)",
               (session["user_id"], request.form["content"]))
    db.commit()
    return jsonify(code=200, msg="检测完成！已为您生成个性化信息推荐")

@app.route("/api/info")
def api_info():
    db = get_db()
    data = db.execute("SELECT * FROM infos").fetchall()
    return jsonify(code=200, data=[dict(d) for d in data])

@app.route("/api/post", methods=["POST"])
def api_post():
    if "user_id" not in session: return jsonify(code=401, msg="请先登录")
    db = get_db()
    db.execute("INSERT INTO posts (user_id,title,content) VALUES (?,?,?)",
               (session["user_id"], request.form["title"], request.form["content"]))
    db.commit()
    return jsonify(code=200, msg="发布成功")

@app.route("/api/posts")
def api_posts():
    db = get_db()
    posts = db.execute("SELECT * FROM posts ORDER BY create_time DESC").fetchall()
    return jsonify(code=200, data=[dict(p) for p in posts])

# ===================== 启动项目 =====================
if __name__ == "__main__":
    init_database()
    print("✅ 导茫犬平台启动成功 → http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)