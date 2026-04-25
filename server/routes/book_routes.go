package routes

import (
	"bvis/server/impl/content"
	"bvis/server/impl/render"
	"html/template"
	"net/http"

	"github.com/go-chi/chi/v5"
	log "github.com/sirupsen/logrus"
)

type BookLoaderHandler struct {
	Service *content.BookLoaderService
	Tmpl    *template.Template
}

type BookViewData struct {
	User        string
	BookID      string
	ChapterID   string
	ChapterHTML template.HTML
}

func (h *BookLoaderHandler) GetBookChapter(w http.ResponseWriter, r *http.Request) {

	printRequestPath(r)

	// check of the user is login
	session, err := Session.Get(r, "auth-session")
	if err != nil {
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	user, ok := session.Values["user"].(string)
	if !ok || user == "" {
		log.Errorf("User %s is not signed in", user)
		http.Redirect(w, r, "/login", http.StatusSeeOther)
		return
	}

	bookID := chi.URLParam(r, "bookID")
	chapterID := chi.URLParam(r, "chapterID")

	md, err := h.Service.LoadChapterMarkdown(bookID, chapterID)
	if err != nil {
		log.Errorf("Loading book: %s choater: %s failed with error %s", bookID, chapterID, err)
		http.Error(w, err.Error(), http.StatusNotFound)
		return
	}

	html, err := render.MarkdownToHTML(md)
	if err != nil {
		http.Error(w, "failed to render markdown", 500)
		return
	}

	data := BookViewData{
		User:        user,
		BookID:      bookID,
		ChapterID:   chapterID,
		ChapterHTML: template.HTML(html),
	}

	w.WriteHeader(http.StatusOK)
	h.Tmpl.Execute(w, data)

}
