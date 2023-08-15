# ee's blog
**纸片君ee的博客｜PAPEREE**

## 使用方法
### 安装库
- `pip3 install flask`
- `pip3 install gunicorn`

别问为什么没有`requirements.txt`，~~ee懒~~（被打

### 开始运行
- 根据实际情况修改`config.py`
- 输入`gunicorn --config=config.py main:app`

默认运行在`127.0.0.1:1234`，浏览器打开网址就能看到博客。

## 如何写文章
- 使用你喜欢的编辑器，用Markdown或HTML编写`.md`文件，将文件放置`notes`文件夹。
- 如果博客正在运行，打开你的网址就能看到这篇文章。

有个~~BUG~~特性，如果在文章拥有评论的情况下重命名`notes`中的文章，那么评论不会自动更新到新的文章。  

### 解决方法
进入`client/_`，手动将评论数据重命名为新的文章名（对文件夹名是下划线（划掉
