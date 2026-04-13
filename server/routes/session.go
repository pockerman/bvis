package routes

import (
	"os"

	"github.com/gorilla/sessions"
)

// better fetch everything from the environment
var Session = sessions.NewCookieStore([]byte(os.Getenv("SESSION_KEY")))
