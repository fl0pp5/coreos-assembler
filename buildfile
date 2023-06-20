#!/usr/bin/env python3
import argparse
import dataclasses
import logging
import os
import pathlib

import pydantic
import yaml
from altcos import ostree, build
from gi.repository import GLib

import cmdlib

SR = cmdlib.import_env(cmdlib.STREAMS_ROOT_ENV)
BR = cmdlib.import_env(cmdlib.BUILDS_ROOT_ENV)


def get_build_script(fmt: build.Format) -> pathlib.Path:
    """
    :param fmt:
    :return: Абсолютный путь до скрипта.
    """
    return cmdlib.SCRIPTS_ROOT.joinpath(f"build-{fmt}")


def get_path_to_image(stream: ostree.Stream,
                      version: ostree.Version,
                      platform: build.Platform,
                      fmt: build.Format) -> pathlib.Path:
    substream = stream.substream or "base"

    prefix = f"{stream.branch}_{substream}" \
        if stream.substream \
        else f"{stream.branch}"

    return pathlib.Path(BR,
                        stream.branch.value,
                        stream.arch.value,
                        substream,
                        str(version),
                        platform.value,
                        fmt.value,
                        f"{prefix}.{stream.arch}.{version}.{platform}.{fmt}")


class ImageOptions(pydantic.BaseModel):
    sign: bool = False
    archive: bool = False


class Config(pydantic.BaseModel):
    repo: ostree.Repository.Mode
    commit: str = "latest"
    build: dict[build.Platform, dict[build.Format, ImageOptions | None]]


@dataclasses.dataclass
class BuildOptions:
    stream: ostree.Stream
    config: Config
    sign_key: str | os.PathLike


def handle_build(opt: BuildOptions) -> None:
    repo = cmdlib.wrap_err(ostree.Repository(opt.stream, opt.config.repo).open,
                           None, GLib.Error)

    if opt.config.commit == "latest":
        commit = cmdlib.wrap_err(repo.last_commit, None, GLib.Error)
    else:
        commit = cmdlib.wrap_err(ostree.Commit(repo, opt.config.commit).open,
                                 None, GLib.Error)

    for platform in opt.config.build:
        for fmt in opt.config.build[platform]:
            opts = opt.config.build[platform][fmt]
            script = get_build_script(fmt)
            cmdlib.runcmd(f"sudo -E {script} "
                          f"{opt.stream.like_ostree_ref()} "
                          f"{commit} "
                          f"{opt.config.repo}")

            if opts is None:
                continue

            image = get_path_to_image(opt.stream, commit.version(), platform, fmt)

            if opts.sign:
                logging.info("creating an signature")
                cmdlib.sign_file(image, opt.sign_key)

            if opts.archive:
                logging.info("creating an archive.")
                cmdlib.archive_file(image)
                tar_image = f"{image}.tar.gz"

                if opts.sign:
                    logging.info("creating an archive signature.")
                    cmdlib.sign_file(tar_image, opt.sign_key)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("sign_key")

    args = parser.parse_args()

    with open(args.config) as file:
        content = yaml.safe_load(file)

    opts = []

    for ref in content:
        stream = cmdlib.stream_from_ref(SR, ref)
        config = Config.parse_obj(content[stream.like_ostree_ref()])
        opts.append(BuildOptions(stream, config, args.sign_key))

    [handle_build(opt) for opt in opts]


if __name__ == '__main__':
    main()
