use std::io::{self, BufRead, Write};

mod commands;
use commands::handle_input;

fn main() {
    let stdin = io::stdin();
    print!("> ");
    io::stdout().flush().unwrap();

    for line in stdin.lock().lines() {
        let input = line.unwrap();
        let trimmed = input.trim();

        if let Some(response) = handle_input(trimmed) {
            println!("{}", response);
            if trimmed == "/종료" {
                break;
            }
        }

        print!("> ");
        io::stdout().flush().unwrap();
    }
}
