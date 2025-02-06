use crate::parser::{Node, TypeDefinition};
use convert_case::{Case, Casing};
use std::error::Error;
const HEADER_TEMPLATE: &str = "
pub struct {name} {
";
const FOOTER_TEMPLATE: &str = "
}
";
fn normalize_type_name(type_name: &str) -> String {
    type_name.to_case(Case::Pascal)
}
fn convert_type_name(type_name: &Vec<TypeDefinition>) -> String {
    if type_name.len() == 1 {
        normalize_type_name(&type_name[0].type_name)
    } else {
        format!(
            "Union<{}>",
            type_name
                .iter()
                .map(|t| normalize_type_name(&t.type_name))
                .collect::<Vec<String>>()
                .join(", ")
        )
    }
}
pub(crate) fn generate_cst(node_types: &Vec<Node>) -> Result<String, Box<dyn Error>> {
    let mut cst = String::new();
    for node in node_types {
        if !node.named {
            continue;
        }
        cst.push_str(&HEADER_TEMPLATE.replace("{name}", &normalize_type_name(&node.type_name)));
        if let Some(fields) = &node.fields {
            for (name, field) in &fields.fields {
                if field.multiple {
                    cst.push_str(&format!(
                        "    pub {name}: Vec<{}>;\n",
                        convert_type_name(&field.types)
                    ));
                } else {
                    cst.push_str(&format!(
                        "    pub {name}: {type_name},\n",
                        name = name,
                        type_name = convert_type_name(&field.types)
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
    Ok(cst)
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
