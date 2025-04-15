from flask import Flask, jsonify, send_from_directory, redirect
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import warnings
import mplfinance as mpf
import matplotlib.pyplot as plt
import os
from FinMind.data import DataLoader
from flask_cors import CORS
from tqdm import tqdm
import threading
import gc
import numpy as np
x = np.nan


warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["https://bullishmacddivergence-456915.web.app/"],
                            "methods": ["GET", "POST", "OPTIONS"],
                            "allow_headers": ["Content-Type", "Authorization"],
                            "supports_credentials": True}})

progress = {'total': 0, 'completed': 0, 'is_running': False}

# 根路徑處理
@app.route('/')
def home():
    return jsonify({'message': 'Welcome to Bullish MACD Divergence API! Use /stocks to get the list of stocks.'})

# 抓取歷史數據
def fetch_historical_data(stock_id, start_date, end_date):
    try:
        ticker = f"{stock_id}.TW"
        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            print(f"{stock_id} 回傳空數據")
            return None
        df = df.reset_index().rename(columns={
            'Date': '日期',
            'Open': '開盤價',
            'High': '最高價',
            'Low': '最低價',
            'Close': '收盤價',
            'Volume': '成交量'
        })
        df['日期'] = pd.to_datetime(df['日期'])
        print(f"{stock_id} 獲取 {len(df)} 天數據")
        return df[['日期', '開盤價', '最高價', '最低價', '收盤價', '成交量']]
    except Exception as e:
        print(f"無法獲取股票 {stock_id} 的數據：{e}")
        return None

# 計算技術指標
def calculate_indicators(df):
    try:
        df['收盤價'] = pd.to_numeric(df['收盤價'], errors='coerce')
        df['開盤價'] = pd.to_numeric(df['開盤價'], errors='coerce')
        df['最高價'] = pd.to_numeric(df['最高價'], errors='coerce')
        df['最低價'] = pd.to_numeric(df['最低價'], errors='coerce')
        df['成交量'] = pd.to_numeric(df['成交量'], errors='coerce')
        df.dropna(subset=['收盤價', '開盤價', '最高價', '最低價', '成交量'], inplace=True)
        macd = df.ta.macd(close='收盤價', fast=12, slow=26, signal=9)
        df['MACD'] = macd['MACD_12_26_9']
        df['Signal'] = macd['MACDs_12_26_9']
        df['Histogram'] = macd['MACDh_12_26_9']
        return df
    except Exception as e:
        print(f"計算技術指標失敗：{e}")
        return df

# 檢測 MACD 背離
def detect_macd_divergence(df, lookback_days=180, recent_days=30):
    if len(df) < lookback_days:
        print(f"股票數據少於 {lookback_days} 天，無法檢測背離")
        return pd.DataFrame(columns=df.columns).fillna(x)
    try:
        df['Price_Low'] = df['最低價'].rolling(window=lookback_days, min_periods=1).min()
        df['MACD_Low'] = df['Histogram'].rolling(window=lookback_days, min_periods=1).min()
        df['Bullish_Divergence'] = (df['最低價'] == df['Price_Low']) & (df['Histogram'] > df['MACD_Low'])
        recent_date = df['日期'].max() - timedelta(days=recent_days)
        divergent_rows = df[(df['Bullish_Divergence']) & (df['日期'] >= recent_date)]
        print(f"檢測到 {len(divergent_rows)} 個背離點")
        return divergent_rows
    except Exception as e:
        print(f"檢測 MACD 背離失敗：{e}")
        return pd.DataFrame()

# 繪製股票圖表
def plot_stock_chart(df, stock_id, divergent_data, save_path):
    try:
        df_plot = df.copy()
        df_plot.set_index('日期', inplace=True)
        df_plot = df_plot.rename(columns={
            '開盤價': 'Open',
            '最高價': 'High',
            '最低價': 'Low',
            '收盤價': 'Close',
            '成交量': 'Volume'
        })
        
        mc = mpf.make_marketcolors(up='red', down='green', edge='inherit', wick='inherit', volume='inherit')
        s = mpf.make_mpf_style(marketcolors=mc)
        
        apds = [
            mpf.make_addplot(df_plot['MACD'], panel=1, color='blue', title='MACD'),
            mpf.make_addplot(df_plot['Signal'], panel=1, color='orange'),
            mpf.make_addplot(df_plot['Histogram'], panel=1, type='bar', color='dimgray')
        ]
        
        if not divergent_data.empty:
            scatter_data = df_plot['Low'].where(df_plot.index.isin(divergent_data['日期']), x)
            apds.append(mpf.make_addplot(scatter_data, panel=0, type='scatter', markersize=100, marker='^', color='green', label='Bullish Divergence'))
        
        mpf.plot(
            df_plot,
            type='candle',
            volume=True,
            addplot=apds,
            style=s,
            title=f'\n{stock_id} 股票分析圖 (綠色三角標記為MACD看漲背離點)',
            figsize=(15, 10),
            panel_ratios=(6,2),
            xrotation=45,
            datetime_format='%Y-%m-%d',
            tight_layout=True,
            savefig=save_path
        )
        plt.close()
        if os.path.exists(save_path):
            print(f"圖表 {save_path} 已存在")
        else:
            print(f"圖表 {save_path} 生成失敗")
    except Exception as e:
        print(f"繪製 {stock_id} 圖表失敗：{e}")

