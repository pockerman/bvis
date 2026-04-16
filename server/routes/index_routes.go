package routes

import (
	"html/template"
	"net/http"
)

func BvisIndex(w http.ResponseWriter, r *http.Request) {
	printRequestPath(r)

	var view = template.Must(template.ParseFiles("ui/index.html"))

	w.WriteHeader(http.StatusOK)
	view.Execute(w, nil)

}
