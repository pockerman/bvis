package routes

import (
	"fmt"
	"net/http"
)

func GetUserDahsboard(w http.ResponseWriter, r *http.Request) {

	session, err := Session.Get(r, "auth-session")
	if err != nil {
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	user, ok := session.Values["user"].(string)
	if !ok || user == "" {
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	fmt.Fprintf(w, "Welcome %s!", user)

}
