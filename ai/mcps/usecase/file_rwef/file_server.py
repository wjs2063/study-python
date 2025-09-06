from __future__ import annotations
from mcp.server.fastmcp import FastMCP
from typing import Literal
import os
import sys
import json
import base64
import asyncio
import fnmatch
import glob
import io
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

ROOT_DIR = Path(os.environ.get("ROOT_DIR", os.getcwd())).resolve()
ALLOW_EXEC = os.environ.get("ALLOW_EXEC", "false").lower() == "true"
MAX_BYTES = int(os.environ.get("MAX_BYTES", 2 * 1024 * 1024))  # 2MB


def _assert_in_root(p: Path) -> Path:
    p = p.resolve()
    # ROOT_DIR 자체도 허용
    if not (str(p) == str(ROOT_DIR) or str(p).startswith(str(ROOT_DIR) + os.sep)):
        raise ValueError(f"Path escapes rootDir: path={p}, rootDir={ROOT_DIR}")
    return p


def _trim(data: bytes, limit: int = MAX_BYTES):
    if len(data) <= limit:
        return False, data
    return True, data[:limit]


mcp = FastMCP(name="file_rwef", host="0.0.0.0", port=8080)

def find_exists_files():
    return os.listdir(ROOT_DIR)



@mcp.tool()
async def fs_read(
        encoding: Literal["utf8", "base64"] = "utf8",
):
    """
    서버내에있는 ROOT_DIR 내의 txt 파일을 읽고 요약해주는 도구입니다
    Read a file within ROOT_DIR. Inputs: { path: str, encoding?: 'utf8' }
    Args:
        encoding:

    Returns:

    """
    files = find_exists_files()
    files = [file for file in files if file.endswith(".txt")]
    abs_path = _assert_in_root(ROOT_DIR / files[0])

    if not abs_path.is_file():
        raise FileNotFoundError(f"Not a file: {abs_path}")

    data = abs_path.read_bytes()
    truncated, chunk = _trim(data, MAX_BYTES)

    if encoding == "base64":
        payload = base64.b64encode(chunk).decode("ascii")
    else:
        payload = chunk.decode("utf-8", errors="replace")

    return {
        "meta": {
            "truncated": truncated,
            "bytes": len(data),
            "returnedBytes": len(chunk),
            "rootDir": str(ROOT_DIR),
        },
        "content": payload,
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")