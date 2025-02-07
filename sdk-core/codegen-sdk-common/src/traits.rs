use bytes::Bytes;
use tree_sitter::{self, Point};
pub trait FromNode {
    fn from_node(node: tree_sitter::Node) -> Self;
}
pub trait CSTNode {
    fn start_byte(&self) -> usize;
    fn end_byte(&self) -> usize;
    fn start_position(&self) -> Point;
    fn end_position(&self) -> Point;
    fn text(&self) -> &Bytes;
    fn source(&self) -> String {
        String::from_utf8(self.text().to_vec()).unwrap()
    }
}
