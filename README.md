<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-chatgpt

_✨ ChatGPT AI 对话 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/A-kirami/nonebot-plugin-chatgpt.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-chatgpt">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-chatgpt.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

## 📖 介绍

智能对话聊天插件，核心部分参考 [acheong08/ChatGPT](https://github.com/acheong08/ChatGPT) 实现。

## 💿 安装

<details>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-chatgpt

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-chatgpt
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-chatgpt
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-chatgpt
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-chatgpt
</details>

打开 nonebot2 项目的 `bot.py` 文件, 在其中写入

    nonebot.load_plugin('nonebot_plugin_chatgpt')

</details>


## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的必填配置

| 配置项 | 必填 | 默认值 |  说明 |
|:-----:|:----:|:----:|:----:|
| CHATGPT_SESSION_TOKEN | 是 | 无 | ChatGPT 的 session_token |
| CHATGPT_PROXIES | 否 | None | 代理地址，格式为： `http://ip:port` |

### 获取 session_token

1. 登录 https://chat.openai.com/chat
2. 按 `F12` 打开控制台
3. 切换到 `Application/应用` 选项卡，找到 `Cookies`
4. 复制 `__Secure-next-auth.session-token` 的值，配置到 `CHATGPT_SESSION_TOKEN` 即可

![image](https://user-images.githubusercontent.com/36258159/205494773-32ef651a-994d-435a-9f76-a26699935dac.png)

## 🎉 使用

@机器人加任意文本即可。
