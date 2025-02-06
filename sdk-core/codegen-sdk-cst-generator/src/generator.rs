use crate::parser::{Node, TypeDefinition};
use convert_case::{Case, Casing};
use std::{collections::HashSet, error::Error};
const IMPORTS: &str = "
";
const HEADER_TEMPLATE: &str = "
pub struct {name} {
";
const FOOTER_TEMPLATE: &str = "
}
";
fn normalize_field_name(field_name: &str) -> String {
    if field_name == "type" {
        return "r#type".to_string();
    }
    field_name.to_string()
}
fn normalize_type_name(type_name: &str) -> String {
    type_name.to_case(Case::Pascal)
}
fn convert_type_name(
    type_name: &Vec<TypeDefinition>,
    enums: &mut String,
    field_name: &str,
    node_name: &str,
) -> String {
    if type_name.len() == 1 {
        normalize_type_name(&type_name[0].type_name)
    } else {
        let enum_name = normalize_type_name(
            format!(
                "{}{}",
                normalize_type_name(node_name),
                normalize_type_name(field_name)
            )
            .as_str(),
        );
        enums.push_str(&format!("pub enum {enum_name} {{\n", enum_name = enum_name));
        for t in type_name {
            if t.named {
                enums.push_str(&format!("    {},\n", normalize_type_name(&t.type_name)));
            }
        }
        enums.push_str("}\n");
        enum_name
    }
}
pub(crate) fn generate_cst(node_types: &Vec<Node>) -> Result<String, Box<dyn Error>> {
    let mut cst = String::new();
    let mut enums = String::new();
    let mut nodes = HashSet::new();
    for node in node_types {
        if !node.named {
            continue;
        }
        if nodes.contains(&node.type_name) {
            panic!("Duplicate node type: {}", node.type_name);
        }
        nodes.insert(&node.type_name);
        cst.push_str(&HEADER_TEMPLATE.replace("{name}", &normalize_type_name(&node.type_name)));
        if let Some(fields) = &node.fields {
            for (name, field) in &fields.fields {
                let field_name = normalize_field_name(name);
                if field.multiple {
                    cst.push_str(&format!(
                        "    pub {field_name}: Vec<{}>,\n",
                        convert_type_name(&field.types, &mut enums, &node.type_name, &name)
                    ));
                } else {
                    cst.push_str(&format!(
                        "    pub {field_name}: {type_name},\n",
                        field_name = field_name,
                        type_name =
                            convert_type_name(&field.types, &mut enums, &node.type_name, &name)
                    ));
                }
            }
        }
        // for child in &node.children {
        //     if child.multiple {
        //         cst.push_str(&CHILD_TEMPLATE.replace("{name}", &child.type_name));
        //     } else {
        //         cst.push_str(&CHILD_TEMPLATE.replace("{name}", &child.type_name));
        //     }
        // }
        cst.push_str(&FOOTER_TEMPLATE);
    }
    let mut result = IMPORTS.to_string();
    result.push_str(&enums);
    result.push_str(&cst);
    Ok(result)
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
