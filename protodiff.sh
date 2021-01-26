#!/usr/bin/env bash

set -euo pipefail

tempdir=$(mktemp -d)
trap "rm -rf '$tempdir'" EXIT

left_url="$1"
shift
right_url="$1"
shift

cd "$tempdir" && wget -qO "$tempdir/left.proto" "$left_url"
[[ -f "$tempdir/left.proto" ]]
left_proto="$tempdir/left.proto"
cd "$tempdir" && wget -qO "$tempdir/right.proto" "$right_url"
[[ -f "$tempdir/right.proto" ]]
right_proto="$tempdir/right.proto"

cd "$tempdir" && protoc --python_out=. left.proto || cat left.proto
[[ -f "$tempdir/left_pb2.py" ]]
left_py="$tempdir/left_pb2.py"
cd "$tempdir" && protoc --python_out=. right.proto || cat right.proto
[[ -f "$tempdir/right_pb2.py" ]]
right_py="$tempdir/right_pb2.py"

mkdir "$tempdir/protodiff"
touch "$tempdir/protodiff/__init__.py"
mv "$left_py" "$right_py" "$tempdir/protodiff"
PYTHONPATH="$tempdir" /opt/protodiff/normalize.py "protodiff.left_pb2" >"$tempdir/left.normalized.proto"
[[ -f "$tempdir/left.normalized.proto" ]]
left_normalized_proto="$tempdir/left.normalized.proto"
PYTHONPATH="$tempdir" /opt/protodiff/normalize.py "protodiff.right_pb2" >"$tempdir/right.normalized.proto"
[[ -f "$tempdir/right.normalized.proto" ]]
right_normalized_proto="$tempdir/right.normalized.proto"

diff "$@" "$left_normalized_proto" "$right_normalized_proto"
