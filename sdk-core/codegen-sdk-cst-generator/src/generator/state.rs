use std::collections::HashMap;

use crate::parser::TypeDefinition;

#[derive(Default, Debug)]
pub struct State {
    pub enums: String,
    pub structs: String,
    pub variants: HashMap<String, Vec<TypeDefinition>>,
}
