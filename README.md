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

### 运行测试

```bash
testify tests
```

## 初始化数据库

```bash
sqlite3 moviecrawler/scraping.db < misc/data.sql
```

## 运行程序

```bash
scrapy crawl moviespider -a start='[yyyy-mm-dd]' -a end='[yyyy-mm-dd]'
```

```bash
scrapy crawl moviespider -a start='[yyyy-mm-dd]' -a end='[yyyy-mm-dd] -a only_film'
```

```bash
scrapy crawl moviespider -a start='[yyyy-mm-dd]' -a end='[yyyy-mm-dd] -a get_schedules'
```

## 导出电影


```bash
sqlite3 -header -csv moviecrawler/scraping.db "select * from films;" > films.csv
```

