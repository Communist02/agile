cd ../
flatpak-builder build-dir flatpak.yaml --force-clean
flatpak build-export rclone-explorer-repo build-dir
flatpak build-bundle rclone-explorer-repo rclone_explorer.flatpak com.mazur.rclone_explorer
flatpak uninstall -y --user com.mazur.rclone_explorer
flatpak install -y --bundle --user rclone_explorer.flatpak
flatpak run com.mazur.rclone_explorer
