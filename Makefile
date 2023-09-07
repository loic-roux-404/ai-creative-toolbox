.PHONY: chatgptproxy funcaptcha interference-openai-api start

export GIN_MODE=release

funcaptcha:
	@bazelisk run //:funcaptcha

chatgptproxy:
	@bazelisk run //:chatgptproxy

interference-openai-api:
	@bazelisk run //interference-openai-api:server

start: chatgptproxy interference-openai-api funcaptcha
