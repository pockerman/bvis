package render

import (
	"bytes"

	"github.com/yuin/goldmark"
)

func MarkdownToHTML(md string) (string, error) {

	var buf bytes.Buffer
	err := goldmark.Convert([]byte(md), &buf)

	if err != nil {
		return "", nil
	}

	return buf.String(), nil
}
