use tree_sitter::{self, Point};
pub trait FromNode {
    fn from_node(node: tree_sitter::Node) -> Self;
}
pub trait CSTNode {
    fn start_byte(&self) -> usize;
    fn end_byte(&self) -> usize;
    fn start_position(&self) -> Point;
    fn end_position(&self) -> Point;
}
