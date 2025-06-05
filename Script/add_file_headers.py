# ted-os-project/Script/add_file_headers.py
import os
import subprocess
import sys

def get_git_tracked_files(project_root):
    """Git이 추적하는 파일 목록을 반환합니다."""
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Git 파일 목록을 가져오는 중 오류 발생: {e}", file=sys.stderr)
        return []
    except FileNotFoundError:
        print("오류: Git 명령어를 찾을 수 없습니다. Git이 설치되어 있고 PATH에 등록되어 있는지 확인하세요.", file=sys.stderr)
        return []

def add_header_to_file(file_path_relative, project_root_abs, comment_start, comment_end):
    """파일에 '<comment_start> project-name/path <comment_end>' 형식의 헤더를 추가합니다."""
    try:
        abs_file_path = os.path.join(project_root_abs, file_path_relative)
        
        # 프로젝트 이름 얻기
        project_name = os.path.basename(project_root_abs)
        
        # 헤더에 사용될 경로는 일관성을 위해 슬래시(/)를 사용합니다.
        header_path = f"{project_name}/{file_path_relative.replace(os.sep, '/')}"
        
        # 주석 라인 생성
        if comment_end: # 블록 주석 (예: /* ... */, )
            header_comment_line = f"{comment_start} {header_path} {comment_end}"
        else: # 한 줄 주석 (예: # ..., // ...)
            header_comment_line = f"{comment_start} {header_path}"

        with open(abs_file_path, 'r+', encoding='utf-8') as f:
            lines = f.readlines()
            
            header_exists = False
            if lines: # 파일이 비어있지 않은 경우
                # 첫 줄에 이미 해당 접두사로 시작하는 헤더가 있는지 확인
                if lines[0].strip().startswith(f"{comment_start} {project_name}/"):
                    header_exists = True
            
            if not header_exists:
                new_lines = [header_comment_line + '\n']
                new_lines.extend(lines)
                
                f.seek(0)
                f.writelines(new_lines)
                f.truncate()
                print(f"헤더 추가 완료: {file_path_relative}")
            else:
                print(f"헤더 이미 존재: {file_path_relative}")

    except FileNotFoundError:
        print(f"오류: 파일을 찾을 수 없습니다 - {file_path_relative}", file=sys.stderr)
    except UnicodeDecodeError:
        print(f"오류: UTF-8로 디코딩할 수 없는 파일입니다 - {file_path_relative}. (예: 바이너리 파일)", file=sys.stderr)
    except Exception as e:
        print(f"파일 처리 중 오류 발생 {file_path_relative}: {e}", file=sys.stderr)

def main():
    # 스크립트가 위치한 디렉토리의 부모 디렉토리를 프로젝트 루트로 가정합니다.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    os.chdir(project_root) # 스크립트 실행 위치를 프로젝트 루트로 변경
    print(f"프로젝트 루트에서 스크립트 실행 중: {project_root}")

    file_handlers = {
        ".py": ("#", ""),           # Python
        ".js": ("//", ""),          # JavaScript
        ".ts": ("//", ""),          # TypeScript
        ".svelte": ("<!--", "-->"), # Svelte
        ".css": ("/*", "*/"),       # CSS
        ".html": ("<!--", "-->"),   # HTML
    }
    
    # 지원되는 확장자 목록을 정렬하여 사용자에게 보여주기 위함
    supported_extensions_str = ", ".join(sorted(list(file_handlers.keys())))

    # 사용자 확인 메시지 업데이트
    confirm_message = (
        "주의: 이 스크립트는 Git이 추적하는 파일들 중 다음 확장자를 가진 파일에\n"
        f"헤더 주석을 추가하려고 시도합니다: {supported_extensions_str}\n"
        "JSON 파일과 같이 주석을 지원하지 않거나 위 목록에 없는 다른 확장자 파일은 건너뜁니다.\n"
        "스크립트 실행 전에 현재 변경사항을 모두 커밋했는지 확인하세요.\n"
        "계속 진행하시겠습니까? (yes/no): "
    )
    confirm = input(confirm_message)
    if confirm.lower() != 'yes':
        print("사용자에 의해 작업이 취소되었습니다.")
        return

    tracked_files = get_git_tracked_files(project_root)
    if not tracked_files:
        print("Git이 추적하는 파일을 찾을 수 없거나 오류가 발생했습니다.")
        return

    print(f"\n총 {len(tracked_files)}개의 Git 추적 파일을 찾았습니다. 지원되는 파일에 대해 헤더 추가/확인 작업을 시작합니다...")
    processed_files_count = 0
    skipped_files_count = 0

    for file_path_rel in tracked_files:
        file_name, file_ext = os.path.splitext(file_path_rel)
        file_ext = file_ext.lower() # 확장자를 소문자로 통일하여 비교

        if file_ext in file_handlers:
            comment_start, comment_end = file_handlers[file_ext]
            add_header_to_file(file_path_rel, project_root, comment_start, comment_end)
            processed_files_count += 1
        else:
            # 지원 목록에 없는 파일은 건너뜀 (예: .json, 이미지 파일 등)
            skipped_files_count += 1
            # 어떤 파일이 건너뛰어졌는지 상세히 보고 싶다면 아래 주석을 해제하세요.
            # print(f"지원 목록에 없어 건너뛴 파일: {file_path_rel}")

    print(f"\n총 {processed_files_count}개의 지원되는 파일에 대해 헤더 작업 시도 완료.")
    if skipped_files_count > 0:
        print(f"{skipped_files_count}개의 파일은 지원 목록에 없어 건너뛰었습니다 (예: JSON, 이미지, 문서 파일 등).")
    print("스크립트 실행이 끝났습니다. VS Code의 Git 변경사항을 통해 결과를 확인해주세요.")

if __name__ == "__main__":
    main()