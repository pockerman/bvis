package routes

import (
	"crypto/rand"
	"encoding/hex"
	"net/http"

	log "github.com/sirupsen/logrus"
)

func printRequestPath(r *http.Request) {
	log.Infof("Serving %s", r.URL.Path)
}

func generateSessionID() (string, error) {
	b := make([]byte, 32) // 256-bit
	_, err := rand.Read(b)
	if err != nil {
		return "", err
	}
	return hex.EncodeToString(b), nil
}
