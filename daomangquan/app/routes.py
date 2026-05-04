from flask import Blueprint, render_template, request, jsonify, redirect, session
from app.models import get_db
from werkzeug.security import check_password_hash, generate_password_hash

bp = Blueprint('main', __name__)

# 首页
@bp.route('/')
def index():
    return render_template('index.html')

# 登录
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return jsonify(code=200, msg='登录成功')
        return jsonify(code=400, msg='账号或密码错误')
    return render_template('login.html')

# 注册
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            db = get_db()
            db.execute('INSERT INTO users (username,password,student_id,college,major) VALUES (?,?,?,?,?)', (
                request.form['username'],
                generate_password_hash(request.form['password']),
                request.form['student_id'],
                request.form['college'],
                request.form['major']
            ))
            db.commit()
            return jsonify(code=200, msg='注册成功')
        except:
            return jsonify(code=400, msg='用户名已存在')
    return render_template('register.html')

# 退出
@bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# 迷茫检测
@bp.route('/maze')
def maze():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('maze.html')

# 信息库
@bp.route('/info')
def info():
    return render_template('info.html')

# 论坛
@bp.route('/forum')
def forum():
    return render_template('forum.html')

# ---------------- API ----------------
@bp.route('/api/maze', methods=['POST'])
def api_maze():
    if 'user_id' not in session:
        return jsonify(code=401, msg='请先登录')
    db = get_db()
    db.execute('INSERT INTO maze_detect (user_id,content) VALUES (?,?)',
               (session['user_id'], request.form['content']))
    db.commit()
    return jsonify(code=200, msg='检测完成！已为您生成个性化推荐')

@bp.route('/api/info')
def api_info():
    db = get_db()
    data = db.execute('SELECT * FROM infos').fetchall()
    return jsonify(code=200, data=[dict(d) for d in data])

@bp.route('/api/post', methods=['POST'])
def api_post():
    if 'user_id' not in session:
        return jsonify(code=401, msg='请先登录')
    db = get_db()
    db.execute('INSERT INTO posts (user_id,title,content) VALUES (?,?,?)',
               (session['user_id'], request.form['title'], request.form['content']))
    db.commit()
    return jsonify(code=200, msg='发布成功')

@bp.route('/api/posts')
def api_posts():
    db = get_db()
    posts = db.execute('SELECT * FROM posts ORDER BY create_time DESC').fetchall()
    return jsonify(code=200, data=[dict(p) for p in posts])