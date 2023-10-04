.PHONY: chatgptproxy funcaptcha interference_openai_api start

export GIN_MODE=release
LOGGING:=-v

funcaptcha:
	@bazel run //:funcaptcha

chatgptproxy:
	@bazel run //:chatgptproxy

interference_openai_api:
	@bazel run //interference_openai_api:server -- --env-file $(PWD)/.env $(LOGGING)

start: chatgptproxy funcaptcha interference_openai_api
