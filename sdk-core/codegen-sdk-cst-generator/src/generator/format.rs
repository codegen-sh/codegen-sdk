use std::{
    fs::File,
    io::{BufWriter, Write},
};

use prettyplease;
use syn;

pub fn format_cst(cst: &str) -> String {
    let parsed = syn::parse_str::<syn::File>(&cst)
        .map_err(|e| {
            println!("{:#?}", e);
            e
        })
        .unwrap();
    let formatted = prettyplease::unparse(&parsed);
    formatted
}
