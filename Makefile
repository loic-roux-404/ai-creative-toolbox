.PHONY: proxy captcha app start

export GIN_MODE=release

install:
	@cat .tool-versions | awk '{print $$1}' | xargs -L 1 asdf plugin add
	@asdf plugin-add terraform https://github.com/asdf-community/asdf-hashicorp.git
	@asdf install
	@go install github.com/acheong08/funcaptcha/cmd/api@v1.9.2.1
	@go install github.com/acheong08/ChatGPTProxy@latest
	@curl -f https://get.pnpm.io/v6.16.js | node - add --global pnpm
	@go install github.com/bazelbuild/bazelisk@latest
	@go install github.com/bazelbuild/buildtools/buildifier@latest
	@asdf reshim
	@conda create -y -n $$(basename $$(PWD)) python==3.10.2

captcha:
	@api

proxy:
	@ChatGPTProxy

app:
	@sleep 3
	@python app.py

start: proxy captcha app
