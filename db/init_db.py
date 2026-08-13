from db.database import DB_FILE, init_db


DB_PATH = str(DB_FILE)


def init_database():
    init_db()


if __name__ == "__main__":
    init_database()
    print("数据库初始化完成")
