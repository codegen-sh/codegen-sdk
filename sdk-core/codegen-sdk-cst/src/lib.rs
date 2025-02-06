use std::{
    error::Error,
    fs::File,
    io::{BufReader, Read},
};

use codegen_sdk_cst_generator::traits::FromNode;
use tree_sitter::{Language, Parser};
fn parse_file(file_path: &str, language: Language) -> Result<tree_sitter::Tree, Box<dyn Error>> {
    let file = File::open(file_path)?;
    let mut reader = BufReader::new(file);
    let mut buffer = String::new();
    let mut parser = Parser::new();
    parser.set_language(&language)?;
    reader.read_to_string(&mut buffer)?;
    let tree = parser.parse(&buffer, None).unwrap();
    Ok(tree)
}
// mod python {
//     include!(concat!(env!("OUT_DIR"), "/python.rs"));
// }
pub mod typescript {
    include!(concat!(env!("OUT_DIR"), "/typescript.rs"));
}
fn parse_file_typescript(file_path: &str) -> Result<typescript::Program, Box<dyn Error>> {
    let tree = parse_file(
        file_path,
        tree_sitter_typescript::LANGUAGE_TYPESCRIPT.into(),
    )?;
    let module = typescript::Program::from_node(tree.root_node());
    Ok(module)
}
mod tests {
    use std::io::Write;

    use super::*;
    #[test]
    fn test_snazzy_items() {
        let content = "
        class SnazzyItems {
            constructor() {
                this.items = [];
            }
        }
        ";

        let mut file = File::create("snazzy_items.ts").unwrap();
        file.write_all(&content.as_bytes()).unwrap();
        let module = parse_file_typescript("snazzy_items.ts").unwrap();
        panic!("{:#?}", module);
    }
}
