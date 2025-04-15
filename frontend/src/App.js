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
        <Route exact path="/" element={<HomePage />} /> {/* 修正：使用 JSX */}
        <Route path="/stocks" element={<StockList />} /> {/* 修正：使用 JSX */}
        <Route path="/stock/:stockId" element={<StockDetail />} /> {/* 修正：使用 JSX */}
      </Routes>
    </Router>
  );
}

export default App;