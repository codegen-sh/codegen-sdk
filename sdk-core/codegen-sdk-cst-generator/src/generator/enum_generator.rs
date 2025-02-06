use super::naming::normalize_type_name;
use crate::generator::state::State;
use crate::parser::TypeDefinition;
fn get_cases(
    variants: &Vec<TypeDefinition>,
    cases: &mut String,
    state: &State,
    override_variant_name: Option<&str>,
    existing_cases: &mut Vec<String>,
) {
    for t in variants {
        if t.named {
            let normalized_variant_name = normalize_type_name(&t.type_name);
            let variant_name = override_variant_name
                .clone()
                .unwrap_or_else(|| &normalized_variant_name);
            let prefix = format!("{}::{}", "Self", variant_name);
            if let Some(variants) = state.variants.get(&normalized_variant_name) {
                get_cases(variants, cases, state, Some(variant_name), existing_cases);
            } else if !existing_cases.contains(&t.type_name) {
                existing_cases.push(t.type_name.clone());
                cases.push_str(&format!(
                    "\"{}\" => {}({variant_name}::from_node(node)),",
                    t.type_name, prefix,
                ));
            }
        }
    }
}
pub fn generate_enum(variants: &Vec<TypeDefinition>, state: &mut State, enum_name: &str) {
    state.enums.push_str(&format!(
        "
    #[derive(Debug, Clone, PartialEq, Eq)]
    pub enum {enum_name} {{\n",
        enum_name = enum_name
    ));
    for t in variants {
        if t.named {
            let variant_name = normalize_type_name(&t.type_name);
            state
                .enums
                .push_str(&format!("    {}({variant_name}),\n", variant_name));
        }
    }
    state.enums.push_str("}\n");
    let mut cases = String::new();
    let mut existing_cases = Vec::new();
    get_cases(variants, &mut cases, state, None, &mut existing_cases);
    state.enums.push_str(&format!(
        "
    impl FromNode for {enum_name} {{
        fn from_node(node: tree_sitter::Node) -> Self {{
            match node.kind() {{
                {cases}
                _ => panic!(\"Unexpected node type: {{}}\", node.kind()),
            }}
        }}
    }}
    ",
        enum_name = enum_name,
        cases = cases
    ));
}
