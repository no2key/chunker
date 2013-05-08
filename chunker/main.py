#!/usr/bin/env python

import argparse
import sys
import json
import os
from glob import glob

from chunker.repo import Repo
from chunker.util import get_config_path, heal, log
from chunker.net import MetaNet


config_file_path = get_config_path("main.conf")


def cmd_chunk(args, config):
    r = Repo(args.output, args.input, args.name or os.path.basename(args.input))
    r.save(args.output, state=False)
    return {"status": "ok"}


def cmd_save(args, config):
    file(config_file_path, "w").write(json.dumps(config))
    return {"status": "ok"}


def cmd_add(args, config):
    r = Repo(
        args.filename,
        args.directory,
        args.name or os.path.basename(args.directory),
    )
    r.save_state()


def cmd_heal(args, config):
    known = []
    missing = []
    for filename in glob(get_config_path("*.state")):
        r = Repo(filename)
        known.extend(r.get_known_chunks())
        missing.extend(r.get_missing_chunks())
    saved = heal(known, missing)
    return {"status": "ok", "saved": saved}


def cmd_fetch(args, config):
    repos = []
    all_known_chunks = []
    all_missing_chunks = []
    for filename in glob(get_config_path("*.state")):
        repo = Repo(filename)
        repos.append(repo)
        all_known_chunks.extend(repo.get_known_chunks())
        all_missing_chunks.extend(repo.get_missing_chunks())
    log("Repos:")
    for repo in repos:
        log(repo)

    mn = MetaNet(config)

    for chunk in all_known_chunks:
        mn.offer(chunk)

    for chunk in all_missing_chunks:
        mn.request(chunk)


def cmd_stat(args, config):
    r = Repo(args.filename, args.directory, os.path.basename(args.filename))
    chunks = r.get_known_chunks()
    seen = {}
    for chunk in chunks:
        if chunk.id not in seen:
            seen[chunk.id] = 0
        seen[chunk.id] = seen[chunk.id] + 1
    import pprint
    pprint.pprint(seen)

    saved = 0
    for id, count in seen.items():
        dupes = count - 1
        type, size, hash = id.split(":")
        saved = saved + int(size) * dupes
    print "Saved %d bytes from deduplication" % saved


def main():
    try:
        config = json.loads(open(config_file_path).read())
    except Exception as e:
        log("Error loading default config: %s" % str(e))
        config = {}
    args = sys.argv[1:]
    if args:
        do(args, config)
    else:
        while True:
            cmd = raw_input("chunker> ")
            try:
                print do(cmd.split(), config)
            except Exception as e:
                print {"status": "error", "message": str(e)}


class NonExitingArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        raise Exception(message)


def do(argv, config):
    parser = NonExitingArgumentParser(description="a thing")
    subparsers = parser.add_subparsers()

    p_chunk = subparsers.add_parser("chunk")
    p_chunk.add_argument("output")
    p_chunk.add_argument("input")
    p_chunk.add_argument("--name")
    p_chunk.set_defaults(func=cmd_chunk)

    p_heal = subparsers.add_parser("heal")
    #p_heal.add_argument("filename")
    #p_heal.add_argument("directory")
    p_heal.set_defaults(func=cmd_heal)

    p_add = subparsers.add_parser("add")
    p_add.add_argument("--name")
    p_add.add_argument("filename")
    p_add.add_argument("directory")
    p_add.set_defaults(func=cmd_add)

    p_fetch = subparsers.add_parser("fetch")
    p_fetch.set_defaults(func=cmd_fetch)

    p_stat = subparsers.add_parser("stat")
    p_stat.add_argument("filename")
    p_stat.add_argument("directory")
    p_stat.set_defaults(func=cmd_stat)

    args = parser.parse_args(argv)
    return args.func(args, config)


if __name__ == "__main__":
    sys.exit(main())
