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

  useEffect(() => {
    const fetchStocks = async () => {
      try {
        const response = await axios.get('http://localhost:5000/stocks');
        setStocks(response.data.stocks);
        setError('');
      } catch (error) {
        console.error('Error fetching stocks:', error);
        setError('無法獲取背離股票清單，請檢查後端服務');
      }
    };
    fetchStocks();
  }, []);

  const fetchStockChart = async () => {
    if (!selectedStockId) {
      setError('請輸入股票代碼');
      return;
    }
    try {
      const response = await axios.get(`http://localhost:5000/stock/${selectedStockId}`);
      setChartUrl(response.data.chartUrl);
      setError('');
    } catch (error) {
      console.error('Error fetching stock chart:', error);
      setError('無法獲取圖表，請確認股票代碼是否正確');
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>台股 MACD 背離分析</h1>
      {error && <p style={{ color: 'red' }}>{error}</p>}
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
          <p>正在載入股票清單...</p>
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
