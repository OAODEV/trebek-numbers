from golang
maintainer jesse.miller@adops.com

add . /go/src/github.com/oaodev/trebek-numbers
run go install github.com/oaodev/trebek-numbers

expose 8000
cmd ["/go/bin/trebek-numbers"]