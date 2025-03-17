import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

interface Stock {
  stockId: string;
  divergentDates: string[];
}

const App: React.FC = () => {
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [selectedStockId, setSelectedStockId] = useState('');
  const [chartUrl, setChartUrl] = useState('');
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const backendUrl = 'https://bullishmacddivergence-b4738fb587c2.herokuapp.com/';

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await axios.get(`${backendUrl}/stocks`);
        setStocks(response.data.stocks);
        setError('');
      } catch (error: any) {
        console.error('Error fetching stocks:', error.message);
        setError(`無法獲取背離股票清單：${error.message}`);
      }
    };

    const fetchProgress = async () => {
      try {
        const response = await axios.get(`${backendUrl}/progress`);
        setProgress(response.data.progress);
        setIsRunning(response.data.is_running);
      } catch (error: any) {
        console.error('Error fetching progress:', error.message);
      }
    };

    fetchStocks();
    fetchProgress();

    // 每 2 秒輪詢一次
    const interval = setInterval(() => {
      fetchStocks();
      fetchProgress();
    }, 2000);

    return () => clearInterval(interval); // 清理間隔計時器
  }, []);

  const fetchStockChart = async () => {
    if (!selectedStockId) {
      setError('請輸入股票代碼');
      return;
    }
    try {
      const response = await axios.get(`${backendUrl}/stock/${selectedStockId}`);
      setChartUrl(`${backendUrl}${response.data.chartUrl}`);
      setError('');
    } catch (error: any) {
      console.error('Error fetching stock chart:', error.message);
      setError(`無法獲取圖表：${error.message}`);
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>台股 MACD 背離分析</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {isRunning && <p>分析進度：{progress}%</p>}
      <div style={{ marginBottom: '20px' }}>
        <h3>背離股票清單</h3>
        {stocks.length > 0 ? (
          <table style={{ width: '400px', borderCollapse: 'collapse', marginBottom: '20px' }}>
            <thead>
              <tr>
                <th style={{ border: '1px solid gray', padding: '5px' }}>股票代碼</th>
                <th style={{ border: '1px solid gray', padding: '5px' }}>背離日期</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((stock) => (
                <tr key={stock.stockId}>
                  <td style={{ border: '1px solid gray', padding: '5px' }}>{stock.stockId}</td>
                  <td style={{ border: '1px solid gray', padding: '5px' }}>
                    {stock.divergentDates.join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>{isRunning ? '正在分析股票，請稍候...' : '正在載入股票清單...'}</p>
        )}
        <input
          type="text"
          value={selectedStockId}
          onChange={(e) => setSelectedStockId(e.target.value)}
          placeholder="輸入股票代碼（例如 2330）"
          style={{ width: '300px', height: '40px', marginRight: '10px' }}
        />
        <button onClick={fetchStockChart} style={{ height: '40px' }}>
          查看 K 線圖
        </button>
      </div>
      <div>
        {chartUrl ? (
          <img src={chartUrl} alt="Stock Chart" style={{ width: '1000px' }} />
        ) : (
          <p>請選擇股票代碼以查看 K 線圖</p>
        )}
      </div>
    </div>
  );
};

export default App;

//npm start