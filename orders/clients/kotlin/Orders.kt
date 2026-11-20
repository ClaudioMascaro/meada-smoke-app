import org.springframework.web.client.RestTemplate

class KotlinOrders(private val http: RestTemplate) {
    private fun ordersBase(): String = System.getenv("SMOKE_ORDERS_URL")

    fun sendOrder(): String? {
        return http.postForObject(ordersBase() + "/orders", null, String::class.java)
    }
}
