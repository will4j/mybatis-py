# Meta Repository for Python

Python 模板仓库，功能包含：
+ 环境构建脚本：基于 Taskfile，支持全平台构建执行（Windows 需要依赖 Git Bash）。
+ 单元测试框架：基于 Pytest 和 Pytest-cov。
+ 日志配置：使用系统 logging 库作为日志门面，无缝集成 loguru。
+ 代码规范检查：遵循 PEP-8 规范，使用 flake8 插件。
+ 模块打包配置：共享模块打包，支持其他工程导入使用。

## 环境构建

### 前置准备
1. 安装 conda

    推荐使用[清华源](https://mirrors.tuna.tsinghua.edu.cn/help/anaconda/)安装 `anaconda` 或 `miniconda`。

2. 安装 go-task

    参考[官方安装文档](https://taskfile.dev/installation/)：
    + Mac 系统：

      ```shell
      $ brew install go-task
      ```

    + Linux 系统：

      ```shell
      $ sudo snap install task --classic
      ```

    + Windows 系统：

      使用 powershell 和 [Chocolatey](https://chocolatey.org/install#individual)。

      ```shell
      # 使用 管理员权限 打开 powershell
      # 一行命令安装 Chocolatey
      $ Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
      # 验证 Chocolatey
      $ choco
      # 使用 Chocolatey 安装 go-task
      $ choco install go-task
      ```

3. 安装 git

    参考 [Git 安装指南](https://git-scm.com/book/zh/v2/%E8%B5%B7%E6%AD%A5-%E5%AE%89%E8%A3%85-Git)。

    注意 Windows 版本需要安装 Git Bash，后续构建脚本执行依赖使用。Windows 版本[下载](https://git-scm.com/download/win)。

### 初始化 conda 虚拟环境

在项目根目录执行命令（Windows 在项目根目录打开 Git Bash 后执行）：

```shell
# 输入 task 后回车
$ task
...
environment variables:
PYTHONPATH = xxxx/meta-repository-py
continue to use commands below:
conda activate ./venv (activate conda environment)
conda deactivate (deactivate conda environment)
task --force (force rebuild venv)
task --list (show all tasks)
```

这一步完成的操作包括：

1. 自动执行虚拟环境创建或者更新操作，配置文件：[environment.yml](environment.yml) 和 [requirements.txt](requirements.txt)。
2. 设置 `PYTHONPATH` 环境变量，所有模块导入以项目根目录作为相对路径。

## 任务脚本使用

后续所有操作在 conda 虚拟环境中执行：

```shell
# 进入虚拟环境
$ conda activate ./venv
# 退出虚拟环境
$ conda deactivate
```

### 代码规范检查

检查项：

1. 代码行末尾多余空格检查及自动清除；
2. 源代码文件以空行结尾检查及自动添加；
3. requirements.txt 以字典序排序；
4. PEP-8 代码规范检查，可在 [.flake8](.flake8) 和 [.pre-commit-config.yaml](.pre-commit-config.yaml) 配置文件中调整配置；
5. Python Import 重排序，按系统导入、三方导入、项目内部导入分成三组，可在` .pre-commit-config.yaml` 中调整配置。

> 第一次运行需要到 GitHub 下载插件，可能会比较慢

```shell
$ task pre-commit
task: [pre-commit] pre-commit install
pre-commit installed at .git/hooks/pre-commit
task: [pre-commit] pre-commit run --all-files
trim trailing whitespace.................................................Passed
fix end of files.........................................................Passed
fix requirements.txt.....................................................Passed
flake8...................................................................Passed
Reorder python imports...................................................Passed
```

### 单元测试执行

使用 [Pytest](https://docs.pytest.org/en/7.4.x/how-to/index.html) 编写单测，规范做法是将所有单测放到 `tests` 目录。

单测覆盖率配置可在 [.coveragerc](.coveragerc) 文件中调整。

```shell
# 执行单元测试
$ task pytest
# 执行单测覆盖率统计
$ task pytest:cov
# 执行单测覆盖率统计，但只统计未完全覆盖代码
$ pytest:cov:skip-covered
```

### 启动脚本执行

项目一般在 `scripts` 目录下添加启动脚本，并在 Taskfile 中添加对应调用任务。

```shell
# 以 script/main.py 为例
$ task main
task: [main] python scripts/main.py
2023-11-25 13:03:20.438 | INFO     | __main__:<module>:14 - Hello World
```

## 其他配置

### 日志配置

1. 在启动脚本完成日志配置（日志配置尽早提前，全局生效）

   详细配置在配置文件 [logging.yml](logging.yml) 中。

   ```python
   # 位于 scripts/main.py 或其他启动脚本中
   import logging.config

   import yaml

   from settings import LOGGING_CONFIG


   # 初始化日志配置文件
   with open(LOGGING_CONFIG, "r") as conf:
       conf_dict = yaml.load(conf, Loader=yaml.FullLoader)
       logging.config.dictConfig(conf_dict)
   ```

2. 日志打印

   ```python
   import logging

   # 默认使用 __name__ 创建 logger，可在日志中记录模块信息
   logger = logging.getLogger(__name__)

   # 使用占位符，避免使用 f"" 打印日志
   logger.info("this is a log with %s", "meta-repository")
   ```
