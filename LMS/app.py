from flask import Flask, render_template, request, redirect, url_for, session
from datetime import date, datetime

from LMS.common import Session
from LMS.domain.Board import Board

app = Flask(__name__)
app.secret_key = 'dfgrt24jkkj'

#1. 로그인
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    uid = request.form.get('uid')
    upw = request.form.get('upw')

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            #1. 회원정보 조회
            sql = "SELECT id, name, uid, email, phone_number, role FROM members WHERE uid = %s AND password = %s"

            cursor.execute(sql, (uid, upw,))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']
                session['user_name'] = user['name']
                session['user_uid'] = user['uid']
                session['user_email'] = user['email']
                session['user_phone_number'] = user['phone_number']
                session['user_role'] = user['role']

                return redirect(url_for('index'))

            else:
                return "<script>alert('아이디나 비번이 틀렸습니다.');history.back();</script>"

    finally:
        conn.close()

#2. 로그아웃
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

#3. 회원가입
@app.route('/join', methods=['GET', 'POST'])
def join():
    if request.method == 'GET':
        current_year = datetime.now().year
        return render_template('join.html',year_now=current_year)

    uid = request.form.get('uid')
    password = request.form.get('password')
    name = request.form.get('name')
    email = request.form.get('email')
    nickname = request.form.get('nickname')

    #생년월일 추가
    b_year = request.form.get('birth_year')
    b_month = request.form.get('birth_month')
    b_day = request.form.get('birth_day')

    try:
        if b_year and b_month and b_day:
            birth_date = date(int(b_year), int(b_month), int(b_day))
            today = date.today()
            # 만 나이 계산 로직
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

            if age < 14:
                return '<script>alert("만 14세 이상만 가입 가능합니다.");history.back();</script>'

            # DB에 저장할 날짜 형식 문자열 (YYYY-MM-DD)
            birthdate_str = birth_date.strftime('%Y-%m-%d')

        else:
            return '<script>alert("생년월일을 모두 입력해주세요.");history.back();</script>'

    except ValueError:
        return '<script>alert("올바른 날짜 형식이 아닙니다.");history.back();</script>'

    # 1. 폼 데이터 가져오기 (전화번호 3개를 각각 가져옴)
    p1 = request.form.get('phone1')
    p2 = request.form.get('phone2')
    p3 = request.form.get('phone3')

    # 2. 가져온 3개를 하나로 합치기 (변수 생성)
    phone_number = f"{p1}-{p2}-{p3}"

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            #1. 중복 체크 (아이디, 이메일, 전화번호, 닉네임)
            check_sql = "SELECT id FROM members WHERE uid = %s OR email = %s OR phone_number = %s OR nickname = %s"
            cursor.execute(check_sql, (uid, email, phone_number, nickname))
            if cursor.fetchone():
                return "<script>alert('이미 사용 중인 정보(아이디/이메일/번호/닉네임)가 있습니다.');history.back();</script>"

            #2. 실제 저장 실행 (중요: DB의 AFTER name 구조에 맞게 순서 조정하기 반드시!)
            #순서: uid, password, name, birth_date, email, phone_number, nickname
            sql = """
                    INSERT INTO members 
                    (uid, password, name, birth_date, email, phone_number, nickname) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """

            #위에랑 순서 똑같게하기
            user_data = (uid, password, name, birthdate_str, email, phone_number, nickname)

            cursor.execute(sql, user_data)
            conn.commit()

            return "<script>alert('회원가입이 완료되었습니다!');location.href='/login';</script>"

    except Exception as e:
        conn.rollback()  # 오류 발생 시 되돌리기
        print(f"회원가입 에러 상세 내용: {e}")
        return f"가입 중 오류가 생겼어요. 관리자에게 문의해주세요. (에러: {e})"

    # conn = Session.get_connection()
    # try:
    #     with conn.cursor() as cursor:
    #         # --- [중복 체크 시작] ---
    #
    #         # 1. 아이디 중복 확인
    #         cursor.execute("SELECT id FROM members WHERE uid = %s", (uid,))
    #         if cursor.fetchone():
    #             return "<script>alert('이미 사용 중인 아이디입니다.');history.back();</script>"
    #
    #         # 2. 이메일 중복 확인
    #         cursor.execute("SELECT id FROM members WHERE email = %s", (email,))
    #         if cursor.fetchone():
    #             return "<script>alert('이미 등록된 이메일 주소입니다.');history.back();</script>"
    #
    #         # 3. 휴대폰 번호 중복 확인
    #         cursor.execute("SELECT id FROM members WHERE phone_number = %s", (phone_number,))
    #         if cursor.fetchone():
    #             return "<script>alert('이미 등록된 휴대폰 번호입니다.');history.back();</script>"
    #
    #         # 4. 닉네임 중복 확인
    #         cursor.execute("SELECT id FROM members WHERE nickname = %s", (nickname,))
    #         if cursor.fetchone():
    #             return "<script>alert('이미 사용 중인 닉네임입니다.');history.back();</script>"
    #
    #         # --- [중복 체크 끝] ---
    #
    #         # 모든 검사를 통과했다면 실제 저장 실행
    #         sql = "INSERT INTO members (uid, password, name, birthdate, email, phone_number, nickname) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #         cursor.execute(sql, (uid, password, name, birthdate_str, email, phone_number, nickname))
    #         conn.commit()
    #
    #         return "<script>alert('회원가입이 완료되었습니다!');location.href='/login';</script>"
    #
    # except Exception as e:
    #     print(f"회원가입 에러 발생: {e}")
    #     return "가입 중 오류가 생겼어요. 관리자에게 문의해주세요!"
    #
    # finally:
    #     conn.close()

