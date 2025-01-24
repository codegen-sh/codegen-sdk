from __future__ import annotations

import os
from collections import Counter, defaultdict
from collections.abc import Generator, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from enum import IntEnum, auto, unique
from functools import lru_cache
from os import PathLike
from pathlib import Path
from typing import TYPE_CHECKING, Any

from codeowners import CodeOwners as CodeOwnersParser
from git import Commit as GitCommit
from rustworkx import PyDiGraph, WeightedEdgeList

from codegen.git.repo_operator.repo_operator import RepoOperator
from codegen.sdk.codebase.config import CodebaseConfig, DefaultConfig, ProjectConfig, SessionOptions
from codegen.sdk.codebase.config_parser import ConfigParser, get_config_parser_for_language
from codegen.sdk.codebase.diff_lite import ChangeType, DiffLite
from codegen.sdk.codebase.flagging.flags import Flags
from codegen.sdk.codebase.transaction_manager import TransactionManager
from codegen.sdk.codebase.validation import get_edges, post_reset_validation
from codegen.sdk.core.autocommit import AutoCommit, commiter
from codegen.sdk.core.dataclasses.usage import Usage
from codegen.sdk.core.directory import Directory
from codegen.sdk.core.external.dependency_manager import DependencyManager, get_dependency_manager
from codegen.sdk.core.external.language_engine import LanguageEngine, get_language_engine
from codegen.sdk.core.interfaces.importable import Importable
from codegen.sdk.core.node_id_factory import NodeId
from codegen.sdk.enums import Edge, EdgeType, NodeType, ProgrammingLanguage
from codegen.sdk.extensions.sort import sort_editables
from codegen.sdk.extensions.utils import uncache_all
from codegen.sdk.typescript.external.ts_declassify.ts_declassify import TSDeclassify
from codegen.shared.exceptions.control_flow import StopCodemodException
from codegen.shared.performance.stopwatch_utils import stopwatch, stopwatch_with_sentry

if TYPE_CHECKING:
    from codegen.sdk.codebase.node_classes.node_classes import NodeClasses
    from codegen.sdk.core.expressions import Expression
    from codegen.sdk.core.external_module import ExternalModule
    from codegen.sdk.core.file import SourceFile
    from codegen.sdk.core.parser import Parser

import logging

logger = logging.getLogger(__name__)


GLOBAL_FILE_IGNORE_LIST = [
    ".git/*",
    ".yarn/releases/*",
]


@unique
class SyncType(IntEnum):
    DELETE = auto()
    REPARSE = auto()
    ADD = auto()


def get_node_classes(programming_language: ProgrammingLanguage) -> NodeClasses:
    if programming_language == ProgrammingLanguage.PYTHON:
        from codegen.sdk.codebase.node_classes.py_node_classes import PyNodeClasses

        return PyNodeClasses
    elif programming_language == ProgrammingLanguage.TYPESCRIPT:
        from codegen.sdk.codebase.node_classes.ts_node_classes import TSNodeClasses

        return TSNodeClasses
    else:
        raise ValueError(f"Unsupported programming language: {programming_language}!")


