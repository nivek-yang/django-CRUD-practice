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
