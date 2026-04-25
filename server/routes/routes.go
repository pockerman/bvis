package routes

import (
	"net/http"

	"github.com/go-chi/chi/v5"
)

func RegisterRoutes(bookLoadHandler *BookLoaderHandler, aiHandler *AIRequestHandler) http.Handler {
	r := chi.NewRouter()

	// static files. Because we use chi, order matters. Static files should
	// come first
	r.Handle("/static/*", http.StripPrefix("/static/", http.FileServer(http.Dir("./static"))))

	// index
	r.Get("/", BvisIndex)
	r.Get("/upload-book", UploadBook)

	// authentication
	r.Get("/login", LogIn)
	r.Post("/login", LogIn)
	r.Get("/logout", Logout)

	// user dashboard
	r.Get("/dashboard", GetUserDahsboard)

	// fetch a chapter route
	r.Get("/books/{bookID}/chapters/{chapterID}", bookLoadHandler.GetBookChapter)

	// AI queries
	r.Post("/api/ai", aiHandler.HandleQuery)
	return r
}
