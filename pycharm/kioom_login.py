import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *


class KiwoomLoginTest(QMainWindow):
    def __init__(self):
        super().__init__()
        print("키움 API 컨트롤 로드 중...")

        # 키움 Open API+ OCX 연결
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        # 로그인 결과 이벤트 슬롯 연결
        self.kiwoom.OnEventConnect.connect(self.login_slot)

        # 로그인 실행
        self.login_run()

    def login_run(self):
        # 0이 반환되면 정상 실행, 이외는 실패
        res = self.kiwoom.dynamicCall("CommConnect()")
        if res == 0:
            print("로그인 창이 열립니다. 잠시만 기다려주세요...")
        else:
            print(f"로그인 실행 실패: 에러코드 {res}")

    def login_slot(self, err_code):
        if err_code == 0:
            print(">>> [성공] 키움증권 서버에 정상적으로 연결되었습니다!")
        else:
            print(f">>> [실패] 로그인 오류 발생. 에러코드: {err_code}")

        # 테스트 종료 후 프로그램 닫기
        QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_test = KiwoomLoginTest()
    app.exec_()