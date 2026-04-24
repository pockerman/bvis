package routes

import (
	"html/template"
	"net/http"
)

type Chapter struct {
	ID    string
	Title string
}

type Book struct {
	ID       string
	Title    string
	Chapters []Chapter
}

type DashboardData struct {
	User  string
	Books []Book
}

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

	// build the view. TODO: Refactor this to anothe function
	var view = template.Must(template.ParseFiles("ui/dashboard.html"))
	data := DashboardData{
		User: user, // this would come from DB/session in real app
		Books: []Book{
			{
				ID:    "1",
				Title: "Event Driven Design",
				Chapters: []Chapter{
					{ID: "4", Title: "Intro"},
				},
			},
		},
	}

	w.WriteHeader(http.StatusOK)
	view.Execute(w, data)

}
