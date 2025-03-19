# chat 2 resx

## 介绍

使用大模型将前后端多语言资源文件从指定语言翻译为目标语言。

## 支持

- 前端支持用 ts 文件存放的资源文件，可以指定目录批量翻译。

- 后端支持.Net 的 resx 文件，可以将 xml 格式解析出来逐个或分批翻译。

## 使用

打包为可执行文件

```sh
pyinstaller --onefile --windowed main.py --icon=logo.ico
```
