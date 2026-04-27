# cmake_to_bazel/cmake_to_bazel.bzl — run the transpiler as a Bazel action.

def _cmake_to_bazel_impl(ctx):
    build = ctx.outputs.build
    out_dir = build.dirname
    ctx.actions.run(
        mnemonic = "CmakeToBazel",
        progress_message = "Transpiling CMake to Bazel (%{label})",
        executable = ctx.executable._tool,
        arguments = [ctx.file.cmake_file.path, out_dir],
        inputs = [ctx.file.cmake_file],
        outputs = [build],
    )

cmake_to_bazel = rule(
    implementation = _cmake_to_bazel_impl,
    attrs = {
        "cmake_file": attr.label(
            allow_single_file = True,
            mandatory = True,
        ),
        "_tool": attr.label(
            default = Label("//cmake_to_bazel:cli"),
            executable = True,
            cfg = "exec",
        ),
    },
    outputs = {"build": "%{name}/BUILD"},
)
