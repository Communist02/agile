import QtQuick
import QtQuick.Controls
import Qt.labs.qmlmodels
import QtQuick.Layouts
import QtQuick.Dialogs
import Qt.labs.platform as Labs

Rectangle {
    id: table
    required property var tree
    required property var diskName
    anchors.fill: parent
    // The background color will show through the cell
    // spacing, and therefore become the grid line color.
    color: Application.styleHints.appearance === Qt.Light ? palette.mid : palette.midlight

    HorizontalHeaderView {
        id: horizontalHeader
        anchors.left: tableView.left
        anchors.top: parent.top
        syncView: tableView
        model: [' ' + qsTr("Name"), ' ' + qsTr("Size"), ' ' + qsTr(
                "Modified"), ' ' + qsTr("Type")]
        clip: true
        delegate: Label {
            text: modelData
        }
    }

    VerticalHeaderView {
        id: verticalHeader
        anchors.top: tableView.top
        anchors.left: parent.left
        syncView: tableView
        clip: true
    }

    TableView {
        id: tableView
        anchors.left: verticalHeader.right
        anchors.top: horizontalHeader.bottom
        anchors.right: parent.right
        anchors.bottom: parent.bottom
        clip: true

        property int current1: -1

        ScrollBar.horizontal: ScrollBar {
            id: hbar
            active: vbar.active
        }
        ScrollBar.vertical: ScrollBar {
            id: vbar
            active: hbar.active
        }

        selectionModel: ItemSelectionModel {}

        model: TableModel {
            TableModelColumn {
                display: "name"
            }
            TableModelColumn {
                display: "size"
            }
            TableModelColumn {
                display: "modified"
            }
            TableModelColumn {
                display: "type"
            }

            rows: tree ? tree.slice() : []
        }

        delegate: Rectangle {
            implicitWidth: index == 0 ? 400 : 200
            implicitHeight: 20
            color: row == tableView.current1 ? palette.highlight : palette.base

            Label {
                text: display
            }

            MouseArea {
                anchors.fill: parent
                acceptedButtons: Qt.LeftButton | Qt.RightButton

                onClicked: mouse => {
                               tableView.current1 = model.row
                               if (mouse.button === Qt.RightButton) {
                                   contextMenu.popup()
                               }
                           }

                onDoubleClicked: mouse => {
                                     if (mouse.button === Qt.LeftButton) {
                                         if (tree[model.row].is_dir) {
                                             tableView.current1 = -1
                                             backend.open_folder(
                                                 false, diskName,
                                                 tree[model.row].path)
                                         } else {
                                             backend.open_file(
                                                 diskName, tree[model.row].path)
                                         }
                                     }
                                 }

                Menu {
                    id: contextMenu
                    MenuItem {
                        text: qsTr("Open")
                        onTriggered: {
                            if (tree[model.row].is_dir) {
                                tableView.current1 = -1
                                backend.open_folder(false, diskName,
                                                    tree[model.row].path)
                            } else {
                                backend.open_file(diskName,
                                                  tree[model.row].path)
                            }
                        }
                    }
                    MenuItem {
                        text: qsTr("Download")

                        onTriggered: fileDialog.open()

                        FolderDialog {
                            id: fileDialog

                            onAccepted: {
                                backend.download_file(diskName,
                                                      tree[model.row].path,
                                                      selectedFolder,
                                                      tree[model.row].name)
                            }
                        }
                    }
                    MenuItem {
                        text: qsTr("Copy")
                    }
                    MenuItem {
                        text: qsTr("Rename")
                    }
                    MenuItem {
                        text: qsTr("Delete")
                    }
                }
            }
        }
    }

    Connections {
        target: backend
        function onOpen_folder_signal(title, files) {
            tableView.model.rows = files ? files.slice() : []
            tree = files
        }
    }
}
