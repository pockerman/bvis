package content

type BookLoaderService struct {
	Repo *BookRepository
}

func (s *BookLoaderService) LoadChapterMarkdown(bookID, chapterID string) (string, error) {
	return s.Repo.GetChapterMarkdown(bookID, chapterID)
}
