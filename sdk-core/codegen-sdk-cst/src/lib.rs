// mod python {
//     include!(concat!(env!("OUT_DIR"), "/python.rs"));
// }
mod typescript {
    include!(concat!(env!("OUT_DIR"), "/typescript.rs"));
}

mod tests {
    use super::*;
    #[test]
    fn test_snazzy_items() {
        println!("{}", SNUZZY_ITEMS);
    }
}
