package main

import (
	"bvis/server/impl/content"
	"bvis/server/impl/utils"
	"bvis/server/routes"
	"fmt"
	"html/template"
	"net/http"
	"os"
	"time"

	log "github.com/sirupsen/logrus"
)

func main() {

	utils.InitLogger()

	PORT := ":8001"
	log.Infof("Starting server... listening at port: %s", PORT)

	// ---- Dependencies ----
	repo := &content.BookRepository{
		BasePath: "./data/books",
	}

	service := &content.BookLoaderService{
		Repo: repo,
	}

	tmpl := template.Must(template.ParseFiles("ui/book_view.html"))

	bookHandler := &routes.BookLoaderHandler{
		Service: service,
		Tmpl:    tmpl,
	}

	aiHandler := &routes.AIRequestHandler{
		OrchestratorBaseURL: "http://localhost:8000",
		OrchestratorPrefix:  "/api",
	}

	// ---- Router ----
	router := routes.RegisterRoutes(bookHandler, aiHandler)

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
