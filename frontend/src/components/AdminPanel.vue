<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import {useRouter} from 'vue-router'

// Компоненты PrimeVue
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import IconField from 'primevue/iconfield'
import InputIcon from 'primevue/inputicon'
import InputText from 'primevue/inputtext'
import Skeleton from 'primevue/skeleton'

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
    const userInfo = JSON.parse(localStorage.getItem('user-info'));

    // 1. Проверяем права ДО того, как включать индикатор загрузки
    const isAdmin = userInfo?.role_code === 'admin' || userInfo?.permissions?.is_admin === true;

    if (!isAdmin) {
        console.warn('Доступ запрещен: пользователь не является администратором');
        isLoading.value = false;
        // Если ты на главной странице используешь currentPage для переключения, 
        // то router.push может не понадобиться, но для надежности оставим
        router.push('/');
        return;
    }

    isLoading.value = true
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/admin/users/', {
            headers: { 'Authorization': `Token ${localStorage.getItem('user-token')}` }
        });
        users.value = response.data
    } catch (e) {
        console.error(e);
        // Исправлено: используем 'e', так как в catch(e)
        if (e.response?.status === 403) {
            router.push('/dashboard');
        } else {
            Swal.fire('Ошибка', 'Не удалось загрузить список пользователей', 'error');
        }
    } finally {
        isLoading.value = false // Теперь точно сработает
    }
}

const updateUserRole = async (userId, newRole) => {
    // Не забывай про токен и здесь тоже!
    try {
        await axios.post(`http://127.0.0.1:8000/api/admin/users/${userId}/role/`,
            { role: newRole },
            { headers: { 'Authorization': `Token ${localStorage.getItem('user-token')}` } }
        )

        const user = users.value.find(u => u.id === userId)
        if (user) user.role_code = newRole

        Swal.fire({
            icon: 'success',
            title: 'Права обновлены',
            timer: 1000,
            showConfirmButton: false
        })
    } catch (e) {
        Swal.fire('Ошибка', e.response?.data?.error || 'Не удалось сменить роль', 'error')
    }
}

onMounted(fetchUsers)
</script>

<template>
    <div class="p-6 md:p-10 min-h-screen bg-slate-50">
        <div class="max-w-7xl mx-auto space-y-8">

            <header
                class="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-200">
                <div>
                    <h1 class="text-3xl font-black text-slate-950 uppercase tracking-tighter italic">Панель управления
                    </h1>
                    <p class="text-slate-500 mt-1 font-medium">Администрирование прав доступа сотрудников Росстата</p>
                </div>
                <div class="flex items-center gap-3">
                    <IconField>
                        <InputIcon class="pi pi-search" />
                        <InputText v-model="globalFilter" placeholder="Поиск сотрудника..."
                            class="!rounded-2xl !bg-white" />
                    </IconField>
                    <Button icon="pi pi-refresh" rounded outlined severity="secondary" @click="fetchUsers"
                        :loading="isLoading" />
                </div>
            </header>

            <div
                class="card bg-white rounded-[2.5rem] shadow-xl shadow-slate-100/50 overflow-hidden border border-slate-100">

                <div v-if="isLoading" class="p-6 space-y-4">
                    <Skeleton v-for="i in 5" :key="i" height="3rem" borderRadius="1rem" />
                </div>

                <DataTable v-else :value="users" :paginator="true" :rows="10"
                    :filters="{ 'global': { value: globalFilter, matchMode: 'contains' } }" stripedRows
                    responsiveLayout="stack" class="p-datatable-modern">
                    <Column header="Сотрудник / Email" sortable field="username">
                        <template #body="{ data }">
                            <div class="flex items-center gap-3">
                                <div class="flex flex-col">
                                    <div class="font-extrabold text-slate-950 flex items-center gap-2">
                                        {{ data.username }}
                                        <i v-if="data.role === 'admin'" class="pi pi-shield text-amber-500 text-xs"></i>
                                    </div>
                                    <span class="text-xs text-slate-500 font-medium">{{ data.email }}</span>
                                </div>
                            </div>
                        </template>
                    </Column>

                    <Column header="Отдел" sortable field="department">
                        <template #body="{ data }">
                            <span class="text-slate-600 font-semibold text-sm">{{ data.department }}</span>
                        </template>
                    </Column>

                    <Column header="Регистрация" sortable field="date_joined">
                        <template #body="{ data }">
                            <span class="text-slate-400 text-xs font-mono">{{ data.date_joined }}</span>
                        </template>
                    </Column>

                    <Column header="Текущая роль">
                        <template #body="{ data }">
                            <Tag :value="availableRoles.find(r => r.code === data.role)?.name.split(' ')[0]"
                                :severity="availableRoles.find(r => r.code === data.role)?.severity"
                                class="!text-[9px] !font-black uppercase tracking-widest" />
                        </template>
                    </Column>

                    <Column header="Назначить права" headerClass="text-right" bodyClass="text-right">
                        <template #body="{ data }">
                            <Select v-model="data.role" :options="availableRoles" optionLabel="name" optionValue="code"
                                @change="(e) => updateUserRole(data.id, e.value)"
                                class="!text-xs !font-bold !bg-slate-50 !border-slate-200 !rounded-xl text-left"
                                style="min-width: 200px;" />
                        </template>
                    </Column>

                    <template #empty>
                        <div class="text-center py-20 text-slate-400">
                            <i class="pi pi-users text-4xl mb-3 block"></i>
                            <p class="text-xl font-bold">Сотрудники не найдены</p>
                        </div>
                    </template>
                </DataTable>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Кастомизация таблицы под общий стиль */
:deep(.p-datatable-header) {
    background: transparent;
    border: none;
}

:deep(.p-datatable-thead > tr > th) {
    background: #0f172a;
    /* slate-900 */
    color: white;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    padding: 1.5rem;
}

:deep(.p-datatable-tbody > tr) {
    transition: background-color 0.2s;
}

:deep(.p-datatable-tbody > tr:hover) {
    background-color: #f1f5f9 !important;
}

:deep(.p-paginator) {
    border-radius: 0 0 2.5rem 2.5rem;
    padding: 1rem;
    border-top: 1px solid #f1f5f9;
}
</style>