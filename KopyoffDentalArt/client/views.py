from django.shortcuts import render
from django.views.generic import TemplateView
from django.views import View
from .models import Comment

insurances_page_view = lambda request: render(request, "insurances.html")

class ContactView(TemplateView):
    template_name = "contact.html"

class HomeView(View):

    def get(self, request):
        comments = Comment.objects.all()
        return render(request, "index.html", {"comments": comments})
    
    def post(self, request):
        errors = []
        name = request.POST["name"]
        content = request.POST["comment"]
        if len(name) > 40:
            errors.append("Name can't contain more than 40 characters")
        if len(content) > 400:
            errors.append("Comment can't contain more than 400 characters")
        if errors:
            comments = Comment.objects.all()
            return render(request, "index.html", {"comments": comments})
        else:
            comment = Comment(name=name, content=content)
            comment.save() 
            comments = Comment.objects.all()
            return render(request, "index.html", {"comments": comments})
