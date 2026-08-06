hl.on("hyprland.start", function ()
   hl.exec_cmd("noctalia")

   hl.exec_cmd("gnome-keyring-daemon --start --components=secrets")
   --hl.exec_cmd("hypridle")
   hl.exec_cmd("dbus-update-activation-environment --all")
   hl.exec_cmd("sleep 1 && dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP")

   -- Import shipped dconf settings on first boot (no existing theme key)
   hl.exec_cmd("dconf read /org/gnome/desktop/interface/gtk-theme || dconf load / < ~/.config/dconf/all.ini")

   hl.exec_cmd("hyprctl setcursor Bibata-Modern-Classic 24")
   hl.exec_cmd("fcitx5")
end)

hl.env("XCURSOR_SIZE", "24")
hl.env("HYPRCURSOR_SIZE", "24")

hl.env("QT_QPA_PLATFORM", "wayland;xcb")
hl.env("QT_QPA_PLATFORMTHEME", "qt6ct")

hl.env("ELECTRON_OZONE_PLATFORM_HINT", "auto")
hl.env("XMODIFIERS","@im=fcitx")
