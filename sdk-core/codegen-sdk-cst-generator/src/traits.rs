use tree_sitter;
pub trait FromNode {
    fn from_node(node: tree_sitter::Node) -> Self;
}
