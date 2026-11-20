import org.springframework.web.client.RestTemplate;

final class OrdersClient {
    private final RestTemplate http = new RestTemplate();

    private String ordersBase() {
        return System.getenv("SMOKE_ORDERS_URL");
    }

    String sendOrder() {
        return http.postForObject(ordersBase() + "/orders", null, String.class);
    }
}
