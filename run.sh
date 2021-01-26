#!/usr/bin/env bash

set -euo pipefail

script_dir="$(readlink -e "${BASH_SOURCE[0]}")"
script_dir="$(dirname "$script_dir")"

PROGRAM_NAME=run.sh

function print_error_message ()
{
  if [[ -t 2 ]] && type -t tput >/dev/null; then
    if (( "$(tput colors)" == 256 )); then
      echo "$(tput setaf 9)$1$(tput sgr0)" >&2
    else
      echo "$(tput setaf 1)$1$(tput sgr0)" >&2
    fi
  else
    echo "$1" >&2
  fi
}

function die_with_user_error ()
{
  print_error_message "$PROGRAM_NAME: error: $1"
  print_error_message "Try \`$PROGRAM_NAME --help' for more information."
  exit 1
}

function die_with_runtime_error ()
{
  print_error_message "$PROGRAM_NAME: error: $1"
  exit 1
}

function print_usage ()
{
  cat <<'EOF'
Usage: ./run.sh LEFT_URL RIGHT_URL -- [OPTION]...
Compare two .proto files specified by `LEFT_URL' and `RIGHT_URL'. The trailing
options are passed to `diff' as-is.

  -h, --help                 Display this help and exit.
EOF
}

if getopt -T; (( $? != 4 )); then
  die_with_runtime_error "$PROGRAM_NAME" "\`getopt' is not an enhanced version."
fi
opts="$(getopt -n "$PROGRAM_NAME" -l help -- h "$@")"
eval set -- "$opts"

while (( $# > 0 )); do
  arg="$1"
  shift
  case "$arg" in
  -h|--help)
    print_usage
    exit 0
    ;;
  --)
    if (( $# < 2 )); then
      die_with_user_error "Too few arguments."
    fi
    left="$1"
    shift
    right="$1"
    shift
    options=("$@")
    break
    ;;
  *)
    die_with_user_error "An invalid argument \`$arg'."
    ;;
  esac
done

tempdir="$(mktemp -d)"
trap "rm -rf '$tempdir'" EXIT

docker build . >"$tempdir/docker-build.log" \
  || die_with_runtime_error "Failed to execute \`docker build .'"
image="$(grep -E '^Successfully built [[:alnum:]]+$' "$tempdir/docker-build.log" | grep -Eo '[[:alnum:]]+$')"

docker run -t "$image" "$left" "$right" "${options[@]}"
