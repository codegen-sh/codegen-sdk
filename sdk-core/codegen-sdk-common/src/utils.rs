use bytes::{Bytes, BytesMut};
use tree_sitter::{self, TextProvider};
pub fn named_children_without_field_names<'a>(node: tree_sitter::Node) -> Vec<tree_sitter::Node> {
    let mut children = Vec::new();
    for (index, child) in node.named_children(&mut node.walk()).enumerate() {
        if node.field_name_for_named_child(index as u32) == None {
            children.push(child);
        }
    }
    children
}
pub fn get_text_from_node(node: tree_sitter::Node) -> Bytes {
    BytesMut::zeroed(node.end_byte() - node.start_byte()).into()
}
