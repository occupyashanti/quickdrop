import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Dashboard from "./pages/Dashboard";
import Orders from "./pages/Orders";
import Earnings from "./pages/Earnings";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";
import "./App.css";
import "./styles/global.css";

function App() {
  return (
    <Router> {/* Ensure Router wraps everything */}
      <div className="dashboard-container">
        <Sidebar /> {/* Sidebar must be inside Router */}
        <main className="content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/earnings" element={<Earnings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
