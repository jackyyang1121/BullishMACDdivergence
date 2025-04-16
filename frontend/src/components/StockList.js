import React, { useState, useEffect } from 'react';
import { Container, Typography, LinearProgress, Grid, Card, CardContent, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Box } from '@mui/system';

const StockList = () => {
  const [stocks, setStocks] = useState([]);
  const [progress, setProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const stocksResponse = await axios.get('https://bullishmacddivergence-537561792277.asia-east1.run.app/stocks');
        setStocks(stocksResponse.data.stocks || []);
        const progressResponse = await axios.get('https://bullishmacddivergence-537561792277.asia-east1.run.app/progress');
        setProgress(progressResponse.data.progress || 0);
        setIsRunning(progressResponse.data.is_running || false);
      } catch (error) {
        console.error('獲取數據失敗', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        股票列表
      </Typography>

      {/* 當分析正在進行時顯示進度條 */}
      {isRunning ? (
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1">分析正在進行中，請稍候...</Typography>
          <LinearProgress variant="determinate" value={progress} />
          <Typography variant="body2">進度：{progress}%</Typography>
        </Box>
      ) : stocks.length === 0 ? (
        <Typography variant="body1" sx={{ mt: 4 }}>
          目前沒有可顯示的股票數據。可能正在分析中，請稍後再試。
        </Typography>
      ) : (
        <Grid container spacing={3}>
          {stocks.map((stock) => (
            <Grid item xs={12} sm={6} md={4} key={stock.stockId}>
              <Card>
                <CardContent>
                  <Typography variant="h6">{stock.stockId}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    背離日期: {stock.divergentDates?.join(', ') || '無數據'}
                  </Typography>
                  <Button
                    component={Link}
                    to={`/stock/${stock.stockId}`}
                    variant="outlined"
                    sx={{ mt: 2 }}
                  >
                    查看詳情
                  </Button>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default StockList;