import React, { useState, useEffect } from 'react';
import { Container, Typography, LinearProgress, Grid, Card, CardContent, Button } from '@mui/material';
import { Link } from 'react-router-dom';
import axios from 'axios';

const StockList = () => {
  const [stocks, setStocks] = useState([]);
  const [progress, setProgress] = useState(0);
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const stocksResponse = await axios.get('https://stock-backend-XXXXX-uc.a.run.app/stocks');
        setStocks(stocksResponse.data.stocks);

        const progressResponse = await axios.get('https://stock-backend-XXXXX-uc.a.run.app/progress');
        setProgress(progressResponse.data.progress);
        setIsRunning(progressResponse.data.is_running);
      } catch (error) {
        console.error('獲取數據失敗', error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000); // 每5秒更新
    return () => clearInterval(interval);
  }, []);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        股票列表
      </Typography>
      {isRunning && (
        <Box sx={{ mb: 4 }}>
          <Typography variant="body1">分析進度：{progress}%</Typography>
          <LinearProgress variant="determinate" value={progress} />
        </Box>
      )}
      <Grid container spacing={3}>
        {stocks.map(stock => (
          <Grid item xs={12} sm={6} md={4} key={stock.stockId}>
            <Card>
              <CardContent>
                <Typography variant="h6">{stock.stockId}</Typography>
                <Typography variant="body2" color="text.secondary">
                  背離日期: {stock.divergentDates.join(', ')}
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
    </Container>
  );
};

export default StockList;