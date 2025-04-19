# Django 面試記錄系統開發筆記

本專案實現了一個面試記錄系統，允許使用者新增、查看、更新和刪除（CRUD）面試記錄，並可以為面試添加評論。

## Django開發流程與順序

在Django專案開發中，通常遵循以下順序：

1. **Models (模型)** - 首先
   - 定義資料結構和關係
   - 確定要儲存什麼數據及其類型
   - 建立資料庫遷移文件並應用

2. **URLs (網址)** - 其次
   - 設計應用的URL結構
   - 確定路由邏輯並連接到適當的視圖

3. **Views (視圖)** - 再次
   - 實現處理用戶請求的邏輯
   - 從模型獲取數據
   - 準備要傳遞給模板的上下文

4. **Templates (模板)** - 最後
   - 設計用戶界面
   - 顯示從視圖傳來的數據

這種開發順序被稱為「自下而上」的開發方法，從數據層開始，經過邏輯層，最後到表現層。

### 為什麼按這個順序開發？

- **以數據為中心**: Django是一個以數據驅動的框架
- **清晰的依賴關係**: 視圖依賴於模型，模板依賴於視圖
- **測試驅動開發**: 先有模型和業務邏輯，再考慮表現層
- **避免重工**: 模型設計變更會影響整個應用程式，因此先定義模型可以減少後期修改的工作量

在實際開發中，這個順序不一定嚴格遵循，有時會根據需求進行調整，尤其是在採用迭代式開發時。

## 階段一：專案初始化

### 1. 安裝 uv 並建立環境

```bash
# 安裝 uv
curl -sSf https://astral.sh/uv/install.sh | bash

# 創建虛擬環境
uv init
uv venv
```

### 2. 建立 Django 專案

```bash
# 使用 uv 安裝 Django
uv add django

# 創建專案
django-admin startproject my_project

# 進入專案目錄
cd my_project
```

### 3. 管理依賴

```bash
# 使用 uv 建立 requirements.txt
uv pip freeze > requirements.txt
```

### 4. 創建應用程式

```bash
# 創建 Interview 應用
uv run manage.py startapp Interview

# 創建 Pages 應用 (用於首頁)
uv run manage.py startapp Pages
```

### 5. 設定 Makefile 簡化命令

創建 `Makefile` 以簡化開發流程：

```makefile
runserver:
	uv run python manage.py runserver

startapp:
	uv run python manage.py startapp $(name)
```

使用方式：
```bash
# 啟動伺服器
make runserver

# 創建新應用程式
make startapp name=NewApp
```

### 6. 註冊應用程式

在 `my_project/settings.py` 中註冊應用程式：

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'Interview',  # 新增
    'Pages',      # 新增
]
```

## 階段二：建立模型

### 1. 定義面試模型

在 `Interview/models.py` 中：

```python
from django.db import models

class Interview(models.Model):
    company_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    interview_at = models.DateField(null=True)
    rating = models.PositiveSmallIntegerField()
    review = models.TextField()
    result = models.CharField(max_length=100)
```

### 2. 定義評論模型

```python
class Comment(models.Model):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. 建立與應用資料庫遷移

```bash
uv run manage.py makemigrations
uv run manage.py migrate
```

## 階段三：建立表單

創建 `Interview/forms.py`：

```python
from django.forms import ModelForm, DateInput
from .models import Interview

class InterviewForm(ModelForm):
    class Meta:
        model = Interview
        fields = [
            "company_name",
            "position",
            "interview_at",
            "rating",
            "review",
            "result"
        ]
        labels = {
            "company_name": "公司名稱",
            "position": "職位",
            "interview_at": "面試日期",
            "rating": "評分",
            "review": "心得",
            "result": "面試結果",
        }
        widgets = {"interview_at": DateInput({"type":"date"})}
```

## 階段四：設定 URL 配置

### 1. 專案層級 URL 配置

在 `my_project/urls.py` 中：

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("Pages.urls")),
    path('interviews/', include("Interview.urls"))
]
```

### 2. 應用層級 URL 配置

在 `Interview/urls.py` 中：

```python
from django.urls import path
from . import views

app_name = "Interview"

