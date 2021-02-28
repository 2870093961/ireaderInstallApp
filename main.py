from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5 import QtWidgets, QtGui
from ui import UI
import webbrowser
import zipfile
import time
import sys
import os
import re


class Install(QThread):
    stop = pyqtSignal()
    status = True

    def __init__(self):
        super(Install, self).__init__()

    def run(self):
        ui.textEdit.append('')
        while self.status:
            main.showLog(text='.', br=True)
            main.execCmd(f"{os.path.join(os.getcwd(), 'adb/adb.exe')} install {self.apk['filePath']}")
            time.sleep(0.2)
        self.stop.emit()


class Main():
    aapt = os.path.join(os.getcwd(), r'adb\aapt.exe')

    def showLog(self, text, color='#333333', size=14, br=False, stime=True):
        if br:
            ui.textEdit.insertPlainText(text)
        else:
            ui.textEdit.append(
                f'<font color="{color}" style="font-size:{size}px">{time.strftime("%H:%M:%S", time.localtime()) + " - " if stime else ""}{text}</font>')
        ui.textEdit.moveCursor(QTextCursor.End)

    def execCmd(self, cmd):
        exe = os.popen(cmd)
        result = exe.buffer.read().decode(encoding='utf8')
        exe.close()
        return result

    def size_format(self, b):
        if b < 1024:
            return '%d B' % b
        elif 1024 <= b < 1048576:
            return '%.2f KB' % (b / 1024)
        elif 1048576 <= b < 1073741824:
            return '%.2f MB' % (b / 1048576)
        elif 1073741824 <= b < 1099511627776:
            return '%.2f GB' % (b / 1073741824)
        elif 1099511627776 <= b:
            return '%.2f TB' % (b / 1099511627776)

    def apkInfo(self, aapt, apk):
        info = self.execCmd(f"{aapt} dump badging {apk}")
        line1 = re.search("name='.+\n", info).group().split(' ')
        line2 = re.search("application: label='.+' icon='.+'", info).group().split(' icon')
        name = line2[0][20:-1]
        icon = line2[1][2:-1]
        package = line1[0][6:-1]
        version = line1[2][13:-1]
        size = self.size_format(os.path.getsize(apk))
        zip = zipfile.ZipFile(apk)
        iconData = zip.read(icon)
        iconPath = os.path.join('res/', name + os.path.splitext(icon)[-1])
        if os.path.splitext(icon)[-1] == '.xml':
            iconPath = 'res/apk.png'
        else:
            with open(iconPath, 'wb') as fp:
                fp.write(iconData)
        return {
            "name": name,
            "package": package,
            "version": version,
            "filePath": apk,
            "iconPath": iconPath,
            "size": size
        }

    def openApk(self):
        file = QFileDialog.getOpenFileName(None, "选择你需要的app安装包", os.path.join(os.getcwd(), "apk"), "APK Files (*.apk)")[
            0]
        if file:
            info = self.apkInfo(self.aapt, file)
            ui.label_2.setText('名称：' + info['name'])
            ui.label_4.setText('包名：' + info['package'])
            ui.label_3.setText('版本号：' + info['version'])
            ui.label_5.setText('大小：' + info['size'])
            ui.label.setPixmap(QtGui.QPixmap(info['iconPath']))
            ui.apk = info
            for i, j in info.items():
                self.showLog(f"{i}:{j}")

    def stop(self):
        self.showLog('已停止安装', '#FF0000')
        ui.pushButton_2.setText('开始安装')

    def about(self):
        ui.msg = QMessageBox()
        ui.msg.setWindowTitle('关于')
        ui.msg.setText("名称：ireader阅读器第三方应用安装\n版本：v1.0.0\n作者: 洛月\n联系方式：QQ2870093961")
        ui.msg.show()

    def installApk(self):
        if ui.pushButton_2.text() == '停止安装':
            ui.install.status = False
            return
        if ui.apk:
            ui.install = Install()
            ui.install.apk = ui.apk
            ui.install.stop.connect(self.stop)
            ui.install.start()
            self.showLog(f'开始安装：{ui.apk["name"]}', '#FF0000')
            ui.pushButton_2.setText('停止安装')
            QMessageBox.warning(None, '重启阅读器', '请反复重启阅读器，直到安装成功！！！\n[长按开机按钮>重启>确定]\n打开阅读器 [我的>工具>全部] 进行查看')
        else:
            QMessageBox.warning(None, '请先选择安装包', '点击 [打开APK] 按钮')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QWidget()
    ui = UI()
    ui.setupUi(window)
    main = Main()
    ui.pushButton.clicked.connect(main.openApk)
    ui.pushButton_2.clicked.connect(main.installApk)
    ui.pushButton_3.clicked.connect(main.about)
    ui.pushButton_4.clicked.connect(lambda: webbrowser.open('http://note.youdao.com/s/GWsTGFuh'))
    ui.pushButton_5.clicked.connect(lambda: webbrowser.open('http://www.ferebook.com/books/'))
    ui.pushButton_6.clicked.connect(lambda: webbrowser.open('http://note.youdao.com/s/SAyXXFaz'))
    main.showLog('1.把阅读器用数据线连接到电脑（请确保只没有其它安卓手机或设备连接）打开文件管理查看是否连接成功', color="#008080", stime=False)
    main.showLog('2.点击［打开APK］按钮选择需要安装的app文件', color="#008080", stime=False)
    main.showLog('3.点击［开始安装］', color="#008080", stime=False)
    main.showLog('4.长按阅读器开机键选择重启', color="#008080", stime=False)
    main.showLog('5.等待阅读器重启完成打开［我的>工具>全部］查看应用是否安装成功，如果没有安装成功请再次重启(如多次尝试无效请联系qq2870093961)', color="#008080",
                 stime=False)
    main.showLog('6.安装成功后点击［停止安装］，至此安装完成', color="#008080", stime=False)
    window.show()
    sys.exit(app.exec_())
