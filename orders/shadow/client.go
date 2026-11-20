package shadow

import (
	"net/http"
	"os"
)

type Client struct {
	os string
}

func New() *Client {
	return &Client{os: "linux"}
}

func (c *Client) CreateOrder() (*http.Request, error) {
	return http.NewRequest(http.MethodPost, os.Getenv("SMOKE_ORDERS_URL")+"/orders", nil)
}

func platform(os string) string {
	return os
}
