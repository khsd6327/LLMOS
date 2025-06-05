# ted-os-project/src/llmos/utils/output_renderer.py
# src/llmos/utils/output_renderer.py
"""
LLM OS - 출력 렌더러
"""

import re
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OutputRenderer:
    """AI 출력 텍스트 렌더링 및 후처리"""

    def __init__(self):
        self.post_processors = [
            self._clean_whitespace,
            self._fix_markdown_formatting,
            self._enhance_code_blocks,
            self._fix_list_formatting,
        ]

    def process_output(self, text: str) -> str:
        """텍스트 후처리"""
        if not text:
            return text

        processed_text = text

        for processor in self.post_processors:
            try:
                processed_text = processor(processed_text)
            except Exception as e:
                logger.warning(f"Error in post-processor {processor.__name__}: {e}")

        return processed_text

    def _clean_whitespace(self, text: str) -> str:
        """공백 정리"""
        # 연속된 빈 줄 제거 (최대 2개까지만 허용)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 줄 끝 공백 제거
        lines = text.split("\n")
        cleaned_lines = [line.rstrip() for line in lines]

        return "\n".join(cleaned_lines)

    def _fix_markdown_formatting(self, text: str) -> str:
        """마크다운 형식 수정"""
        # 제목 앞뒤 공백 정리
        text = re.sub(r"\n(#+)\s*([^\n]+)\s*\n", r"\n\1 \2\n\n", text)

        # 목록 항목 들여쓰기 정리
        text = re.sub(r"\n(\s*)([-*+])\s+", r"\n\1\2 ", text)

        # 코드 블록 정리
        text = re.sub(r"```(\w+)?\n\n+", r"```\1\n", text)
        text = re.sub(r"\n\n+```", r"\n```", text)

        return text

    def _enhance_code_blocks(self, text: str) -> str:
        """코드 블록 개선"""
        # 인라인 코드 정리
        text = re.sub(r"`\s+([^`]+)\s+`", r"`\1`", text)

        # 코드 블록 언어 지정 개선
        def improve_code_lang(match):
            lang = match.group(1) or ""
            code = match.group(2)

            # 언어 추론
            if not lang and code:
                if "def " in code or "import " in code or "print(" in code:
                    lang = "python"
                elif "function " in code or "const " in code or "let " in code:
                    lang = "javascript"
                elif (
                    "<" in code
                    and ">" in code
                    and ("html" in code.lower() or "div" in code.lower())
                ):
                    lang = "html"
                elif (
                    "{" in code
                    and "}" in code
                    and ("background" in code or "color" in code)
                ):
                    lang = "css"

            return f"```{lang}\n{code}\n```"

        text = re.sub(
            r"```(\w+)?\n(.*?)\n```", improve_code_lang, text, flags=re.DOTALL
        )

        return text

    def _fix_list_formatting(self, text: str) -> str:
        """목록 형식 수정"""
        lines = text.split("\n")
        fixed_lines = []

        for i, line in enumerate(lines):
            # 번호 목록 정리
            if re.match(r"^\s*\d+\.\s+", line):
                # 앞에 빈 줄이 없고 이전 줄이 목록이 아니면 빈 줄 추가
                if (
                    i > 0
                    and lines[i - 1].strip()
                    and not re.match(r"^\s*\d+\.\s+", lines[i - 1])
                    and not re.match(r"^\s*[-*+]\s+", lines[i - 1])
                ):
                    fixed_lines.append("")

            # 불릿 목록 정리
            elif re.match(r"^\s*[-*+]\s+", line):
                # 앞에 빈 줄이 없고 이전 줄이 목록이 아니면 빈 줄 추가
                if (
                    i > 0
                    and lines[i - 1].strip()
                    and not re.match(r"^\s*\d+\.\s+", lines[i - 1])
                    and not re.match(r"^\s*[-*+]\s+", lines[i - 1])
                ):
                    fixed_lines.append("")

            fixed_lines.append(line)

        return "\n".join(fixed_lines)

    def add_post_processor(self, processor_func):
        """사용자 정의 후처리 함수 추가"""
        self.post_processors.append(processor_func)

    def remove_post_processor(self, processor_func):
        """후처리 함수 제거"""
        if processor_func in self.post_processors:
            self.post_processors.remove(processor_func)

    def render_with_metadata(
        self, text: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """메타데이터와 함께 렌더링"""
        processed_text = self.process_output(text)

        result = {
            "content": processed_text,
            "original_length": len(text),
            "processed_length": len(processed_text),
            "has_code_blocks": "```" in processed_text,
            "has_lists": bool(
                re.search(r"^\s*[-*+\d]+\.\s+", processed_text, re.MULTILINE)
            ),
            "has_headers": bool(re.search(r"^#+\s+", processed_text, re.MULTILINE)),
        }

        if metadata:
            result["metadata"] = metadata

        return result


class SpecializedRenderer(OutputRenderer):
    """특수 용도 렌더러"""

    def __init__(self, output_type: str = "markdown"):
        super().__init__()
        self.output_type = output_type

        if output_type == "html":
            self.post_processors.append(self._markdown_to_html_basic)
        elif output_type == "plain":
            self.post_processors.append(self._strip_markdown)

    def _markdown_to_html_basic(self, text: str) -> str:
        """기본적인 마크다운 → HTML 변환"""
        # 헤더
        text = re.sub(r"^### (.+)$", r"<h3>\1</h3>", text, flags=re.MULTILINE)
        text = re.sub(r"^## (.+)$", r"<h2>\1</h2>", text, flags=re.MULTILINE)
        text = re.sub(r"^# (.+)$", r"<h1>\1</h1>", text, flags=re.MULTILINE)

        # 굵게, 기울임
        text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
        text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)

        # 인라인 코드
        text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)

        # 줄바꿈
        text = text.replace("\n", "<br>\n")

        return text

    def _strip_markdown(self, text: str) -> str:
        """마크다운 형식 제거"""
        # 헤더
        text = re.sub(r"^#+\s+(.+)$", r"\1", text, flags=re.MULTILINE)

        # 굵게, 기울임
        text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
        text = re.sub(r"\*(.+?)\*", r"\1", text)

        # 인라인 코드
        text = re.sub(r"`(.+?)`", r"\1", text)

        # 코드 블록
        text = re.sub(r"```[\w]*\n(.*?)\n```", r"\1", text, flags=re.DOTALL)

        # 목록
        text = re.sub(r"^\s*[-*+]\s+", "• ", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

        return text
