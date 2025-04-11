# M8Test 插件市场

需要配合 [M8Test 插件](https://github.com/m8test/pluginstore) 使用

本仓库需要遵循以下格式:

1. 根目录下的文件夹包含插件类型文件夹，可以是以下几种：
    + builder: 构建插件
    + common: 通用插件
    + component: 组件插件
    + language: 语言插件
    + editor: 编辑器插件
2. 插件类型文件夹中文件夹表示一个个插件
3. 每个插件文件夹内容包含多个版本文件夹以及一个latest.txt文件表示最新的版本. 每个文件夹表示一个版本,
   每个版本文件夹包含以下内容:
    + download_url.txt: 文件内容是插件下载地址
    + repository.txt: 文件内容是插件仓库,可以不存在,如果不存在则默认为空字符串
    + README.md: 文件内容是插件的描述信息,可以不存在,如果不存在则使用repository.txt中的仓库中的README.md

文件树结构示例:

```text

│  README.md
│
├─builder
├─common
│  └─accessibility
│      │  latest.txt
│      │
│      └─0.1.0
│              download_url.txt
│              README.md
│              repository.txt
│
├─component
├─editor
└─language
```