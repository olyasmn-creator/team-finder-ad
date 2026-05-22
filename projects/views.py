from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project
from .forms import ProjectForm
from users.models import User


def project_list_view(request):
    """
    Главная страница: список всех проектов с пагинацией
    Сортировка: новые сверху (по -created_at)
    """
    # Базовый queryset: все проекты
    queryset = Project.objects.all().select_related('owner')
    
    # Пагинация: 12 проектов на странице
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'projects': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, pk):
    """
    Детальная страница проекта
    Отображает информацию, участников, кнопки управления (для владельца)
    """
    project = get_object_or_404(Project.objects.select_related('owner'), pk=pk)
    is_owner = request.user == project.owner
    
    # Участники проекта (для отображения в шаблоне)
    participants = project.participants.all()
    
    context = {
        'project': project,
        'is_owner': is_owner,
        'participants': participants,
    }
    return render(request, 'projects/project-details.html', context)


@login_required
def project_create_view(request):
    """
    Создание нового проекта
    При сохранении: текущий пользователь становится автором и участником
    """
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            # Автор автоматически становится участником
            project.participants.add(request.user)
            messages.success(request, 'Проект успешно создан!')
            return redirect('projects:project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': False,
    })


@login_required
def project_edit_view(request, pk):
    """
    Редактирование проекта (только для владельца)
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверка прав: только владелец может редактировать
    if request.user != project.owner:
        messages.error(request, 'У вас нет прав для редактирования этого проекта.')
        return redirect('projects:project_detail', pk=pk)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Проект успешно обновлён.')
            return redirect('projects:project_detail', pk=pk)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/create-project.html', {
        'form': form,
        'is_edit': True,
    })


@login_required
def project_complete_view(request, pk):
    """
    API: завершить проект (только для владельца, только если статус 'open')
    Возвращает JSON: {"status": "ok", "project_status": "closed"}
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Проверки: авторизован, владелец, проект открыт
    if request.user != project.owner or project.status != 'open':
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    project.status = 'closed'
    project.save(update_fields=['status'])
    
    return JsonResponse({
        'status': 'ok',
        'project_status': 'closed',
    })


@login_required
def toggle_participate_view(request, pk):
    """
    API: присоединиться к проекту / покинуть проект
    Возвращает JSON: {"status": "ok", "participant": true/false}
    """
    project = get_object_or_404(Project, pk=pk)
    
    # Нельзя участвовать в закрытом проекте 
    if project.status == 'closed':
        return JsonResponse({'error': 'Project is closed'}, status=400)
    
    user = request.user
    is_participant = project.participants.filter(pk=user.pk).exists()
    
    if is_participant:
        # Удалить пользователя из участников
        project.participants.remove(user)
        participant = False
    else:
        # Добавить пользователя в участники
        project.participants.add(user)
        participant = True
    
    return JsonResponse({
        'status': 'ok',
        'participant': participant,
    })

@login_required
def remove_participant_view(request, project_pk, participant_pk):
    """
    Удалить участника из проекта (только для владельца)
    """
    project = get_object_or_404(Project, pk=project_pk)
    
    # Проверка: только владелец может удалять
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    # Нельзя удалить самого владельца
    if participant_pk == project.owner.id:
        return JsonResponse({'error': 'Cannot remove owner'}, status=400)
    
    participant = get_object_or_404(User, pk=participant_pk)
    project.participants.remove(participant)
    
    return JsonResponse({'status': 'ok'})
    
