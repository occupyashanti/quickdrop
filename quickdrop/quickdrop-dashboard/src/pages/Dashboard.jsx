import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Home from "../pages/Home";
import Orders from "../pages/Orders";
import Earnings from "../pages/Earnings";
import Profile from "../pages/Profile";
import Settings from "../pages/Settings";
import "../App.css";

function App() {
  return (
    
      <div className="dashboard-container">
        <Sidebar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/earnings" element={<Earnings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    
  );
}

export default App;