class CodebaseGraph:
    """MultiDiGraph Wrapper with TransactionManager"""

    # =====[ __init__ attributes ]=====
    node_classes: NodeClasses
    programming_language: ProgrammingLanguage
    repo_path: str
    repo_name: str
    codeowners_parser: CodeOwnersParser | None
    config: CodebaseConfig

    # =====[ computed attributes ]=====
    transaction_manager: TransactionManager
    pending_syncs: list[DiffLite]  # Diffs that have been applied to disk, but not the graph (to be used for sync graph)
    all_syncs: list[DiffLite]  # All diffs that have been applied to the graph (to be used for graph reset)
    _autocommit: AutoCommit
    pending_files: set[SourceFile]
    generation: int
    parser: Parser[Expression]
    synced_commit: GitCommit | None
    directories: dict[Path, Directory]
    base_url: str | None
    extensions: list[str]
    config_parser: ConfigParser | None
    dependency_manager: DependencyManager | None
    language_engine: LanguageEngine | None
    _computing = False
    _graph: PyDiGraph[Importable, Edge]
    filepath_idx: dict[str, NodeId]
    _ext_module_idx: dict[str, NodeId]
    flags: Flags
    session_options: SessionOptions = SessionOptions()
    projects: list[ProjectConfig]

    def __init__(
        self,
        projects: list[ProjectConfig],
        config: CodebaseConfig = DefaultConfig,
    ) -> None:
        """Initializes codebase graph and TransactionManager"""
        from codegen.sdk.core.parser import Parser

        self._graph = PyDiGraph()
        self.filepath_idx = {}
        self._ext_module_idx = {}
        self.generation = 0

        # NOTE: The differences between base_path, repo_name, and repo_path
        # /home/codegen/projects/my-project/src
        #                                   ^^^  <-  Base Path (Optional)
        #                        ^^^^^^^^^^  <-----  Repo Name
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  <-----  Repo Path
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  <-  Full Path
        # (full_path is unused for CGB, but is used elsewhere.)

        # =====[ __init__ attributes ]=====
        self.projects = projects
        context = projects[0]
        self.node_classes = get_node_classes(context.programming_language)
        self.config = config
        self.repo_name = context.repo_operator.repo_name
        self.repo_path = str(Path(context.repo_operator.repo_path).resolve())
        self.codeowners_parser = context.repo_operator.codeowners_parser
        self.base_url = context.repo_operator.base_url
        # =====[ computed attributes ]=====
        self.transaction_manager = TransactionManager()
        self._autocommit = AutoCommit(self)
        self.init_nodes = None
        self.init_edges = None
        self.directories = dict()
        self.parser = Parser.from_node_classes(self.node_classes, log_parse_warnings=config.feature_flags.debug)
        self.extensions = self.node_classes.file_cls.get_extensions()
        # ORDER IS IMPORTANT HERE!
        self.config_parser = get_config_parser_for_language(context.programming_language, self)
        self.dependency_manager = get_dependency_manager(context.programming_language, self)
        self.language_engine = get_language_engine(context.programming_language, self)
        self.programming_language = context.programming_language

        # Build the graph
        self.build_graph(context.repo_operator)
        try:
            self.synced_commit = context.repo_operator.head_commit
        except ValueError as e:
            logger.error("Error getting commit head %s", e)
            self.synced_commit = None
        self.pending_syncs = []
        self.all_syncs = []
        self.pending_files = set()
        self.flags = Flags()

    def __repr__(self):
        return self.__class__.__name__

    @stopwatch_with_sentry(name="build_graph")
    @commiter
    def build_graph(self, repo_operator: RepoOperator) -> None:
        """Builds a codebase graph based on the current file state of the given repo operator"""
        self._graph.clear()

        # =====[ Add all files to the graph in parallel ]=====
        syncs = defaultdict(lambda: [])
        for filepath, _ in repo_operator.iter_files(subdirs=self.projects[0].subdirectories, extensions=self.extensions, ignore_list=GLOBAL_FILE_IGNORE_LIST):
            syncs[SyncType.ADD].append(self.to_absolute(filepath))
        logger.info(f"> Parsing {len(syncs[SyncType.ADD])} files in {self.projects[0].subdirectories} with {self.extensions} extensions")
        self._process_diff_files(syncs, incremental=False)
        files: list[SourceFile] = self.get_nodes(NodeType.FILE)
        logger.info(f"> Found {len(files)} files")
        logger.info(f"> Found {len(self.nodes)} nodes and {len(self.edges)} edges")
        if self.config.feature_flags.track_graph:
            self.old_graph = self._graph.copy()

    @stopwatch
    @commiter
    def apply_diffs(self, diff_list: list[DiffLite]) -> None:
        """Applies the given set of diffs to the graph in order to match the current file system content"""
        if self.session_options:
            self.session_options = self.session_options.model_copy(update={"max_seconds": None})
        logger.info(f"Applying {len(diff_list)} diffs to graph")
        files_to_sync: dict[Path, SyncType] = {}
        # Gather list of deleted files, new files to add, and modified files to reparse
        file_cls = self.node_classes.file_cls
        extensions = file_cls.get_extensions()
        for diff in diff_list:
            filepath = Path(diff.path)
            if extensions is not None and filepath.suffix not in extensions:
                continue
            if self.projects[0].subdirectories is not None and not any(filepath.relative_to(subdir) for subdir in self.projects[0].subdirectories):
                continue

            if diff.change_type == ChangeType.Added:
                # Sync by adding the added file to the graph
                files_to_sync[filepath] = SyncType.ADD
            elif diff.change_type == ChangeType.Modified:
                files_to_sync[filepath] = SyncType.REPARSE
            elif diff.change_type == ChangeType.Renamed:
                files_to_sync[diff.rename_from] = SyncType.DELETE
                files_to_sync[diff.rename_to] = SyncType.ADD
            elif diff.change_type == ChangeType.Removed:
                files_to_sync[filepath] = SyncType.DELETE
            else:
                logger.warning(f"Unhandled diff change type: {diff.change_type}")
        by_sync_type = defaultdict(lambda: [])
        for filepath, sync_type in files_to_sync.items():
            if self.get_file(filepath) is None:
                if sync_type is SyncType.DELETE:
                    # SourceFile is already deleted, nothing to do here
                    continue
                elif sync_type is SyncType.REPARSE:
                    # SourceFile needs to be parsed for the first time
                    sync_type = SyncType.ADD
            elif sync_type is SyncType.ADD:
                # If the file was deleted earlier, we need to reparse so we can remove old edges
                sync_type = SyncType.REPARSE

            by_sync_type[sync_type].append(filepath)
        self.generation += 1
        self._process_diff_files(by_sync_type)

    @stopwatch
    def reset_codebase(self) -> None:
        files = {}
        # Start at the oldest sync and work backwards
        for sync in reversed(self.pending_syncs + self.all_syncs):
            if sync.change_type == ChangeType.Removed:
                files[sync.path] = sync.old_content
            elif sync.change_type == ChangeType.Modified:
                files[sync.path] = sync.old_content
            elif sync.change_type == ChangeType.Renamed:
                files[sync.rename_from] = sync.old_content
                files[sync.rename_to] = None
            elif sync.change_type == ChangeType.Added:
                files[sync.path] = None
        for filepath, content in files.items():
            if content is None:
                filepath.unlink()
            else:
                filepath.write_text(content)

    @stopwatch
    def undo_applied_diffs(self) -> None:
        self.transaction_manager.clear_transactions()
        self.reset_codebase()
        self.check_changes()
        self.pending_syncs.clear()  # Discard pending changes
        if len(self.all_syncs) > 0:
            logger.info(f"Unapplying {len(self.all_syncs)} diffs to graph. Current graph commit: {self.synced_commit}")
            self._revert_diffs(list(reversed(self.all_syncs)))
        self.all_syncs.clear()

    @stopwatch
    @commiter(reset=True)
    def _revert_diffs(self, diff_list: list[DiffLite]) -> None:
        """Resets the graph to its initial solve branch file state"""
        reversed_diff_list = list(DiffLite.from_reverse_diff(diff) for diff in diff_list)
        self._autocommit.reset()
        self.apply_diffs(reversed_diff_list)
        # ====== [ Re-resolve lost edges from previous syncs ] ======
        self.prune_graph()
        if self.config.feature_flags.verify_graph:
            post_reset_validation(self.old_graph.nodes(), self._graph.nodes(), get_edges(self.old_graph), get_edges(self._graph), self.repo_name, self.projects[0].subdirectories)

    def save_commit(self, commit: GitCommit) -> None:
        if commit is not None:
            self.synced_commit = commit
            if self.config.feature_flags.verify_graph:
                self.old_graph = self._graph.copy()

    @stopwatch
    def prune_graph(self) -> None:
        # ====== [ Remove orphaned external modules ] ======
        external_modules = self.get_nodes(NodeType.EXTERNAL)
        for module in external_modules:
            if not any(self.predecessors(module.node_id)):
                self.remove_node(module.node_id)
                self._ext_module_idx.pop(module._idx_key, None)

    def build_directory_tree(self, files: list[SourceFile]) -> None:
        """Builds the directory tree for the codebase"""
        # Reset and rebuild the directory tree
        self.directories = dict()
        for file in files:
            directory = self.get_directory(file.path.parent, create_on_missing=True)
            directory.add_file(file)
            file._set_directory(directory)

    def get_directory(self, directory_path: PathLike, create_on_missing: bool = False, ignore_case: bool = False) -> Directory | None:
        """Returns the directory object for the given path, or None if the directory does not exist.

        If create_on_missing is set, use a recursive strategy to create the directory object and all subdirectories.
        """
        # If not part of repo path, return None
        absolute_path = self.to_absolute(directory_path)
        if not self.is_subdir(absolute_path):
            assert False, f"Directory {absolute_path} is not part of repo path {self.repo_path}"
            return None

        # Get the directory
        if dir := self.directories.get(absolute_path, None):
            return dir
        if ignore_case:
            for path, directory in self.directories.items():
                if str(absolute_path).lower() == str(path).lower():
                    return directory

        # If the directory does not exist, create it
        if create_on_missing:
            # Get the parent directory and create it if it does not exist
            parent_path = absolute_path.parent

            # Base Case
            if str(absolute_path) == str(self.repo_path) or str(absolute_path) == str(parent_path):
                root_directory = Directory(path=absolute_path, dirpath="", parent=None)
                self.directories[absolute_path] = root_directory
                return root_directory

            # Recursively create the parent directory
            parent = self.get_directory(parent_path, create_on_missing=True)
            # Create the directory
            directory = Directory(path=absolute_path, dirpath=str(self.to_relative(absolute_path)), parent=parent)
            # Add the directory to the parent
            parent.add_subdirectory(directory)
            # Add the directory to the tree
            self.directories[absolute_path] = directory
            return directory
        return None

    def _process_diff_files(self, files_to_sync: Mapping[SyncType, list[Path]], incremental: bool = True) -> None:
        # If all the files are empty, don't uncache
        assert self._computing is False
        skip_uncache = incremental and ((len(files_to_sync[SyncType.DELETE]) + len(files_to_sync[SyncType.REPARSE])) == 0)
        if not skip_uncache:
            uncache_all()

        # Step 0: Start the dependency manager and language engine if they exist
        # Start the dependency manager. This may or may not run asynchronously, depending on the implementation
        if self.dependency_manager is not None:
            # Check if its inital start or a reparse
            if not self.dependency_manager.ready() and not self.dependency_manager.error():
                # TODO: We do not reparse dependencies during syncs as it is expensive. We should probably add a flag for this
                logger.info("> Starting dependency manager")
                self.dependency_manager.start(async_start=False)

        # Start the language engine. This may or may not run asynchronously, depending on the implementation
        if self.language_engine is not None:
            # Check if its inital start or a reparse
            if not self.language_engine.ready() and not self.language_engine.error():
                logger.info("> Starting language engine")
                self.language_engine.start(async_start=False)
            else:
                logger.info("> Reparsing language engine")
                self.language_engine.reparse(async_start=False)

        # Step 1: Wait for dependency manager and language engines to finish before graph construction
        if self.dependency_manager is not None:
            self.dependency_manager.wait_until_ready(ignore_error=self.config.feature_flags.ignore_process_errors)
        if self.language_engine is not None:
            self.language_engine.wait_until_ready(ignore_error=self.config.feature_flags.ignore_process_errors)

        # ====== [ Refresh the graph] ========
        # Step 2: For any files that no longer exist, remove them during the sync
        add_to_remove = []
        if incremental:
            for file_path in files_to_sync[SyncType.ADD]:
                if not self.to_absolute(file_path).exists():
                    add_to_remove.append(file_path)
                    logger.warning(f"SYNC: SourceFile {file_path} no longer exists! Removing from graph")
            reparse_to_remove = []
            for file_path in files_to_sync[SyncType.REPARSE]:
                if not self.to_absolute(file_path).exists():
                    reparse_to_remove.append(file_path)
                    logger.warning(f"SYNC: SourceFile {file_path} no longer exists! Removing from graph")
            files_to_sync[SyncType.ADD] = [f for f in files_to_sync[SyncType.ADD] if f not in add_to_remove]
            files_to_sync[SyncType.REPARSE] = [f for f in files_to_sync[SyncType.REPARSE] if f not in reparse_to_remove]
            for file_path in add_to_remove + reparse_to_remove:
                if self.get_file(file_path) is not None:
                    files_to_sync[SyncType.DELETE].append(file_path)
                else:
                    logger.warning(f"SYNC: SourceFile {file_path} does not exist and also not found on graph!")

        # Step 3: Remove files to delete from graph
        to_resolve = []
        for file_path in files_to_sync[SyncType.DELETE]:
            file = self.get_file(file_path)
            file.remove_internal_edges()
            to_resolve.extend(file.unparse())
        to_resolve = list(filter(lambda node: self.has_node(node.node_id) and node is not None, to_resolve))
        for file_path in files_to_sync[SyncType.REPARSE]:
            file = self.get_file(file_path)
            file.remove_internal_edges()

        files_to_resolve = []
        # Step 4: Reparse updated files
        for file_path in files_to_sync[SyncType.REPARSE]:
            file = self.get_file(file_path)
            to_resolve.extend(file.unparse(reparse=True))
            to_resolve = list(filter(lambda node: self.has_node(node.node_id) and node is not None, to_resolve))
            file.sync_with_file_content()
            files_to_resolve.append(file)

        # Step 5: Add new files as nodes to graph (does not yet add edges)
        for filepath in files_to_sync[SyncType.ADD]:
            content = filepath.read_text(errors="ignore")
            # TODO: this is wrong with context changes
            if filepath.suffix in self.extensions:
                file_cls = self.node_classes.file_cls
                new_file = file_cls.from_content(filepath, content, self, sync=False, verify_syntax=False)
                if new_file is not None:
                    files_to_resolve.append(new_file)
        for file in files_to_resolve:
            to_resolve.append(file)
            to_resolve.extend(file.get_nodes())

        to_resolve = list(filter(lambda node: self.has_node(node.node_id) and node is not None, to_resolve))
        counter = Counter(node.node_type for node in to_resolve)

        # Step 6: Build directory tree
        logger.info("> Building directory tree")
        files = [f for f in sort_editables(self.get_nodes(NodeType.FILE), alphabetical=True, dedupe=False)]
        self.build_directory_tree(files)

        # Step 7: Build configs
        if self.config_parser is not None:
            self.config_parser.parse_configs()

        # Step 8: Add internal import resolution edges for new and updated files
        if not skip_uncache:
            uncache_all()
        self._computing = True
        try:
            logger.info(f"> Computing import resolution edges for {counter[NodeType.IMPORT]} imports")
            for node in to_resolve:
                if node.node_type == NodeType.IMPORT:
                    node._remove_internal_edges(EdgeType.IMPORT_SYMBOL_RESOLUTION)
                    node.add_symbol_resolution_edge()
                    to_resolve.extend(node.symbol_usages)
            if counter[NodeType.EXPORT] > 0:
                logger.info(f"> Computing export dependencies for {counter[NodeType.EXPORT]} exports")
                for node in to_resolve:
                    if node.node_type == NodeType.EXPORT:
                        node._remove_internal_edges(EdgeType.EXPORT)
                        node.compute_export_dependencies()
                        to_resolve.extend(node.symbol_usages)
            if counter[NodeType.SYMBOL] > 0:
                from codegen.sdk.core.interfaces.inherits import Inherits

                logger.info("> Computing superclass dependencies")
                for symbol in to_resolve:
                    if isinstance(symbol, Inherits):
                        symbol._remove_internal_edges(EdgeType.SUBCLASS)
                        symbol.compute_superclass_dependencies()

            if not skip_uncache:
                uncache_all()
            self._compute_dependencies(to_resolve, incremental)
        finally:
            self._computing = False

    def _compute_dependencies(self, to_update: list[Importable], incremental: bool):
        seen = set()
        while to_update:
            step = to_update.copy()
            to_update.clear()
            logger.info(f"> Incrementally computing dependencies for {len(step)} nodes")
            for current in step:
                if current not in seen:
                    seen.add(current)
                    to_update.extend(current.recompute(incremental))
            if not incremental:
                for node in self._graph.nodes():
                    if node not in seen:
                        to_update.append(node)
        seen.clear()

    def build_subgraph(self, nodes: list[NodeId]) -> PyDiGraph[Importable, Edge]:
        """Builds a subgraph from the given set of nodes"""
        subgraph = PyDiGraph()
        subgraph.add_nodes_from(self._graph.nodes())
        subgraph.add_edges_from(self._graph.weighted_edge_list())
        return subgraph.subgraph(nodes)

    def get_node(self, node_id: int) -> Any:
        return self._graph.get_node_data(node_id)

    def get_nodes(self, node_type: NodeType | None = None, exclude_type: NodeType | None = None) -> list[Importable]:
        if node_type is not None and exclude_type is not None:
            raise ValueError("node_type and exclude_type cannot both be specified")
        if node_type is not None:
            return [self.get_node(node_id) for node_id in self._graph.filter_nodes(lambda node: node.node_type == node_type)]
        if exclude_type is not None:
            return [self.get_node(node_id) for node_id in self._graph.filter_nodes(lambda node: node.node_type != node_type)]
        return self._graph.nodes()

    def get_edges(self) -> list[tuple[NodeId, NodeId, EdgeType, Usage | None]]:
        return [(x[0], x[1], x[2].type, x[2].usage) for x in self._graph.weighted_edge_list()]

    def get_file(self, file_path: os.PathLike, ignore_case: bool = False) -> SourceFile | None:
        node_id = self.filepath_idx.get(str(self.to_relative(file_path)), None)
        if node_id is not None:
            return self.get_node(node_id)
        if ignore_case:
            parent = self.to_absolute(file_path).parent
            if parent == Path(self.repo_path):
                for file in self.to_absolute(self.repo_path).iterdir():
                    if str(file_path).lower() == str(self.to_absolute(file)).lower():
                        return self.get_file(file, ignore_case=False)
            if directory := self.get_directory(parent, ignore_case=ignore_case):
                return directory.get_file(os.path.basename(file_path), ignore_case=ignore_case)

    def get_external_module(self, module: str, import_name: str) -> ExternalModule | None:
        node_id = self._ext_module_idx.get(module + "::" + import_name, None)
        if node_id is not None:
            return self.get_node(node_id)

    def add_node(self, node: Importable) -> int:
        if self.config.feature_flags.debug:
            if self._graph.find_node_by_weight(node.__eq__):
                raise Exception("Node already exists")
        if self.config.feature_flags.debug and self._computing and node.node_type != NodeType.EXTERNAL:
            assert False, f"Adding node during compute dependencies: {node!r}"
        return self._graph.add_node(node)

    def add_child(self, parent: NodeId, node: Importable, type: EdgeType, usage: Usage | None = None) -> int:
        if self.config.feature_flags.debug:
            if self._graph.find_node_by_weight(node.__eq__):
                raise Exception("Node already exists")
        if self.config.feature_flags.debug and self._computing and node.node_type != NodeType.EXTERNAL:
            assert False, f"Adding node during compute dependencies: {node!r}"
        return self._graph.add_child(parent, node, Edge(type, usage))

    def has_node(self, node_id: NodeId):
        return isinstance(node_id, int) and self._graph.has_node(node_id)

    def has_edge(self, u: NodeId, v: NodeId, edge: Edge):
        return self._graph.has_edge(u, v) and edge in self._graph.get_all_edge_data(u, v)

    def add_edge(self, u: NodeId, v: NodeId, type: EdgeType, usage: Usage | None = None) -> None:
        edge = Edge(type, usage)
        if self.config.feature_flags.debug:
            assert self._graph.has_node(u)
            assert self._graph.has_node(v), v
            assert not self.has_edge(u, v, edge), (u, v, edge)
        self._graph.add_edge(u, v, edge)

    def add_edges(self, edges: list[tuple[NodeId, NodeId, Edge]]) -> None:
        if self.config.feature_flags.debug:
            for u, v, edge in edges:
                assert self._graph.has_node(u)
                assert self._graph.has_node(v), v
                assert not self.has_edge(u, v, edge), (self.get_node(u), self.get_node(v), edge)
        self._graph.add_edges_from(edges)

    @property
    def nodes(self):
        return self._graph.nodes()

    @property
    def edges(self) -> WeightedEdgeList[Edge]:
        return self._graph.weighted_edge_list()

    def predecessor(self, n: NodeId, *, edge_type: EdgeType | None) -> Importable:
        return self._graph.find_predecessor_node_by_edge(n, lambda edge: edge.type == edge_type)

    def predecessors(self, n: NodeId, edge_type: EdgeType | None = None) -> Sequence[Importable]:
        if edge_type is not None:
            return sort_editables(self._graph.find_predecessors_by_edge(n, lambda edge: edge.type == edge_type), by_id=True)
        return self._graph.predecessors(n)

    def successors(self, n: NodeId, *, edge_type: EdgeType | None = None, sort: bool = True) -> Sequence[Importable]:
        if edge_type is not None:
            res = self._graph.find_successors_by_edge(n, lambda edge: edge.type == edge_type)
        else:
            res = self._graph.successors(n)
        if sort:
            return sort_editables(res, by_id=True, dedupe=False)
        return res

    def get_edge_data(self, *args, **kwargs) -> set[Edge]:
        return set(self._graph.get_all_edge_data(*args, **kwargs))

    def in_edges(self, n: NodeId) -> WeightedEdgeList[Edge]:
        return self._graph.in_edges(n)

    def out_edges(self, n: NodeId) -> WeightedEdgeList[Edge]:
        return self._graph.out_edges(n)

    def remove_node(self, n: NodeId):
        return self._graph.remove_node(n)

    def remove_edge(self, u: NodeId, v: NodeId, *, edge_type: EdgeType | None = None):
        for edge in self._graph.edge_indices_from_endpoints(u, v):
            if edge_type is not None:
                if self._graph.get_edge_data_by_index(edge).type != edge_type:
                    continue
            self._graph.remove_edge_from_index(edge)

    def check_changes(self) -> None:
        for file in self.pending_files:
            file.check_changes()
        self.pending_files.clear()

    def write_files(self, files: set[Path] | None = None) -> None:
        to_write = set(filter(lambda f: f.filepath in files, self.pending_files)) if files is not None else self.pending_files
        with ThreadPoolExecutor() as exec:
            exec.map(lambda f: f.write_pending_content(), to_write)
        self.pending_files.difference_update(to_write)

    @lru_cache(maxsize=10000)
    def to_absolute(self, filepath: PathLike | str) -> Path:
        path = Path(filepath)
        if not path.is_absolute():
            path = Path(self.repo_path) / path
        return path.resolve()

    @lru_cache(maxsize=10000)
    def to_relative(self, filepath: PathLike | str) -> Path:
        path = self.to_absolute(filepath)
        if path == Path(self.repo_path) or Path(self.repo_path) in path.parents:
            return path.relative_to(self.repo_path)
        return path

    def is_subdir(self, path: PathLike | str) -> bool:
        path = self.to_absolute(path)
        return path == Path(self.repo_path) or path.is_relative_to(self.repo_path) or Path(self.repo_path) in path.parents

    @commiter
    def commit_transactions(self, sync_graph: bool = True, sync_file: bool = True, files: set[Path] | None = None) -> None:
        """Commits all transactions to the codebase, and syncs the graph to match the latest file changes.
        Should be called at the end of `execute` for every codemod group run.

        Arguments:
            sync_graph (bool): If True, syncs the graph with the latest set of file changes
            sync_file (bool): If True, writes any pending file edits to the file system
            files (set[str] | None): If provided, only commits transactions for the given set of files
        """
        # Commit transactions for all contexts
        files_to_lock = self.transaction_manager.to_commit(files)
        diffs = self.transaction_manager.commit(files_to_lock)
        # Filter diffs to only include files that are still in the graph
        diffs = [diff for diff in diffs if self.get_file(diff.path) is not None]
        self.pending_syncs.extend(diffs)

        # Write files if requested
        if sync_file:
            self.write_files(files)

        # Sync the graph if requested
        if sync_graph and len(self.pending_syncs) > 0:
            self.apply_diffs(self.pending_syncs)
            self.all_syncs.extend(self.pending_syncs)
            self.pending_syncs.clear()

    @commiter
    def add_single_file(self, filepath: PathLike) -> None:
        """Adds a file to the graph and computes it's dependencies"""
        sync = DiffLite(ChangeType.Added, self.to_absolute(filepath))
        self.all_syncs.append(sync)
        self.apply_diffs([sync])
        self.transaction_manager.check_limits()

    @contextmanager
    def session(self, sync_graph: bool = True, commit: bool = True, session_options: SessionOptions = SessionOptions()) -> Generator[None, None, None]:
        self.session_options = session_options
        self.transaction_manager.set_max_transactions(self.session_options.max_transactions)
        self.transaction_manager.reset_stopwatch(self.session_options.max_seconds)
        try:
            yield None
        except StopCodemodException as e:
            logger.info(f"{e}, committing transactions and resetting graph")
            raise
        finally:
            if commit:
                self.commit_transactions(sync_graph)

    def remove_directory(self, directory_path: PathLike, force: bool = False, cleanup: bool = True) -> None:
        """Removes a directory from the graph"""
        # Get the directory
        directory = self.get_directory(directory_path)

        # Check errors
        if directory is None:
            raise ValueError(f"Directory {directory_path} does not exist")
        if not force and len(directory.items) > 0:
            raise ValueError(f"Directory {directory_path} is not empty")

        # Remove the directory from the tree
        if str(directory_path) in self.directories:
            del self.directories[str(directory_path)]

        # Remove the directory from the parent
        if directory.parent is not None:
            directory.parent.remove_subdirectory(directory)
            # Cleanup
            if cleanup and len(directory.parent.items) == 0:
                self.remove_directory(directory.parent.path, cleanup=cleanup)

    ####################################################################################################################
    # EXTERNAL UTILS
    ####################################################################################################################

    _ts_declassify: TSDeclassify | None = None

    @property
    def ts_declassify(self) -> TSDeclassify:
        if self._ts_declassify is None:
            self._ts_declassify = TSDeclassify(self.repo_path, self.projects[0].base_path)
            self._ts_declassify.start()  # Install react-declassify
        return self._ts_declassify
