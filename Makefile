.PHONY: proxy captcha app start

export GIN_MODE=release

install:
	@go install github.com/acheong08/funcaptcha/cmd/api@v1.9.2.1
	@go install github.com/acheong08/ChatGPTProxy@latest
	@asdf reshim golang

captcha:
	@api

proxy:
	@ChatGPTProxy

app:
	@sleep 3
	@python app.py

start: proxy captcha app
