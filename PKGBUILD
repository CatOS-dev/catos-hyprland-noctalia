pkgname=catos-hyprland-noctaliav5
pkgver=1.0.0
pkgrel=1
pkgdesc="CatOS Hyprland desktop profile powered by Noctalia v5"
arch=('any')
url="https://github.com/CatOS-dev/catos-hyprland-noctaliav5"
license=('GPL-3.0-only')

depends=(
  "catdot"
  "hyprland"
  "xdg-desktop-portal-gtk"
  "xdg-desktop-portal-hyprland"
  "noctalia"
  "cava"
  "adw-gtk-theme"
  "breeze"
  "breeze5"
  "breeze-gtk"
  "papirus-icon-theme"
  "qt6-multimedia"
  "wtype"
  "kitty"
  "brightnessctl"
  "playerctl"
  "wireplumber"
  "qt5ct"
  "qt6ct"
  "catos-bibata-cursor"
  "dconf"
  "nautilus"
  "gnome-keyring"
  "fcitx5"
  "firefox"
  "grim"
  "slurp"
  "swappy"
  "fish"
  "ttf-jetbrains-mono-nerd"
)

makedepends=('git')

source=('git+https://github.com/CatOS-dev/catos-hyprland-noctaliav5.git')
sha256sums=('SKIP')

package() {
  cd "${srcdir}/${pkgname}"

  install -d "${pkgdir}/usr"
  cp -a usr/. "${pkgdir}/usr/"
}
