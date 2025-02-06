use convert_case::{Case, Casing};

pub fn normalize_field_name(field_name: &str) -> String {
    if field_name == "type" {
        return "r#type".to_string();
    }
    field_name.to_string()
}
pub fn normalize_type_name(type_name: &str) -> String {
    type_name.to_case(Case::Pascal)
}
