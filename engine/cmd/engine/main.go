// Command engine runs the game engine HTTP server.
// It is stateless: every request carries the child's state in and gets the new state back.
package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"

	"example.com/engine/internal/auth"
)

// engineVersion is returned on every response and stored on each attempt by the api,
// so trial data can prove the rules did not change mid-trial.
const engineVersion = "0.0.0-dev"

func main() {
	addr := getenv("ENGINE_ADDR", ":8080")
	key := os.Getenv("ENGINE_KEY")
	if key == "" {
		log.Fatal("ENGINE_KEY is required")
	}

	// TODO: load content (CONTENT_PATH) and model (MODEL_PATH) once, here, before serving.

	mux := http.NewServeMux()
	mux.HandleFunc("GET /healthz", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(map[string]string{
			"status":        "ok",
			"engineVersion": engineVersion,
		})
	})
	// /v1/* routes are registered from internal/api (generated from api/engine.yaml).

	handler := auth.Bearer(key, mux, "/healthz")
	log.Printf("engine %s listening on %s", engineVersion, addr)
	log.Fatal(http.ListenAndServe(addr, handler))
}

func getenv(k, def string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return def
}
