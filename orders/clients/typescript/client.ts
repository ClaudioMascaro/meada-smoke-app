function ordersBase() {
  return process.env.SMOKE_ORDERS_URL;
}

export function sendOrder() {
  return fetch(ordersBase() + "/orders", { method: "POST" });
}
