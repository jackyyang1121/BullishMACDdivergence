from flask import Flask, jsonify, send_from_directory
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import pandas_ta as ta
import warnings
import mplfinance as mpf
import matplotlib.pyplot as plt
from FinMind.data import DataLoader

warnings.filterwarnings('ignore')

app = Flask(__name__)

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
        return df[['日期', '開盤價', '最高價', '最低價', '收盤價', '成交量']]
    except Exception as e:
        print(f"無法獲取股票 {stock_id} 的數據：{e}")
        return None

# 計算技術指標
def calculate_indicators(df):
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

# 檢測 MACD 背離
def detect_macd_divergence(df, lookback_days=180, recent_days=30):
    if len(df) < lookback_days:
        print(f"股票數據少於 {lookback_days} 天，無法檢測背離")
        return pd.DataFrame()
    df['Price_Low'] = df['最低價'].rolling(window=lookback_days, min_periods=1).min()
    df['MACD_Low'] = df['Histogram'].rolling(window=lookback_days, min_periods=1).min()
    df['Bullish_Divergence'] = (df['最低價'] == df['Price_Low']) & (df['Histogram'] > df['MACD_Low'])
    recent_date = df['日期'].max() - timedelta(days=recent_days)
    divergent_rows = df[(df['Bullish_Divergence']) & (df['日期'] >= recent_date)]
    return divergent_rows

# 繪製股票圖表
def plot_stock_chart(df, stock_id, divergent_data, save_path):
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
        mpf.make_addplot(df_plot['Histogram'], panel=1, type='bar', color='dimgray'),
        mpf.make_addplot(df_plot['Low'].where(df_plot.index.isin(divergent_data['日期']), float('nan')), 
                        panel=0, type='scatter', markersize=100, marker='^', color='green', label='Bullish Divergence')
    ]
    mpf.plot(
        df_plot,
        type='candle',
        volume=True,
        addplot=apds,
        style=s,
        title=f'\n{stock_id} 股票分析圖 (綠色三角標記為MACD看漲背離點)',
        figsize=(15, 10),
        panel_ratios=(6,2),
        savefig=save_path
    )
    plt.close()

# 獲取背離股票清單
@app.route('/stocks')
def get_divergent_stocks():
    csv_path = 'macd_divergent_stocks.csv'
    if os.path.exists(csv_path):
        divergent_stocks = pd.read_csv(csv_path)
        return jsonify({
            'stocks': divergent_stocks.to_dict(orient='records')
        })
    
    # 如果 CSV 不存在，重新分析
    api = DataLoader()
    stock_list = api.taiwan_stock_info()
    stock_list = stock_list[(stock_list['type'] == 'twse') & 
                            (stock_list['industry_category'] != 'ETF') & 
                            (~stock_list['industry_category'].str.contains('基金|特別股', na=False)) & 
                            (~stock_list['stock_id'].str.match(r'^01\d{2}T$'))]
    stock_ids = stock_list['stock_id'].tolist()[:10]  # 可加[:10]測試
    
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    
    divergent_stocks = []
    chart_folder = "stock_charts"
    if not os.path.exists(chart_folder):
        os.makedirs(chart_folder)
    
    for stock_id in stock_ids:
        stock_data = fetch_historical_data(stock_id, start_date, end_date)
        if stock_data is None or len(stock_data) < 180:
            continue
        stock_data = calculate_indicators(stock_data)
        divergent_data = detect_macd_divergence(stock_data)
        if not divergent_data.empty:
            divergent_stocks.append({
                'stockId': stock_id,
                'divergentDates': [date.strftime('%Y-%m-%d') for date in divergent_data['日期']]
            })
            save_path = os.path.join(chart_folder, f'{stock_id}_analysis.png')
            plot_stock_chart(stock_data.tail(180), stock_id, divergent_data, save_path)
    
    if divergent_stocks:
        pd.DataFrame(divergent_stocks).to_csv(csv_path, index=False, encoding='utf-8-sig')
    return jsonify({'stocks': divergent_stocks})

# 獲取單一股票圖表
@app.route('/stock/<stock_id>')
def get_stock_data(stock_id):
    start_date = (datetime.today() - timedelta(days=365)).strftime('%Y-%m-%d')
    end_date = datetime.today().strftime('%Y-%m-%d')
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
    app.run(host='0.0.0.0', port=5000)

#python 台股MACD背離graph.py