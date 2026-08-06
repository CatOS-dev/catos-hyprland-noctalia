#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROFILE_ID="catos-hyprland-noctaliav5"
MANIFEST="$SCRIPT_DIR/usr/share/catdot/profiles/$PROFILE_ID/profile.toml"
CONTENT="$SCRIPT_DIR/usr"
INSTALL_PACKAGES="${INSTALL_PACKAGES:-1}"
DO_SELECT="${DO_SELECT:-1}"
REMOVE_PACKAGES="${REMOVE_PACKAGES:-0}"

info() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }
ok()   { printf '\033[1;32m==>\033[0m %s\n' "$*"; }
warn() { printf '\033[1;33m==>\033[0m %s\n' "$*"; }
die()  { printf '\033[1;31m==>\033[0m %s\n' "$*" >&2; exit 1; }
confirm() {
    while :; do
        read -r -p "$1 [y/N] " answer
        case "$answer" in
            y|Y) return 0 ;;
            n|N|"") return 1 ;;
            *) warn "please answer y or n" ;;
        esac
    done
}

ensure_root() {
    if [ "$(id -u)" -ne 0 ]; then
        if command -v sudo >/dev/null 2>&1; then
            exec sudo bash "$0" "$@"
        fi
        die "run as root (or make sure sudo is available)"
    fi
}

read_packages() {
    python3 -c '
import sys, tomllib
m = tomllib.load(open(sys.argv[1], "rb"))
print(" ".join(m.get("packages", [])))
' "$MANIFEST"
}

do_install() {
    [ -f "$MANIFEST" ] || die "manifest not found: $MANIFEST"
    [ -d "$CONTENT" ] || die "payload tree missing: $CONTENT"

    packages="$(read_packages)"

    info "installing profile payload to /usr"
    cp -a "$SCRIPT_DIR/usr" /

    if [ "$INSTALL_PACKAGES" = "1" ] && [ -n "$packages" ]; then
        info "installing required packages with pacman"
        pacman -S --needed --noconfirm $packages
    fi

    info "refreshing profile payload owned by catdot"
    if command -v catdot >/dev/null 2>&1; then
        if [ "$DO_SELECT" = "1" ]; then
            catdot select "$PROFILE_ID"
        else
            catdot update "$PROFILE_ID"
        fi
    else
        warn "catdot not found on PATH; run 'catdot select $PROFILE_ID' manually"
    fi

    ok "installed: $PROFILE_ID"
}

do_uninstall() {
    profile_manifest="/usr/share/catdot/profiles/$PROFILE_ID"
    profile_content="/usr/share/$PROFILE_ID"

    if [ ! -d "$profile_manifest" ] && [ ! -d "$profile_content" ]; then
        die "profile is not installed: $PROFILE_ID"
    fi

    if command -v catdot >/dev/null 2>&1; then
        info "deselecting profile with catdot"
        catdot deselect "$PROFILE_ID" 2>/dev/null || catdot update --reset 2>/dev/null || true
    fi

    info "removing /usr/share/catdot/profiles/$PROFILE_ID"
    rm -rf "$profile_manifest"
    info "removing /usr/share/$PROFILE_ID"
    rm -rf "$profile_content"

    if [ "$REMOVE_PACKAGES" = "1" ]; then
        packages="$(read_packages)"
        if [ -n "$packages" ]; then
            installed="$(pacman -Qq 2>/dev/null)"
            remove=""
            for pkg in $packages; do
                case " $installed " in *" $pkg "*) remove="$remove $pkg" ;; esac
            done
            if [ -n "$remove" ]; then
                info "removing packages:${remove# }"
                pacman -R --noconfirm $remove
            else
                info "none of the profile packages are installed"
            fi
        fi
    else
        warn "skipping package removal (set REMOVE_PACKAGES=1 to remove them)"
    fi

    ok "uninstalled: $PROFILE_ID"
}

case "${1:-install}" in
    install) ensure_root "$0" "$@"; do_install ;;
    uninstall) ensure_root "$0" "$@"; do_uninstall ;;
    *) die "usage: $0 [install|uninstall]" ;;
esac
