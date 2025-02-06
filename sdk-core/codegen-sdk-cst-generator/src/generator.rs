use crate::parser::{Children, Fields, Node, TypeDefinition};
use convert_case::{Case, Casing};
use enum_generator::generate_enum;
use naming::normalize_type_name;
use state::State;
use std::{collections::HashSet, error::Error, fmt::format};
use struct_generator::generate_struct;
mod enum_generator;
mod format;
mod naming;
mod state;
mod struct_generator;
const IMPORTS: &str = "
use codegen_sdk_cst_generator::traits::FromNode;
use tree_sitter;
extern crate ouroboros;
use codegen_sdk_cst_generator::utils::*;
";

pub(crate) fn generate_cst(node_types: &Vec<Node>) -> Result<String, Box<dyn Error>> {
    let mut state = State::default();
    let mut nodes = HashSet::new();
    for node in node_types {
        if node.subtypes.len() > 0 {
            state
                .variants
                .insert(normalize_type_name(&node.type_name), node.subtypes.clone());
        }
    }
    for node in node_types {
        if !node.named {
            continue;
        }
        if nodes.contains(&node.type_name) {
            panic!("Duplicate node type: {}", node.type_name);
        }
        nodes.insert(&node.type_name);
        let name = normalize_type_name(&node.type_name);
        if node.subtypes.len() > 0 {
            generate_enum(&node.subtypes, &mut state, &name);
        } else {
            generate_struct(node, &mut state, &name);
        }
    }
    let mut result = IMPORTS.to_string();
    result.push_str(&state.enums);
    result.push_str(&state.structs);
    let formatted = format::format_cst(&result);
    Ok(formatted)
}
#[cfg(test)]
mod tests {
    use crate::parser::parse_node_types;

    use super::*;
    #[test]
    fn test_generate_cst() {
        let node_types = parse_node_types(tree_sitter_python::NODE_TYPES).unwrap();
        let cst = generate_cst(&node_types).unwrap();
        println!("{}", cst);
    }
}