#4. 마이페이지(수정)
@app.route('/member/edit', methods=['GET', 'POST'])
def member_edit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            if request.method == 'GET':
                cursor.execute("SELECT * FROM members WHERE id = %s", (session['user_id'],))
                user = cursor.fetchone()
                return render_template('member_edit.html', user=user)

            new_name = request.form.get('name')
            new_pw = request.form.get('password')
            new_email = request.form.get('email')
            new_phone = request.form.get('phone_number')


            if new_name:
                sql = "UPDATE members SET name = %s WHERE id = %s"
                cursor.execute(sql, (new_name, session['user_id']))
                session['user_name'] = new_name

            if new_pw:
                sql = "UPDATE members SET password = %s WHERE id = %s"
                cursor.execute(sql, (new_pw, session['user_id']))

            if new_email:
                sql = "UPDATE members SET email = %s WHERE id = %s"
                cursor.execute(sql, (new_email, session['user_id']))

            if new_phone:
                sql = "UPDATE members SET phone_number = %s WHERE id = %s"
                cursor.execute(sql, (new_phone, session['user_id']))

            conn.commit()
            return "<script>alert('정보가 수정되었습니다.');location.href='/mypage';</script>"


    except Exception as e:
        print(f"정보 수정 에러:{e}")
        return "수정 중 오류가 발생했습니다.\n member_edit()메서드를 확인하세요."

    finally:
        conn.close()

#5. 마이페이지(조회)
@app.route('/mypage')
def mypage():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = Session.get_connection()

    try:
        with conn.cursor() as cursor:
            #1. 내정보 상세 조회
            cursor.execute("SELECT * FROM members WHERE id = %s", (session['user_id'],))
            #로그인 정보 db에서 가져오기
            user_info = cursor.fetchone()

            #2. 내가 쓴 게시글 개수 조회
            cursor.execute("SELECT COUNT(*) as cnt FROM boards WHERE member_id = %s", (session['user_id'],))
            result = cursor.fetchone()

            board_count = result['cnt'] if isinstance(result, dict) else result[0]
            return render_template('mypage.html', user=user_info, board_count=board_count)

    finally:
        conn.close()

