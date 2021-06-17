from socket import *
from threading import *

HOST = ''
PORT = 8081
ADDR = (HOST, PORT)
BUFF = 1024 # 메시지 버퍼 사이즈


def recieve(client_sock):
    while True:
        msg = client_sock.recv(BUFF).decode()

        # 서버로부터 "input"이라는 메세지 받으면 1~3의 숫자 입력
        if msg == "input":
            while True:
                num = input("숫자 입력(1~3): ")
                if num.isdigit() and int(num) >= 1 and int(num) <= 3:
                    client_sock.send(num.encode())
                    break
                elif num == "/quit":
                    client_sock.send(num.encode())
                    print("게임 종료")
                    client_sock.close()
                    exit(1)
                else:
                    print("1~3의 숫자만 입력할 수 있습니다.")
                    continue
        else:
            print(msg)
            
        


if __name__ == '__main__':

    nickname = input("닉네임 입력: ")

    client_sock = socket(AF_INET, SOCK_STREAM)

    try:
        client_sock.connect(ADDR)
        print("연결성공")
    except ConnectionRefusedError:
        print("연결실패 or 정원(2인) 가득 참")
        exit(1)

    client_sock.send(nickname.encode())

    recieveTh = Thread(target=recieve, args=(client_sock,))
    recieveTh.daemon = False
    recieveTh.start()
    



    