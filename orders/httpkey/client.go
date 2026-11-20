package httpkey

import (
	"net/http"
	"os"
)

type Client struct {
	http *http.Client
}

func New() *Client {
	return &Client{http: http.DefaultClient}
}

func (c *Client) CreateOrder() (*http.Request, error) {
	return http.NewRequest(http.MethodPost, os.Getenv("SMOKE_ORDERS_URL")+"/orders", nil)
}
