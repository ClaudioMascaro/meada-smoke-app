using System;
using System.Net.Http;
using System.Threading.Tasks;

sealed class OrdersClient {
    private readonly HttpClient http = new HttpClient();

    private string OrdersBase() => Environment.GetEnvironmentVariable("SMOKE_ORDERS_URL")!;

    public Task<HttpResponseMessage> SendOrder() {
        return http.PostAsync(OrdersBase() + "/orders", null);
    }
}
