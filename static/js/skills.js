(function() {
    'use strict';
    
    document.addEventListener('DOMContentLoaded', function() {
        const container = document.getElementById('skills-container');
        if (!container) return;
        
        const userId = container.getAttribute('data-user-id');
        if (!userId) {
            console.error('User ID not found');
            return;
        }
        
        console.log('Skills module loaded for user:', userId);
        
        // Элементы управления
        const addBtn = document.getElementById('add-skill-btn');
        const inputBlock = document.getElementById('skill-input-block');
        const skillInput = document.getElementById('skill-input');
        const saveBtn = document.getElementById('save-skill-btn');
        const cancelBtn = document.getElementById('cancel-skill-btn');
        const suggestions = document.getElementById('skill-suggestions');
        
        let debounceTimer;
        
        // === Кнопка "Добавить навык" ===
        if (addBtn) {
            addBtn.addEventListener('click', function() {
                console.log('Add skill button clicked');
                inputBlock.style.display = 'block';
                this.style.display = 'none';
                skillInput.focus();
            });
        }
        
        // === Кнопка "Отмена" ===
        if (cancelBtn) {
            cancelBtn.addEventListener('click', function() {
                inputBlock.style.display = 'none';
                skillInput.value = '';
                suggestions.style.display = 'none';
                if (addBtn) addBtn.style.display = 'inline';
            });
        }
        
        // === Автодополнение ===
        if (skillInput) {
            skillInput.addEventListener('input', function() {
                const query = this.value.trim();
                clearTimeout(debounceTimer);
                
                if (query.length < 2) {
                    suggestions.style.display = 'none';
                    return;
                }
                
                debounceTimer = setTimeout(function() {
                    fetch('/users/skills/?q=' + encodeURIComponent(query))
                        .then(response => {
                            if (!response.ok) throw new Error('Network error');
                            return response.json();
                        })
                        .then(skills => {
                            if (skills.length > 0) {
                                suggestions.innerHTML = skills.map(function(skill) {
                                    return '<li class="list-group-item skill-suggestion" data-skill-id="' + skill.id + '" style="cursor:pointer;">' + skill.name + '</li>';
                                }).join('');
                            } else {
                                suggestions.innerHTML = '<li class="list-group-item skill-suggestion" data-skill-name="' + query + '" style="cursor:pointer;">+ Создать "' + query + '"</li>';
                            }
                            suggestions.style.display = 'block';
                        })
                        .catch(error => console.error('Error fetching skills:', error));
                }, 300);
            });
        }
        
        // === Выбор из списка ===
        if (suggestions) {
            suggestions.addEventListener('click', function(e) {
                const item = e.target.closest('.skill-suggestion');
                if (!item) return;
                
                const skillId = item.getAttribute('data-skill-id');
                const skillName = item.getAttribute('data-skill-name');
                
                if (skillId) {
                    addSkill(skillId, null);
                } else if (skillName) {
                    addSkill(null, skillName);
                }
                
                suggestions.style.display = 'none';
                skillInput.value = '';
            });
        }
        
        // === Сохранение по кнопке ===
        if (saveBtn) {
            saveBtn.addEventListener('click', function() {
                const skillName = skillInput.value.trim();
                if (skillName) {
                    addSkill(null, skillName);
                }
            });
        }
        
        // === Удаление навыка  ===
        container.addEventListener('click', function(e) {
            // Ищем кнопку удаления в цепочке элементов (включая иконку внутри)
            const removeBtn = e.target.closest('[data-skill-id]');
            
            // Проверяем, что это действительно кнопка удаления с классом remove-skill
            if (removeBtn && removeBtn.classList.contains('remove-skill')) {
                e.preventDefault();
                e.stopPropagation();
                
                const skillId = removeBtn.getAttribute('data-skill-id');
                console.log('Remove skill clicked, ID:', skillId);
                
                if (!skillId) {
                    alert('Ошибка: не найден ID навыка');
                    return;
                }
                
                if (confirm('Удалить этот навык?')) {
                    removeSkill(skillId);
                }
            }
        });
        
        // === Функция добавления навыка ===
        function addSkill(skillId, skillName) {
            const data = {};
            if (skillId) data.skill_id = skillId;
            if (skillName) data.name = skillName;
            
            console.log('Adding skill:', data);
            
            fetch('/users/' + userId + '/skills/add/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    return response.json().then(err => Promise.reject(err));
                }
            })
            .catch(error => {
                console.error('Error adding skill:', error);
                alert('Ошибка при добавлении навыка');
            });
        }
        
        // === Функция удаления навыка ===
        function removeSkill(skillId) {
            console.log('Removing skill ID:', skillId, 'for user:', userId);
            
            const url = '/users/' + userId + '/skills/' + skillId + '/remove/';
            console.log('Request URL:', url);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json'
                }
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (response.ok) {
                    location.reload();
                } else {
                    return response.json().then(err => {
                        console.error('Server error:', err);
                        return Promise.reject(err);
                    });
                }
            })
            .catch(error => {
                console.error('Error removing skill:', error);
                alert('Ошибка при удалении: ' + (error.error || error.message || 'неизвестная ошибка'));
            });
        }
        
        // === Получение CSRF-токена ===
        function getCookie(name) {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + '=')) {
                    return decodeURIComponent(cookie.substring(name.length + 1));
                }
            }
            return null;
        }
    });
})();