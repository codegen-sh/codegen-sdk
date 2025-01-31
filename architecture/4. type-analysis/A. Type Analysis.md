# Type Analysis

The type analysis system builds a complete understanding of types and symbols across the codebase.

## Basic flow

- Discover names that need to be resolved
- Resolve names
- Convert resolutions into graph edges

## The resolution stack

To accomplish this, we have an in house computation engine - the ResolutionStack. Each stack frame contains a reference to it's parent frame. However, a parent can have multiple child frames (IE: Union Types).

When we resolve types on a node, we call resolved_type_frames to get the resolved types. Once we know what goes in the next frame, we call with_resolution_frame to construct the next frame. This is a generator that yields the next frame until we've resolved all the types. Resolved_type_frames is a property caches a list of the generated frames.
Therefore, once you have computed type resolution on a node, you don't need to recompute it. That way, we can start at arbitrary nodes without performance overhead.

This is similar to how other's implement incremental computation engines with a few weaknesses:

- There is only 1 query in the query engine
- Partial cache invalidation isn't implemented

## Next Step

After understanding the type analysis system overview, let's look at how we [walk the syntax tree](./B.%20Tree%20Walking.md) to analyze code structure.
