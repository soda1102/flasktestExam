class Member:
    def __init__(self, id, uid, pw, name, email, phone_number, birth_date, nickname, role="user", active=True):
        self.id = id
        self.uid = uid
        self.pw = pw
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.birth_date = birth_date
        self.nickname = nickname
        self.role = role
        self.active = active

    @classmethod
    def from_db(cls, row:dict):

        if not row:
            return None

        return cls(
            id=row.get('id'),
            uid=row.get('uid'),
            pw=row.get('pw'),
            name=row.get('name'),
            email=row.get('email'),
            phone_number=row.get('phone_number'),
            nickname=row.get('nickname'),
            role=row.get('role'),
            active=bool(row.get('active'))
        )

    def is_admin(self):
        return self.role == "admin"

    def __str__(self):
        return f"{self.role}, {self.name}님. 아이디 : {self.uid}입니다."