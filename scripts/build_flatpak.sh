cd ../
flatpak-builder build-dir flatpak.yaml --force-clean
flatpak build-export rclone-explorer-repo build-dir
flatpak build-bundle rclone-explorer-repo rclone_explorer.flatpak com.mazur.rclone_explorer
