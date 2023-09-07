def _install_asdf_impl(ctx):
    output = ctx.actions.declare_file("install_asdf.log")
    ctx.actions.run_shell(
        outputs = [output],
        inputs = ctx.files.srcs,
        command = """
        set -e
        cat .tool-versions | awk \'{print $1}\' | xargs -I {} asdf plugin-add {} || true > $@
        asdf install > $@
        npm install -g pnpm > $@
        asdf reshim > $@
        pnpm install > $@
        echo "ASDF tools installed" > $@
        """,
        use_default_shell_env = True,
        arguments = [output.path],
    )
    return DefaultInfo(files = depset([output]))

install_asdf = rule(
    implementation = _install_asdf_impl,
    attrs = {
        "srcs": attr.label_list(allow_files = True),
    },
    outputs = {"log": "install_asdf.log"},
)
