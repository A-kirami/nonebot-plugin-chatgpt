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

智能对话聊天插件。

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

在 nonebot2 项目的 `.env` 文件中添加下表中的必填配置（在 **ARM** 平台，可能必须使用 `CHATGPT_SESSION_TOKEN` 登录）

> ⚠️ **Windows** 系统下需要在 `.env.dev` 文件中设置 `FASTAPI_RELOAD=false`

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| CHATGPT_SESSION_TOKEN | 否 | 空字符串 | ChatGPT 的 session_token，如配置则优先使用 |
| CHATGPT_ACCOUNT | 否 | 空字符串 | ChatGPT 登陆邮箱，未配置则使用 session_token |
| CHATGPT_PASSWORD | 否 | 空字符串 | ChatGPT 登陆密码，未配置则使用 session_token |
| CHATGPT_CD_TIME | 否 | 60 | 冷却时间，单位：秒|
| CHATGPT_PROXIES | 否 | None | 代理地址，格式为： `http://ip:port` |
| CHATGPT_REFRESH_INTERVAL | 否 | 30 | session_token 自动刷新间隔，单位：分钟 |
| CHATGPT_COMMAND | 否 | 空字符串 | 触发聊天的命令，可以是 `字符串` 或者 `字符串列表`。<br>如果为空字符串或者空列表，则默认响应全部消息  |
| CHATGPT_TO_ME | 否 | True | 是否需要@机器人 |
| CHATGPT_TIMEOUT | 否 | 30 | 请求服务器的超时时间，单位：秒 |
| CHATGPT_API | 否 | https://chat.openai.com/ | API 地址，可配置反代 |
| CHATGPT_IMAGE | 否 | False | 是否以图片形式发送。<br>如果无法显示文字，请[点击此处](https://github.com/kexue-z/nonebot-plugin-htmlrender#%E5%B8%B8%E8%A7%81%E7%96%91%E9%9A%BE%E6%9D%82%E7%97%87)查看解决办法 |
| CHATGPT_IMAGE_WIDTH | 否 | 500 | 消息图片宽度，单位：像素 |
| CHATGPT_PRIORITY | 否 | 999 | 事件响应器优先级 |
| CHATGPT_BLOCK | 否 | True | 是否阻断消息传播 |
| CHATGPT_PRIVATE | 否 | True | 是否允许私聊使用 |
| CHATGPT_SCOPE | 否 | private | 设置公共会话或私有会话<br>private：私有会话，群内成员会话各自独立<br>public：公共对话，群内成员共用同一会话 |
| CHATGPT_DATA | 否 | 插件目录下 | 插件数据保存目录的路径 |
| CHATGPT_MAX_ROLLBACK | 否 | 5 | 设置最多支持回滚多少会话 |
| CHATGPT_DETAILED_ERROR | 否 | 否 | 是否允许输出详细错误信息 |

### 获取 session_token

1. 登录 https://chat.openai.com/chat，并点掉所有弹窗
2. 按 `F12` 打开控制台
3. 切换到 `Application/应用` 选项卡，找到 `Cookies`
4. 复制 `__Secure-next-auth.session-token` 的值，配置到 `CHATGPT_SESSION_TOKEN` 即可

![image](https://user-images.githubusercontent.com/36258159/205494773-32ef651a-994d-435a-9f76-a26699935dac.png)

## 🎉 使用

默认配置下，@机器人加任意文本即可。

如果需要修改插件的触发方式，自定义 `CHATGPT_COMMAND` 和 `CHATGPT_TO_ME` 配置项即可。

| 指令 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|
| 刷新会话/刷新对话 | 是 | 群聊/私聊 | 重置会话记录，开始新的对话 |
| 导出会话/导出对话 | 是 | 群聊/私聊 | 导出当前会话记录 |
| 导入会话/导入对话 + 会话ID + 父消息ID(可选) | 是 | 群聊/私聊 | 将会话记录导入，这会替换当前的会话 |
| 保存会话/保存对话 + 会话名称 | 是 | 群聊/私聊 | 将当前会话保存 |
| 查看会话/查看对话 | 是 | 群聊/私聊 | 查看已保存的所有会话 |
| 切换会话/切换对话 + 会话名称 | 是 | 群聊/私聊 | 切换到指定的会话 |
| 回滚会话/回滚对话 | 是 | 群聊/私聊 | 返回到之前的会话，输入数字可以返回多个会话，但不可以超过最大支持数量 |


## 🤝 贡献

### 🎉 鸣谢

感谢以下开发者对该项目做出的贡献：

<a href="https://github.com/A-kirami/nonebot-plugin-chatgpt/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=A-kirami/nonebot-plugin-chatgpt" />
</a>
