import React from 'react';
import ReactDOM from 'react-dom/client'; // 正確導入
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root')); // 創建 root
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
