package routes

import (
	"net/http"
)

func RegisterRoutes() *http.ServeMux {
	mux := http.NewServeMux()
	mux.Handle("/", http.HandlerFunc(BvisIndex))
	mux.Handle("/upload-book", http.HandlerFunc(UploadBook))
	mux.Handle("/login", http.HandlerFunc(LogIn))
	mux.Handle("/logout", http.HandlerFunc(Logout))
	mux.Handle("/dashboard", http.HandlerFunc(GetUserDahsboard))
	return mux
}
