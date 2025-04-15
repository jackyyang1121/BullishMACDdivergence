import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
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
      <Switch>
        <Route exact path="/" component={HomePage} />
        <Route path="/stocks" component={StockList} />
        <Route path="/stock/:stockId" component={StockDetail} />
      </Switch>
    </Router>
  );
}

export default App;
