# catos-hyprland-noctaliav5

Complete CatOS Hyprland desktop Profile powered by Noctalia.

The repository contains the installed Profile tree directly:

```text
usr/share/catdot/profiles/catos-hyprland-noctaliav5/profile.toml
usr/share/catos-hyprland-noctaliav5/...
```

Select the Profile with:

```sh
catdot select catos-hyprland-noctaliav5
```

Catdot installs the exact package names declared by the Profile and maps the
content below `/usr/share/catos-hyprland-noctaliav5` into the user's HOME. Switching a
Profile does not restart applications or the desktop session.

## Managed configuration

The Profile owns and refreshes these paths:

```text
.config/dconf/all.ini
.config/gtk-3.0/gtk.css
.config/gtk-3.0/settings.ini
.config/gtk-4.0/settings.ini
.config/hypr/hyprland.lua
.config/kitty/kitty.conf
.config/noctalia/config.toml
.config/qt6ct/qt6ct.conf
```

Run the following command to explicitly accept a newer installed revision:

```sh
catdot update catos-hyprland-noctaliav5
```

## Seed configuration

All other files under `/usr/share/catos-hyprland-noctaliav5` are initial Profile seeds.
The managed main Hyprland config loads the modular profile seeds from
`~/.config/hypr/modules/`. Its `input.lua`, `monitors.lua`, `keybinds.lua`,
`rules.lua` and the rest are installed once and are never managed, so later
selections and updates preserve user changes.

Noctalia's generated outputs are seeds as well. Bootable snapshots shipped next
to them let a clean HOME start before Noctalia runs for the first time:

```text
.config/hypr/noctalia.lua
.config/gtk-3.0/noctalia.css
.config/gtk-4.0/noctalia.css
.config/kitty/themes/noctalia.conf
.config/qt6ct/colors/noctalia.conf
```

Hyprland starts noctalia, gnome-keyring, fcitx5 and dconf import directly from
the `autostart` module. Terminal, file manager and Noctalia bindings invoke
kitty, nautilus and noctalia directly; no Catdot runtime wrapper is used.