#!/usr/bin/env bash

SR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

RED=$(tput setaf 1)
GREEN=$(tput setaf 2)
RESET=$(tput sgr0)

check_root_uid() {
    [ $UID -eq 0 ] || {
        fatal "$(basename "$0") needs to be run as root (uid=0) only"
        exit 1
    }
}

check_no_root_uid() {
    [ $UID -ne 0 ] || {
        fatal "$(basename "$0") need to be run as non-root (uid!=0) only"
        exit 1
    }
}

fatal() {
    if test -t 1; then
        echo "${RED}fatal:${RESET} $*" 1>&2
    else
        echo "fatal: $*" 1>&2
    fi
}

info() {
	if test -t 1; then
		echo "${GREEN}info:${RESET} $*" 1>&2
	else
		echo "info: $*" 1>&2
	fi
}

get_apt_repo_namespace() {
    local branch=$1
    local ns=alt
    if [ "$branch" != sisyphus ]; then
        ns="$branch"
    fi
    echo "$ns"
}

get_apt_repo_branch() {
    local branch=$1
    local repo_branch=Sisyphus

    if [ "$branch" != sisyphus ]; then
        repo_branch="$branch/branch"
    fi
    echo "$repo_branch"
}

get_apt_repo_arch() {
    local arch=$1
    case "$arch" in
        x86_64)
            echo 64;;
        i586)
            echo 32;;
        -)
            fatal "Architecture \"$arch\" not allowed."
            exit 1
    esac
}

# Split passwd file (/etc/passwd) into
# /usr/etc/passwd - home users password file (uid >= 500)
# /lib/passwd - system users password file (uid < 500)
split_passwd() {
    local from_pass=$1
    local sys_pass=$2
    local user_pass=$3

    touch "$sys_pass"
    touch "$user_pass"

    set -f

    local ifs=$IFS

    exec < "$from_pass"
    while read -r line
    do
        IFS=:;set -- $line;IFS=$ifs

        user=$1
        uid=$3

        if [[ $uid -ge 500 || $user = "root" || $user = "systemd-network" ]]
        then
            echo "$line" >> "$user_pass"
        else
            echo "$line" >> "$sys_pass"
        fi
    done
}

# Split group file (/etc/group) into
# /usr/etc/group - home users group file (uid >= 500)
# /lib/group - system users group file (uid < 500)
split_group() {
    local from_group=$1
    local sys_group=$2
    local user_group=$3

    touch "$sys_group"
    touch "$user_group"

    set -f

    local ifs=$IFS

    exec < "$from_group"
    while read -r line
    do
        IFS=:;set -- $line;IFS="$ifs"
        user=$1
        uid=$3
        if [[ $uid -ge 500 ||
              $user = "root" ||
              $user = "adm" ||
              $user = "wheel" ||
              $user = "systemd-network" ||
              $user = "systemd-journal" ||
              $user = "docker" ]]
        then
            echo "$line" >> "$user_group"
        else
            echo "$line" >> "$sys_group"
        fi
    done
}

export_stream() {
    local branch=$1
    local arch=$2
    local substream=$3

    if [ -z "$substream" ]
    then
        to_export=$(python3 "$SR"/export-stream -a "$arch" -b "$branch") || exit 1
    else
        to_export=$(python3 "$SR"/export-stream -a "$arch" -b "$branch" -s "$substream") || exit 1
    fi
    eval "$to_export"
}

export_stream_by_ref() {
    local ref=$1

    to_export=$(python3 "$SR"/ref-info "$ref") || exit 1
    eval "$to_export"
}

check_envs() {
    failed=false
    for env in "$@"
    do
        if [ -z "${!env}" ]
        then
            fatal "Environment variable \"$env\" is not set."
            failed=true
        fi
    done

    if $failed; then exit 1; fi
}

ref_info() {
    python3 "$SR"/ref-info "${@}" || exit 1
}

check_version_part() {
    local part=$1
    case "$part" in
        major|minor);;
        *)
            fatal "Invalid part to increment ($part)."
            exit 1;;
    esac
}

prepare_apt_dirs() {
    local root_dir=$1

    sudo mkdir -p \
        "$root_dir"/var/lib/apt/lists/partial \
        "$root_dir"/var/cache/apt/archives/partial \
        "$root_dir"/var/cache/apt/gensrclist \
        "$root_dir"/var/cache/apt/genpkglist

    sudo chmod -R 770 "$root_dir"/var/cache/apt
    sudo chmod -R g+s "$root_dir"/var/cache/apt
    sudo chown root:rpm "$root_dir"/var/cache/apt
}

is_base_ref() {
    local ref=$1
    python3 "$SR"/ref-info "$ref" -b | grep True &>/dev/null || return 1
    return 0
}

get_platform_dirs() {
    local platform=$1
    echo "$(python3 -c "from altcos.build import *; print(*ALLOWED_FORMATS[Platform(\"$platform\")])")"
}

init_platform_dir() {
    local platform=$1
    local stream_ref=$2
    local builds_dir=$3
    local version=$4
    (
        export_stream_by_ref "$stream_ref"

        dir="$builds_dir"/"$BRANCH"/"$ARCH"/base/"$version"/"$platform"
        if ! is_base_ref "$stream_ref"; then
            dir="$builds_dir"/"$BRANCH"/"$ARCH"/"$SUBSTREAM"/"$version"/"$platform"
        fi

        for dirname in $(get_platform_dirs "$platform"); do
            mkdir -p "$dir"/"$dirname"
        done
        echo "$dir"
    )
}

sign_file() {
    local file=$1
    gpg \
        --output "$file".sig \
        --sign "$file"
    echo "$file".sig
}

get_allowed_architectures() {
    echo "$(python3 -c "from altcos.ostree import *; print(*Arch)")"
}

get_allowed_branches() {
    echo "$(python3 -c "from altcos.ostree import *; print(*Branch)")"
}

get_img_stream_prefix() {
    local stream_ref=$1
    (
        export_stream_by_ref "$stream_ref"

        img_stream_prefix="$BRANCH"
        if ! is_base_ref "$STREAM_REF"; then
            img_stream_prefix="$BRANCH"_"$SUBSTREAM"
        fi

        echo "$img_stream_prefix"
    )
}

get_ostree_dir() {
    local stream_ref=$1
    local mode=$2
    (
        export_stream_by_ref "$stream_ref"
        case "$mode" in
        bare)
            ostree_dir="$OSTREE_BARE_DIR";;
        archive)
            ostree_dir="$OSTREE_ARCHIVE_DIR";;
        esac
        echo "$ostree_dir"
    )
}