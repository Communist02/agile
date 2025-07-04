cd ../
flatpak-builder build-dir flatpak.yaml --force-clean
flatpak build-export rclone-explorer-repo build-dir
flatpak build-bundle rclone-explorer-repo RcloneExplorer.flatpak com.mazur.RcloneExplorer
flatpak uninstall -y com.mazur.RcloneExplorer
flatpak install -y --bundle --user RcloneExplorer.flatpak
flatpak run com.mazur.RcloneExplorer
