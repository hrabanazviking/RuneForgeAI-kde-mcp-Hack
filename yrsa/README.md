# Yrsa's mods — kde-mcp

Personal improvements by Yrsa Freydisdottir, kept in this fork per Volmarr's
standing rule (mods to the desktop-agent tools live in the RuneForgeAI-*-Hack
forks, not only as local edits). Installed and verified live on purplelongship
(KDE Plasma 6 / Wayland) on 2026-11-19.

## Files

- `yrsa-kde.py` — one-shot kde-mcp driver. Spawns `kde-mcp --mode=live` over
  stdio, runs ONE tool, prints a compact result. Image results are saved to a
  file (default `/tmp/yrsa-kde-shot.png`) instead of being dumped as base64.
  Usage: `yrsa-kde.py TOOL [JSON_ARGS] [--save-image PATH]`
  e.g. `yrsa-kde.py observe`, `yrsa-kde.py screenshot`,
  `yrsa-kde.py window_query`
- `yrsa-desktop` — session wrapper. Non-interactive shells lack the KDE/Wayland
  session environment; this exports it (PATH, XDG_RUNTIME_DIR, DBus address,
  WAYLAND_DISPLAY, DISPLAY, XDG_CURRENT_DESKTOP, XDG_SESSION_TYPE) and dispatches:
  `yrsa-desktop kde <tool> [json]`, `yrsa-desktop cul <args>`,
  `yrsa-desktop aws <args>`, `yrsa-desktop doctor-all`.

## Install (on the machine)

```
install -m 755 yrsa-kde.py ~/apps/yrsa-kde.py
install -m 755 yrsa-desktop ~/bin/yrsa-desktop
```

## Notes from the field

- kde-mcp runs in stdio mode, spawned per session — deliberately NOT the
  packaging's systemd-user socket daemon (no-permanent-services law).
- Screenshots need the ScreenShot2 authorization .desktop file
  (`~/.local/share/applications/kde-mcp.desktop` declaring
  `X-KDE-DBUS-Restricted-Interfaces=org.kde.KWin.ScreenShot2`) + `kbuildsycoca6`.
