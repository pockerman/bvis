package main

import (
	"bvis/routes"
	"fmt"
	"net/http"
	"os"
	"time"
)

func main() {

	// The port number and the hostname should be separated with a colon (:),
	//which should be there even if there is no hostname
	PORT := ":8001"
	fmt.Println("Starting server...listening at port: ", PORT)

	// register the routes the servere handles
	mux := routes.RegisterRoutes()
	s := &http.Server{
		Addr:         PORT,
		Handler:      mux,
		IdleTimeout:  10 * time.Second,
		ReadTimeout:  time.Second,
		WriteTimeout: time.Second,
	}

	// begin the HTTP server using the predefined PORT number
	err := s.ListenAndServe()

	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

}
