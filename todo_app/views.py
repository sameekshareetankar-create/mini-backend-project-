from django.shortcuts import get_object_or_404, redirect, render
from .models import todo_table

# Create your views here.
def home(request):
    data = todo_table.objects.all()
    return render(request, 'home.html', {'data': data})

def add_task(request):
    if request.method == "POST":
        title = request.POST.get('title')
        description = request.POST.get('description')
        todo_table.objects.create(title=title, description=description)
        return redirect('home')
    return render(request, 'add_task.html')


def edit_task(request, task_id):
    task = get_object_or_404(todo_table, id=task_id)
    if request.method == "POST":
        task.title = request.POST.get('title', '').strip()
        task.description = request.POST.get('description', '').strip()
        task.done = request.POST.get('done') == 'on'
        task.save()
        return redirect('home')
    return render(request, 'edit_task.html', {'task': task})


def delete_task(request, task_id):
    task = get_object_or_404(todo_table, id=task_id)
    task.delete()
    return redirect('home')

def task_completed(request, task_id):
   task_id=todo_table.objects.get(id=task_id)
   task_id.done=request.POST.get('checkbox')=='True'
   task_id.save()
   return redirect('home')
