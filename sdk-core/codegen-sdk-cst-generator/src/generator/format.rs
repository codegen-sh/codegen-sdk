use prettyplease;
use syn;

pub fn format_cst(cst: &str) -> String {
    let formatted = prettyplease::unparse(&syn::parse_str::<syn::File>(&cst).unwrap());
    formatted
}
