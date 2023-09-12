.PHONY: chatgptproxy funcaptcha interference-openai-api start

export GIN_MODE=release

funcaptcha:
	@bazelisk run //:funcaptcha

chatgptproxy:
	@bazelisk run //:chatgptproxy

interference_openai_api:
	@bazelisk run //interference_openai_api:server

start: chatgptproxy interference-openai-api funcaptcha
