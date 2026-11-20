package evidence

import (
	"net/http"
	"os"
)

type Client struct{}

func (Client) ordersBase() string { return os.Getenv("SMOKE_ORDERS_URL") }

func (c Client) ViaMethod() {
	_, _ = http.Post(c.ordersBase()+"/orders", "application/json", nil)
}

func post(env, path string) {
	_, _ = http.Post(os.Getenv(env)+path, "application/json", nil)
}

func ViaParameter() { post("SMOKE_ORDERS_URL", "/orders") }

func ViaUnknownParameter(name string) { post(name, "/orders") }

func Relative() { _, _ = http.Post("/orders", "application/json", nil) }

func QueryAppend(filter string) {
	path := "/orders"
	if filter != "" {
		path += "?status=" + filter
	}
	_, _ = http.Post(os.Getenv("SMOKE_ORDERS_URL")+path, "application/json", nil)
}

func QuerySuffix(filter string) {
	query := ""
	if filter != "" {
		query = "?status=" + filter
	}
	_, _ = http.Post(os.Getenv("SMOKE_ORDERS_URL")+"/orders"+query, "application/json", nil)
}

func PathSuffix(id string) {
	path := "/orders"
	if id != "" {
		path += "/" + id
	}
	_, _ = http.Post(os.Getenv("SMOKE_ORDERS_URL")+path, "application/json", nil)
}
