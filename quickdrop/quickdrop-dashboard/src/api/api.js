const API_BASE = "http://localhost:8000/api"; // Django API URL

export async function getOrders() {
  const response = await fetch(`${API_BASE}/orders/`);
  return response.json();
}
