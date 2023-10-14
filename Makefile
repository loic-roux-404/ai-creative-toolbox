.PHONY: chatgptproxy funcaptcha interference_openai_api start

export GIN_MODE=release
LOGGING:=-v
ENV:=$(PWD)/.env

funcaptcha:
	@bazel run //:funcaptcha

chatgptproxy:
	@bazel run //:chatgptproxy

interference_openai_api:
	@bazel run //interference_openai_api:server -- --env-file $(ENV) $(LOGGING)

all: chatgptproxy funcaptcha interference_openai_api

start:
	$(MAKE) all -j3
