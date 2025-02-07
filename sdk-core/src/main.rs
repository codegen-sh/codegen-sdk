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
        .num_threads(10)
        .stack_size(1024 * 1024 * 1024 * 10)
        .build_global()
        .unwrap();
    let args = Args::parse();
    let dir = args.input;
    let mut errors: Vec<Box<dyn Error>> = Vec::new();
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
                return parse_file_typescript(file.to_str().unwrap()).ok();
            }
            return None;
        })
        .collect();
    let end = Instant::now();
    let duration: std::time::Duration = end.duration_since(start);
    let s = System::new_all();
    let current = s.process(sysinfo::get_current_pid().unwrap()).unwrap();
    let memory = current.memory();
    println!(
        "{} files parsed in {:?} seconds with {} errors. Using {} MB of memory",
        files.len(),
        duration.as_secs(),
        errors.len(),
        memory / 1024 / 1024
    );
}
