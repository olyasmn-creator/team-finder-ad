from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator
from .models import User, Skill
from .forms import RegisterForm, LoginForm, ProfileEditForm, CustomPasswordChangeForm
from django.contrib.auth.forms import PasswordChangeForm


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('projects:project_list')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """Вход в аккаунт по email и паролю"""
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'С возвращением, {user.name}!')
            return redirect('projects:project_list')
        else:
            messages.error(request, 'Неверный email или пароль.')
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    """Выход из аккаунта"""
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('projects:project_list')


def profile_view(request, pk):
    """Публичный профиль пользователя"""
    user = get_object_or_404(User, pk=pk)
    is_owner = request.user == user
    owned_projects = user.owned_projects.all()[:10]
    
    context = {
        'user': user,
        'is_owner': is_owner,
        'owned_projects': owned_projects,
    }
    return render(request, 'users/user-details.html', context)


@login_required
def profile_edit_view(request, pk):
    """Редактирование профиля (только владелец)"""
    user = get_object_or_404(User, pk=pk)
    
    if request.user != user:
        messages.error(request, 'У вас нет прав для редактирования этого профиля.')
        return redirect('users:profile', pk=pk)
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('users:profile', pk=pk)
    else:
        form = ProfileEditForm(instance=user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def password_change_view(request):
    """Смена пароля"""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Пароль успешно изменён.')
            return redirect('users:profile', pk=request.user.pk)
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})


def user_list_view(request):
    """
    Список всех пользователей с фильтрацией по навыкам (Вариант 2)
    """
    # Базовый запрос: все активные пользователи
    queryset = User.objects.filter(is_active=True).order_by('-id')
    
    # Фильтр по НАЗВАНИЮ навыка (регистронезависимый)
    active_skill = request.GET.get('skill', '').strip()
    if active_skill:
        queryset = queryset.filter(skills__name__iexact=active_skill)
    
    # Пагинация: 12 пользователей на странице
    paginator = Paginator(queryset, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Все навыки для панели фильтров (отсортированы по алфавиту)
    all_skills = Skill.objects.all().order_by('name')
    
    context = {
        'participants': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'users/participants.html', context)


# === API для навыков ===

def skill_search_api(request):
    """API: поиск навыков для автодополнения"""
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)
    
    skills = Skill.objects.filter(
        name__istartswith=query
    ).order_by('name')[:10].values('id', 'name')
    
    return JsonResponse(list(skills), safe=False)


@login_required
def skill_add_api(request, user_id):
    """API: добавить навык пользователю"""
    if request.user.id != user_id:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    import json
    data = json.loads(request.body)
    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    
    created = False
    added = False
    
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=400)
    
    if not request.user.skills.filter(pk=skill.pk).exists():
        request.user.skills.add(skill)
        added = True
    
    return JsonResponse({
        'skill_id': skill.id,
        'created': created,
        'added': added,
    })


@login_required
def skill_remove_api(request, user_id, skill_id):
    """API: удалить навык у пользователя"""
    if request.user.id != user_id:
        return JsonResponse({'error': 'Forbidden'}, status=403)
    
    skill = get_object_or_404(Skill, pk=skill_id)
    
    if request.user.skills.filter(pk=skill.pk).exists():
        request.user.skills.remove(skill)
    
    return JsonResponse({'status': 'ok'})