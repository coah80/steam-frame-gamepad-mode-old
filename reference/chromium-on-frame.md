# Chromium and Electron apps on the Frame

## Steam's injected libraries crash Chromium

Steam starts every game, non-Steam shortcuts included, with:

- `LD_PRELOAD` = its overlay (`ubuntu12_64/gameoverlayrenderer.so`, `ubuntu12_32/...`, plus an arm64 entry)
- `LD_LIBRARY_PATH` = its runtime's pinned libraries

With both set, Chromium's zygote dies before any app code runs:

```
FATAL:content/browser/zygote_host/zygote_host_impl_linux.cc:213] Zygote process exited prematurely with exit code -1
ERROR:content/zygote/zygote_linux.cc:662] write: Broken pipe (32)
```

Removing either variable is enough. The same binary started over SSH works, which hides the problem until it is launched from Steam. To reproduce, replay Steam's environment exactly: read `/proc/<pid>/environ` of the running `reaper SteamLaunch AppId=<id>` process and pass it to `subprocess` (shell quoting mangles values with spaces).

The fix is a launcher that is the program Steam starts: it drops `LD_PRELOAD` and `LD_LIBRARY_PATH` and `execve`s the real binary next to it, passing argv and every other variable through. FrameTube's is [`launcher/launcher.c`](https://github.com/coah80/frametube/blob/main/launcher/launcher.c): static and freestanding (raw syscalls, own `_start`, aarch64 and x86_64), so it has no libraries for Steam's variables to affect, built with any clang + lld. Name the launcher as the app's program (a `.desktop` file with `Exec=<launcher>` makes FramePort and app menus pick it over the larger Electron binary). The Steam overlay then doesn't hook the app.

A shell script works too (`#!/bin/sh` + `exec env -u LD_PRELOAD -u LD_LIBRARY_PATH "$(dirname "$0")/app-binary" "$@"`) if you add the script to Steam yourself. FrameTube's launcher is a static ELF because FramePort only offers ELF programs as an app's program, and because a static binary has nothing for Steam's `LD_PRELOAD` to load into.

## The setuid sandbox helper

Electron ships `chrome-sandbox`, a setuid helper that must be owned by root with mode 4755. Copied into a home folder on the Frame it is not, and Chromium aborts: "The SUID sandbox helper binary was found, but is not configured correctly". Delete it from the build (FrameTube: an electron-builder `afterPack` hook). Chromium then sandboxes with unprivileged user namespaces, which SteamOS allows (`unshare -U -r true` succeeds, `/proc/sys/user/max_user_namespaces` is large). The sandbox stays on; on the test Frame no `--no-sandbox` was needed.

Desktop distros that restrict unprivileged user namespaces with AppArmor (Ubuntu 23.10+) fail with "No usable sandbox!". There the app needs `--no-sandbox` in its launch options.

## Other Chromium notes

- `app.commandLine.appendSwitch(...)` cannot fix startup problems: the zygote and sandbox start before Electron runs the main script.
- Cross-building the arm64 app on x86_64 works with `electron-builder --linux dir --arm64` when the app has no native Node modules.
- On the Frame the log shows harmless `GetVSyncParametersIfAvailable() failed` and `Gamescope WSI` lines; rendering works.
- A web app that only serves its TV interface to TVs (youtube.com/tv) accepts a Cobalt user agent, e.g. `Mozilla/5.0 (Linux; Android 12) Cobalt/22.2.3-gold (PS4)`, set through `session.defaultSession.setUserAgent`.
