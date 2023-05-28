from __future__ import annotations

import dataclasses
import datetime
import enum
import os
import pathlib
import typing

import gi


gi.require_version("OSTree", "1.0")

from gi.repository import Gio, OSTree


class StrEnum(str, enum.Enum):
    def __repr__(self) -> str:
        return str.__repr__(self.value)

    def __str__(self) -> str:
        return self.value


class OSName(StrEnum):
    ALTCOS = "altcos"


class Arch(StrEnum):
    X86_64 = "x86_64"


class Branch(StrEnum):
    SISYPHUS = "sisyphus"
    P10 = "p10"


class Platform(StrEnum):
    QEMU = "qemu"
    METAL = "metal"


class Format(StrEnum):
    QCOW2 = "qcow2"
    ISO = "iso"
    RAW = "raw"


@dataclasses.dataclass
class Disk:
    location: str | os.PathLike
    signature: typing.Optional[str | os.PathLike]
    uncompressed: typing.Optional[str | os.PathLike]
    uncompressed_signature: typing.Optional[str | os.PathLike]


@dataclasses.dataclass
class Artifact:
    disk: typing.Optional[Disk]


ALLOWED_FORMATS = {
    Platform.QEMU: {
        Format.QCOW2,
    },
    Platform.METAL: {
        Format.ISO,
        Format.RAW,
    }
}


class Stream:
    def __init__(self,
                 streams_root: str | os.PathLike,
                 osname: OSName,
                 arch: Arch,
                 branch: Branch,
                 substream: str | None = None) -> None:
        self.streams_root = streams_root
        self.osname = osname
        self.arch = arch
        self.branch = branch
        self.substream = substream

    def base_stream(self) -> Stream:
        """
        :return: экземпляр "Stream" без поля substream
        """
        return Stream(self.streams_root,
                      self.osname,
                      self.arch,
                      self.branch)

    def like_ostree_ref(self) -> str:
        """
        :return: строка вида: "altcos/x86_64/p10", "altcos/x86_64/P10/k8s"
        """
        return str(pathlib.Path(self.osname.value,
                                self.arch.value,
                                self.branch.value.title() if self.substream else self.branch.value,
                                self.substream or ""))

    @classmethod
    def from_ostree_ref(cls, streams_root: str, ref: str) -> Stream:
        """
        :param streams_root: путь до хранилища потоков
        :param ref: ветка вида: "altcos/x86_64/Sisyphus/k8s"
        :return: экземпляр "Stream"
        """
        if len(parts := ref.lower().split("/")) not in [3, 4]:
            raise ValueError(f"Invalid reference format :: \"{ref}\".")

        return Stream(streams_root,
                      OSName(parts[0]),
                      Arch(parts[1]),
                      Branch(parts[2]),
                      parts[3] if len(parts) == 4 else None)

    @property
    def stream_dir(self) -> pathlib.Path:
        """
        :return: корень потока
        """
        return pathlib.Path(self.streams_root,
                            self.branch.value,
                            self.arch.value,
                            self.substream or "")

    @property
    def rootfs_dir(self) -> pathlib.Path:
        """
        :return: путь до хранилища rootfs-образов, полученых при помощи mkimage-profiles
        """
        return self.base_stream().stream_dir.joinpath("rootfs")

    @property
    def ostree_bare_dir(self) -> pathlib.Path:
        """
        :return: путь до OSTree-репозитория в режиме bare
        """
        return self.base_stream().stream_dir.joinpath("ostree", "bare")

    @property
    def ostree_archive_dir(self) -> pathlib.Path:
        """
        :return: путь до OSTree-репозитория в режиме archive
        """
        return self.base_stream().stream_dir.joinpath("ostree", "archive")

    @property
    def vars_dir(self) -> pathlib.Path:
        """
        :return: путь к директории версий пользовательского слоя (относящиеся к OSTree-коммитам)
        """
        return self.stream_dir.joinpath("vars")

    @property
    def work_dir(self) -> pathlib.Path:
        """
        содержит необходимые директории для работы в overlay-режиме
        :return: путь до рабочей директории
        """
        return self.stream_dir.joinpath("work")

    @property
    def merged_dir(self) -> pathlib.Path:
        """
        :return: путь до директории, примонтированной в overlay-режиме
        """
        return self.work_dir.joinpath("merged")


class Repository:
    class Mode(StrEnum):
        BARE = "bare"
        ARCHIVE = "archive"

    def __init__(self, stream: Stream, mode: Repository.Mode = Mode.BARE) -> None:
        self.stream = stream
        match mode:
            case Repository.Mode.BARE:
                path = stream.ostree_bare_dir
            case Repository.Mode.ARCHIVE:
                path = stream.ostree_archive_dir
            case _:
                raise ValueError(f"Invalid mode: \"{mode}\". "
                                 f"Allowed only: {' '.join(*Repository.Mode)}.")
        self.storage: OSTree.Repo = OSTree.Repo.new(Gio.file_new_for_path(str(path)))

    def open(self) -> Repository:
        self.storage.open(None)
        return self

    def last_commit(self) -> Commit:
        hashsum = self.storage.resolve_rev(self.stream.like_ostree_ref(), False)[1]
        return Commit(self, hashsum)


class Version:
    def __init__(self,
                 major: int,
                 minor: int,
                 branch: Branch,
                 substream: str | None = None,
                 date: str | None = None):
        self.major = major
        self.minor = minor
        self.branch = branch
        self.substream = substream
        self.date = date or datetime.datetime.now().strftime("%Y%m%d")

    def __str__(self) -> str:
        """
        :return: строка версии вида: "20220101.1.0"
        """
        return f"{self.date}.{self.major}.{self.minor}"

    @property
    def full_version(self) -> str:
        """
        :return: строка версии вида: "p10_k8s.20220101.1.0"
        """
        return f"{self.branch}_{self.substream or 'base'}.{self}"

    @classmethod
    def from_str(cls, version: str) -> Version:
        """
        :param version: e.g. "p10_base.20230101.0.0"
        :return: экземпляр "Version"
        """
        if len(parts := version.split(".")) != 4:
            raise ValueError(f"Invalid version format \"{version}\".")

        if len(prefix := parts[0].split("_")) != 2:
            raise ValueError(f"Invalid version prefix format \"{version}\".")

        [branch, substream] = Branch(prefix[0]), prefix[1]
        [date, major, minor] = parts[1], *map(int, parts[2:])

        return Version(major, minor, branch, substream, date)


class Commit:
    def __init__(self, repo: Repository, hashsum: str) -> None:
        self.repo = repo
        self.hashsum = hashsum

    def __str__(self) -> str:
        return self.hashsum

    def open(self) -> Commit:
        self.repo.storage.load_commit(self.hashsum)
        return self

    def version(self) -> Version:
        content = self.repo.storage.load_commit(self.hashsum)
        return Version.from_str(content[1][0]["version"])

    def parent(self) -> Commit | None:
        content = self.repo.storage.load_commit(self.hashsum)
        parent_hashsum = OSTree.commit_get_parent(content[1])

        return Commit(self.repo, parent_hashsum) \
            if parent_hashsum \
            else None
