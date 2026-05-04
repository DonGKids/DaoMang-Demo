import datetime

class Config:
    SECRET_KEY = 'daomangquan_20251021'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=7)
    DATABASE = 'daomangquan.db'