urlpatterns = [
    path("", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("<int:id>/", views.show, name="show"),
    path("<int:id>/update/", views.update, name="update"),
    path("<int:id>/delete/", views.delete, name="delete"),
    path("<int:id>/comment/", views.comment, name="comment"),
]
```

## 階段五：實現視圖功能

在 `Interview/views.py` 中：

```python
from django.shortcuts import render, get_object_or_404, redirect
from .forms import InterviewForm
from .models import Interview, Comment

# 首頁 - 顯示所有面試記錄
def index(req):
    interviews = Interview.objects.order_by("-id")
    fields_to_display = ["company_name", "position", "rating"]  # 可以自定義要顯示的欄位
    interview_forms = [
        {
            'form': InterviewForm(instance=interview), 
            'id': interview.id,
            'fields_to_display': fields_to_display
        } 
        for interview in interviews
    ]
    return render(req, "Interview/index.html", {"interview_forms": interview_forms})

# 新增面試記錄
def add(req):
    if req.method == "POST":
        form = InterviewForm(req.POST)
        interview = form.save()
        return redirect("Interview:show", id = interview.id)
    else:
        form = InterviewForm
        return render(req, "Interview/add.html", {"form": form})
    
# 顯示面試詳情
def show(req, id):
    interview = get_object_or_404(Interview, pk=id)
    form = InterviewForm(instance=interview)
    comments = interview.comment_set.all().order_by("-id")
    return render(req, "Interview/show.html", {"form": form, "id": id, "comments": comments})

# 更新面試記錄
def update(req, id):
    interview = get_object_or_404(Interview, pk=id)
    
    if req.method == "POST":
        form = InterviewForm(req.POST, instance=interview)
        form.save()
        return redirect("Interview:show", id)
    else:
        form = InterviewForm(instance=interview)
        return render(req, "Interview/update.html", {"form": form, "id": id})
    
# 刪除面試記錄
def delete(req, id):
    interview = get_object_or_404(Interview, pk=id)
    interview.delete()
    return redirect("Interview:index")

# 新增評論
def comment(req, id):
    interview = get_object_or_404(Interview, pk=id)
    interview.comment_set.create(content = req.POST["content"])
    return redirect("Interview:show", id)
```

## 階段六：建立模板

### 1. 建立基本目錄結構
```
Interview/
└── templates/
    └── Interview/
        ├── index.html
        ├── add.html
        ├── show.html
        └── update.html
```

### 2. 首頁模板 (index.html)

```html
<h1>面試列表</h1>

<a href="{% url 'Interview:add' %}">新增</a>

<ul>
    {% for interview_data in interview_forms %}
        <li>
            <a href="{% url 'Interview:show' interview_data.id %}">
                <section>
                    {% for field in interview_data.form %}
                        {% if field.name in interview_data.fields_to_display %}
                            <p>{{ field.label_tag }} {{ field.value }}</p>
                        {% endif %}
                    {% endfor %}
                </section>
            </a>
        </li> 
    {% endfor %}  
</ul>
```

### 3. 新增模板 (add.html)

```html
<h1>新增面試心得</h1>

<form action="{% url 'Interview:add' %}" method="post">
    {% csrf_token %}
    {{ form }}
    <button>新增</button>
</form>
```

### 4. 顯示模板 (show.html)

```html
<h1>面試詳情</h1>

<ul>
    {% for field in form %}
    <p>{{ field.label_tag }} {{ field.value }}</p>   
    {% endfor %}
</ul>

<a href="{% url 'Interview:update' id %}">編輯</a>
<a href="{% url 'Interview:delete' id %}" onclick="return confirm('確定要刪除嗎？')">刪除</a>
<a href="{% url 'Interview:index' %}">回面試列表</a>

<h2>評論</h2>

<form action="{% url 'Interview:comment' id %}" method="post">
    {% csrf_token %}
    <textarea name="content" cols="30" rows="5"></textarea>
    <button>新增評論</button>
</form>

<ul>
    {% for comment in comments %}
    <li>{{ comment.content }}</li>
    {% endfor %}
</ul>
```

### 5. 更新模板 (update.html)

```html
<h1>編輯面試記錄</h1>

<form action="{% url 'Interview:update' id %}" method="post">
    {% csrf_token %}
    {{ form }}
    <button>更新</button>
</form>

<a href="{% url 'Interview:show' id %}">返回詳情</a>
```

## 階段七：運行與測試

```bash
# 使用 Makefile 啟動開發伺服器
make runserver

# 或直接使用 uv 啟動
uv run python manage.py runserver

# 訪問 http://localhost:8000/interviews/
```

如果需要創建新的應用程式，可以使用：

```bash
# 使用 Makefile 創建新應用
make startapp name=NewAppName

# 或直接使用 uv
uv run python manage.py startapp NewAppName
```

Makefile 的優勢在於簡化了命令，減少了敲擊按鍵的數量，提高了開發效率。

## 功能摘要

本專案實現了以下功能：

1. **Create (新增)**
   - 新增面試記錄表單
   - 新增評論功能

2. **Read (查詢)**
   - 顯示所有面試記錄列表
   - 顯示單一面試詳情與評論

3. **Update (更新)**
   - 編輯現有面試記錄

4. **Delete (刪除)**
   - 刪除面試記錄

## 學到的技術重點

1. 使用 uv 進行 Python 依賴管理與虛擬環境建置
2. Django ModelForm 的使用與自定義
3. 使用列表推導式進行資料處理
4. 實現一對多關係 (Interview -> Comments)
5. 自訂 URL Patterns 與 URL 命名空間
6. 使用 redirect 與 render 函數
7. 透過模板標籤在模板中顯示動態資料
8. POST 與 GET 請求處理方式
9. 資料庫關聯與查詢方法
10. 使用 ruff 進行程式碼檢查與自動修正
11. 使用 Makefile 簡化常用命令，提高開發效率

## 改進方向

1. 添加使用者認證功能
2. 添加分頁功能
3. 添加搜尋與過濾功能
4. 添加前端樣式美化
5. 添加錯誤處理與表單驗證
6. 添加單元測試 