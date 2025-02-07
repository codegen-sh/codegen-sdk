use std::{
    fs::File,
    io::{BufWriter, Write},
};

use prettyplease;
use syn;

pub fn format_cst(cst: &str) -> String {
    let file = File::create("tmp.rs").unwrap();
    let mut writer = BufWriter::new(file);
    writer.write_all(cst.as_bytes()).unwrap();
    let parsed = syn::parse_str::<syn::File>(&cst)
        .map_err(|e| {
            println!("{:#?}", e);
            e
        })
        .unwrap();
    let formatted = prettyplease::unparse(&parsed);
    formatted
}
