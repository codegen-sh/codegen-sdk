use crate::parser::{Children, Fields, Node, TypeDefinition};

use super::{
    enum_generator::generate_enum,
    naming::{normalize_field_name, normalize_type_name},
};
use crate::generator::state::State;
const HEADER_TEMPLATE: &str = "
#[derive(Debug, Clone)]
pub struct {name} {
    start_byte: usize,
    end_byte: usize,
    start_position: Point,
    end_position: Point,
";
const FOOTER_TEMPLATE: &str = "
}
";

const CONSTRUCTOR_TEMPLATE: &str = "
impl CSTNode for {{name}} {
    fn start_byte(&self) -> usize {
        self.start_byte
    }
    fn end_byte(&self) -> usize {
        self.end_byte
    }
    fn start_position(&self) -> Point {
        self.start_position
    }
    fn end_position(&self) -> Point {
        self.end_position
    }
}
impl FromNode for {{name}} {
    fn from_node(node: tree_sitter::Node) -> Self {
        Self {
            start_byte: node.start_byte(),
            end_byte: node.end_byte(),
            start_position: node.start_position(),
            end_position: node.end_position(),
            {{fields}}
        }
    }
}
";
fn convert_type_definition(
    type_name: &Vec<TypeDefinition>,
    state: &mut State,
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
        generate_enum(type_name, state, &enum_name, true);
        enum_name
    }
}

fn generate_multiple_field(
    field_name: &str,
    converted_type_name: &str,
    state: &mut State,
    constructor_fields: &mut Vec<String>,
    original_name: &str,
) {
    state.structs.push_str(&format!(
        "    pub {field_name}: Vec<{}>,\n",
        converted_type_name
    ));
    constructor_fields.push(format!("    {field_name}: node.children_by_field_name(\"{name}\", &mut node.walk()).map(|node| {converted_type_name}::from_node(node)).collect()", field_name = field_name, converted_type_name = converted_type_name, name=original_name));
}
fn generate_required_field(
    field_name: &str,
    converted_type_name: &str,
    state: &mut State,
    constructor_fields: &mut Vec<String>,
    original_name: &str,
) {
    state.structs.push_str(&format!(
        "    pub {field_name}: Box<{type_name}>,\n",
        field_name = field_name,
        type_name = converted_type_name
    ));
    constructor_fields.push(format!("    {field_name}: {converted_type_name}::from_node(node.child_by_field_name(\"{name}\").unwrap()).into()", field_name = field_name, converted_type_name = converted_type_name, name=original_name));
}
fn generate_optional_field(
    field_name: &str,
    converted_type_name: &str,
    state: &mut State,
    constructor_fields: &mut Vec<String>,
    original_name: &str,
) {
    state.structs.push_str(&format!(
        "    pub {field_name}: Box<Option<{type_name}>>,\n",
        field_name = field_name,
        type_name = converted_type_name
    ));
    constructor_fields.push(format!("    {field_name}: node.child_by_field_name(\"{name}\").map(|node| {converted_type_name}::from_node(node)).into()", field_name = field_name, converted_type_name = converted_type_name, name=original_name));
}
fn generate_fields(
    fields: &Fields,
    state: &mut State,
    node_name: &str,
    node: &Node,
    constructor_fields: &mut Vec<String>,
) {
    for (name, field) in &fields.fields {
        let field_name = normalize_field_name(name);
        let converted_type_name =
            convert_type_definition(&field.types, state, &node.type_name, &name);
        if field.multiple {
            generate_multiple_field(
                &field_name,
                &converted_type_name,
                state,
                constructor_fields,
                &name,
            );
        } else if field.required {
            generate_required_field(
                &field_name,
                &converted_type_name,
                state,
                constructor_fields,
                &name,
            );
        } else {
            generate_optional_field(
                &field_name,
                &converted_type_name,
                state,
                constructor_fields,
                &name,
            );
        }
    }
}
fn generate_children(
    children: &Children,
    state: &mut State,
    node_name: &str,
    constructor_fields: &mut Vec<String>,
) {
    let converted_type_name =
        convert_type_definition(&children.types, state, node_name, &"children");
    state.structs.push_str(&format!(
        "    pub children: Vec<{}>,\n",
        converted_type_name
    ));
    constructor_fields.push(format!("    children: named_children_without_field_names(node).into_iter().map(|node| {converted_type_name}::from_node(node)).collect()", converted_type_name = converted_type_name));
}
pub fn generate_struct(node: &Node, state: &mut State, name: &str) {
    state
        .structs
        .push_str(&HEADER_TEMPLATE.replace("{name}", &name));
    let mut constructor_fields = Vec::new();
    if let Some(fields) = &node.fields {
        generate_fields(
            fields,
            state,
            &node.type_name,
            &node,
            &mut constructor_fields,
        );
    }
    if let Some(children) = &node.children {
        generate_children(children, state, &node.type_name, &mut constructor_fields);
    }
    state.structs.push_str(&FOOTER_TEMPLATE);
    state.structs.push_str(
        &CONSTRUCTOR_TEMPLATE
            .replace("{{fields}}", &constructor_fields.join(",\n       "))
            .replace("{{name}}", &name),
    );
}
