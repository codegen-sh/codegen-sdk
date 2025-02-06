mod generator;
pub(crate) mod parser;
use std::error::Error;

pub fn generate_cst(source: &str, language: &str) -> Result<(), Box<dyn Error>> {
    let node_types = parser::parse_node_types(source)?;
    let cst = generator::generate_cst(&node_types)?;
    let out_dir = std::env::var("OUT_DIR").unwrap();
    let out_file = format!("{}/{}.rs", out_dir, language);
    std::fs::write(out_file, cst)?;
    Ok(())
}
