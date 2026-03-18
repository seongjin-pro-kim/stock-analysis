import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *


class KiwoomBalance(QMainWindow):
    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        self.kiwoom.OnEventConnect.connect(self.login_slot)
        self.kiwoom.OnReceiveTrData.connect(self.receive_tr_data)

        self.kiwoom.dynamicCall("CommConnect()")

    def login_slot(self, err_code):
        if err_code == 0:
            print("로그인 성공! 계좌 정보를 가져옵니다...")
            account_list = self.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
            self.account_number = account_list.split(';')[0]
            print(f"사용 계좌: {self.account_number}")
            self.get_account_balance()
        else:
            print("로그인 실패:", err_code)
            QCoreApplication.instance().quit()

    def get_account_balance(self):
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_number)
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")  # 실계좌면 실제 비번
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")

        # rqname = "계좌잔고요청"
        self.kiwoom.dynamicCall(
            "CommRqData(QString, QString, int, QString)",
            "계좌잔고요청",   # rqname
            "opw00018",      # trcode
            0,               # prev_next
            "8000"           # screen_no
        )

    # ★ 인자 이름을 rqname으로, 내부에서도 rqname으로 사용
    def receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        # 어떤 TR 응답인지 구분
        if rqname == "계좌잔고요청":
            total_buy = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                trcode, recordname, 0, "총매입금액"
            )
            total_profit = self.kiwoom.dynamicCall(
                "GetCommData(QString, QString, int, QString)",
                trcode, recordname, 0, "총수익률(%)"
            )

            print("=" * 30)
            try:
                print(f"총 매입금액: {int(total_buy.strip() or '0'):,}원")
            except ValueError:
                print(f"총 매입금액(raw): {total_buy}")
            print(f"총 수익률: {total_profit.strip()}%")
            print("=" * 30)

            QCoreApplication.instance().quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    balance = KiwoomBalance()
    app.exec_()
