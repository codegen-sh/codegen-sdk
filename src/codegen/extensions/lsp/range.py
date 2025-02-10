from lsprotocol.types import Position, Range

from codegen.sdk.core.interfaces.editable import Editable


def get_range(node: Editable) -> Range:
    start_point = node.start_point
    end_point = node.end_point
    for extended_node in node.extended_nodes:
        if extended_node.start_point.row < start_point.row:
            start_point = extended_node.start_point
        if extended_node.end_point.row > end_point.row:
            end_point = extended_node.end_point
    return Range(
        start=Position(line=start_point.row, character=start_point.column),
        end=Position(line=end_point.row, character=end_point.column),
    )
