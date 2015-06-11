package main

import(
	"fmt"
	"log"
	"net/http"
	"strconv"
	"strings"
)

var numbers []int64

func handleNumbers(w http.ResponseWriter, r *http.Request) {
	/* handle the numbers endpoint.
         *
         *   /[<num>, ...] adds legal numbers you are allowed to add
         *                 to the set then returns all the numbers you
         *                 are allowed to see.
         */

	log.Println("Request recieved:", r.URL.Path)

	requestedNumbers := strings.Split(r.URL.Path, "/")
	log.Println("Requested Numbers:", requestedNumbers)

	// fill newNumbers by parsing requested numbers
	for _, s := range requestedNumbers {
		log.Println("Parsing:", s)
		parsed, err := strconv.ParseInt(s, 10, 0)
		if err != nil {
			log.Println("ERR:", err)
			continue
		}
		// and appending everything we can parse
		log.Println("Parsed:", parsed)
		numbers = append(numbers, parsed)
	}

	// then return all the numbers they have access to
	log.Println("returning numbers:", numbers)
	fmt.Fprintf(w, "For you, the numbers are: %v", numbers)
}

func main() {
	http.HandleFunc("/", handleNumbers)
	fmt.Println("Listening for numbers ...")
	http.ListenAndServe("0.0.0.0:8000", nil)
}
