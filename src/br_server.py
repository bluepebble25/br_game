from socket import *
from threading import *
import time
import random

HOST = ''
PORT = 8081
ADDR = (HOST, PORT)
MAX_USER = 2        # 최대 접속 가능 인원수
BUFF = 1024         # 메세지 버퍼 크기

connections = []    # 관리할 소켓 목록
users = []          # 관리할 유저 목록

# 유저와 관련된 정보를 저장하기 위한 객체
class User:
    def __init__(self, client_sock, addr_info, nickname):
        self.client_sock = client_sock
        self.addr_info = addr_info
        self.nickname = nickname


def error_handling(message):
    print(message)
    exit(1)

""" 메시지를 접속한 모두에게 전송하는 함수 """
def send_to_all(msg):
    global connections
    for con in connections:
        con.send(msg.encode())

""" 메시지를 특정 유저에게 전송하는 함수 """
def send_to_user(user, msg):
    global users
    for u in users:
        if u == user:
            user.client_sock.send(msg.encode())


""" 입장 처리 함수 - 스레드로 실행 """
def accept_client(serv_sock, connections, users):
    while True:
        if len(users) < MAX_USER:
            client_sock, addr_info = serv_sock.accept()
            nickname = client_sock.recv(1024).decode()
            print(f"[{nickname}님 입장]\n")
            users.append(User(client_sock, addr_info, nickname))
            connections.append(client_sock)
            send_to_all(f"[{nickname}님 입장]\n")
            if len(users) == 1:
                send_to_all("현재 접속자: 1명\n상대방이 들어오기를 기다리고 있습니다...\n")
            else:
                send_to_all("현재 접속자: 2명\n")

            # isQuitTh = Thread(target=isQuit, args=(client_sock, users))
            # isQuitTh.start()

""" 유저가 나갔는지 검사하는 함수 - 스레드로 실행 """
# 구현 실패
def isQuit(client_sock, users):
    msg = client_sock.recv(BUFF).decode()
    while True:
        # 만약 받은 메시지가 0(연결 종료)거나 '/quit'(나가기) 인 경우
        if msg == 0 or msg == "/quit":
            # 메세지를 받은 클라이언트 소켓의 닉네임 알아내고 제거, 남은 유저에게 메시지 보내기
            for user in users:
                if user.client_sock == client_sock:
                    msg = f"[{user.nickname}님이 나갔습니다]"
                    client_sock.close()
                    users.remove(users)
                    send_to_all(msg)
                    return

""" 게임 시작 함수 """
def game_start(users):
    print("게임 시작")
    global connections
    num = 0
    temp = ''

    startNum = random.randrange(0, 2)   # 0 또는 1 숫자 랜덤생성. 시작할 유저 선택
    i = startNum
    while True:
        # 만약 게임 도중 상대방이 나가면
        if len(users) == 1:
            return "stop"

        # 만약 i가 인덱스 범위(1) 넘어가면 0부터 다시 시작
        if i >= 2:
            i = 0

        # 클라이언트 프로그램은 input을 받을 때에만 숫자를 송신할 수 있음
        send_to_user(users[i], "input")

        """ 게임 로직 고치기 (for j in range에서 msg 만들고 안 보낸 거 고치고 경우의 수까지 고려해서 어디에 위치하면 좋을까 고치기) """
        # 해당 턴의 유저가 숫자를 제대로 입력할 때 까지 반복
        while True:
            msg = ''
            recvMsg = users[i].client_sock.recv(BUFF).decode()
            temp = recvMsg
            if temp.isdigit():
                temp = int(temp)
                for j  in range(1, temp + 1):
                    num += 1
                    msg += ' ' + str(num)   # 예)그 전 숫자가 4였고 받은 숫자가 3이면 최종적으로 msg는 5 6 7이 됨
                
                if num == 31:
                    if i == 0:  # 31을 부른 user가 user[0]이면 user[1]이 승리, 반대도 마찬가지
                        win = 1
                    else:
                        win = 0
                    send_to_all(msg + f'\n[{users[win].nickname}님이 승리하였습니다]\n')
                    return "end"
                elif num > 31:  # 31보다 더 크게되게 숫자를 불렀을 경우
                    num -= temp  # 원래대로 되돌림
                    send_to_user(users[i], "숫자는 31까지만 부를 수 있습니다.")
                    send_to_user(users[i], "input") # 숫자 입력하라는 신호 보내기
                    continue
                else:   # 받은 숫자가 범위 내의 숫자인 경우
                    send_to_all(f'{users[i].nickname}님: {msg}')    #예를 들어 '{nickname}님: 5 6 7' 을 전송
                    break
            elif temp == 0 or temp == "/quit":    # 유저가 나갔거나 종료한다는 메세지 보낸 경우

                msg = f"[{users[i].nickname}님이 나갔습니다]"
                users[i].client_sock.close()
                users.remove(users[i])

                print(users[i])
                print(connections)

                connections.remove(users[i].client_sock)
                
                send_to_all(msg)
                print("게임 종료")
                return "stop"
        
        i += 1  # 다음 유저에게 턴 넘어가기


""" 서버 시작 함수 """
def server_start(users, connections):
    #서버 소켓 생성 및 연결
    serv_sock = socket(AF_INET, SOCK_STREAM)
    serv_sock.bind(ADDR)
    if serv_sock.listen(5) == -1:
        error_handling("listen() error")

    print('서버 시작 (port 정보: ', PORT, '번)')

    acceptTh = Thread(target=accept_client, args=(serv_sock, connections, users,))
    acceptTh.start()

    while True:
        if len(users) == MAX_USER:
            send_to_all("곧 게임이 시작됩니다...\n")
            time.sleep(1)
            result = game_start(users)
            if result == "end":
                continue
            elif result == "stop":
                send_to_all("상대방이 게임을 나가 게임을 중지합니다.\n새로운 사용자를 기다립니다...\n")
                continue

if __name__ == '__main__':
    server_start(users, connections)
    