use std::io::{self, BufRead, Write};

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

/// 커맨드 입력을 처리한다.
/// `/`로 시작하는 커맨드면 Some(응답), 일반 텍스트면 None 반환.
fn handle_input(input: &str) -> Option<String> {
    if !input.starts_with('/') {
        return None;
    }
    let response = match input {
        "/시나리오"   => "시나리오를 작성합니다".to_string(),
        "/런시나리오" => "테스트를 수행합니다".to_string(),
        "/종료"       => "종료합니다.".to_string(),
        other         => format!("알 수 없는 커맨드: {}", other),
    };
    Some(response)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_시나리오() {
        assert_eq!(
            handle_input("/시나리오"),
            Some("시나리오를 작성합니다".to_string())
        );
    }

    #[test]
    fn test_런시나리오() {
        assert_eq!(
            handle_input("/런시나리오"),
            Some("테스트를 수행합니다".to_string())
        );
    }

    #[test]
    fn test_종료() {
        assert_eq!(
            handle_input("/종료"),
            Some("종료합니다.".to_string())
        );
    }

    #[test]
    fn test_알수없는_커맨드() {
        assert_eq!(
            handle_input("/없는커맨드"),
            Some("알 수 없는 커맨드: /없는커맨드".to_string())
        );
    }

    #[test]
    fn test_일반_텍스트는_무시() {
        assert_eq!(handle_input("안녕"), None);
        assert_eq!(handle_input("hello world"), None);
        assert_eq!(handle_input(""), None);
    }
}
