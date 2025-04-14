from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import CardTemplate
from .forms import CardTemplateForm

def card_templates_list(request):
    templates = CardTemplate.objects.all()
    return render(request, 'cards/templates_list.html', {'templates': templates})

@login_required
def create_template(request):
    if request.method == 'POST':
        form = CardTemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save(commit=False)
            template.creator = request.user
            template.save()
            return redirect('templates_list')
        else:
            # Логируем ошибки для отладки
            print("Ошибки формы:", form.errors)
    else:
        form = CardTemplateForm()
    return render(request, 'cards/create_template.html', {'form': form})