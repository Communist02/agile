import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Window

ApplicationWindow {
    width: 1280
    height: 720
    visible: true
    title: qsTr("Cloud Explorer")

    menuBar: MenuBar {
        Menu {
            title: qsTr("&Client")
            Action {
                text: qsTr("&Add disk")
            }
            MenuSeparator {}
            Action {
                text: qsTr("&Preferences")
            }
            MenuSeparator {}
            Action {
                text: qsTr("&Quit")
                onTriggered: backend.quit()
            }
        }
        Menu {
            title: qsTr("&Other")
            Action {
                text: qsTr("&About")
            }
        }
    }

    header: ToolBar {
        RowLayout {
            anchors.fill: parent
            ToolButton {
                text: "ᐸ"
                onClicked: stack.pop()
            }
            ToolButton {
                text: "ᐳ"
                onClicked: stack.pop()
            }
            ToolButton {
                text: "ᐱ"
                onClicked: backend.exit_folder()
            }
            Label {
                id: currentPathLabel
                text: ""
                elide: Label.ElideRight
                horizontalAlignment: Qt.AlignHCenter
                verticalAlignment: Qt.AlignVCenter
                Layout.fillWidth: true
            }
            ToolButton {
                text: "⋮"
                onClicked: {

                }
            }
        }
    }

    RowLayout {
        anchors.fill: parent
        ColumnLayout {
            spacing: 2
            Layout.preferredWidth: 200
            Layout.fillHeight: true

            ListView {
                model: disksListModel
                Layout.fillHeight: true
                delegate: Button {
                    width: 200
                    text: model.modelData.text
                    onClicked: backend.open_folder(true,
                                                   model.modelData.text, "")
                }
            }
        }

        // Правая колонка с вкладками
        ColumnLayout {
            Layout.fillHeight: true
            Layout.fillWidth: true
            spacing: 5

            TabBar {
                id: tabBar
                Layout.fillWidth: true

                TabButton {
                    text: qsTr("Home")
                }
            }

            StackLayout {
                id: tabs
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: tabBar.currentIndex

                Item {}
            }
        }
    }

    Connections {
        target: backend
        function onOpen_disk_signal(diskName, tree) {
            Qt.createQmlObject(`
                               import QtQuick
                               import QtQuick.Controls
                               TabButton {
                               text: "` + diskName + `"
                               }
                               `, tabBar)
            var component = Qt.createComponent("FileList.qml")

            component.createObject(tabs, {
                                       "diskName": diskName,
                                       "tree": tree
                                   })
        }

        function onCurrent_disk_path_update_signal(path) {
            currentPathLabel.text = path
        }
    }
}
