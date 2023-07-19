package main

import (
	"fmt"

	"github.com/acheong08/funcaptcha"
)

func main() {
	token, _, _ := funcaptcha.GetOpenAIToken()
	fmt.Println(token)
}