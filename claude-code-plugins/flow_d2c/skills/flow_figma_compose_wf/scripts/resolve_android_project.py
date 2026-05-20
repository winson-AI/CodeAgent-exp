#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


CONFIG_RELATIVE_PATH = ".cache/starting-figma-react-compose/config.json"
DEFAULT_ANDROID_SHELL_REPO = "https://gitcode.com/OpenHarmonyToolkitsPlaza/kmp_shell.git"
DEFAULT_ANDROID_SHELL_DIR = "kmp_shell"
DEFAULT_SHELL_COMPOSE_CODE_DIR = "app/src/main/java/com/example/myapplication/"


def dump_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read and write Android Compose target directory data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    getdata = subparsers.add_parser("getdata", help="Read saved Android Compose target directory data.")
    add_common_args(getdata)
    getdata.add_argument(
        "--use-default-shell",
        action="store_true",
        help="Use and save the default Android shell project under the task working directory.",
    )
    getdata.add_argument(
        "--compose-code-dir",
        help=(
            "Compose implementation directory used with --use-default-shell. "
            "Relative paths are resolved from the Android project root. "
            f"Defaults to {DEFAULT_SHELL_COMPOSE_CODE_DIR} for the default shell."
        ),
    )
    getdata.add_argument(
        "--default-shell-dir",
        default=DEFAULT_ANDROID_SHELL_DIR,
        help=f"Directory name for the default shell. Defaults to {DEFAULT_ANDROID_SHELL_DIR}.",
    )
    getdata.add_argument(
        "--default-shell-repo",
        default=DEFAULT_ANDROID_SHELL_REPO,
        help=f"Git repository for the default shell. Defaults to {DEFAULT_ANDROID_SHELL_REPO}.",
    )

    setdata = subparsers.add_parser("setdata", help="Save Android Compose target directory data.")
    add_common_args(setdata)
    setdata.add_argument("--android-project-dir", help="Android project root directory.")
    setdata.add_argument(
        "--compose-code-dir",
        help=(
            "Compose implementation directory. Relative paths are resolved from the Android project root. "
            "Defaults to the Android project root."
        ),
    )
    setdata.add_argument("--android-project-source", default="user-specified")
    setdata.add_argument("--compose-code-source", default="user-specified")

    return parser


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--workdir", default=".", help="Task working directory. Defaults to the current directory.")
    parser.add_argument(
        "--config-path",
        help=f"Optional config file path. Defaults to <workdir>/{CONFIG_RELATIVE_PATH}.",
    )


def resolve_workdir(value: str) -> Path:
    path = Path(value).expanduser().resolve()
    if not path.exists():
        raise ValueError(f"Workdir does not exist: {path}")
    if not path.is_dir():
        raise ValueError(f"Workdir is not a directory: {path}")
    return path


def resolve_path(path_value: str, *, base_dir: Path) -> Path:
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        path = base_dir / path
    return path.resolve()


def config_path_for(args: argparse.Namespace, workdir: Path) -> Path:
    if args.config_path:
        return resolve_path(args.config_path, base_dir=workdir)
    return workdir / CONFIG_RELATIVE_PATH


def load_config(config_path: Path) -> dict[str, Any] | None:
    if not config_path.exists():
        return None
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def write_config(
    config_path: Path,
    *,
    android_project_dir: Path,
    compose_code_dir: Path,
    android_project_source: str,
    compose_code_source: str,
) -> None:
    payload = {
        "androidProjectDir": str(android_project_dir),
        "androidProjectSource": android_project_source,
        "composeCodeDir": str(compose_code_dir),
        "composeCodeSource": compose_code_source,
    }
    temp_path = config_path.with_suffix(config_path.suffix + ".tmp")
    config_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp_path.replace(config_path)


def require_non_empty_path(value: str | None, *, field_name: str) -> str:
    if value is None or not value.strip():
        raise ValueError(f"{field_name} is required.")
    return value.strip()


def resolve_compose_code_dir(path_value: str | None, *, project_dir: Path) -> tuple[Path, str]:
    if path_value is None or not path_value.strip():
        return project_dir, "android-project-root"
    return resolve_path(path_value.strip(), base_dir=project_dir), "user-specified"


