import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './store';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Analysis from './pages/Analysis';
import Users from './pages/Users';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/analysis" element={<Analysis />} />
            <Route path="/users" element={<Users />} />
          </Routes>
        </div>
      </Router>
    </Provider>
  );
}

export default App;