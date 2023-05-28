import logging
import os
import subprocess
import sys
import typing

import altcos

STREAMS_ROOT_ENV = "STREAMS_ROOT"
BUILDS_ROOT_ENV = "BUILDS_ROOT"


def import_env(env: str) -> str:
    if (value := os.getenv(env)) is None:
        logging.fatal(f"Environment variable \"{env}\" is not set.")
        sys.exit(1)
    return value


def stream_from_ref(streams_root: str | os.PathLike, ref: str) -> altcos.Stream:
    try:
        return altcos.Stream.from_ostree_ref(streams_root, ref)
    except ValueError as e:
        logging.fatal(e)
        sys.exit(1)


def stream_to_export(stream: altcos.Stream) -> str:
    attrs = [attr for attr in dir(altcos.Stream) if isinstance(getattr(altcos.Stream, attr), property)]
    exports = [f"export {attr.upper()}={getattr(stream, attr)}" for attr in attrs]
    exports.extend([f"export {attr.upper()}={getattr(stream, attr)}" for attr in stream.__dict__])
    exports.append(f"export STREAM_REF={stream.like_ostree_ref()}")

    return ";".join(exports)


def wrap_err(f: typing.Callable, message: str | None = None, *errors: typing.Type[Exception]) -> typing.Any:
    try:
        return f()
    except errors as e:
        if message is None:
            logging.fatal(e)
        else:
            logging.fatal(message)
        sys.exit(1)


def aruncmd(command: str) -> subprocess.Popen:
    p = subprocess.Popen(command,
                         shell=True,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    return p


def runcmd(cmd: str, quite: bool = False) -> subprocess.CompletedProcess:
    if not quite:
        logging.info(f"start command :: `{cmd}`")

    try:
        cp = subprocess.run(cmd,
                            shell=True,
                            capture_output=True,
                            check=True)
    except subprocess.CalledProcessError as e:
        if not quite:
            if e.stdout:
                logging.error(f" STDOUT :: {e.stdout.decode()}")
            if e.stderr:
                logging.error(f" STDERR :: {e.stderr.decode()}")

        raise e

    if not quite:
        logging.info(f" STDOUT :: {cp.stdout.decode()}")
        logging.info(f" STDERR :: {cp.stderr.decode()}")

    return cp


def aruncmd_with_print(command: str) -> str:
    p = aruncmd(command)
    buf = ""

    for out in p.stdout:
        out = out.decode()
        print(out, end="")
        buf += out

    if p.returncode not in [0, None]:
        raise ValueError(f"\"{command}\" returns exit code \"{p.returncode}\".")

    return buf


def fatal_if(condition: bool, message: str, code: int = 1) -> None:
    if condition:
        logging.fatal(message)
        sys.exit(code)


def make_export_env_cmd(env: dict[str, str]) -> str:
    cmd = [f"export {k}=\"{v}\"" for k, v in env.items()]
    return ";".join(cmd).strip() + ";" if cmd else ""


def sign_file(filename: str | os.PathLike,
              keyfile: str | os.PathLike) -> subprocess.CompletedProcess:
    return runcmd(f"sudo -E openssl dgst -sha256 -sign {keyfile} -out {filename}.sig {filename}",
                  quite=True)


def archive_file(filename: str | os.PathLike) -> subprocess.CompletedProcess:
    return runcmd(f"sudo -E tar -czf {filename}.tar.gz {filename}",
                  quite=True)

