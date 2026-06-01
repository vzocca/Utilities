# -*- coding: utf-8 -*-
"""
Created on Thu May 14 19:10:47 2026

@author: vzocc
"""

"""
Document Validity & Issues Chatbot
Uses Claude API to analyze uploaded documents and discuss their validity and issues.

Supported file types: PDF, TXT, MD, CSV, JSON, PY, JS, HTML, XML, DOCX (text extraction)

Usage:
    pip install anthropic python-dotenv pypdf python-docx
    export ANTHROPIC_API_KEY=your_key_here
    python doc_chatbot.py
"""

import os
import sys
import base64
import mimetypes
from pathlib import Path

# ── Dependencies ──────────────────────────────────────────────────────────────
try:
    import anthropic
except ImportError:
    sys.exit("Missing dependency. Run:  pip install anthropic")

# ── Constants ─────────────────────────────────────────────────────────────────
# Anthropic API key stored in a dedicated key file
with open("anthropic/anthropic.key") as f:
    ANTHROPIC_API_KEY = f.read().strip()
    
MODEL = "claude-sonnet-4-20250514"
MAX_TOKENS = 4096

SYSTEM_PROMPT = """You are an expert document analyst specializing in identifying validity issues, 
logical inconsistencies, factual errors, structural problems, and potential risks in documents.

When analyzing documents, you evaluate:
- **Factual accuracy** – Are claims supported by evidence? Are there contradictions?
- **Logical consistency** – Does the reasoning flow coherently? Are there gaps or fallacies?
- **Structural integrity** – Is the document well-organized and complete?
- **Compliance & legal issues** – Are there regulatory or legal red flags?
- **Clarity & ambiguity** – Are terms defined? Is language precise?
- **Data validity** – Are figures, citations, and references accurate and consistent?
- **Risk areas** – What could go wrong if this document is acted upon?

Be specific, cite the relevant sections, and provide actionable recommendations.
When the user asks follow-up questions, refer back to the loaded document(s) in context."""