# 背景分析股票
def analyze_stocks_in_background():
    global progress
    csv_path = 'macd_divergent_stocks.csv'
    if os.path.exists(csv_path):
        print(f"{csv_path} 已存在，跳過重新分析")
        return
    
    print("CSV 不存在，開始重新分析...")
    try:
        api = DataLoader()
        stock_list = api.taiwan_stock_info()
        stock_list = stock_list[(stock_list['type'] == 'twse') & 
                                (stock_list['industry_category'] != 'ETF') & 
                                (~stock_list['industry_category'].str.contains('基金|特別股', na=False)) & 
                                (~stock_list['stock_id'].str.match(r'^01\d{2}T$'))]
        stock_ids = stock_list['stock_id'].tolist()
        print(f"從 FinMind 獲取 {len(stock_ids)} 檔股票清單")
    except Exception as e:
        print(f"獲取股票清單失敗：{e}")
        return
    
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    divergent_stocks = []
    chart_folder = "stock_charts"
    if not os.path.exists(chart_folder):
        os.makedirs(chart_folder)
    
    batch_size = 200
    progress['total'] = len(stock_ids)
    progress['completed'] = 0
    progress['is_running'] = True
    
    for i in range(0, len(stock_ids), batch_size):
        batch_ids = stock_ids[i:i + batch_size]
        print(f"處理批次 {i // batch_size + 1}，股票數量：{len(batch_ids)}")
        for stock_id in tqdm(batch_ids, desc="分析股票"):
            try:
                stock_data = fetch_historical_data(stock_id, start_date, end_date)
                if stock_data is None or len(stock_data) < 180:
                    print(f"{stock_id} 數據不足，跳過")
                else:
                    stock_data = calculate_indicators(stock_data)
                    divergent_data = detect_macd_divergence(stock_data)
                    if not divergent_data.empty:
                        divergent_stocks.append({
                            'stockId': stock_id,
                            'divergentDates': [date.strftime('%Y-%m-%d') for date in divergent_data['日期']]
                        })
            except Exception as e:
                print(f"處理股票 {stock_id} 時出錯：{e}")
            progress['completed'] += 1
            if progress['completed'] > progress['total']:
                progress['completed'] = progress['total']
        gc.collect()
    
    if divergent_stocks:
        try:
            pd.DataFrame(divergent_stocks).to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"已保存 {len(divergent_stocks)} 檔背離股票到 {csv_path}")
        except Exception as e:
            print(f"保存 CSV 失敗：{e}")
    else:
        print("未檢測到背離股票")
    progress['is_running'] = False

@app.route('/stocks')
def get_divergent_stocks():
    global progress
    csv_path = 'macd_divergent_stocks.csv'
    if os.path.exists(csv_path):
        try:
            divergent_stocks = pd.read_csv(csv_path)
            divergent_stocks = divergent_stocks.rename(columns={'股票代碼': 'stockId', '背離日期': 'divergentDates'})
            divergent_stocks['divergentDates'] = divergent_stocks['divergentDates'].apply(
                lambda x: [pd.Timestamp(date).strftime('%Y-%m-%d') for date in eval(x)] if isinstance(x, str) and x.startswith('[') else x
            )
            print(f"從 {csv_path} 載入 {len(divergent_stocks)} 檔股票")
            return jsonify({'stocks': divergent_stocks.to_dict(orient='records')})
        except Exception as e:
            print(f"讀取 CSV 失敗：{e}")
            return jsonify({'stocks': []})
    
    if not progress['is_running']:
        thread = threading.Thread(target=analyze_stocks_in_background)
        thread.start()
    return jsonify({'stocks': []})

@app.route('/progress')
def get_progress():
    global progress
    if progress['total'] == 0:
        return jsonify({'progress': 0, 'is_running': False})
    percentage = (progress['completed'] / progress['total']) * 100
    return jsonify({'progress': min(round(percentage, 2), 100), 'is_running': progress['is_running']})

@app.route('/stock/<stock_id>')
def get_stock_data(stock_id):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    stock_data = fetch_historical_data(stock_id, start_date, end_date)
    if stock_data is None or len(stock_data) < 180:
        return jsonify({'error': '數據不足或無法獲取'}), 404
    
    stock_data = calculate_indicators(stock_data)
    divergent_data = detect_macd_divergence(stock_data)
    
    chart_folder = "stock_charts"
    if not os.path.exists(chart_folder):
        os.makedirs(chart_folder)
    chart_path = os.path.join(chart_folder, f'{stock_id}_analysis.png')
    plot_stock_chart(stock_data.tail(180), stock_id, divergent_data, chart_path)
    
    chart_url = f"/charts/{stock_id}_analysis.png"
    return jsonify({'chartUrl': chart_url})

@app.route('/charts/<filename>')
def serve_chart(filename):
    return send_from_directory('stock_charts', filename)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
#執行 python app.py