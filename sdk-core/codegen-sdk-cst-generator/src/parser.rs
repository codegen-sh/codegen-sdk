use std::error::Error;

use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Node {
    #[serde(rename = "type")]
    pub type_name: String,
    pub named: bool,
    #[serde(default)]
    pub subtypes: Vec<Subtype>,
    #[serde(default)]
    pub fields: Option<Fields>,
    #[serde(default)]
    pub children: Option<Children>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Subtype {
    #[serde(rename = "type")]
    pub type_name: String,
    pub named: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Fields {
    #[serde(flatten)]
    pub fields: std::collections::HashMap<String, FieldDefinition>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct FieldDefinition {
    pub multiple: bool,
    pub required: bool,
    #[serde(default)]
    pub types: Vec<TypeDefinition>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct TypeDefinition {
    #[serde(rename = "type")]
    pub type_name: String,
    pub named: bool,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Children {
    pub multiple: bool,
    pub required: bool,
    #[serde(default)]
    pub types: Vec<TypeDefinition>,
}

pub fn parse_node_types(source: &str) -> Result<Vec<Node>, Box<dyn Error>> {
    let parsed: Vec<Node> = serde_json::from_str(&source)?;
    Ok(parsed)
}
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_node_types() {
        let source = tree_sitter_python::NODE_TYPES;
        let cst = parse_node_types(source).unwrap();
        panic!();
    }
}
