from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ProjectForm
from .models import Project
from .service import get_paginated_queryset


def project_list_view(request):
    """
    Главная страница: список всех проектов с пагинацией
    Сортировка: новые сверху (по -created_at)
    """
    queryset = Project.objects.all().select_related('owner').prefetch_related('participants')
    page_obj = get_paginated_queryset(queryset, request, per_page=12)
    
    context = {
        'projects': page_obj,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail_view(request, pk):
    """
    Детальная страница проекта
    Отображает информацию, участников, кнопки управления (для владельца)
    """
    project = get_object_or_404(
        Project.objects.select_related('owner').prefetch_related('participants'),
        pk=pk
    )
    
    is_owner = request.user == project.owner
    
    context = {
        'project': project,
        'is_owner': is_owner,
    }
    return render(request, 'projects/project-details.html', context)


@login_required
def project_create_view(request):
    """
    Создание нового проекта
    При сохранении: текущий пользователь становится автором и участником
    """
    form = ProjectForm(request.POST or None)
    
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        
        project.participants.add(request.user)
        messages.success(request, 'Проект успешно создан!')
        return redirect('projects:project_detail', pk=project.pk)
    
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
    
    if request.user != project.owner:
        messages.error(request, 'У вас нет прав для редактирования этого проекта.')
        return redirect('projects:project_detail', pk=pk)
    
    form = ProjectForm(request.POST or None, instance=project)
    
    if form.is_valid():
        form.save()
        messages.success(request, 'Проект успешно обновлён.')
        return redirect('projects:project_detail', pk=pk)
    
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
    
    if request.user != project.owner or project.status != Project.STATUS_OPEN:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)
    
    project.status = Project.STATUS_CLOSED
    project.save(update_fields=['status'])
    
    return JsonResponse({
        'status': 'ok',
        'project_status': Project.STATUS_CLOSED,
    })


@login_required
def toggle_participate_view(request, pk):
    """
    API: присоединиться к проекту / покинуть проект
    Возвращает JSON: {"status": "ok", "participant": true/false}
    """
    project = get_object_or_404(Project, pk=pk)
    
    if project.status == Project.STATUS_CLOSED:
        return JsonResponse({'error': 'Project is closed'}, status=HTTPStatus.BAD_REQUEST)
    
    user = request.user
    if is_participant := project.participants.filter(pk=user.pk).exists():
        project.participants.remove(user)
    else:
        project.participants.add(user)
    
    return JsonResponse({
        'status': 'ok',
        'participant': not is_participant,
    })


@login_required
def remove_participant_view(request, project_pk, participant_pk):
    """
    Удалить участника из проекта (только для владельца)
    """
    project = get_object_or_404(Project, pk=project_pk)
    
    if request.user != project.owner:
        return JsonResponse({'error': 'Forbidden'}, status=HTTPStatus.FORBIDDEN)
    
    if participant_pk == project.owner.id:
        return JsonResponse({'error': 'Cannot remove owner'}, status=HTTPStatus.BAD_REQUEST)
    
    participant = get_object_or_404(User, pk=participant_pk)
    project.participants.remove(participant)
    
    return JsonResponse({'status': 'ok'})
