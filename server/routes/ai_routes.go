package routes

import (
	"bytes"
	"encoding/json"
	"net/http"

	log "github.com/sirupsen/logrus"
)

type AIRequestHandler struct {
	OrchestratorURL string
}

type AIRequest struct {
	BookID    string `json:"book_id"`
	ChapterID string `json:"chapter_id"`
	Query     string `json:"query"`
}

type OrchestratorPayload struct {
	Query   string            `json:"query"`
	Context map[string]string `json:"context"`
}

type AIResponse struct {
	Result string `json:"result"`
}

func (h *AIRequestHandler) HandleQuery(w http.ResponseWriter, r *http.Request) {

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

	if r.Method != http.MethodPost {
		log.Errorf("Method %s is not allowed", r.Method)
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req AIRequest
	err = json.NewDecoder(r.Body).Decode(&req)
	if err != nil {
		log.Errorf("JSON could not be decoded error: %s ", err)
		http.Error(w, "invalid JSON", http.StatusBadRequest)
		return
	}

	// basic validation
	if req.BookID == "" || req.ChapterID == "" || req.Query == "" {
		log.Errorf("BookID:  %s or ChapterID:  %s or query:  %s ", req.BookID, req.ChapterID, req.Query)
		http.Error(w, "missing fields", http.StatusBadRequest)
		return
	}

	log.Info("Book", req.BookID, " chapter: ", req.ChapterID, "Query: ", req.Query)

	// build payload for orchestrator
	payload := OrchestratorPayload{
		Query: req.Query,
		Context: map[string]string{
			"book_id":    req.BookID,
			"chapter_id": req.ChapterID,
		},
	}

	body, err := json.Marshal(payload)
	if err != nil {
		http.Error(w, "failed to encode payload", 500)
		return
	}

	// send to orchestrator
	resp, err := http.Post(
		h.OrchestratorURL+"/task",
		"application/json",
		bytes.NewBuffer(body),
	)
	if err != nil {
		http.Error(w, "orchestrator unavailable", 502)
		return
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		http.Error(w, "orchestrator error", 500)
		return
	}

	var result AIResponse
	err = json.NewDecoder(resp.Body).Decode(&result)
	if err != nil {
		http.Error(w, "invalid orchestrator response", 500)
		return
	}

	// return to frontend
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(result)
}
