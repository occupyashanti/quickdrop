import React from "react";

function Home() {
  return (
    <section>
      <h1>Dashboard Overview</h1>
      <div className="overview">
        <div className="card">📦 Deliveries: 12</div>
        <div className="card">💰 Earnings: $450</div>
        <div className="card">⏳ Pending Orders: 5</div>
      </div>
    </section>
  );
}

export default Home;
