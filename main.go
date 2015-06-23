package main

import(
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
)

var numbers []int64

func insertNumber(n int64) {
	numbers = append(numbers, n)
}

func parseNumbers(path string) []int64 {
	var parsed []int64
	requestedNumbers := strings.Split(string, "/")

	log.Println("Parsing:", path)

	// fill newNumbers by parsing requested numbers
	for _, s := range requestedNumbers {
		parsed, err := strconv.ParseInt(s, 10, 0)
		if err != nil {
			log.Println("ERR:", err)
			continue
		}
		// and appending everything we can parse
		log.Println("Parsed:", parsed)
		parsed = append(numbers, parsed)
	}

	return parsed
}

func handleNumbers(w http.ResponseWriter, r *http.Request) {
	/* handle the numbers endpoint.
         *
         *   /[<num>, ...] adds legal numbers you are allowed to add
         *                 to the set then returns all the numbers you
         *                 are allowed to see.
         */

	log.Println("Request recieved:", r.URL.Path)
	requestedNubmers := parseNumbers(r.URL.Path)

	// insert numbers they are allowed to insert
	insertNumbers(filterByPerms(user, "insert", requestedNumbers))

	// then return all the numbers they are allowed to see
	viewableNumbers := filterByPerms(user, "see", numbers)
	log.Println("Returning numbers:", viewableNumbers)
	fmt.Fprintf(w, "For you, the numbers are: %v", viewableNumbers)
}

func main() {
	http.HandleFunc("/", handleNumbers)
	log.Println("Listening for numbers ...")
	http.ListenAndServe("0.0.0.0:8000", nil)
}
