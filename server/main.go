package main

import (
	"bvis/routes"
	"fmt"
	"net/http"
	"os"
)

/*type hello struct{}

func (h hello) ServeHTTP(w http.ResponseWriter, r *http.Request) {

	msg := "<h1>Hello World</h1>"
	w.Write([]byte(msg))
}

func printRequestPath(r *http.Request) {
	fmt.Printf("Serving: %s\n", r.URL.Path)
}

func bvisIndex(w http.ResponseWriter, r *http.Request) {

	printRequestPath(r)
	msg := "<h1>Welcome to bvis. Please login to continue</h1>"
	w.Write([]byte(msg))
}

func uploadBook(w http.ResponseWriter, r *http.Request) {
	printRequestPath(r)

	switch r.Method {
	case http.MethodGet:
		// Show upload form
		html := `
		<h1>Upload Book</h1>
		<form enctype="multipart/form-data" action="/upload-book" method="post">
			<input type="file" name="book" />
			<input type="submit" value="Upload" />
		</form>`
		w.Write([]byte(html))

	case http.MethodPost:
		// Parse uploaded file (limit to ~10MB)
		err := r.ParseMultipartForm(10 << 20)
		if err != nil {
			http.Error(w, "Unable to parse form", http.StatusBadRequest)
			return
		}

		file, handler, err := r.FormFile("book")
		if err != nil {
			http.Error(w, "Error retrieving file", http.StatusBadRequest)
			return
		}
		defer file.Close()

		// Create destination file we will use some kind of blob storage for this
		dst, err := os.Create("./uploads/" + handler.Filename)
		if err != nil {
			http.Error(w, "Unable to save file", http.StatusInternalServerError)
			return
		}
		defer dst.Close()

		// Copy uploaded file to destination
		_, err = dst.ReadFrom(file)
		if err != nil {
			http.Error(w, "Error saving file", http.StatusInternalServerError)
			return
		}

		fmt.Fprintf(w, "File uploaded successfully: %s\n", handler.Filename)

	default:
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
	}
}

*/

func main() {

	PORT := ":8001"
	fmt.Println("Starting server...listening at port: ", PORT)

	routes.RegisterRoutes()

	// the default handler
	//http.HandleFunc("/", bvisIndex)
	//http.HandleFunc("/upload-book", uploadBook)

	// begin the HTTP server using the predefined PORT number
	err := http.ListenAndServe(PORT, nil)

	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}

}
