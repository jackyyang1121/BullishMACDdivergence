import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AppBar, Toolbar, Typography } from '@mui/material';
import HomePage from './components/HomePage';
import StockList from './components/StockList';
import StockDetail from './components/StockDetail';

function App() {
  return (
    <Router>
      <AppBar position="static" sx={{ mb: 4 }}>
        <Toolbar>
          <Typography variant="h6">台股 MACD 背離分析</Typography>
        </Toolbar>
      </AppBar>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stocks" element={<StockList />} />
        <Route path="/stock/:stockId" element={<StockDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
