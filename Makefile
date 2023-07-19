.PHONY: proxy captcha app start

export GIN_MODE=release

install:
	@go install github.com/acheong08/funcaptcha/cmd/api@v1.9.2.1
	@go install github.com/acheong08/ChatGPTProxy@ccc0f231bcee0ddc58b588a59a28f93246e0a037
	@asdf reshim golang

captcha:
	@api

proxy:
	@ChatGPTProxy

app:
	@python app.py

start: proxy captcha app
