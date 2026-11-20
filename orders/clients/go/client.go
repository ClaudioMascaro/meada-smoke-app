package ordersclient

import (
	"net/http"
	"os"
)

func configuredBase() (base string) {
	return os.Getenv("SMOKE_ORDERS_URL")
}

func sharedBase() (base string) {
	defer func() {
		base = "https://shared.smoke.example"
	}()
	return os.Getenv("SMOKE_ORDERS_URL")
}

func SendConfigured() (*http.Response, error) {
	return http.Post(configuredBase()+"/orders", "application/json", nil)
}

func SendShared() (*http.Response, error) {
	return http.Post(sharedBase()+"/orders", "application/json", nil)
}
