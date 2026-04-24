from pathlib import Path 
import json

def json_blocks_to_markdown(blocks):
    md = []
    in_list = False

    for block in sorted(blocks, key=lambda x: x.get("index", 0)):
        btype = block.get("type")
        text = block.get("text", "").strip()

        if not text:
            continue

        # ---- TITLE ----
        if btype == "title":
            if in_list:
                md.append("")  # close list
                in_list = False
            md.append(f"\n## {text}\n")

        # ---- LIST ITEMS ----
        elif btype == "list_item":
            if not in_list:
                md.append("")  # spacing before list
                in_list = True
            md.append(f"- {text}")

        # ---- NARRATIVE TEXT ----
        elif btype == "narrative_text":
            if in_list:
                md.append("")  # close list
                in_list = False

            # naive code detection (you can improve this later)
            if looks_like_code(text):
                md.append("\n```go")
                md.append(text)
                md.append("```\n")
            else:
                md.append(f"{text}\n")

        else:
            # fallback
            md.append(f"{text}\n")

    return "\n".join(md)


def looks_like_code(text):
    code_signals = ["{", "}", "()", "//", ";", "==", "!="]
    return any(sig in text for sig in code_signals)

def convert_file(input_path: Path, output_path: Path):
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    md = json_blocks_to_markdown(data)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == '__main__':
    input_path = Path("/home/alex/qi3/bvis/evals/books/1/chapters/4/4.json")
    output_path = Path("/home/alex/qi3/bvis/evals/books/1/chapters/4/4.md")
    convert_file(input_path=input_path, output_path=output_path)