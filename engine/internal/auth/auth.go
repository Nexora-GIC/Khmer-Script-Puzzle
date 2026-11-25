// Package auth checks the shared secret the api sends on every call.
package auth

import (
	"crypto/subtle"
	"net/http"
)

// Bearer rejects requests without "Authorization: Bearer <key>".
// Paths listed in open (e.g. /healthz) are let through without a key.
func Bearer(key string, next http.Handler, open ...string) http.Handler {
	want := []byte("Bearer " + key)
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		for _, p := range open {
			if r.URL.Path == p {
				next.ServeHTTP(w, r)
				return
			}
		}
		got := []byte(r.Header.Get("Authorization"))
		if subtle.ConstantTimeCompare(got, want) != 1 {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		next.ServeHTTP(w, r)
	})
}
