package auth

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestBearer(t *testing.T) {
	ok := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {})
	h := Bearer("secret", ok, "/healthz")

	cases := []struct {
		path, header string
		want         int
	}{
		{"/v1/attempts/judge", "Bearer secret", http.StatusOK},
		{"/v1/attempts/judge", "Bearer wrong", http.StatusUnauthorized},
		{"/v1/attempts/judge", "", http.StatusUnauthorized},
		{"/healthz", "", http.StatusOK},
	}
	for _, c := range cases {
		req := httptest.NewRequest(http.MethodPost, c.path, nil)
		if c.header != "" {
			req.Header.Set("Authorization", c.header)
		}
		rec := httptest.NewRecorder()
		h.ServeHTTP(rec, req)
		if rec.Code != c.want {
			t.Errorf("%s %q: got %d, want %d", c.path, c.header, rec.Code, c.want)
		}
	}
}
