import React from 'react';
import { Button, Typography, Container } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Container maxWidth="lg" sx={{ textAlign: 'center', mt: 8 }}>
      <Typography variant="h3" gutterBottom>
        歡迎使用股票分析系統
      </Typography>
      <Typography variant="body1" sx={{ mb: 4 }}>
        點擊下方按鈕查看最新的股票列表。
      </Typography>
      <Button
        component={Link}
        to="/stocks"
        variant="contained"
        color="primary"
        size="large"
      >
        股票列表
      </Button>
    </Container>
  );
};

export default HomePage;