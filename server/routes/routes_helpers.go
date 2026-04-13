package routes

import (
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"net/http"
)

func printRequestPath(r *http.Request) {
	fmt.Printf("Serving: %s\n", r.URL.Path)
}

func generateSessionID() (string, error) {
	b := make([]byte, 32) // 256-bit
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}
