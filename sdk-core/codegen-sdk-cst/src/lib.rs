use std::{
    error::Error,
    fmt::{self, Display},
    fs::File,
    io::{BufReader, Read},
    panic::catch_unwind,
};

use codegen_sdk_common::traits::FromNode;
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
pub mod tsx {
    include!(concat!(env!("OUT_DIR"), "/tsx.rs"));
}

#[derive(Debug)]
struct ParseError {}
impl Error for ParseError {}
impl Display for ParseError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "ParseError")
    }
}
pub fn parse_file_typescript(file_path: &str) -> Result<Box<tsx::Program>, Box<dyn Error>> {
    let tree = parse_file(file_path, tree_sitter_typescript::LANGUAGE_TSX.into())?;
    Ok(
        catch_unwind(|| Box::new(tsx::Program::from_node(tree.root_node())))
            .map_err(|e| ParseError {})?,
    )
}
#[cfg(test)]
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