TEXT_EXTENSIONS = {
    ".txt", ".md", ".csv", ".json", ".xml", ".html", ".htm",
    ".py", ".js", ".ts", ".java", ".cpp", ".c", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".rst", ".tex", ".sql",
}

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_file(path: str) -> dict:
    """
    Load a file and return an Anthropic content block.
    Supports: PDF (native), plain text, and DOCX (text extraction).
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = p.suffix.lower()

    # ── PDF → native document block ──────────────────────────────────────────
    if ext == ".pdf":
        raw = p.read_bytes()
        return {
            "type": "document",
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": base64.standard_b64encode(raw).decode("utf-8"),
            },
            "title": p.name,
            "context": "Uploaded PDF document for analysis.",
        }

    # ── DOCX → extract text ──────────────────────────────────────────────────
    if ext == ".docx":
        try:
            from docx import Document as DocxDocument
        except ImportError:
            raise ImportError("Install python-docx to read .docx files:  pip install python-docx")
        doc = DocxDocument(str(p))
        text = "\n".join(para.text for para in doc.paragraphs if para.text.strip())
        return {
            "type": "text",
            "text": f"[Document: {p.name}]\n\n{text}",
        }

    # ── Plain text / code / data files ──────────────────────────────────────
    if ext in TEXT_EXTENSIONS or mimetypes.guess_type(str(p))[0] in ("text/plain", None):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            return {
                "type": "text",
                "text": f"[Document: {p.name}]\n\n{text}",
            }
        except Exception as e:
            raise ValueError(f"Cannot read file as text: {e}")

    raise ValueError(
        f"Unsupported file type '{ext}'. Supported: PDF, DOCX, TXT, MD, CSV, JSON, "
        "XML, HTML, PY, JS, and other plain-text formats."
    )


def format_size(path: str) -> str:
    size = Path(path).stat().st_size
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} GB"


def print_banner():
    print("\n" + "=" * 60)
    print("  📄  Document Validity & Issues Chatbot")
    print("  Powered by Claude AI")
    print("=" * 60)
    print("\nCommands:")
    print("  /upload <path>   – Load a document into the session")
    print("  /docs            – List loaded documents")
    print("  /clear           – Clear conversation history")
    print("  /reset           – Clear documents + history")
    print("  /help            – Show this help")
    print("  /quit            – Exit\n")


def print_separator():
    print("\n" + "─" * 60 + "\n")

# ── Main chatbot ──────────────────────────────────────────────────────────────

def main():
    api_key = ANTHROPIC_API_KEY
    if not api_key:
        sys.exit(
            "Error: ANTHROPIC_API_KEY environment variable not set.\n"
            "Export it with:  export ANTHROPIC_API_KEY=your_key_here"
        )

    client = anthropic.Anthropic(api_key=api_key)

    # Conversation state
    conversation_history: list[dict] = []   # full message history
    loaded_docs: list[dict] = []            # content blocks for documents
    doc_names: list[str] = []               # human-readable doc names

    print_banner()

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\nGoodbye!")
            break

        if not user_input:
            continue

        # ── Commands ──────────────────────────────────────────────────────────
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()

            if cmd == "/quit":
                print("Goodbye!")
                break

            elif cmd == "/help":
                print_banner()

            elif cmd == "/docs":
                if doc_names:
                    print(f"\nLoaded documents ({len(doc_names)}):")
                    for i, name in enumerate(doc_names, 1):
                        print(f"  {i}. {name}")
                    print()
                else:
                    print("\nNo documents loaded. Use /upload <path> to add one.\n")

            elif cmd == "/clear":
                conversation_history.clear()
                print("\n✓ Conversation history cleared. Documents are still loaded.\n")

            elif cmd == "/reset":
                conversation_history.clear()
                loaded_docs.clear()
                doc_names.clear()
                print("\n✓ Session reset. All documents and history cleared.\n")

            elif cmd == "/upload":
                if len(parts) < 2 or not parts[1].strip():
                    print("\nUsage: /upload <path-to-file>\n")
                    continue
                file_path = parts[1].strip().strip('"').strip("'")
                try:
                    block = load_file(file_path)
                    loaded_docs.append(block)
                    name = Path(file_path).name
                    doc_names.append(f"{name} ({format_size(file_path)})")
                    print(f"\n✓ Loaded: {name} ({format_size(file_path)})")
                    print("  Type a question or ask me to analyze it.\n")
                except (FileNotFoundError, ValueError, ImportError) as e:
                    print(f"\n✗ Error loading file: {e}\n")

            else:
                print(f"\nUnknown command: {cmd}. Type /help for available commands.\n")

            continue

        # ── Build message with optional document context ───────────────────
        # Documents are prepended to the first human turn of each request
        # so Claude always has them in context.
        user_content: list = []

        if loaded_docs and not conversation_history:
            # First turn: attach all documents
            user_content.extend(loaded_docs)
            user_content.append({
                "type": "text",
                "text": (
                    f"I have uploaded {len(loaded_docs)} document(s) for analysis: "
                    f"{', '.join(doc_names)}.\n\n{user_input}"
                ),
            })
        elif loaded_docs and conversation_history:
            # Subsequent turns: documents already in history; just send text
            user_content.append({"type": "text", "text": user_input})
        else:
            if not loaded_docs:
                print(
                    "\n⚠  No documents loaded. You can chat generally, or use "
                    "/upload <path> to add a document.\n"
                )
            user_content.append({"type": "text", "text": user_input})

        conversation_history.append({"role": "user", "content": user_content})

        # ── Call Claude API ────────────────────────────────────────────────
        try:
            print("\nClaude: ", end="", flush=True)

            response_text = ""
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                system=SYSTEM_PROMPT,
                messages=conversation_history,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    response_text += text

            print()  # newline after streaming

            # Save assistant reply to history
            conversation_history.append({
                "role": "assistant",
                "content": response_text,
            })

            print_separator()

        except anthropic.AuthenticationError:
            print("\n✗ Authentication failed. Check your ANTHROPIC_API_KEY.\n")
        except anthropic.RateLimitError:
            print("\n✗ Rate limit reached. Please wait a moment and try again.\n")
        except anthropic.BadRequestError as e:
            print(f"\n✗ Bad request: {e}\n")
            # Remove the failed user message from history
            conversation_history.pop()
        except anthropic.APIError as e:
            print(f"\n✗ API error: {e}\n")
            conversation_history.pop()


if __name__ == "__main__":
    main()