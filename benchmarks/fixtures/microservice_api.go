package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

type HealthResponse struct {
	Status    string `json:"status"`
	UptimeSec int64  `json:"uptime_sec"`
}

var startTime = time.Now()

func healthHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	resp := HealthResponse{
		Status:    "HEALTHY",
		UptimeSec: int64(time.Since(startTime).Seconds()),
	}
	json.NewEncoder(w).Encode(resp)
}

func main() {
	http.HandleFunc("/healthz", healthHandler)
	fmt.Println("Starting API gateway on port 8080...")
	http.ListenAndServe(":8080", nil)
}
