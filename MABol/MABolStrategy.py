from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
import datetime 
from talib import SMA,STDDEV 
import numpy as np

 
#visual
import mplfinance as mpf
import seaborn as sns
#finance
import talib

class MABolClass():
    def BuyTheTrend(self, ui, KBar):
        self.ui = ui
        import pandas as pd
        import datetime
        from talib import SMA,STDDEV
        import numpy as np
        import matplotlib.pyplot as plt 
        import matplotlib.ticker as plticker
        
        # 初始資金
        InitCapital=1000000
        #進場價格
        OrderPrice = None
        #進場數量
        OrderQty = 0
        #出場價格
        CoverPrice = None

        # 總獲利 、 交易次數
        TotalProfit = []
        TotalTreadeNum = 0 
        
        data = {
                '買進時間': [], 
                '買進原因': [],
                '買進價格': [],
                '售出時間': [],
                '售出價格': [],
                '售出原因': [],
                '數量': [],
                '獲利': []#[(CoverPrice-OrderPrice)*OrderQty*1000],
                }   
        
        #計算移動平均線
        KBar['MA'] = SMA(KBar['close'], timeperiod= 10)
        #計算乖離率
        KBar['bias'] = (KBar['close']- KBar['MA']) / KBar['MA']
        
        for i in range(len(KBar['date'])):
            Date = KBar['date'][i]
            Close = KBar['close'][i]
            Bias = KBar['bias'][i]
            LastBias = KBar['bias'][i-1]
            status = []
            
            if LastBias > 0 and OrderQty == 0 and i < len(KBar['date'])-1:
                #正乖離率進場
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                status = ' 正乖離率 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
            elif LastBias < 0 and OrderQty != 0  and i < len(KBar['date'])-1:
                # 負乖離率出場
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 負乖離率 '
                print( '售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 回測時間結束，則出場
            elif OrderQty != 0 and i == len(KBar['date'])-1:
                # 出場時間、價格
                CoverDate = Date
                CoverPrice = Close
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 結束 '
                print( '結束 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'盈虧:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
        result = pd.DataFrame(data) #把字典轉成DataFrame
        #print(result)
        self.change_data(result, self.ui.tableWidget)
        
        #作圖
        bar = pd.DataFrame(KBar)
        bar['date'] = pd.to_datetime(bar['date'])
        bar.set_index(['date'], inplace=True)
        stock_id = "Apple"
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        add_plot =[mpf.make_addplot(bar['bias'],panel= 2,color="b")]
        mpf.plot(bar,type='candle', mav=(5,10), volume = True,figsize=(20, 10),title = stock_id, style=s,addplot=add_plot,savefig='bar_chart.png')
        self.change_plot("bar_chart.png")

        
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        plot_X = list(range(1, len(TotalProfit) + 1))
        plot_Y = np.cumsum(TotalProfit)
        ax = plt.subplot(111)           # 新增繪圖圖片
        
        ax.bar( plot_X, plot_Y )      # 繪製圖案 ( X軸物件, Y軸物件 )
        ax.ticklabel_format(style = "plain") # 設定Y軸為實數顯示，否則預設顯示為科學符號
        
        # 設定X軸間隔為1
        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        ax.xaxis.set_major_locator(loc)
        
        # 設定文字
        for x, y in zip(plot_X, plot_Y):
            text_show = int(y)
            # plt.text(X座標, Y座標, 顯示內容, 水平對齊方式, 垂直對齊方式)
            if y > 0:
                plt.text(x ,y ,text_show, ha = "center", va = "bottom")
            else:
                plt.text(x ,y ,text_show, ha = "center", va = "top") 
        
        plt.savefig("profit_chart.png")
        self.change_plot2("profit_chart.png")
        plt.clf()
        
        #計算最大資金回落
        MDD,Capital,MaxCapital = 0,0,0
        for p in TotalProfit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
            #print(MaxCapital,Capital,DD)
        
        
        #平均損益
        avgprofit = sum(TotalProfit)/len(TotalProfit)
        
        #勝率
        winprofit=[]
        loseprofit=[]
        for p in TotalProfit:
            if p >=0:
                winprofit+=[p]
            if p < 0:
                loseprofit+=[p]
        #勝率
        win = len(winprofit)/(len(winprofit)+len(loseprofit))
        
        #賺賠比
        avg_win = sum(winprofit)/len(TotalProfit)
        avg_lose = sum(loseprofit)/len(TotalProfit)
        win_lose = avg_win / abs(avg_lose)
        #獲利因子
        get_money = sum(winprofit) / abs(sum(loseprofit))
        
        #夏普率
        buy = pd.DataFrame()
        buy['date'] = pd.to_datetime(result['買進時間'])
        buy['price'] = result['買進價格']
        sale = pd.DataFrame()
        sale['date'] = pd.to_datetime(result['售出時間'])
        sale['price'] = result['售出價格']
        buy_sale = pd.DataFrame()
        buy_sale = pd.concat([buy,sale],axis=0 ,ignore_index=True)
        buy_sale.index=pd.to_datetime(buy_sale.date)
        buy_sale.drop('date',axis=1,inplace=True)
        pct_change = buy_sale.pct_change()
        profit1 = pct_change.mean()
        risk = pct_change.std()
        sharpe = profit1 / (risk * ( (TotalTreadeNum*2) ** 0.5))
         
        print( '總交易次數:' , TotalTreadeNum , '總損益:', sum(TotalProfit) ,'平均損益',avgprofit,
              '勝率', win,'賺賠比' ,win_lose,'獲利因子',get_money,'夏普比率',sharpe)
        dict = {'總交易次數' : [TotalTreadeNum],
                '總損益' : [sum(TotalProfit)],
                '平均損益' : [avgprofit],
                '最大資金回落' : [MDD],
                '勝率' : [win],
                '賺賠比' : [win_lose],
                '獲利因子' : [get_money],
                '夏普比率' : [sharpe]
                    }
        df = pd.DataFrame(dict)
        self.change_data(df, self.ui.tableWidget_2)
        
    def Counter_trend(self, ui, KBar):    
        self.ui = ui
        import pandas as pd
        import datetime
        from talib import SMA,STDDEV
        import numpy as np
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        
        
        # 初始資金
        InitCapital=1000000
        #進場價格
        OrderPrice = None
        #進場數量
        OrderQty = 0
        #出場價格
        CoverPrice = None

        # 總獲利 、 交易次數
        TotalProfit = []
        TotalTreadeNum = 0 
        
        data = {
                '買進時間': [], 
                '買進原因': [],
                '買進價格': [],
                '售出時間': [],
                '售出價格': [],
                '售出原因': [],
                '數量': [],
                '獲利': []#[(CoverPrice-OrderPrice)*OrderQty*1000],
                }   
        
        #計算移動平均線
        KBar['MA'] = SMA(KBar['close'], timeperiod= 10)
        #計算乖離率
        KBar['bias'] = (KBar['close']- KBar['MA']) / KBar['MA']
        
        for i in range(len(KBar['date'])):
            Date = KBar['date'][i]
            Close = KBar['close'][i]
            Bias = KBar['bias'][i]
            LastBias = KBar['bias'][i-1]
            
            status = []
            
            if LastBias < 0 and OrderQty == 0 and i < len(KBar['date'])-1:
                #負乖離率進場
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                status = ' 負乖離率 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
            elif LastBias > 0 and OrderQty != 0 and i < len(KBar['date'])-1:
                # 正乖離率出場
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 正乖離率 '
                print( '售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 回測時間結束，則出場
            elif OrderQty != 0 and i == len(KBar['date'])-1:
                # 出場時間、價格
                CoverDate = Date
                CoverPrice = Close
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 結束 '
                print( '結束 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'盈虧:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
        result = pd.DataFrame(data) #把字典轉成DataFrame
        print(result)
        self.change_data(result, self.ui.tableWidget)
        
        #作圖
        bar = pd.DataFrame(KBar)
        bar['date'] = pd.to_datetime(bar['date'])
        bar.set_index(['date'], inplace=True)
        stock_id = "Apple"
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        add_plot =[mpf.make_addplot(bar['bias'],panel= 2,color="b")]
        mpf.plot(bar,type='candle', mav=(5,10), volume = True,figsize=(20, 10),title = stock_id, style=s,addplot=add_plot,savefig='bar_chart.png')
        self.change_plot("bar_chart.png")
        
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        plot_X = list(range(1, len(TotalProfit) + 1))
        plot_Y = np.cumsum(TotalProfit)
        ax = plt.subplot(111)           # 新增繪圖圖片
        
        ax.bar( plot_X, plot_Y )      # 繪製圖案 ( X軸物件, Y軸物件 )
        ax.ticklabel_format(style = "plain") # 設定Y軸為實數顯示，否則預設顯示為科學符號
        
        # 設定X軸間隔為1
        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        ax.xaxis.set_major_locator(loc)
        
        # 設定文字
        for x, y in zip(plot_X, plot_Y):
            text_show = int(y)
            # plt.text(X座標, Y座標, 顯示內容, 水平對齊方式, 垂直對齊方式)
            if y > 0:
                plt.text(x ,y ,text_show, ha = "center", va = "bottom")
            else:
                plt.text(x ,y ,text_show, ha = "center", va = "top") 
        
        plt.savefig("profit_chart.png")
        self.change_plot2("profit_chart.png")
        plt.clf()
        
        #計算最大資金回落
        MDD,Capital,MaxCapital = 0,0,0
        for p in TotalProfit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
            #print(MaxCapital,Capital,DD)
        #print(MDD)
        
        #平均損益
        avgprofit = sum(TotalProfit)/len(TotalProfit)
        
        #勝率
        winprofit=[]
        loseprofit=[]
        for p in TotalProfit:
            if p >=0:
                winprofit+=[p]
            if p < 0:
                loseprofit+=[p]
        #勝率
        win = len(winprofit)/(len(winprofit)+len(loseprofit))
        
        #賺賠比
        avg_win = sum(winprofit)/len(TotalProfit)
        avg_lose = sum(loseprofit)/len(TotalProfit)
        win_lose = avg_win / abs(avg_lose)
        #獲利因子
        get_money = sum(winprofit) / abs(sum(loseprofit))
        
        #夏普率
        buy = pd.DataFrame()
        buy['date'] = pd.to_datetime(result['買進時間'])
        buy['price'] = result['買進價格']
        sale = pd.DataFrame()
        sale['date'] = pd.to_datetime(result['售出時間'])
        sale['price'] = result['售出價格']
        buy_sale = pd.DataFrame()
        buy_sale = pd.concat([buy,sale],axis=0 ,ignore_index=True)
        buy_sale.index=pd.to_datetime(buy_sale.date)
        buy_sale.drop('date',axis=1,inplace=True)
        pct_change = buy_sale.pct_change()
        profit1 = pct_change.mean()
        risk = pct_change.std()
        sharpe = profit1 / (risk * ( (TotalTreadeNum*2) ** 0.5))
        
        print( '總交易次數:' , TotalTreadeNum , '總損益:', sum(TotalProfit) ,'平均損益',avgprofit,
              '勝率', win,'賺賠比' ,win_lose,'獲利因子',get_money,'夏普率',sharpe)
        dict = {'總交易次數' : [TotalTreadeNum],
                '總損益' : [sum(TotalProfit)],
                '平均損益' : [avgprofit],
                '最大資金回落' : [MDD],
                '勝率' : [win],
                '賺賠比' : [win_lose],
                '獲利因子' : [get_money],
                '夏普比率' : [sharpe]
                    }
        df = pd.DataFrame(dict)
        self.change_data(df, self.ui.tableWidget_2)
        
    def AddFilter(self, ui, KBar):
        self.ui = ui
        import pandas as pd
        import datetime
        from talib import SMA,STDDEV
        import numpy as np
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        
        
        # 初始資金
        InitCapital=1000000
        #進場價格
        OrderPrice = None
        #進場數量
        OrderQty = 0
        #出場價格
        CoverPrice = None

        # 總獲利 、 交易次數
        TotalProfit = []
        TotalTreadeNum = 0 
        
        data = {
                '買進時間': [], 
                '買進原因': [],
                '買進價格': [],
                '售出時間': [],
                '售出價格': [],
                '售出原因': [],
                '數量': [],
                '獲利': []#[(CoverPrice-OrderPrice)*OrderQty*1000],
                }   
        
        #計算短期移動平均線
        KBar['SMA'] = SMA(KBar['close'], timeperiod= 10)
        print(KBar['SMA'])
        #計算長期移動平均線
        KBar['LMA'] = SMA(KBar['close'], timeperiod= 60)
        #計算均線乖離率
        KBar['AMA'] = ( ( KBar['SMA'] - KBar['LMA'] ) / KBar['LMA'] ) 
        print(KBar['AMA'])
        #計算乖離率
        KBar['bias'] = ( (KBar['close']- KBar['SMA']) / KBar['SMA'] )
        print( KBar['bias'])
        for i in range(len(KBar['date'])):
            Date = KBar['date'][i]
            Close = KBar['close'][i]
            LastClose = KBar['close'][i-1]
            Bias = KBar['bias'][i]
            LastBias = KBar['bias'][i-1]
            AMA = KBar['AMA'][i]
            LastAMA = KBar['AMA'][i-1]
            SMA = KBar['SMA'] [i]
            LastSMA = KBar['SMA'] [i-1]
            BuyAMA = KBar['AMA'][i] < 0
            SellAMA = KBar['AMA'][i] > 0
            status = []
            
            if KBar['close'][i-1] > KBar['close'][i-11] and LastBias < -LastAMA and Bias >= AMA and OrderQty == 0 and i < len(KBar['date'])-1:
                #負乖離率由下往上穿越均線乖離時進場(負乖離過大)
                #均線上彎做多
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                status = ' 負乖離率 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
                
            if  LastClose < LastSMA and Close >= SMA*1.01 and OrderQty == 0 and i < len(KBar['date'])-1:
                #空單回補
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                # 停損價、停利價
                StopLoss = OrderPrice *0.8
                TakeProfit = OrderPrice *1.6
                status = ' 空單回補 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
                
            elif KBar['close'][i-1] < KBar['close'][i-11] and LastBias > LastAMA and Bias <= AMA and OrderQty != 0 and i < len(KBar['date'])-1:
                # 正乖離率由上往下穿越均線乖離時出場(正乖離過大)
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 正乖離率 '
                print( '售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 停損判斷
            elif OrderQty != 0 and Close < StopLoss :
                # 出場時間、價格
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 停損 '
                print( '停損 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'虧損:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
            # 停利判斷
            elif OrderQty != 0 and Close > TakeProfit   :
                # 出場時間、價格
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 停利 '
                print( '停利 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 回測時間結束，則出場
            elif OrderQty != 0 and i == len(KBar['date'])-1:
                # 出場時間、價格
                CoverDate = Date
                CoverPrice = Close
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 結束 '
                print( '結束 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'盈虧:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
        result = pd.DataFrame(data) #把字典轉成DataFrame
        print(result)
        self.change_data(result, self.ui.tableWidget)
        
        #作圖
        bar = pd.DataFrame(KBar)
        bar['date'] = pd.to_datetime(bar['date'])
        bar.set_index(['date'], inplace=True)
        stock_id = "Apple"
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        add_plot =[mpf.make_addplot(bar['bias'],panel= 2,color="b")]
        mpf.plot(bar,type='candle', mav=(5,10), volume = True,figsize=(20, 10),title = stock_id, style=s,addplot=add_plot,savefig='bar_chart.png')
        self.change_plot("bar_chart.png")
        
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        plot_X = list(range(1, len(TotalProfit) + 1))
        plot_Y = np.cumsum(TotalProfit)
        ax = plt.subplot(111)           # 新增繪圖圖片
        
        ax.bar( plot_X, plot_Y )      # 繪製圖案 ( X軸物件, Y軸物件 )
        ax.ticklabel_format(style = "plain") # 設定Y軸為實數顯示，否則預設顯示為科學符號
        
        # 設定X軸間隔為1
        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        ax.xaxis.set_major_locator(loc)
        
        # 設定文字
        for x, y in zip(plot_X, plot_Y):
            text_show = int(y)
            # plt.text(X座標, Y座標, 顯示內容, 水平對齊方式, 垂直對齊方式)
            if y > 0:
                plt.text(x ,y ,text_show, ha = "center", va = "bottom")
            else:
                plt.text(x ,y ,text_show, ha = "center", va = "top") 
        
        plt.savefig("profit_chart.png")
        self.change_plot2("profit_chart.png")
        plt.clf()
        
        #計算最大資金回落
        MDD,Capital,MaxCapital = 0,0,0
        for p in TotalProfit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
            #print(MaxCapital,Capital,DD)
        #print(MDD)
        
        #平均損益
        avgprofit = sum(TotalProfit)/len(TotalProfit)
        
        #勝率
        winprofit=[]
        loseprofit=[]
        for p in TotalProfit:
            if p >=0:
                winprofit+=[p]
            if p < 0:
                loseprofit+=[p]
        #勝率
        win = len(winprofit)/(len(winprofit)+len(loseprofit))
        
        #賺賠比
        avg_win = sum(winprofit)/len(TotalProfit)
        avg_lose = sum(loseprofit)/len(TotalProfit)
        win_lose = avg_win / abs(avg_lose)
        #獲利因子
        get_money = sum(winprofit) / abs(sum(loseprofit))
        
        #夏普率
        buy = pd.DataFrame()
        buy['date'] = pd.to_datetime(result['買進時間'])
        buy['price'] = result['買進價格']
        sale = pd.DataFrame()
        sale['date'] = pd.to_datetime(result['售出時間'])
        sale['price'] = result['售出價格']
        buy_sale = pd.DataFrame()
        buy_sale = pd.concat([buy,sale],axis=0 ,ignore_index=True)
        buy_sale.index=pd.to_datetime(buy_sale.date)
        buy_sale.drop('date',axis=1,inplace=True)
        pct_change = buy_sale.pct_change()
        profit1 = pct_change.mean()
        risk = pct_change.std()
        sharpe = profit1 / (risk * ( (TotalTreadeNum*2) ** 0.5))
        
        print( '總交易次數:' , TotalTreadeNum , '總損益:', sum(TotalProfit) ,'平均損益',avgprofit,
              '勝率', win,'賺賠比' ,win_lose,'獲利因子',get_money,'夏普率',sharpe)
        dict = {'總交易次數' : [TotalTreadeNum],
                '總損益' : [sum(TotalProfit)],
                '平均損益' : [avgprofit],
                '最大資金回落' : [MDD],
                '勝率' : [win],
                '賺賠比' : [win_lose],
                '獲利因子' : [get_money],
                '夏普比率' : [sharpe]
                    }
        df = pd.DataFrame(dict)
        self.change_data(df, self.ui.tableWidget_2)
        
    def UpAndDown(self, ui, KBar):
        self.ui = ui
        import pandas as pd
        import datetime
        from talib import SMA,STDDEV
        import numpy as np
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        
        
        # 初始資金
        InitCapital=1000000
        #進場價格
        OrderPrice = None
        #進場數量
        OrderQty = 0
        #出場價格
        CoverPrice = None

        # 總獲利 、 交易次數
        TotalProfit = []
        TotalTreadeNum = 0 
        
        data = {
                '買進時間': [], 
                '買進原因': [],
                '買進價格': [],
                '售出時間': [],
                '售出價格': [],
                '售出原因': [],
                '數量': [],
                '獲利': []#[(CoverPrice-OrderPrice)*OrderQty*1000],
                }   
        
        #計算短期移動平均線
        KBar['SMA'] = SMA(KBar['close'], timeperiod= 10)
        print(KBar['SMA'])
        #計算長期移動平均線
        KBar['LMA'] = SMA(KBar['close'], timeperiod= 60)
        #計算均線乖離率
        KBar['AMA'] = ( ( KBar['SMA'] - KBar['LMA'] ) / KBar['LMA'] ) 
        print(KBar['AMA'])
        #計算乖離率
        KBar['bias'] = ( (KBar['close']- KBar['SMA']) / KBar['SMA'] )
        print( KBar['bias'])
        for i in range(len(KBar['date'])):
            Date = KBar['date'][i]
            Close = KBar['close'][i]
            LastClose = KBar['close'][i-1]
            Bias = KBar['bias'][i]
            LastBias = KBar['bias'][i-1]
            AMA = KBar['AMA'][i]
            LastAMA = KBar['AMA'][i-1]
            SMA = KBar['SMA'] [i]
            LastSMA = KBar['SMA'] [i-1]
            status = []
            
            if LastBias < -LastAMA and Bias >= AMA and OrderQty == 0 and i < len(KBar['date'])-1:
                #負乖離率由下往上穿越均線乖離時進場(負乖離過大)
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                status = ' 負乖離率 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
                
            if  LastClose < LastSMA and Close >= SMA*1.01 and OrderQty == 0 and i < len(KBar['date'])-1:
                #空單回補
                OrderDate = KBar['date'][i+1]
                OrderPrice = KBar['open'][i+1]
                OrderQty = int(InitCapital/(Close)/1000)
                # 停損價、停利價
                StopLoss = OrderPrice *0.8
                TakeProfit = OrderPrice *1.6
                status = ' 空單回補 '
                print( '買進時間:', OrderDate.strftime('%Y/%m/%d') , '買進價格:',OrderPrice , '買進數量:' ,OrderQty )
                data['買進時間'].append(OrderDate.strftime('%Y/%m/%d'))
                data['買進原因'].append(status)
                data['買進價格'].append(OrderPrice)
                data['數量'].append(OrderQty)
                
            elif LastBias > LastAMA and Bias <= AMA and OrderQty != 0 and i < len(KBar['date'])-1:
                # 正乖離率由上往下穿越均線乖離時出場(正乖離過大)
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 正乖離率 '
                print( '售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 停損判斷
            elif OrderQty != 0 and Close < StopLoss :
                # 出場時間、價格
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 停損 '
                print( '停損 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'虧損:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
            # 停利判斷
            elif OrderQty != 0 and Close > TakeProfit   :
                # 出場時間、價格
                CoverDate = KBar['date'][i+1]
                CoverPrice = KBar['open'][i+1]
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 停利 '
                print( '停利 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'獲利:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
                
            # 回測時間結束，則出場
            elif OrderQty != 0 and i == len(KBar['date'])-1:
                # 出場時間、價格
                CoverDate = Date
                CoverPrice = Close
                # 績效紀錄
                Profit = (CoverPrice-OrderPrice)*OrderQty*1000
                TotalProfit += [Profit]
                TotalTreadeNum += 1
                # InitCapital += Profit
                # 下單數量歸零，重新進場
                OrderQty = 0
                status = ' 結束 '
                print( '結束 售出時間:', CoverDate.strftime('%Y/%m/%d') , '售出價格:' , CoverPrice ,'盈虧:',Profit  )
                data['售出時間'].append(CoverDate.strftime('%Y/%m/%d'))
                data['售出原因'].append(status)
                data['售出價格'].append(CoverPrice)
                data['獲利'].append(Profit)
        result = pd.DataFrame(data) #把字典轉成DataFrame
        print(result)
        self.change_data(result, self.ui.tableWidget)
        
        #作圖
        bar = pd.DataFrame(KBar)
        bar['date'] = pd.to_datetime(bar['date'])
        bar.set_index(['date'], inplace=True)
        stock_id = "6547"
        mc = mpf.make_marketcolors(up='r', down='g', inherit=True)
        s  = mpf.make_mpf_style(base_mpf_style='yahoo', marketcolors=mc)
        add_plot =[mpf.make_addplot(bar['bias'],panel= 2,color="b")]
        mpf.plot(bar,type='candle', mav=(5,10), volume = True,figsize=(20, 10),title = stock_id, style=s,addplot=add_plot,savefig='bar_chart.png')
        self.change_plot("bar_chart.png")
        
        import matplotlib.pyplot as plt # 匯出績效圖表
        import matplotlib.ticker as plticker
        plot_X = list(range(1, len(TotalProfit) + 1))
        plot_Y = np.cumsum(TotalProfit)
        ax = plt.subplot(111)           # 新增繪圖圖片
        
        ax.bar( plot_X, plot_Y )      # 繪製圖案 ( X軸物件, Y軸物件 )
        ax.ticklabel_format(style = "plain") # 設定Y軸為實數顯示，否則預設顯示為科學符號
        
        # 設定X軸間隔為1
        loc = plticker.MultipleLocator(base=1.0) # this locator puts ticks at regular intervals
        ax.xaxis.set_major_locator(loc)
        
        # 設定文字
        for x, y in zip(plot_X, plot_Y):
            text_show = int(y)
            # plt.text(X座標, Y座標, 顯示內容, 水平對齊方式, 垂直對齊方式)
            if y > 0:
                plt.text(x ,y ,text_show, ha = "center", va = "bottom")
            else:
                plt.text(x ,y ,text_show, ha = "center", va = "top") 
        
        plt.savefig("profit_chart.png")
        self.change_plot2("profit_chart.png")
        plt.clf()
        
        #計算最大資金回落
        MDD,Capital,MaxCapital = 0,0,0
        for p in TotalProfit:
            Capital += p
            MaxCapital = max(MaxCapital,Capital)
            DD = MaxCapital - Capital
            MDD = max(MDD,DD)
            #print(MaxCapital,Capital,DD)
        #print(MDD)
        
        #平均損益
        avgprofit = sum(TotalProfit)/len(TotalProfit)
        
        #勝率
        winprofit=[]
        loseprofit=[]
        for p in TotalProfit:
            if p >=0:
                winprofit+=[p]
            if p < 0:
                loseprofit+=[p]
        #勝率
        win = len(winprofit)/(len(winprofit)+len(loseprofit))
        
        #賺賠比
        avg_win = sum(winprofit)/len(TotalProfit)
        avg_lose = sum(loseprofit)/len(TotalProfit)
        win_lose = avg_win / abs(avg_lose)
        #獲利因子
        get_money = sum(winprofit) / abs(sum(loseprofit))
        
        #夏普率
        buy = pd.DataFrame()
        buy['date'] = pd.to_datetime(result['買進時間'])
        buy['price'] = result['買進價格']
        sale = pd.DataFrame()
        sale['date'] = pd.to_datetime(result['售出時間'])
        sale['price'] = result['售出價格']
        buy_sale = pd.DataFrame()
        buy_sale = pd.concat([buy,sale],axis=0 ,ignore_index=True)
        buy_sale.index=pd.to_datetime(buy_sale.date)
        buy_sale.drop('date',axis=1,inplace=True)
        pct_change = buy_sale.pct_change()
        profit1 = pct_change.mean()
        risk = pct_change.std()
        sharpe = profit1 / (risk * ( (TotalTreadeNum*2) ** 0.5))
        
        print( '總交易次數:' , TotalTreadeNum , '總損益:', sum(TotalProfit) ,'平均損益',avgprofit,
              '勝率', win,'賺賠比' ,win_lose,'獲利因子',get_money,'夏普率',sharpe)
        dict = {'總交易次數' : [TotalTreadeNum],
                '總損益' : [sum(TotalProfit)],
                '平均損益' : [avgprofit],
                '最大資金回落' : [MDD],
                '勝率' : [win],
                '賺賠比' : [win_lose],
                '獲利因子' : [get_money],
                '夏普比率' : [sharpe]
                    }
        df = pd.DataFrame(dict)
        self.change_data(df, self.ui.tableWidget_2)
                
    def change_plot(self, plot_path):
        # 根據lineEdit 中的文字，呼叫 yF_Kbar 製作 K 線圖
        self.ui.label_3.setPixmap(QtGui.QPixmap("bar_chart.png")) # label 置換圖片
        
    def change_plot2(self, plot_path):
        # 根據lineEdit 中的文字， 製作 績效圖
        self.ui.label_5.setPixmap(QtGui.QPixmap("profit_chart.png")) # label 置換圖片
        
    def change_data(self, df, target):
        columns_num = df.shape[1] # DataFrame 的 欄位數
        index_num = df.shape[0] # DataFrame 的 列數
        df_columns = df.columns # DataFrame 的 欄位名稱
        df_index = df.index # DataFrame 的 索引列表
        
        target.setColumnCount(columns_num) # 修改 Table Wedget 的欄位數
        target.setRowCount(index_num) # 修改 Table Wedget 的列數
        
        _translate = QtCore.QCoreApplication.translate
        
        # 修改欄位相關資訊
        for c in range(columns_num):
            item = QtWidgets.QTableWidgetItem()
            target.setHorizontalHeaderItem(c, item) # 依據欄位列表依序建構欄位
            
            item = target.horizontalHeaderItem(c) # 選取該欄位
            item.setText(_translate("MainWindow", df_columns[c])) # 修改欄位標題文字
             
        for i in range(index_num):
            item = QtWidgets.QTableWidgetItem()
            target.setVerticalHeaderItem(i, item) # 依據索引列表依序建構欄位
            
            item = target.verticalHeaderItem(i) # 選取該索引
            item.setText(_translate("MainWindow", str(df_index[i]) )) # 修改索引標題文字
            
        for c in range(columns_num): # 走訪欄位
            for i in range(index_num): # 走訪索引
                item = QtWidgets.QTableWidgetItem()
                target.setItem(i, c, item) # 建構儲存格

                item = target.item(i, c) # 選取儲存格
                item.setText(_translate("MainWindow", str(df.iloc[i, c]))) # 修改儲存格文字
