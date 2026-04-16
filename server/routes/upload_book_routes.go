package routes

import (
	"fmt"
	"html/template"
	"net/http"
	"os"
)

func UploadBook(w http.ResponseWriter, r *http.Request) {
	printRequestPath(r)

	switch r.Method {
	case http.MethodGet:
		// html := `
		// <h1>Upload Book</h1>
		// <form enctype="multipart/form-data" action="/upload-book" method="post">
		// 	<input type="file" name="book" />
		// 	<input type="submit" value="Upload" />
		// </form>`
		// w.Write([]byte(html))

		// build the view. TODO: Refactor this to anothe function
		var view = template.Must(template.ParseFiles("ui/upload_book.html"))
		w.WriteHeader(http.StatusOK)
		view.Execute(w, nil)

	case http.MethodPost:
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

		dst, err := os.Create("./uploads/" + handler.Filename)
		if err != nil {
			http.Error(w, "Unable to save file", http.StatusInternalServerError)
			return
		}
		defer dst.Close()

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
