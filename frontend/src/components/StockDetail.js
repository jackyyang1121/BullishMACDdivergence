import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Container, Typography, Box, Card, CardContent } from '@mui/material';
import axios from 'axios';

const StockDetail = () => {
  const { stockId } = useParams();
  const [chartUrl, setChartUrl] = useState('');
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`bullishmacddivergence-456915.web.app/stock/${stockId}`)
      .then(response => {
        setChartUrl(`bullishmacddivergence-456915.web.app${response.data.chartUrl}`);
      })
      .catch(err => {
        setError('無法獲取股票數據');
        console.error(err);
      });
  }, [stockId]);

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom sx={{ mt: 4 }}>
        股票詳情 - {stockId}
      </Typography>
      {error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <Card>
          <CardContent>
            {chartUrl ? (
              <Box sx={{ textAlign: 'center' }}>
                <img src={chartUrl} alt={`${stockId} 分析圖表`} style={{ maxWidth: '100%' }} />
              </Box>
            ) : (
              <Typography>正在載入圖表...</Typography>
            )}
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default StockDetail;