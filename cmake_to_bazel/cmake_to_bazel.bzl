# cmake_to_bazel/cmake_to_bazel.bzl
"""
Bazel CMake to bazel custom rule
"""

def _cmake_to_bazel_impl(ctx):
    cmake_file = ctx.file.cmake_file
    output_dir = ctx.outputs.output_dir
    ctx.actions.run(
        arguments = [cmake_file.path, output_dir.path],
        outputs = [output_dir],
        executable = ctx.executable._parser,
    )

cmake_to_bazel = rule(
    1,
    implementation = _cmake_to_bazel_impl,
    attrs = {
        "cmake_file": attr.label(allow_single_file = True),
        "output_dir": attr.output(),
        "_parser": attr.label(
            allow_single_file = True,
            executable = True,
            default = Label("//cmake_to_bazel:main"),
        ),
    },
)
