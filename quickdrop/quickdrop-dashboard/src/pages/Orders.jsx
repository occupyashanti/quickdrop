import { useEffect, useState } from "react";
import { getOrders } from "../api/api"; // Ensure you have an API function

function Orders() {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    getOrders().then(setOrders);
  }, []);

  return (
    <section>
      <h1>Orders</h1>
      <ul>
        {orders.map((order) => (
          <li key={order.id}>{order.description} - {order.status}</li>
        ))}
      </ul>
    </section>
  );
}

export default Orders;
