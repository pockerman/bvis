package main

import (
	"bvis/server/impl/content"
	"bvis/server/routes"
	"fmt"
	"html/template"
	"net/http"
	"os"
	"time"
)

func main() {

	PORT := ":8001"
	fmt.Println("Starting server... listening at port:", PORT)

	// ---- Dependencies ----

	repo := &content.BookRepository{
		BasePath: "./data/books",
	}

	service := &content.BookLoaderService{
		Repo: repo,
	}

	tmpl := template.Must(template.ParseFiles("ui/book_view.html"))

	handler := &routes.BookLoaderHandler{
		Service: service,
		Tmpl:    tmpl,
	}

	// ---- Router ----
	router := routes.RegisterRoutes(handler)

	// ---- Server ----
	s := &http.Server{
		Addr:         PORT,
		Handler:      router,
		IdleTimeout:  10 * time.Second,
		ReadTimeout:  time.Second,
		WriteTimeout: time.Second,
	}

	// ---- Start Server ----
	err := s.ListenAndServe()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
