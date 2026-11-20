package neutral

import (
	"net/http"
	"os"
)

type Client struct {
	label string
}

func New() *Client {
	return &Client{label: "orders"}
}

func (c *Client) CreateOrder() (*http.Request, error) {
	return http.NewRequest(http.MethodPost, os.Getenv("SMOKE_ORDERS_URL")+"/orders", nil)
}
