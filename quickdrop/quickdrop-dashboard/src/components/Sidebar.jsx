import React from "react";
import { NavLink } from "react-router-dom";
import "./Sidebar.css";

const Sidebar = () => {
  return (
    <div className="sidebar">
      <h2>QuickDrop</h2>
      <nav>
        <NavLink to="/" className={({ isActive }) => (isActive ? "active" : "")}>Dashboard</NavLink>
        <NavLink to="/orders" className={({ isActive }) => (isActive ? "active" : "")}>Orders</NavLink>
        <NavLink to="/history" className={({ isActive }) => (isActive ? "active" : "")}>History</NavLink>
        <NavLink to="/payments" className={({ isActive }) => (isActive ? "active" : "")}>Payments</NavLink>
      </nav>
    </div>
  );
};
export default Sidebar;
