use std::env;

fn orders_base() -> String {
    env::var("SMOKE_ORDERS_URL").unwrap()
}

pub async fn send_order() -> Result<reqwest::Response, reqwest::Error> {
    reqwest::Client::new()
        .post(orders_base() + "/orders")
        .send()
        .await
}
