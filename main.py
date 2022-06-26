import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

import StockData.function_data as fdata
import MABol.MABolStrategy as MAB
import Ui_HW_GUI

if __name__ == '__main__': 
    app = QApplication(sys.argv) 
    MainWindow = QMainWindow() 
#----------------------------------------    
    ui = Ui_HW_GUI.Ui_MainWindow() 
    ui.setupUi(MainWindow) 
    # 取得資料
    kb = fdata.stockdataclass()
    KBar=kb.getKbar()
    # 呼叫策略類別MABolClass產生物件實體mab
    
    mab = MAB.MABolClass()
    # 呼叫繼承自類別的策略方法-順勢交易
    ui.radioButton.clicked.connect(lambda: mab.BuyTheTrend(ui,KBar))    
    # 呼叫繼承自類別的策略方法-逆勢交易
    ui.radioButton_2.clicked.connect(lambda: mab.Counter_trend(ui,KBar)) 
    # 呼叫繼承自類別的策略方法-乖離率上下穿越均線乖離
    ui.radioButton_3.clicked.connect(lambda: mab.UpAndDown(ui,KBar)) 
    # 呼叫繼承自類別的策略方法-低點買進+順勢買進+高點出場+停損停利
    ui.radioButton_4.clicked.connect(lambda: mab.AddFilter(ui,KBar)) 

#----------------------------------------    
    MainWindow.show() 
    sys.exit(app.exec_())
