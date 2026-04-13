package routes

import (
	"fmt"
	"net/http"
)

func handleGETLogin(w http.ResponseWriter) {

	html := `
	<h1>Log in</h1>
		<form action="/login" method="post">
			<input type="email" name="email" />
			<input type="password" name="password" />
			<input type="submit" value="Log in" />
	</form>`
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(html))
}

func handleRedirect(w http.ResponseWriter, r *http.Request) {
	// 3. Get session
	session, err := Session.Get(r, "auth-session")
	if err != nil {
		http.Error(w, "Server error", http.StatusInternalServerError)
		return
	}

	email := r.FormValue("email")
	// 4. Store user info in session
	session.Values["user"] = email

	// 5. Save session (THIS sets the cookie)
	err = session.Save(r, w)
	if err != nil {
		http.Error(w, "Failed to save session", http.StatusInternalServerError)
		return
	}

	http.Redirect(w, r, "/dashboard", http.StatusSeeOther)

}

func handlePOSTLogin(w http.ResponseWriter, r *http.Request) {

	err := r.ParseForm()
	if err != nil {
		http.Error(w, "Error parsing form", http.StatusBadRequest)
		return
	}

	// validate data
	email := r.FormValue("email")
	password := r.FormValue("password")

	fmt.Println("Email:", email)
	fmt.Println("Password:", password)

	// ... data is ok redirect to
	// the user dashboard
	handleRedirect(w, r)
}

func LogIn(w http.ResponseWriter, r *http.Request) {
	printRequestPath(r)

	switch r.Method {
	case http.MethodGet:
		handleGETLogin(w)
	case http.MethodPost:
		handlePOSTLogin(w, r)
	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)

	}
}

func Logout(w http.ResponseWriter, r *http.Request) {
	session, _ := Session.Get(r, "auth-session")

	session.Options.MaxAge = -1 // delete cookie
	session.Save(r, w)

	http.Redirect(w, r, "/login", http.StatusSeeOther)
}
