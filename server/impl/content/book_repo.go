package content

import (
	"errors"
	"log"
	"os"
	"path/filepath"
)

type BookRepository struct {
	BasePath string
}

func (r *BookRepository) GetChapterMarkdown(bookID, chapterID string) (string, error) {

	log.Println("Fetching book", bookID, "chapter", chapterID)
	if bookID == "" || chapterID == "" {
		return "", errors.New("Invalid book or chapter id")
	}

	cleanBookID := filepath.Clean(bookID)
	cleanChapterID := filepath.Clean(chapterID)

	bookPath := filepath.Join(r.BasePath, cleanBookID, "chapters", cleanChapterID, cleanChapterID+".md")

	log.Println("Book path: ", bookPath)
	data, err := os.ReadFile(bookPath)
	if err != nil {

		log.Println("Book", bookID, " chapter", chapterID, "is not found")

		if os.IsNotExist(err) {
			return "", errors.New("Chapter not found")
		}
		return "", err
	}

	return string(data), nil

}
