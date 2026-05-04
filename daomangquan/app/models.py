import sqlite3
from werkzeug.security import generate_password_hash
from config import Config

def get_db():
    db = sqlite3.connect(Config.DATABASE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    return db

def init_database():
    db = get_db()

    # 用户表
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        student_id TEXT,
        college TEXT,
        major TEXT
    )''')

    # 迷茫检测
    db.execute('''CREATE TABLE IF NOT EXISTS maze_detect (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # 分类
    db.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT
    )''')

    # 信息库
    db.execute('''CREATE TABLE IF NOT EXISTS infos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cate_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )''')

    # 论坛
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