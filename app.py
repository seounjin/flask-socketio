from flask import Flask, render_template
from flask_socketio import SocketIO, send, join_room, leave_room, emit
import database

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

user_Id = {}  # connect id list
room_dic = {"room_Info": {0: [], 1: [], 2: []}}   # key : 방번호 value : id list
room_state = {0: {"white": False, "black": False}, 1: {"white": False,"black": False}, 2: {"white": False,"black":False}}

db = database.Database()

@app.route('/')
def index():
    return render_template('data.html')


#  로그인 메시지
@socketio.on('login')
def login_message(rev_id):  # 메세지 받는
    print('received id: ' + rev_id)
    user_Id[rev_id] = rev_id + str('님')  # 접속한 유저아이디 저장
    emit('login', rev_id)


# 사용자 정보 메세지 받는
@socketio.on('join')
def join_message(user_info):  # 메세지 받는
    print(user_info)
    print(user_info["join"]["id"],
     user_info["join"]["password"],
     user_info["join"]["name"],
     user_info["join"]["email"])

    db.insert_user(user_info["join"]["id"],
     user_info["join"]["password"],
     user_info["join"]["name"],
     user_info["join"]["email"])

    emit('join_check', 'T')


# id 중복 체크
@socketio.on('check')
def join_message(rev_id):  # 메세지 받는
    db.user_id_check()
    db_info = db.executeAll()
    print(db_info)
    for row in db_info:
        if rev_id == row['ID']:
            emit('client_id_check', 'F')
        else:
            emit('client_id_check', 'T')

    db.close_db()

#  연결 종료 메세지 받는
@socketio.on('exit')
def login_message(rev_id):
    print(rev_id," 연결 종료함")
    # user_Id[rev_id] = rev_id + str('님')  # 접속한 유저아이디 저장
    # emit('login', rev_id)


# 방 리스트 요청 받고 방리스트 보내주는 매서드
@socketio.on('battle', namespace='/battle')
def handle_message(message):  # 메세지 받는

    if message == "room_list":
        print(message + "받음")
        send(room_dic)

    elif "ready" in message.keys():
        mes = message["ready"]
        mes_index = mes["room_index"]
        mes_color = mes["color"]
        w_b = room_dic["room_Info"]

        if room_state[mes_index][mes_color] == False:  # 레디안한 상태
            room_state[mes_index][mes_color] = True
            send({"ready": "레디 완료"})
        else:
            room_state[mes_index][mes_color] = False
            send({"ready": "레디 안됨"})

        if room_state[mes_index]["white"] == True and room_state[mes_index]["black"] == True:
            #send("gamestart", room=mes_index)
            send({"gamestart":{w_b[mes_index][0]: "White", w_b[mes_index][1]: "Black"}}, room=mes_index)  # room에 있는 유저가 백인지 흑인지 보내줌

    elif "tile_set"in message.keys():
        print("타일셋 받음")
        mes = message["tile_set"]
        mes_x = mes["X"]
        mes_y = mes["Y"]
        mes_sender = mes["Sender"]
        mes_tile = mes["Tile"]
        mes_index = mes["room_index"]

        send({"tile_set": {"Sender": mes_sender, "X": mes_x, "Y": mes_y, "Tile": mes_tile}}, room=mes_index)


@socketio.on('join', namespace='/battle')  # room join
def on_join(r_info):
    room_info = room_dic["room_Info"]

    # 방 인원수 제한 2명
    if len(room_info[r_info["room_index"]]) == 2:
        send("full")
    else:
        send("pos")
        r_index = r_info["room_index"]
        username = user_Id[r_info["user_id"]]
        #room_info = room_dic["room_Info"]

        # room_Info 방이 있는지 검사
        if r_index in room_info.keys():
            if not len(room_info[r_index]):  # 방에 사람이 없을 경우 방에 사람 추가
                room_info[r_index] = [username]
            else:
                room_info[r_index] = room_info.get(r_index, []) + [username]
        else:  # room_Info 방이 없을경우 방 추가
            room_info[r_index] = [username]

        room = r_index
        join_room(room)

        # 실시간 방업데이트
        if len(room_info[r_index]) == 2:  # 방에 두명일경우
            send({"white_black": {"white": room_info[r_index][0], "black": room_info[r_index][1]}}, room=room)
        else:
            send({"white_black": {"white": room_info[r_index][0], "black": "대기중"}}, room=room)


@socketio.on('leave', namespace='/battle')  # room leave
def on_leave(r_info):

    r_index = r_info["room_index"]
    username = user_Id[r_info["user_id"]]

    room_info = room_dic["room_Info"]

    room_info[r_index].remove(username)  # 방에서 나간 id 제거
    print(room_info)
    room = r_index
    leave_room(room)

    # 실시간 방업데이트
    if len(room_info[r_index]) == 1:  # 방에 두명일경우
        send({"white_black": {"white": room_info[r_index][0], "black": "대기중"}}, room=room)

@socketio.on('disconnect', namespace='/battle')
def trax_disconnect():
    print("연결 종료")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
    #socketio.run(app, port=5000, debug=True)









