# operating-system-groupwork

操作系统课程小组作业仓库。

## 项目简介

> 待补充：项目选题、目标与验收标准。

根据仓库现有目录与 `.gitignore` 规则，本仓库围绕 **LLVM 插桩** 与 **AFL / ConFuzzer 模糊测试** 展开，涉及以下部分（由 `.gitignore` 推断，待确认）：

- `tool/AFL-2.52b/`：AFL 2.52b 源码，构建产物不入库
- `tool/ConFuzzer/`：并发模糊测试工具（LLVM mode + build 产物）
- `test/uaf/`、`test/transfer/`：测试用例
- `evaluation/BUILD/`、`evaluation/FUZZ/`：评测构建与 fuzz 结果
- `DBDS/`：示例脚本

## 环境要求

> 待补充：LLVM / clang 版本、Python 版本、构建与运行命令。

## 开发约定

1. **提交信息必须以「学号 姓名」开头**，例如：

   ```
   1240007426 田一麟 完善 README
   ```

2. 主分支为 `main`，请勿直接提交到 `main`。

3. 功能开发新建分支，完成后提 Pull Request：

   ```bash
   git checkout -b feature/模块名
   git add .
   git commit -m "学号 姓名 做了什么"
   git push -u origin feature/模块名
   ```

4. 编译产物、trace、评测数据等大文件不入库，忽略规则见 `.gitignore`。

## 小组成员

| 学号 | 姓名 | GitHub | 负责模块 |
| --- | --- | --- | --- |
| 1240007426 | 田一麟 | @tyl171 | 待补充 |
| 待补充 | 待补充 | 待补充 | 待补充 |
| 待补充 | 待补充 | 待补充 | 待补充 |
| 待补充 | 待补充 | 待补充 | 待补充 |

## 常见问题：GitHub 连不上

国内直连 `github.com` 常出现 `Connection reset`。可在本仓库内配置代理：

```bash
git config http.proxy http://127.0.0.1:7890
git config http.sslBackend openssl
```

`7890` 为 Clash / FlClash 等工具的默认混合代理端口，按自己实际端口调整。
