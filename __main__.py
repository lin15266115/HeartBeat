import os
import sys
import json
import asyncio

is_frozen = getattr(sys, 'frozen', False)

frozenvname = "1.2.1-alpha"
frozenver = 1.002001

from writer import logger, init_config

if is_frozen:
    __version__ = frozenvname
    ver = frozenver
else:
    __version__ = '1.2.1'
    ver = 1.00200102
    # 检查或创建文件
    os.makedirs("log", exist_ok=True)
    with open("version.json", "w", encoding="utf-8") as f:
        data = {
             "name": __version__
            ,"version": ver
            ,"frozen-name":  frozenvname
            ,"frozen-version": frozenver
            ,"index": "https://gitcode.com/lin15266115/HeartBeat/releases/v1.2.0-alpha"
        }
        json.dump(data, f, ensure_ascii=False, indent=4)

logger.info(f'运行程序 -{__version__}[{ver}] -{__file__}')

init_config()


from UI import HeartRateMonitorGUI, QApplication, QEventLoop

import urllib.request

# 检查更新
def checkupdata() -> tuple[bool, str]:
    logger.info("检查更新中...")
    try:
        url = "https://raw.gitcode.com/lin15266115/HeartBeat/raw/main/version.json"

        with urllib.request.urlopen(url) as response: 
            # 读取json格式
            data = json.loads(response.read().decode('utf-8'))

            if is_frozen:
                vnumber = data['frozen-version']
                vname = data['frozen-name']
                up_index  = data['index']
            else:
                vnumber = data['version']
                vname = data['name']
                up_index = 'https://gitcode.com/lin15266115/HeartBeat'
            if vnumber > ver:
                logger.info(f"发现新版本 {vname}[{vnumber}]")
                return True, up_index
            else:
                logger.info("当前已是最新版本")
    except Exception as e:
        logger.warning(f"更新检查失败: {e}")
    return False, ''

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)

        # 设置异步事件循环
        loop = QEventLoop(app)
        asyncio.set_event_loop(loop)

        window = HeartRateMonitorGUI(__version__)
        window.show()

        def handle_exception(exc_type, exc_value, exc_traceback):
            """全局异常处理函数"""
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            logger.error(
                "严重错误: \n",
                exc_info=(exc_type, exc_value, exc_traceback)
            )
            # 报错弹窗
            window.verylarge_error(f"{exc_type.__name__}: {exc_value}")

        # 设置全局异常钩子
        sys.excepthook = handle_exception

        with loop:
            screens = app.screens()
            updata, index = checkupdata()
            if updata:
                window.updata_window_show(index)
            loop.run_forever()
    except Exception as e:
        logger.error(f"未标识的异常：{e}")
        if window:
            window.close_application()
        sys.exit(1)