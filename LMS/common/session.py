import pymysql

class Session:
    
    login_member = None
    
    @staticmethod
    def get_connection():
        print("mysql 접속중 ... ")
        return pymysql.connect(
            host='127.0.0.1',
            user='ksh',
            password='1102',
            db='core',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

    @classmethod
    def login(cls,member):
        cls.login_member = member

    @classmethod
    def logout(cls):
        cls.login_member = None

    @classmethod
    def is_login(cls):
        return cls.login_member is not None

    @classmethod
    def is_admin(cls):
        return cls.is_login() and cls.login_member.role == 'admin'

    @classmethod
    def is_manager(cls):
        return cls.is_login() and cls.login_member.role in ('manager','admin')