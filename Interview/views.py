from django.shortcuts import render, get_object_or_404, redirect
from .forms import InterviewForm
from .models import Interview

# Create your views here.
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

def add(req):
    if req.method == "POST":
        form = InterviewForm(req.POST)
        interview = form.save()
        return redirect("Interview:show", id = interview.id)
    else:
        form = InterviewForm
        return render(req, "Interview/add.html", {"form": form})
    
def show(req, id):
    interview = get_object_or_404(Interview, pk=id)
    form = InterviewForm(instance=interview)
    return render(req, "Interview/show.html", {"form": form, "id": id})

def update(req, id):
    interview = get_object_or_404(Interview, pk=id)
    
    if req.method == "POST":
        form = InterviewForm(req.POST, instance=interview)
        form.save()
        return redirect("Interview:show", id)
    else:
        form = InterviewForm(instance=interview)
        return render(req, "Interview/update.html", {"form": form, "id": id})