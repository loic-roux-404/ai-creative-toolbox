.PHONY: proxy captcha app start

captcha:
	@go run captcha/main.go

proxy:
	@go run "github.com/acheong08/ChatGPTProxy"

app:
	@python app.py

start: proxy captcha app
