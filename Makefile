.PHONY: chatgptproxy funcaptcha interference_openai_api start

export GIN_MODE=release

funcaptcha:
	@bazelisk run //:funcaptcha

chatgptproxy:
	@bazelisk run //:chatgptproxy

interference_openai_api:
	@bazelisk run //interference_openai_api:server

start: chatgptproxy funcaptcha interference_openai_api
