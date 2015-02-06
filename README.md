# 开发说明
## 安装依赖

```bash
pip install -e .
```

## 测试

### 测试工具

测试工具使用Testify，安装：

```bash
pip install testify
```

运行测试：

```bash
testify tests
```

运行程序：

```bash
scrapy crawl moviespider -a start='[yyyy-mm-dd]' -a end='[yyyy-mm-dd]'
```

