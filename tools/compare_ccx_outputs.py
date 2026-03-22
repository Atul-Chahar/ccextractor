#!/usr/bin/env python3
"""Compare the outputs of two CCExtractor binaries on the same input."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


TEXT_EXTENSIONS = {
    ".ass",
    ".ccd",
    ".csv",
    ".json",
    ".sami",
    ".scc",
    ".smi",
    ".srt",
    ".ssa",
    ".stl",
    ".sub",
    ".txt",
    ".ttml",
    ".ttxt",
    ".vtt",
    ".xml",
}


def sha256_bytes(data: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(data)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def decode_text(data: bytes) -> str:
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("latin-1")


def normalize_text(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def build_text_diff(
    base_path: Path,
    candidate_path: Path,
    diff_path: Path,
    *,
    force_text: bool = False,
) -> bool:
    if not force_text and base_path.suffix.lower() not in TEXT_EXTENSIONS:
        return False

    base_text = normalize_text(decode_text(base_path.read_bytes())).splitlines(keepends=True)
    candidate_text = normalize_text(decode_text(candidate_path.read_bytes())).splitlines(keepends=True)
    diff = list(
        difflib.unified_diff(
            base_text,
            candidate_text,
            fromfile=base_path.name,
            tofile=candidate_path.name,
        )
    )
    diff_path.write_text("".join(diff), encoding="utf-8")
    return bool(diff)


def run_binary(
    binary: Path,
    input_path: Path,
    output_path: Path,
    extra_args: list[str],
    timeout: int,
    log_path: Path,
    *,
    force_output_file: bool,
) -> dict[str, Any]:
    command = [str(binary), str(input_path), *extra_args]
    if force_output_file:
        command.extend(["-o", str(output_path)])

    completed = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=False,
        timeout=timeout,
        check=False,
    )
    stdout_bytes = completed.stdout
    log_path.write_bytes(stdout_bytes)

    result: dict[str, Any] = {
        "command": command,
        "exit_code": completed.returncode,
        "stdout_path": str(log_path),
        "stdout_size": len(stdout_bytes),
        "stdout_sha256": sha256_bytes(stdout_bytes),
        "output_exists": output_path.exists(),
    }

    if output_path.exists():
        result["output_path"] = str(output_path)
        result["output_size"] = output_path.stat().st_size
        result["sha256"] = sha256_file(output_path)

    return result


def compare_stdout_results(
    base_result: dict[str, Any],
    candidate_result: dict[str, Any],
    base_log: Path,
    candidate_log: Path,
    diff_path: Path,
) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        "mode": "stdout",
        "same_exit_code": base_result["exit_code"] == candidate_result["exit_code"],
        "same_stdout_size": base_result["stdout_size"] == candidate_result["stdout_size"],
        "same_stdout_sha256": base_result["stdout_sha256"] == candidate_result["stdout_sha256"],
        "stdout_diff_generated": True,
    }
    comparison["stdout_diff_present"] = build_text_diff(
        base_log,
        candidate_log,
        diff_path,
        force_text=True,
    )
    comparison["stdout_diff_path"] = str(diff_path)
    return comparison


def compare_output_results(
    base_result: dict[str, Any],
    candidate_result: dict[str, Any],
    base_output: Path,
    candidate_output: Path,
    diff_path: Path,
) -> dict[str, Any]:
    comparison: dict[str, Any] = {
        "mode": "output_file",
        "same_exit_code": base_result["exit_code"] == candidate_result["exit_code"],
        "both_outputs_exist": base_result["output_exists"] and candidate_result["output_exists"],
        "same_output_presence": base_result["output_exists"] == candidate_result["output_exists"],
    }

    if base_result["output_exists"] and candidate_result["output_exists"]:
        comparison["same_size"] = base_result["output_size"] == candidate_result["output_size"]
        comparison["same_sha256"] = base_result["sha256"] == candidate_result["sha256"]
        comparison["text_diff_generated"] = False
        comparison["text_diff_present"] = False

        if base_output.suffix.lower() in TEXT_EXTENSIONS:
            comparison["text_diff_generated"] = True
            comparison["text_diff_present"] = build_text_diff(base_output, candidate_output, diff_path)
            comparison["diff_path"] = str(diff_path)

    return comparison


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run two CCExtractor binaries with the same input and arguments, "
            "then compare exit codes, output files, hashes, and text diffs."
        )
    )
    parser.add_argument("--base-binary", required=True, help="Path to the baseline CCExtractor binary.")
    parser.add_argument(
        "--candidate-binary", required=True, help="Path to the candidate CCExtractor binary."
    )
    parser.add_argument("--input", required=True, help="Path to the input sample.")
    parser.add_argument(
        "--output-extension",
        help="File extension for the forced output file, for example: srt, ttxt, vtt.",
    )
    parser.add_argument(
        "--stdout-as-output",
        action="store_true",
        help=(
            "Treat captured stdout as the primary artifact to compare. "
            "Useful for modes like --out report that do not write an output file."
        ),
    )
    parser.add_argument(
        "--arg",
        dest="extra_args",
        action="append",
        default=[],
        help="Extra argument to pass to both binaries. Repeat for multiple arguments.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=120,
        help="Timeout in seconds for each binary run. Default: 120.",
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to store logs and comparison artifacts. Defaults to a temporary directory.",
    )
    parser.add_argument(
        "--keep-temp",
        action="store_true",
        help="Keep the temporary directory when --output-dir is not provided.",
    )
    return parser.parse_args()


def ensure_path(path_str: str, description: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"{description} does not exist: {path}")
    return path


def main() -> int:
    args = parse_args()

    if not args.stdout_as_output and not args.output_extension:
        print("--output-extension is required unless --stdout-as-output is set.", file=sys.stderr)
        return 2

    try:
        base_binary = ensure_path(args.base_binary, "Base binary")
        candidate_binary = ensure_path(args.candidate_binary, "Candidate binary")
        input_path = ensure_path(args.input, "Input file")
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    created_temp_dir = False
    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="ccx-compare-")).resolve()
        created_temp_dir = True

    output_extension = args.output_extension or "tmp"
    if not output_extension.startswith("."):
        output_extension = f".{output_extension}"

    base_output = output_dir / f"base{output_extension}"
    candidate_output = output_dir / f"candidate{output_extension}"
    base_log = output_dir / "base.log"
    candidate_log = output_dir / "candidate.log"
    diff_name = "stdout.diff" if args.stdout_as_output else "output.diff"
    diff_path = output_dir / diff_name
    report_path = output_dir / "comparison.json"

    try:
        base_result = run_binary(
            base_binary,
            input_path,
            base_output,
            args.extra_args,
            args.timeout,
            base_log,
            force_output_file=not args.stdout_as_output,
        )
        candidate_result = run_binary(
            candidate_binary,
            input_path,
            candidate_output,
            args.extra_args,
            args.timeout,
            candidate_log,
            force_output_file=not args.stdout_as_output,
        )
    except subprocess.TimeoutExpired as exc:
        print(f"Command timed out after {args.timeout}s: {exc.cmd}", file=sys.stderr)
        if created_temp_dir and not args.keep_temp:
            shutil.rmtree(output_dir, ignore_errors=True)
        return 3

    comparison = (
        compare_stdout_results(base_result, candidate_result, base_log, candidate_log, diff_path)
        if args.stdout_as_output
        else compare_output_results(base_result, candidate_result, base_output, candidate_output, diff_path)
    )

    report = {
        "input": str(input_path),
        "output_dir": str(output_dir),
        "stdout_as_output": args.stdout_as_output,
        "base": base_result,
        "candidate": candidate_result,
        "comparison": comparison,
    }

    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"Comparison report written to: {report_path}")
    print(json.dumps(comparison, indent=2))

    if created_temp_dir and not args.keep_temp:
        print(
            f"Artifacts kept in temporary directory: {output_dir}. "
            "Use --output-dir if you want a stable location."
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
