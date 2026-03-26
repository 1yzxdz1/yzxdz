from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.paper_importer import (
    import_normalized_papers,
    parse_input_file,
    serialize_normalized_papers,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import NCRE past papers from PDF / Word / Excel / JSON into the local database.",
    )
    parser.add_argument("--input", required=True, help="Input file path.")
    parser.add_argument(
        "--format",
        default="auto",
        choices=["auto", "json", "xlsx", "csv", "docx", "pdf", "text"],
        help="Force input format. Default: auto detect from extension.",
    )
    parser.add_argument("--subject-code", help="Required for pdf/docx/text import. Optional override for other formats.")
    parser.add_argument("--paper-code", help="Optional paper code override for plain-text import.")
    parser.add_argument("--year", type=int, help="Optional year override for plain-text import.")
    parser.add_argument("--season", help="Optional season override for plain-text import, such as 3月 or 9月.")
    parser.add_argument("--title", help="Optional title override for plain-text import.")
    parser.add_argument(
        "--replace-paper-questions",
        action="store_true",
        help="Replace existing paper-question mappings for the same paper code. Recommended for re-import.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse only and print normalized result summary without writing to database.",
    )
    parser.add_argument(
        "--dump-normalized",
        help="Optional output file path to save normalized JSON payload.",
    )
    return parser


def print_summary(serialized: dict) -> None:
    papers = serialized["papers"]
    print(f"papers: {len(papers)}")
    for paper in papers:
        type_counts: dict[str, int] = {}
        for question in paper["questions"]:
            question_type = question["question_type"]
            type_counts[question_type] = type_counts.get(question_type, 0) + 1
        type_summary = ", ".join(f"{key}={value}" for key, value in sorted(type_counts.items()))
        print(
            f"- {paper['code']} | {paper['title']} | {paper['subject_code']} | "
            f"{paper['year']} {paper['season']} | questions={len(paper['questions'])} | {type_summary}"
        )


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    Base.metadata.create_all(bind=engine)

    papers = parse_input_file(
        args.input,
        input_format=args.format,
        subject_code=args.subject_code,
        paper_code=args.paper_code,
        year=args.year,
        season=args.season,
        title=args.title,
    )
    serialized = serialize_normalized_papers(papers)
    print_summary(serialized)

    if args.dump_normalized:
        output_path = Path(args.dump_normalized)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(serialized, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"normalized_json: {output_path}")

    if args.dry_run:
        print("mode: dry-run")
        return

    with SessionLocal() as db:
        report = import_normalized_papers(
            db,
            papers,
            replace_paper_questions=args.replace_paper_questions,
        )

    print("mode: import")
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
