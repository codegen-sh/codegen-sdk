use clap::Parser;
use codegen_sdk_cst::{parse_file_typescript, typescript};
use glob::glob;
use rayon::prelude::*;
use std::error::Error;
use std::{path, time::Instant};
use sysinfo::{Pid, Process, System};
#[derive(Debug, Parser)]
struct Args {
    input: String,
}
fn main() {
    rayon::ThreadPoolBuilder::new()
        .stack_size(1024 * 1024 * 1024 * 10)
        .build_global()
        .unwrap();
    let args = Args::parse();
    let dir = args.input;
    let mut errors = Vec::new();
    let (tx, rx) = crossbeam::channel::unbounded();
    let start = Instant::now();
    let files_to_parse: Vec<Result<path::PathBuf, glob::GlobError>> =
        glob(&format!("{}/**/*.ts", dir)).unwrap().collect();

    let files: Vec<Box<typescript::Program>> = files_to_parse
        .par_iter()
        .filter_map(|file| {
            if let Ok(file) = file {
                if file.is_dir() {
                    return None;
                }
                return match parse_file_typescript(file.to_str().unwrap()) {
                    Ok(program) => Some(program),
                    Err(e) => {
                        tx.send(()).unwrap();
                        None
                    }
                };
            }
            return None;
        })
        .collect();
    let end = Instant::now();
    let duration: std::time::Duration = end.duration_since(start);
    drop(tx);
    for e in rx.iter() {
        errors.push(e);
    }
    let s = System::new_all();
    let current = s.process(sysinfo::get_current_pid().unwrap()).unwrap();
    let memory = current.memory();
    println!(
        "{} files parsed in {:?}.{} seconds with {} errors. Using {} MB of memory",
        files.len(),
        duration.as_secs(),
        duration.subsec_millis(),
        errors.len(),
        memory / 1024 / 1024
    );
}
