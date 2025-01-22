from codegen_sdk.tree_sitter_parser import get_parser_by_filepath_or_extension


def test_languages() -> None:
    parser = get_parser_by_filepath_or_extension("/root_dir/file1.py")
    parser = get_parser_by_filepath_or_extension("/root_dir/file1.js")
    parser = get_parser_by_filepath_or_extension("/root_dir/file1.jsx")
    parser = get_parser_by_filepath_or_extension("/root_dir/file1.ts")
    parser = get_parser_by_filepath_or_extension("/root_dir/file1.tsx")

    parser = get_parser_by_filepath_or_extension("file1.py")
    parser = get_parser_by_filepath_or_extension("file1.js")
    parser = get_parser_by_filepath_or_extension("file1.jsx")
    parser = get_parser_by_filepath_or_extension("file1.ts")
    parser = get_parser_by_filepath_or_extension("file1.tsx")

    parser = get_parser_by_filepath_or_extension(".py")
    parser = get_parser_by_filepath_or_extension(".js")
    parser = get_parser_by_filepath_or_extension(".jsx")
    parser = get_parser_by_filepath_or_extension(".ts")
    parser = get_parser_by_filepath_or_extension(".tsx")

    parser = get_parser_by_filepath_or_extension("py")
    parser = get_parser_by_filepath_or_extension("js")
    parser = get_parser_by_filepath_or_extension("jsx")
    parser = get_parser_by_filepath_or_extension("ts")
    parser = get_parser_by_filepath_or_extension("tsx")
