use std::{collections::HashMap, iter::Map};

use codegen_sdk_cst_generator::generate_cst;
use tree_sitter_python;
use tree_sitter_typescript;
fn get_node_types() -> HashMap<String, String> {
    HashMap::from([
        (
            "python".to_string(),
            tree_sitter_python::NODE_TYPES.to_string(),
        ),
        (
            "typescript".to_string(),
            tree_sitter_typescript::TYPESCRIPT_NODE_TYPES.to_string(),
        ),
    ])
}
fn main() {
    for (language, node_types) in get_node_types() {
        let cst = generate_cst(&node_types, &language).unwrap();
        // println!("{}", cst);
    }
}