#=======================================================================================================================
# 글쓰기
@app.route('/board/write',methods=['GET','POST'])  #http://localhost:5000/board/write 경로 생성
def board_write():
    #1. 사용자가 '글쓰기' 버튼을 눌러서 들어왔을 때 화면보여주기
    if request.method == 'GET':
        #로그인 체크(안했으면 글 못쓰게)
        if 'user_id' not in session:
            return '<script>alert("로그인 후 이용 가능합니다.");location.href="/login";</script>'
        return render_template('board_write.html')

    #2. 사용자가 '등록하기' 버튼을 눌러서 데이터를 보냈을 때(DB저장)
    elif request.method == 'POST':  # <form action="/member/edit" method="POST">
        title = request.form.get('title')
        content = request.form.get('content')
        #세션에 저장된 로그인 유저의 id (member_id)
        member_id = session.get('user_id')

        conn = Session.get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "INSERT INTO boards (member_id, title, content) VALUES (%s, %s, %s)"
                cursor.execute(sql, (member_id, title, content))
                conn.commit()
            return redirect(url_for('board_list'))  #저장 후 목록으로 이동
            #redirect : 값이 없이 출력할 때 를 의미(get으로 호출)

        except Exception as e:
            print(f"글쓰기 에러 : {e}")
            return "저장 중 에러가 발생하였습니다."

        finally:
            conn.close()

#1. 게시판 목록 조회
@app.route('/board/list')  #http://localhost:5000/board
def board_list():
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            #작성자 이름을 함께 가져오기 위해 JOIN 사용
            sql = """
                SELECT b.*, m.nickname as writer_name FROM boards b
                JOIN members m ON b.member_id = m.id
                ORDER BY b.id DESC
            """

            cursor.execute(sql)
            rows = cursor.fetchall()
            boards = [Board.from_db(row) for row in rows]
            print(boards)
            return render_template('board_list.html', boards=boards)

    finally:
        conn.close()

#2. 게시글 자세히보기
@app.route('/board/view/<int:board_id>')
def board_view(board_id):
    conn = Session.get_connection()

    try:
        with conn.cursor() as cursor:
            #JOIN을 통해 작성자 정보(name, uid)를 함께 조회
            sql = "SELECT b.*, m.nickname as writer_name, m.uid as writer_uid FROM boards b JOIN members m ON b.member_id = m.id WHERE b.id = %s"
            cursor.execute(sql, (board_id,))
            row = cursor.fetchone()

            if not row:
                return "<script>alert('존재하지 않는 게시글 입니다.');history.back();</script>"

            #Board 객체로 변환(앞서 작성한 Board.py의 from_db활용)
            board = Board.from_db(row)
            return render_template('board_view.html', board=board)

    finally:
        conn.close()

#3. 게시글 자세히보기
@app.route('/board/edit/<int:board_id>', methods=['GET', 'POST'])
def board_edit(board_id):
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            #1.화면 보여주기(기존 데이터 로드)
            if request.method == 'GET':
                sql = "SELECT * FROM boards WHERE id = %s"
                cursor.execute(sql, (board_id,))
                row = cursor.fetchone()

                if not row:
                    return "<script>alert('존재하지 않은 게시글 입니다.');history.back();</script>"

                #본인 확인 로직(필요시 추가)
                if row['member_id'] != session.get('user_id'):
                    return "<script>alert('수정 권한이 없습니다..');history.back();</script>"
                print(row)  #콘솔에 테스트 출력용, 없어두댐
                board = Board.from_db(row)
                return render_template('board_edit.html', board=board)

            #2. 실제 DB 업데이트 처리
            elif request.method == 'POST':
                title = request.form.get('title')
                content = request.form.get('content')

                sql = "UPDATE boards SET title=%s, content=%s WHERE id=%s"
                cursor.execute(sql, (title, content, board_id))
                conn.commit()
                return redirect(url_for('board_view', board_id=board_id))

    finally:
        conn.close()

#3. 게시글 삭제
@app.route('/board/delete/<int:board_id>')
def board_delete(board_id):
    conn = Session.get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "DELETE FROM boards WHERE id = %s"  #저장된 테이블면 boards 사용
            cursor.execute(sql, (board_id,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"{board_id}번 게시글 삭제 성공")
            else:
                return "<script>alert('삭제할 게시글이 없거나 권한이 없습니다.');history.back();</script>"

        return redirect(url_for('board_list'))

    except Exception as e:
        print(f"삭제 에러 : {e}")
        return "삭제 중 오류가 발생했습니다."

    finally:
        conn.close()


#=====================================================================================================================
@app.route('/')
def index():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)