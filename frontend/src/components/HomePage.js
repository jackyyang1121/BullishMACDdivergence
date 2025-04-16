import React, { useState, useEffect } from 'react';
import { Container, Typography, Box } from '@mui/material';
import axios from 'axios';

const HomePage = () => {
  const [message, setMessage] = useState('');

  useEffect(() => {
    axios.get('https://bullishmacddivergence-537561792277.asia-east1.run.app/')
      .then(response => setMessage(response.data.message))
      .catch(error => console.error('獲取歡迎消息失敗', error));
  }, []);

  return (
    <Container maxWidth="md">
      <Box sx={{ textAlign: 'center', mt: 8 }}>
        <Typography variant="h4" gutterBottom>
          {message || '歡迎使用台股 MACD 背離分析工具'}
        </Typography>
        <Typography variant="body1">
          點擊「股票列表」查看最新的看漲背離股票。
        </Typography>
      </Box>
    </Container>
  );
};

export default HomePage;