<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

// Компоненты PrimeVue
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'

const props = defineProps({
    user: Object,
    isAdmin: Boolean
})

const users = ref([])
const isLoading = ref(true)
const globalFilter = ref('')
const router = useRouter()

const availableRoles = [
    { code: 'employee', name: 'Сотрудник (Только чтение)', severity: 'info' },
    { code: 'moderator', name: 'Модератор (Загрузка/Редак.)', severity: 'warning' },
    { code: 'admin', name: 'Администратор (Полный доступ)', severity: 'danger' }
]

const fetchUsers = async () => {
    // ВАЖНО: Проверяем isAdmin. Если роутер еще не прокинул пропсу, 
    // берем запасной вариант из localStorage
    const userInfo = JSON.parse(localStorage.getItem('user-info') || '{}');
    const hasAccess = props.isAdmin || userInfo?.role_code === 'admin';

    if (!hasAccess) {
        console.warn('Доступ запрещен');
        router.push('/');
        return;
    }

    isLoading.value = true
    try {
        const token = localStorage.getItem('user-token');
        const response = await axios.get('http://127.0.0.1:8000/api/admin/users/', {
            headers: { 'Authorization': `Token ${token}` }
        });
        users.value = response.data
    } catch (e) {
        console.error("Ошибка загрузки пользователей:", e);
        Swal.fire('Ошибка', 'Не удалось загрузить список', 'error');
    } finally {
        // Гарантируем отключение лоадера
        isLoading.value = false
    }
}

const updateUserRole = async (userId, newRole) => {
    if (userId === props.user?.id) {
        Swal.fire({
            icon: 'warning',
            title: 'Внимание',
            text: 'Вы не можете изменить роль самому себе через эту панель. Это защитный механизм, чтобы вы не потеряли доступ к админке.',
        });

        // Откатываем выбор в таблице назад
        const user = users.value.find(u => u.id === userId);
        if (user) user.role = props.user.role_code;
        return;
    }

    try {
        await axios.post(`http://127.0.0.1:8000/api/admin/users/${userId}/role/`,
            { role: newRole },
            { headers: { 'Authorization': `Token ${localStorage.getItem('user-token')}` } }
        )
        // Локально обновляем роль в списке
        const user = users.value.find(u => u.id === userId)
        if (user) user.role = newRole // убедись, что поле называется role или role_code

        Swal.fire({
            icon: 'success',
            title: 'Права обновлены',
            timer: 1000,
            showConfirmButton: false
        })
    } catch (e) {
        Swal.fire('Ошибка', 'Не удалось сменить роль', 'error')
    }
}

onMounted(fetchUsers)
</script>

<template>
    <div class="min-h-screen bg-[#f8fafc] -m-6 p-6 md:p-12">
        <div class="max-w-7xl mx-auto">
            <nav class="mb-8">
                <Button icon="pi pi-arrow-left" label="Вернуться в архив"
                    class="p-button-text p-button-secondary !text-xs !font-bold uppercase tracking-widest"
                    @click="router.push('/')" />
            </nav>

            <header class="mb-12">
                <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div class="flex items-center gap-3 mb-2">
                            <span
                                class="bg-blue-600 text-white text-[10px] font-black px-3 py-1 rounded-full uppercase">Система</span>
                        </div>
                        <h1 class="text-5xl font-black text-slate-900 tracking-tight uppercase italic">
                            Управление <span class="text-blue-600">Доступом</span>
                        </h1>
                    </div>

                    <div class="flex items-center gap-3 bg-white p-2 rounded-2xl shadow-sm border border-slate-200">
                        <IconField>
                            <InputIcon class="pi pi-search" />
                            <InputText v-model="globalFilter" placeholder="Поиск сотрудника..."
                                class="!border-none !shadow-none !bg-transparent w-64" />
                        </IconField>
                        <Button icon="pi pi-refresh" rounded severity="secondary" @click="fetchUsers"
                            :loading="isLoading" />
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div class="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-sm">
                    <div class="text-slate-400 text-[10px] font-black uppercase mb-1">Всего сотрудников</div>
                    <div class="text-3xl font-black text-slate-900">{{ users.length }}</div>
                </div>
                <div class="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-sm">
                    <div class="text-amber-500 text-[10px] font-black uppercase mb-1">Администраторы</div>
                    <div class="text-3xl font-black text-slate-900">
                        {{users.filter(u => u.role === 'admin').length}}
                    </div>
                </div>
                <div class="bg-white p-6 rounded-[2rem] border border-slate-200 shadow-sm">
                    <div class="text-blue-600 text-[10px] font-black uppercase mb-1">Статус сервера</div>
                    <div class="text-sm font-bold text-green-500 uppercase">Online</div>
                </div>
            </div>

            <div class="bg-white rounded-[3rem] shadow-xl shadow-slate-200/50 border border-slate-200 overflow-hidden">
                <DataTable :value="users" :paginator="true" :rows="10" :loading="isLoading"
                    :filters="{ 'global': { value: globalFilter, matchMode: 'contains' } }" stripedRows
                    class="p-datatable-lg">

                    <Column field="username" header="Сотрудник" sortable></Column>
                    <Column field="email" header="Email"></Column>
                    <Column field="role" header="Роль">
                        <template #body="{ data }">
                            <Tag :value="data.role"
                                :severity="availableRoles.find(r => r.code === data.role)?.severity" />
                        </template>
                    </Column>
                    <Column header="Действие" bodyClass="text-right">
                        <template #body="{ data }">
                            <Select v-model="data.role" :options="availableRoles" optionLabel="name" optionValue="code"                                 :disabled="data.id === props.user?.id"
                                :class="{ 'opacity-50': data.id === props.user?.id }"
                                @change="(e) => updateUserRole(data.id, e.value)"
                                class="!text-xs !bg-slate-50 !rounded-xl" style="min-width: 150px;" />
                        </template>
                    </Column>

                </DataTable>
            </div>
        </div>
    </div>
</template>