def clone_default_shell(repo: str, target_dir: Path, workdir: Path) -> None:
    if target_dir.exists():
        return
    subprocess.run(
        ["git", "clone", repo, str(target_dir)],
        cwd=str(workdir),
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def continue_payload(
    *,
    android_project_dir: Path,
    compose_code_dir: Path,
    android_project_source: str,
    compose_code_source: str,
    config_path: Path,
) -> dict[str, Any]:
    return {
        "status": "ok",
        "nextAction": "continue",
        "agentInstruction": (
            f"Set ANDROID_PROJECT_DIR to {android_project_dir} and COMPOSE_CODE_DIR to {compose_code_dir}. "
            "Use ANDROID_PROJECT_DIR as the Android project root and COMPOSE_CODE_DIR as the Compose "
            "implementation write target."
        ),
        "androidProjectDir": str(android_project_dir),
        "androidProjectSource": android_project_source,
        "composeCodeDir": str(compose_code_dir),
        "composeCodeSource": compose_code_source,
        "configPath": str(config_path),
    }


def ask_user_payload(config_path: Path, reason: str) -> dict[str, Any]:
    return {
        "status": "needs_input",
        "nextAction": "ask_user",
        "reason": reason,
        "configPath": str(config_path),
        "agentInstruction": (
            "Ask the user for the Compose implementation code directory. If the user provides only the "
            "Compose implementation directory, infer the Android project root from the repository layout, "
            "then run setdata with both paths. Offer the default shell option; if selected, rerun getdata "
            "with --use-default-shell."
        ),
        "userPrompt": (
            "Provide the Compose implementation code directory, or choose the default Android shell project."
        ),
        "choices": [
            {
                "id": "setdata",
                "label": "Save specified directories",
                "commandTemplate": (
                    'python3 ${skill dir}/scripts/resolve_android_project.py setdata '
                    '--workdir "$PWD" --android-project-dir "$ANDROID_PROJECT_DIR" '
                    '--compose-code-dir "$COMPOSE_CODE_DIR"'
                ),
            },
            {
                "id": "use-default-shell",
                "label": "Use default Android shell project",
                "commandTemplate": (
                    'python3 ${skill dir}/scripts/resolve_android_project.py getdata '
                    '--workdir "$PWD" --use-default-shell'
                ),
            },
        ],
    }


def stop_payload(message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "nextAction": "stop",
        "agentInstruction": "Stop the workflow and report the message field to the user.",
        "message": message,
    }


def handle_getdata(args: argparse.Namespace) -> dict[str, Any]:
    workdir = resolve_workdir(args.workdir)
    config_path = config_path_for(args, workdir)

    if args.use_default_shell:
        project_dir = resolve_path(args.default_shell_dir, base_dir=workdir)
        clone_default_shell(args.default_shell_repo, project_dir, workdir)
        default_compose_code_dir = args.compose_code_dir or DEFAULT_SHELL_COMPOSE_CODE_DIR
        compose_code_dir, compose_code_source = resolve_compose_code_dir(
            default_compose_code_dir,
            project_dir=project_dir,
        )
        if not args.compose_code_dir:
            compose_code_source = "default-shell"
        write_config(
            config_path,
            android_project_dir=project_dir,
            compose_code_dir=compose_code_dir,
            android_project_source="default-shell",
            compose_code_source=compose_code_source,
        )
        return continue_payload(
            android_project_dir=project_dir,
            compose_code_dir=compose_code_dir,
            android_project_source="default-shell",
            compose_code_source=compose_code_source,
            config_path=config_path,
        )

    config = load_config(config_path)
    if not config:
        return ask_user_payload(config_path, "target_data_not_configured")

    android_project_dir_value = config.get("androidProjectDir")
    if not isinstance(android_project_dir_value, str) or not android_project_dir_value.strip():
        return stop_payload("Saved androidProjectDir is empty. Ask the user for the Android project root directory.")

    project_dir = resolve_path(android_project_dir_value.strip(), base_dir=workdir)
    compose_code_dir_value = config.get("composeCodeDir")
    if isinstance(compose_code_dir_value, str) and compose_code_dir_value.strip():
        compose_code_dir = resolve_path(compose_code_dir_value.strip(), base_dir=project_dir)
        compose_code_source = str(config.get("composeCodeSource") or "saved")
    else:
        compose_code_dir, compose_code_source = resolve_compose_code_dir(None, project_dir=project_dir)

    return continue_payload(
        android_project_dir=project_dir,
        compose_code_dir=compose_code_dir,
        android_project_source=str(config.get("androidProjectSource") or "saved"),
        compose_code_source=compose_code_source,
        config_path=config_path,
    )


def handle_setdata(args: argparse.Namespace) -> dict[str, Any]:
    workdir = resolve_workdir(args.workdir)
    config_path = config_path_for(args, workdir)
    project_dir_value = require_non_empty_path(args.android_project_dir, field_name="androidProjectDir")
    project_dir = resolve_path(project_dir_value, base_dir=workdir)
    compose_code_dir, compose_code_source = resolve_compose_code_dir(args.compose_code_dir, project_dir=project_dir)
    if args.compose_code_dir is not None and args.compose_code_dir.strip():
        compose_code_source = args.compose_code_source

    write_config(
        config_path,
        android_project_dir=project_dir,
        compose_code_dir=compose_code_dir,
        android_project_source=args.android_project_source,
        compose_code_source=compose_code_source,
    )
    return continue_payload(
        android_project_dir=project_dir,
        compose_code_dir=compose_code_dir,
        android_project_source=args.android_project_source,
        compose_code_source=compose_code_source,
        config_path=config_path,
    )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        if args.command == "getdata":
            dump_json(handle_getdata(args))
        elif args.command == "setdata":
            dump_json(handle_setdata(args))
        else:
            raise ValueError(f"Unsupported command: {args.command}")
        return 0
    except subprocess.CalledProcessError as exc:
        dump_json(
            {
                **stop_payload("Default Android shell clone failed."),
                "returncode": exc.returncode,
                "stdout": exc.stdout,
                "stderr": exc.stderr,
            }
        )
        return 1
    except Exception as exc:
        dump_json(stop_payload(str(exc)))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
