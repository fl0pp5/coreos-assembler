#!/usr/bin/env python3
import argparse
import enum
import http
import logging
import os

from flask import Flask, request, jsonify, send_from_directory, Response
from gi.repository import GLib

import cmdlib
import altcos

app = Flask(__name__)

SR = cmdlib.import_env(cmdlib.STREAMS_ROOT_ENV)


class Error(enum.IntEnum):
    BAD_BASEARCH = 1
    BAD_STREAM = 2
    BAD_VERSION = 3
    BAD_REPO = 4


def send_err(kind: int, value: str, log: bool = True) -> tuple[Response, http.HTTPStatus]:
    if log:
        logging.error(value)

    return jsonify({
        "kind": kind,
        "value": value,
    }), http.HTTPStatus.BAD_REQUEST


def get_commits_list(repository: altcos.Repository) -> list[altcos.Commit]:
    commits = [repository.last_commit(), ]
    while True:
        if (commit := commits[-1].parent()) is None:
            break

        commits.append(commit)

    return commits[::-1]


@app.route("/v1/graph")
def v1_graph() -> tuple[Response, http.HTTPStatus]:
    try:
        basearch = altcos.Arch(request.args.get("basearch").lower())
    except ValueError as e:
        return send_err(Error.BAD_BASEARCH, str(e))

    try:
        # Под stream имеется ввиду ветка пакетного репозитория
        branch = altcos.Branch(request.args.get("stream").lower())
    except ValueError as e:
        return send_err(Error.BAD_STREAM, str(e))

    try:
        version = altcos.Version.from_str(request.args.get("os_version"))
    except ValueError as e:
        return send_err(Error.BAD_VERSION, str(e))

    stream = altcos.Stream(SR, altcos.OSName.ALTCOS, basearch, branch, version.substream)

    try:
        archive = altcos.Repository(stream).open()
    except GLib.Error as e:
        return send_err(Error.BAD_REPO, str(e))

    commit_list = {c.hashsum: i for i, c in enumerate(get_commits_list(archive))}

    nodes = []
    edges = []

    for hashsum, index in commit_list.items():
        commit = altcos.Commit(archive, hashsum)
        node = {
            "version": str(commit.version()),
            "metadata": {
                "org.fedoraproject.coreos.releases.age_index": str(index),
                "org.fedoraproject.coreos.scheme": "checksum",
            },
            "payload": hashsum
        }
        nodes.append(node)

        if parent := commit.parent():
            parent_index = commit_list[parent.hashsum]
            edges.append([parent_index, index])

    for i in range(len(nodes)):
        for j in range(i+2, len(nodes)):
            edges.append([i, j])

    graph = {
        "nodes": nodes,
        "edges": edges
    }

    return jsonify(graph), http.HTTPStatus.OK


@app.route("/streams/<branch>/<arch>/ostree/archive/<path:path>")
def stream_content(branch: str, arch: str, path: str | os.PathLike) -> Response:
    stream = altcos.Stream(SR,
                           altcos.OSName.ALTCOS,
                           altcos.Arch(arch),
                           altcos.Branch(branch))

    return send_from_directory(stream.ostree_archive_dir, path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Server for communicating with the zincati daemon.")
    parser.add_argument("host")
    parser.add_argument("port", type=int)
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    app.run(host=args.host,
            port=args.port,
            debug=args.debug)


if __name__ == '__main__':
    main()
