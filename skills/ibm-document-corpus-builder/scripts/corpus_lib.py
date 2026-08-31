from __future__ import annotations

import hashlib
import base64
import json
import mimetypes
import os
import re
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import yaml

TEXT_EXTENSIONS = {".txt", ".csv", ".tsv", ".json", ".yaml", ".yml", ".html", ".htm", ".xml"}
MARKDOWN_EXTENSIONS = {".md", ".qmd", ".markdown"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
DATA_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(data:(image/[A-Za-z0-9.+-]+);base64,([A-Za-z0-9+/=\s]+)\)")
IMAGE_MIME_EXTENSIONS = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/gif": ".gif",
    "image/bmp": ".bmp",
    "image/webp": ".webp",
}


def utc_stamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H%M%SZ")


def load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=False)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=True), encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-._")
    return cleaned or "document"


def resolve_path(path_value: str | Path, base: Path) -> Path:
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return (base / path).resolve()


def corpus_dir_from_manifest(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    value = manifest.get("corpus_dir", "corpus")
    return resolve_path(value, manifest_path.parent)


def source_root_from_manifest(manifest_path: Path, manifest: dict[str, Any]) -> Path:
    value = manifest.get("source_root", ".")
    return resolve_path(value, manifest_path.parent)


def document_dir(corpus_dir: Path, document_id: str) -> Path:
    return corpus_dir / "documents" / safe_id(document_id)


def iter_document_dirs(corpus_dir: Path) -> list[Path]:
    docs_dir = corpus_dir / "documents"
    if not docs_dir.exists():
        return []
    return sorted(path for path in docs_dir.iterdir() if path.is_dir())


def load_metadata(doc_dir: Path) -> dict[str, Any]:
    return load_yaml(doc_dir / "metadata.yaml")


def save_metadata(doc_dir: Path, metadata: dict[str, Any]) -> None:
    write_yaml(doc_dir / "metadata.yaml", metadata)


def text_from_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def image_record(path: Path, base_dir: Path) -> dict[str, Any]:
    rel = path.relative_to(base_dir).as_posix()
    mime, _ = mimetypes.guess_type(str(path))
    width = None
    height = None
    try:
        from PIL import Image

        with Image.open(path) as img:
            width, height = img.size
    except Exception:
        pass
    return {
        "path": rel,
        "sha256": sha256_file(path),
        "mime_type": mime,
        "width": width,
        "height": height,
        "alt_text": None,
        "caption": None,
        "description": None,
        "description_model": None,
        "description_cache_key": None,
    }


def collect_images(doc_dir: Path) -> list[dict[str, Any]]:
    images_dir = doc_dir / "images"
    if not images_dir.exists():
        return []
    records = []
    for path in sorted(images_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            records.append(image_record(path, doc_dir))
    return records


def category_lookup(taxonomy: dict[str, Any]) -> tuple[dict[str, str], dict[str, dict[str, Any]]]:
    aliases: dict[str, str] = {}
    categories_by_name: dict[str, dict[str, Any]] = {}
    for category in taxonomy.get("categories", []) or []:
        if not isinstance(category, dict):
            continue
        name = str(category.get("name") or category.get("id") or "").strip()
        if not name:
            continue
        categories_by_name[name.lower()] = category
        aliases[name.lower()] = name
        for alias in category.get("aliases", []) or []:
            aliases[str(alias).strip().lower()] = name
    return aliases, categories_by_name


def resolve_category(value: str | None, taxonomy: dict[str, Any]) -> str | None:
    if not value:
        return None
    aliases, _ = category_lookup(taxonomy)
    return aliases.get(str(value).strip().lower())


def route_converter(source: Path, doc_config: dict[str, Any], manifest: dict[str, Any]) -> tuple[str, str | None]:
    explicit = doc_config.get("converter")
    if explicit:
        return str(explicit), doc_config.get("fallback")

    ext = source.suffix.lower()
    for route in manifest.get("converter_routes", []) or []:
        match = route.get("match", {}) if isinstance(route, dict) else {}
        if str(match.get("extension", "")).lower() == ext:
            return str(route.get("converter", "auto")), route.get("fallback")

    converter = (manifest.get("defaults", {}) or {}).get("converter", "auto")
    return str(converter), None


def auto_converter_for(source: Path) -> str:
    ext = source.suffix.lower()
    if ext in MARKDOWN_EXTENSIONS:
        return "passthrough"
    if ext in TEXT_EXTENSIONS:
        return "plain_text"
    if ext == ".docx":
        return "docx_basic"
    return "plain_text"


@dataclass
class ConvertResult:
    converter: str
    content: str
    warnings: list[str]
    output_json: dict[str, Any] | None = None


def convert_document(source: Path, converter: str, doc_dir: Path, options: dict[str, Any] | None = None) -> ConvertResult:
    options = options or {}
    selected = auto_converter_for(source) if converter == "auto" else converter
    if selected == "passthrough":
        return ConvertResult(selected, source.read_text(encoding="utf-8", errors="replace"), [])
    if selected == "plain_text":
        return ConvertResult(selected, plain_text_content(source), [])
    if selected == "docx_basic":
        return ConvertResult(selected, docx_basic_content(source), [])
    if selected == "docling":
        return convert_with_docling(source, doc_dir, options)
    if selected == "markitdown":
        return convert_with_markitdown(source, options)
    return ConvertResult(selected, placeholder_content(source, f"Unknown converter: {selected}"), [f"Unknown converter: {selected}"])


def plain_text_content(source: Path) -> str:
    text = source.read_text(encoding="utf-8", errors="replace")
    if source.suffix.lower() in {".html", ".htm"}:
        text = re.sub(r"<(script|style)\b.*?</\1>", "", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = re.sub(r"\s+\n", "\n", text)
        text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip() + "\n"


def docx_basic_content(source: Path) -> str:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    try:
        with zipfile.ZipFile(source) as zf:
            xml = zf.read("word/document.xml")
            root = ElementTree.fromstring(xml)
            paragraphs = []
            for para in root.findall(".//w:p", ns):
                texts = [node.text or "" for node in para.findall(".//w:t", ns)]
                line = "".join(texts).strip()
                if line:
                    paragraphs.append(line)
        return "\n\n".join(paragraphs).strip() + "\n"
    except Exception as exc:
        return placeholder_content(source, f"DOCX fallback extraction failed: {exc}")


def convert_with_docling(source: Path, doc_dir: Path, options: dict[str, Any]) -> ConvertResult:
    output_dir = doc_dir / "_docling"
    output_dir.mkdir(parents=True, exist_ok=True)
    command = options.get("command") or default_docling_command(source, output_dir)
    if isinstance(command, str):
        command = command.format(source=str(source), output_dir=str(output_dir)).split()
    env = docling_environment(options)
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True, env=env)
    except FileNotFoundError:
        return ConvertResult("docling", placeholder_content(source, "Docling CLI not found."), ["Docling CLI not found"])
    except subprocess.CalledProcessError as exc:
        warning = f"Docling failed: {exc.stderr.strip() or exc.stdout.strip() or exc}"
        return ConvertResult("docling", placeholder_content(source, warning), [warning])

    md_files = sorted(output_dir.rglob("*.md"))
    json_files = sorted(output_dir.rglob("*.json"))
    content = md_files[0].read_text(encoding="utf-8", errors="replace") if md_files else placeholder_content(source, "Docling produced no markdown.")
    if json_files:
        shutil.copy2(json_files[0], doc_dir / "converter-output.json")
    images_dir = doc_dir / "images"
    image_link_map = copy_extracted_images(output_dir, images_dir)
    content = rewrite_local_image_links(content, image_link_map)
    content = extract_data_uri_images(content, images_dir)
    warnings = [] if md_files else ["Docling produced no markdown"]
    if completed.stderr.strip():
        warnings.append(completed.stderr.strip())
    return ConvertResult("docling", content, warnings)


def default_docling_command(source: Path, output_dir: Path) -> list[str]:
    executable = Path("/Users/telcott/.pyenv/shims/docling")
    docling = str(executable) if executable.exists() else "docling"
    return [
        docling,
        str(source),
        "--to",
        "md",
        "--to",
        "json",
        "--image-export-mode",
        "referenced",
        "--output",
        str(output_dir),
    ]


def docling_environment(options: dict[str, Any]) -> dict[str, str]:
    env = os.environ.copy()
    env.update({str(key): str(value) for key, value in (options.get("env") or {}).items()})
    env.setdefault("DOCLING_LIBREOFFICE_CMD", "/Applications/LibreOffice.app")
    env["PATH"] = f"/opt/homebrew/bin:{env.get('PATH', '')}"
    return env


def convert_with_markitdown(source: Path, options: dict[str, Any]) -> ConvertResult:
    command = options.get("command") or ["markitdown", str(source)]
    if isinstance(command, str):
        command = command.format(source=str(source)).split()
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        return ConvertResult("markitdown", placeholder_content(source, "MarkItDown CLI not found."), ["MarkItDown CLI not found"])
    except subprocess.CalledProcessError as exc:
        warning = f"MarkItDown failed: {exc.stderr.strip() or exc.stdout.strip() or exc}"
        return ConvertResult("markitdown", placeholder_content(source, warning), [warning])
    content = completed.stdout.strip()
    if not content:
        content = placeholder_content(source, "MarkItDown produced no output.")
    return ConvertResult("markitdown", content + "\n", [])


def copy_extracted_images(source_dir: Path, images_dir: Path) -> dict[str, str]:
    images_dir.mkdir(parents=True, exist_ok=True)
    link_map: dict[str, str] = {}
    index = 1
    for path in sorted(source_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            target = images_dir / f"image_{index:06d}{path.suffix.lower()}"
            shutil.copy2(path, target)
            rel_source = path.relative_to(source_dir).as_posix()
            rel_target = f"images/{target.name}"
            link_map[rel_source] = rel_target
            link_map[path.name] = rel_target
            index += 1
    return link_map


def rewrite_local_image_links(content: str, image_link_map: dict[str, str]) -> str:
    if not image_link_map:
        return content

    def replace(match: re.Match[str]) -> str:
        alt_text = match.group(1)
        target = match.group(2)
        if target.startswith(("http://", "https://", "data:")):
            return match.group(0)
        normalized = target.lstrip("./")
        replacement = image_link_map.get(normalized) or image_link_map.get(Path(normalized).name)
        if not replacement:
            return match.group(0)
        return f"![{alt_text}]({replacement})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, content)


def extract_data_uri_images(content: str, images_dir: Path) -> str:
    if "data:image/" not in content:
        return content
    images_dir.mkdir(parents=True, exist_ok=True)
    index = next_image_index(images_dir)

    def replace(match: re.Match[str]) -> str:
        nonlocal index
        alt_text = match.group(1)
        mime_type = match.group(2).lower()
        encoded = re.sub(r"\s+", "", match.group(3))
        extension = IMAGE_MIME_EXTENSIONS.get(mime_type, mimetypes.guess_extension(mime_type) or ".img")
        target = images_dir / f"image_{index:06d}{extension}"
        index += 1
        try:
            target.write_bytes(base64.b64decode(encoded, validate=True))
        except Exception:
            return match.group(0)
        return f"![{alt_text}](images/{target.name})"

    return DATA_IMAGE_RE.sub(replace, content)


def next_image_index(images_dir: Path) -> int:
    highest = 0
    for path in images_dir.glob("image_*.*"):
        match = re.match(r"image_(\d+)", path.stem)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def placeholder_content(source: Path, warning: str) -> str:
    return f"# {source.stem}\n\n> Conversion warning: {warning}\n\nSource file: `{source.name}`\n"


def metadata_frontmatter(metadata: dict[str, Any]) -> str:
    classification = metadata.get("classification", {}) or {}
    source = metadata.get("source", {}) or {}
    lines = [
        "---",
        f'document_id: "{metadata.get("document_id", "")}"',
        f'entry_id: "{metadata.get("entry_id") or metadata.get("document_id", "")}"',
        f'title: "{str(metadata.get("title") or "").replace(chr(34), chr(39))}"',
        f'source_path: "{source.get("path", "")}"',
        f'category: "{classification.get("category", "")}"',
        "tags:",
    ]
    for tag in classification.get("tags", []) or []:
        lines.append(f"  - {tag}")
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def materialised_content(metadata: dict[str, Any], content: str, *, include_header: bool = True) -> str:
    body = strip_rebuildable_image_links(content).strip()
    sections = []
    if include_header:
        sections.append(document_header(metadata).strip())
    if body:
        sections.append(body)
    image_descriptions = image_descriptions_markdown(metadata)
    if image_descriptions:
        sections.append(image_descriptions)
    return "\n\n".join(sections).strip() + "\n"


def rendered_content(metadata: dict[str, Any], content: str) -> str:
    return materialised_content(metadata, content, include_header=True)


def document_header(metadata: dict[str, Any]) -> str:
    classification = metadata.get("classification", {}) or {}
    bid = metadata.get("bid_library", {}) or {}
    header = [
        f"Question: {bid.get('question') or metadata.get('title') or ''}",
        "",
        f"Category: {classification.get('category') or ''}",
        f"Sub-category: {classification.get('sub_category') or ''}",
        f"Tags: {', '.join(classification.get('tags', []) or [])}",
        f"Language: {classification.get('language') or ''}",
        f"Library URL: {bid.get('library_url') or ''}",
        f"Source path: {(metadata.get('source') or {}).get('path') or ''}",
        "",
    ]
    return "\n".join(header)


def strip_rebuildable_image_links(content: str) -> str:
    def replace(match: re.Match[str]) -> str:
        alt_text = match.group(1).strip()
        target = match.group(2).strip().lstrip("./")
        if not target.startswith("images/"):
            return match.group(0)
        return f"Image: {alt_text}" if alt_text else ""

    stripped = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, content)
    return re.sub(r"\n{3,}", "\n\n", stripped)


def image_descriptions_markdown(metadata: dict[str, Any]) -> str:
    lines = []
    for index, image in enumerate(metadata.get("images", []) or [], start=1):
        description = str(image.get("description") or "").strip()
        if not description:
            continue
        label = str(image.get("caption") or image.get("alt_text") or f"Image {index}").strip()
        lines.append(f"- {label}: {description}")
    if not lines:
        return ""
    return "## Image Descriptions\n\n" + "\n".join(lines)


def parse_question_answer(metadata: dict[str, Any], content: str) -> tuple[str, str]:
    bid = metadata.get("bid_library", {}) or {}
    question = bid.get("question") or metadata.get("title") or metadata.get("document_id") or ""
    answer = content.strip()
    match = re.match(r"Question:\s*(.+?)\n\s*\n(.*)", content.strip(), flags=re.DOTALL)
    if match and not bid.get("question"):
        question = match.group(1).strip()
        answer = match.group(2).strip()
    return str(question), answer
