<script setup>
import { ref, onMounted, computed } from 'vue'
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
import Avatar from 'primevue/avatar'

const props = defineProps({
    user: Object,
    isAdmin: Boolean
})

const users = ref([])
const isLoading = ref(true)
const globalFilter = ref('')
const router = useRouter()

// Конфигурация API
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

// Состояния для модального окна создания пользователя
const isCreateModalOpen = ref(false)
const isSubmitting = ref(false)
const newUser = ref({
    username: '',
    email: '',
    password: '',
    department: 'общий',
    role: 'employee'
})

// Реестр отделов Ростовстата
const departments = [
    { id: 'общий', name: 'Общий отдел' },
    { id: 'сводный', name: 'Отдел сводных статистических работ и общественных связей' },
    { id: 'счета_балансы', name: 'Отдел региональных счетов и балансов' },
    { id: 'цены_финансы', name: 'Отдел статистики цен и финансов' },
    { id: 'сельхоз_природа', name: 'Отдел статистики сельского хозяйства и окружающей природной среды' },
    { id: 'предприятия', name: 'Отдел статистики предприятий' },
    { id: 'услуги', name: 'Отдел статистики рыночных услуг' },
    { id: 'труд_наука', name: 'Отдел статистики труда, образования, науки и инноваций' },
    { id: 'уровень_жизни', name: 'Отдел статистики уровня жизни и обследований домашних хозяйств' },
    { id: 'строительство_жкх', name: 'Отдел статистики строительства, инвестиций и жилищно-коммунального хозяйства' },
    { id: 'население_перепись', name: 'Отдел статистики населения и здравоохранения, организации и проведения переписей и обследований' }
]

const availableRoles = [
    { code: 'employee', name: 'Сотрудник (Чтение)', severity: 'info' },
    { code: 'moderator', name: 'Модератор (Запись)', severity: 'warn' },
    { code: 'admin', name: 'Администратор (Полный)', severity: 'danger' }
]

// Вычисление ID текущего администратора для исключения из списка
const currentAdminId = computed(() => {
    if (props.user && props.user.id) return props.user.id
    try {
        const userInfo = JSON.parse(localStorage.getItem('user-info') || '{}')
        return userInfo.id || userInfo.user_id
    } catch {
        return null
    }
})

const getDepartmentName = (deptId) => {
    const dept = departments.find(d => d.id === deptId)
    return dept ? dept.name : (deptId || 'Общий отдел')
}

const getAuthHeaders = () => {
    const token = localStorage.getItem('user-token')
    return { 'Authorization': `Token ${token}` }
}

// Получение списка пользователей
const fetchUsers = async () => {
    const userInfo = JSON.parse(localStorage.getItem('user-info') || '{}')
    const hasAccess = props.isAdmin || userInfo?.role_code === 'admin'

    if (!hasAccess) {
        router.push('/')
        return
    }

    isLoading.value = true
    try {
        const response = await axios.get(`${API_BASE_URL}/api/admin/users/`, {
            headers: getAuthHeaders()
        })
        users.value = Array.isArray(response.data) ? response.data : []
    } catch (e) {
        console.error("Ошибка загрузки пользователей:", e)
        Swal.fire({
            icon: 'error',
            title: 'Ошибка доступа',
            text: 'Не удалось загрузить реестр сотрудников',
            confirmButtonColor: '#3b82f6'
        })
        users.value = []
    } finally {
        isLoading.value = false
    }
}

// Создание нового сотрудника
const handleCreateUser = async () => {
    if (!newUser.value.username || !newUser.value.password) {
        Swal.fire('Внимание', 'Логин и пароль обязательны', 'warning')
        return
    }

    isSubmitting.value = true
    try {
        const payload = {
            username: newUser.value.username,
            email: newUser.value.email,
            password: newUser.value.password,
            departament: newUser.value.department,
            role: newUser.value.role
        }

        await axios.post(`${API_BASE_URL}/api/admin/users/create/`, payload, {
            headers: getAuthHeaders()
        })

        Swal.fire({
            icon: 'success',
            title: 'Пользователь добавлен',
            text: `Учетная запись ${newUser.value.username} успешно создана.`,
            confirmButtonColor: '#3b82f6'
        })

        isCreateModalOpen.value = false
        newUser.value = { username: '', email: '', password: '', department: 'общий', role: 'employee' }
        await fetchUsers()
    } catch (e) {
        const errorMsg = e.response?.data?.detail || e.response?.data?.error || 'Проверьте корректность данных'
        Swal.fire('Ошибка регистрации', errorMsg, 'error')
    } finally {
        isSubmitting.value = false
    }
}

// Изменение роли сотрудника
const updateUserRole = async (userId, newRole) => {
    if (userId === currentAdminId.value) {
        Swal.fire({
            icon: 'warning',
            title: 'Ограничение доступа',
            text: 'Вы не можете понизить в правах собственную учетную запись.',
            confirmButtonColor: '#3b82f6'
        })
        await fetchUsers()
        return
    }

    try {
        await axios.post(`${API_BASE_URL}/api/admin/users/${userId}/role/`,
            { role: newRole },
            { headers: getAuthHeaders() }
        )
        const user = users.value.find(u => u.id === userId)
        if (user) user.role = newRole

        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true
        })
        Toast.fire({
            icon: 'success',
            title: 'Права успешно обновлены'
        })
    } catch (e) {
        Swal.fire('Ошибка', 'Не удалось изменить уровень доступа', 'error')
        await fetchUsers()
    }
}

// Удаление сотрудника
const deleteUser = async (userItem) => {
    if (userItem.id === currentAdminId.value) {
        Swal.fire('Ошибка', 'Удаление собственной сессии невозможно', 'error')
        return
    }

    const result = await Swal.fire({
        title: 'Удалить сотрудника?',
        text: `Учетная запись ${userItem.username} будет навсегда исключена из ведомственной системы.`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ef4444',
        cancelButtonColor: '#94a3b8',
        confirmButtonText: 'Да, удалить',
        cancelButtonText: 'Отмена',
        customClass: {
            popup: 'rounded-2xl'
        }
    })

    if (result.isConfirmed) {
        try {
            await axios.delete(`${API_BASE_URL}/api/admin/users/${userItem.id}/delete/`, {
                headers: getAuthHeaders()
            })
            await fetchUsers()
            Swal.fire('Успешно', 'Пользователь удален', 'success')
        } catch (e) {
            Swal.fire('Ошибка', 'Не удалось выполнить удаление', 'error')
        }
    }
}

// Реактивный фильтр списка пользователей (исключает текущего админа)
const filteredUsers = computed(() => {
    const list = users.value || []
    const query = globalFilter.value.trim().toLowerCase()

    // Исключаем текущую учетную запись администратора
    const listWithoutMe = list.filter(u => u.id !== currentAdminId.value)

    if (!query) return listWithoutMe

    return listWithoutMe.filter(u => {
        const usernameMatch = u.username?.toLowerCase().includes(query)
        const emailMatch = u.email?.toLowerCase().includes(query)
        const deptName = getDepartmentName(u.department).toLowerCase()
        return usernameMatch || emailMatch || deptName.includes(query)
    })
})

onMounted(fetchUsers)
</script>

<template>
    <div class="min-h-screen bg-slate-50/50 w-full pb-12 antialiased selection:bg-blue-500/10">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

            <nav class="py-5">
                <button @click="router.push('/')"
                    class="group inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-slate-900 transition-colors duration-200">
                    <i class="pi pi-arrow-left text-[10px] transition-transform group-hover:-translate-x-0.5"></i>
                    Вернуться в архив
                </button>
            </nav>

            <header
                class="mb-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-200/60 pb-6">
                <div>
                    <div class="flex items-center gap-2 mb-1.5">
                        <span
                            class="inline-flex items-center bg-blue-50 text-blue-700 text-[11px] font-medium px-2 py-0.5 rounded-md border border-blue-200/40">
                            Панель администратора
                        </span>
                    </div>
                    <h1 class="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900">
                        Управление доступом
                    </h1>
                    <p class="text-xs sm:text-sm text-slate-500 mt-1">
                        Реестр учетных записей сотрудников Ростовстата и конфигурация прав безопасности
                    </p>
                </div>

                <div class="flex flex-col sm:flex-row items-center gap-3 w-full md:w-auto">
                    <IconField class="w-full sm:w-64">
                        <InputIcon class="pi pi-search text-slate-400 !text-sm" />
                        <InputText v-model="globalFilter" placeholder="Поиск сотрудника или отдела..."
                            class="!w-full !rounded-xl !border-slate-200 !bg-white !pl-9 !py-2.5 !text-sm !shadow-sm focus:!border-blue-500 focus:!ring-1 focus:!ring-blue-500" />
                    </IconField>

                    <div class="flex items-center gap-2 w-full sm:w-auto justify-end shrink-0">
                        <Button icon="pi pi-refresh" outlined severity="secondary" @click="fetchUsers"
                            :loading="isLoading"
                            class="!rounded-xl !w-10 !h-10 !p-0 !border-slate-200 !bg-white hover:!bg-slate-50" />
                        <Button icon="pi pi-user-plus" label="Добавить сотрудника" severity="primary"
                            class="!rounded-xl !text-xs !font-semibold !py-2.5 !px-4 !shadow-sm !bg-blue-600 hover:!bg-blue-700 !border-none"
                            @click="isCreateModalOpen = true" />
                    </div>
                </div>
            </header>

            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
                <div class="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm flex items-center gap-4">
                    <div
                        class="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-slate-600 shrink-0">
                        <i class="pi pi-users text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Всего сотрудников</p>
                        <p class="text-2xl font-bold text-slate-900 mt-0.5">{{ filteredUsers?.length + 1 || 0 }}</p>
                    </div>
                </div>

                <div class="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm flex items-center gap-4">
                    <div
                        class="w-10 h-10 rounded-xl bg-amber-50 flex items-center justify-center text-amber-600 shrink-0">
                        <i class="pi pi-shield text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Администраторы</p>
                        <p class="text-2xl font-bold text-slate-900 mt-0.5">
                            {{filteredUsers?.filter(u => u.role === 'admin').length || 0}}
                        </p>
                    </div>
                </div>

                <div class="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm flex items-center gap-4">
                    <div
                        class="w-10 h-10 rounded-xl bg-green-50 flex items-center justify-center text-green-600 shrink-0">
                        <span class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                    </div>
                    <div>
                        <p class="text-xs font-medium text-slate-400 uppercase tracking-wider">Статус системы</p>
                        <p class="text-sm font-bold text-green-600 uppercase tracking-wide mt-1">Online</p>
                    </div>
                </div>
            </div>

            <div class="hidden lg:block bg-white rounded-2xl shadow-sm border border-slate-200/80 overflow-hidden">
                <DataTable :value="filteredUsers" :paginator="true" :rows="10" :loading="isLoading" stripedRows
                    class="modern-admin-table"
                    paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
                    currentPageReportTemplate="{first}-{last} из {totalRecords}">
                    <template #empty>
                        <div class="py-16 text-center">
                            <i class="pi pi-filter-slash text-slate-300 text-3xl mb-3"></i>
                            <p class="text-slate-400 font-medium text-sm">Сотрудники, удовлетворяющие условиям, не
                                найдены.</p>
                        </div>
                    </template>

                    <Column field="username" header="Сотрудник" sortable>
                        <template #body="{ data }">
                            <div class="flex items-center gap-3">
                                <Avatar :label="data.username ? data.username[0].toUpperCase() : 'U'"
                                    class="!w-8 !h-8 !text-xs !font-bold !rounded-lg shrink-0" :class="[
                                        data.role === 'admin' ? '!bg-red-50 !text-red-600' : data.role === 'moderator' ? '!bg-amber-50 !text-amber-600' : '!bg-blue-50 !text-blue-600'
                                    ]" />
                                <div class="flex flex-col">
                                    <span class="font-semibold text-slate-900 text-sm">{{ data.username }}</span>
                                    <span class="text-xs text-slate-400 font-mono">{{ data.email || '—' }}</span>
                                </div>
                            </div>
                        </template>
                    </Column>

                    <Column field="department" header="Подразделение Ростовстата" sortable>
                        <template #body="{ data }">
                            <span class="text-slate-600 text-xs font-medium max-w-sm block leading-relaxed">
                                {{ getDepartmentName(data?.department) }}
                            </span>
                        </template>
                    </Column>

                    <Column field="role" header="Статус доступа">
                        <template #body="{ data }">
                            <Tag :value="availableRoles.find(r => r.code === data.role)?.name || data.role"
                                :severity="availableRoles.find(r => r.code === data.role)?.severity || 'info'"
                                class="!rounded-md !text-[10px] !font-semibold !px-2.5 !py-0.5" />
                        </template>
                    </Column>

                    <Column header="Действия (Контроль уровня)" class="text-right">
                        <template #body="{ data }">
                            <div class="flex items-center justify-end gap-3" @click.stop>
                                <Select v-model="data.role" :options="availableRoles" optionLabel="name"
                                    optionValue="code" :disabled="data.id === currentAdminId"
                                    @change="(e) => updateUserRole(data.id, e.value)"
                                    class="!text-xs !bg-slate-50 !rounded-xl !border-slate-200/80 w-[210px] !h-9 flex items-center shadow-sm" />
                                <Button icon="pi pi-trash" severity="danger" text rounded
                                    :disabled="data.id === currentAdminId" class="hover:!bg-red-50 !w-9 !h-9"
                                    @click="deleteUser(data)" />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>

            <div class="block lg:hidden space-y-3">
                <div v-if="isLoading" class="space-y-3">
                    <div v-for="i in 3" :key="i"
                        class="h-32 bg-white rounded-2xl border border-slate-200/60 animate-pulse"></div>
                </div>

                <div v-else-if="filteredUsers && filteredUsers.length > 0" class="space-y-3">
                    <div v-for="member in filteredUsers" :key="member.id"
                        class="bg-white rounded-2xl border border-slate-200/80 shadow-sm overflow-hidden flex flex-col">
                        <div class="p-4 flex items-start justify-between gap-3">
                            <div class="flex items-center gap-3 min-w-0">
                                <Avatar :label="member.username ? member.username[0].toUpperCase() : 'U'"
                                    class="!w-10 !h-10 !text-sm !font-bold !rounded-xl shrink-0" :class="[
                                        member.role === 'admin' ? '!bg-red-50 !text-red-600' : member.role === 'moderator' ? '!bg-amber-50 !text-amber-600' : '!bg-blue-50 !text-blue-600'
                                    ]" />
                                <div class="flex flex-col min-w-0">
                                    <span class="text-sm font-bold text-slate-900 truncate">{{ member.username }}</span>
                                    <span class="text-[11px] text-slate-400 font-medium leading-tight my-0.5">
                                        {{ getDepartmentName(member.department) }}
                                    </span>
                                    <span class="text-xs font-mono text-slate-400 truncate">{{ member.email || 'Почта не привязана'
                                        }}</span>
                                </div>
                            </div>

                            <div class="flex flex-col items-end gap-2 shrink-0">
                                <Tag :value="availableRoles.find(r => r.code === member.role)?.name.split(' ')[0] || member.role"
                                    :severity="availableRoles.find(r => r.code === member.role)?.severity || 'info'"
                                    class="!rounded-md !text-[9px] !font-bold uppercase !px-2" />
                                <Button icon="pi pi-trash" severity="danger" text rounded size="small"
                                    :disabled="member.id === currentAdminId" @click="deleteUser(member)" />
                            </div>
                        </div>

                        <div class="px-4 py-3 bg-slate-50 border-t border-slate-100/80 flex flex-col gap-1.5"
                            @click.stop>
                            <label class="text-[10px] font-semibold text-slate-400 uppercase tracking-wider pl-0.5">
                                Корректировка роли безопасности
                            </label>
                            <Select v-model="member.role" :options="availableRoles" optionLabel="name"
                                optionValue="code" :disabled="member.id === currentAdminId"
                                @change="(e) => updateUserRole(member.id, e.value)"
                                class="!text-xs !bg-white !rounded-xl !border-slate-200 w-full !h-10 flex items-center shadow-sm" />
                        </div>
                    </div>
                </div>

                <div v-else
                    class="bg-white p-12 text-center text-slate-400 rounded-2xl border border-slate-200/60 text-xs">
                    Сотрудники не найдены.
                </div>
            </div>
        </div>

        <div v-if="isCreateModalOpen"
            class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[999] flex items-center justify-center p-4 transition-all"
            @click.self="isCreateModalOpen = false">
            <div
                class="bg-white w-full max-w-md rounded-2xl border border-slate-100 shadow-xl overflow-hidden transform transition-all duration-300">
                <div class="px-6 py-4 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
                    <div>
                        <h3 class="text-base font-bold text-slate-900">Регистрация сотрудника</h3>
                        <p class="text-xs text-slate-400 mt-0.5">Создание новой учетной записи ведомства</p>
                    </div>
                    <Button icon="pi pi-times" severity="secondary" text rounded @click="isCreateModalOpen = false"
                        class="!w-8 !h-8" />
                </div>

                <form @submit.prevent="handleCreateUser" class="p-6 space-y-4">
                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold text-slate-600 pl-0.5">Имя пользователя (Логин)</label>
                        <InputText v-model="newUser.username" placeholder="Например: ivanov_aa"
                            class="!rounded-xl !text-sm w-full !py-2.5" required />
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold text-slate-600 pl-0.5">Служебный Email</label>
                        <InputText v-model="newUser.email" type="email" placeholder="username@rostovstat.ru"
                            class="!rounded-xl !text-sm w-full !py-2.5" />
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold text-slate-600 pl-0.5">Первичный временный пароль</label>
                        <InputText v-model="newUser.password" type="text" placeholder="Минимум 8 символов"
                            class="!rounded-xl !text-sm font-mono w-full !py-2.5" required />
                    </div>

                    <div class="flex flex-col gap-1.5 w-full">
                        <label class="text-xs font-semibold text-slate-600 pl-0.5">Профильный отдел ведомства</label>
                        <Select v-model="newUser.department" :options="departments" optionLabel="name" optionValue="id"
                            placeholder="Выберите отдел из реестра"
                            class="w-full !rounded-xl !text-sm !bg-slate-50 !border-slate-200 shadow-sm mobile-friendly-select"
                            panelClass="mobile-friendly-panel" required />
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-xs font-semibold text-slate-600 pl-0.5">Уровень полномочий (Роль)</label>
                        <Select v-model="newUser.role" :options="availableRoles" optionLabel="name" optionValue="code"
                            class="!rounded-xl !text-sm w-full !bg-slate-50" />
                    </div>

                    <div class="flex items-center gap-3 pt-3">
                        <Button label="Отмена" severity="secondary" text
                            class="w-full !rounded-xl !text-xs !font-semibold !py-2.5"
                            @click="isCreateModalOpen = false" :disabled="isSubmitting" />
                        <Button type="submit" label="Внести в реестр" severity="primary"
                            class="w-full !rounded-xl !text-xs !font-semibold !py-2.5 !bg-blue-600 hover:!bg-blue-700 !border-none"
                            :loading="isSubmitting" />
                    </div>
                </form>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Кастомизация PrimeVue таблицы под Clean UI Design */
:deep(.modern-admin-table .p-datatable-thead > tr > th) {
    background: #f8fafc;
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 14px 16px;
    border-bottom: 1px solid #e2e8f0;
}

:deep(.modern-admin-table .p-datatable-tbody > tr) {
    background-color: #ffffff;
    transition: background-color 0.15s ease;
}

:deep(.modern-admin-table .p-datatable-tbody > tr:hover) {
    background-color: #f8fafc !important;
}

:deep(.modern-admin-table .p-datatable-tbody > tr > td) {
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
}

:deep(.p-paginator) {
    border-top: 1px solid #e2e8f0 !important;
    background: #ffffff !important;
    padding: 0.75rem 1rem !important;
    font-size: 13px;
}

:deep(.p-select) {
    border-radius: 10px;
    transition: all 0.2s;
}

:deep(.p-select:not(.p-disabled):hover) {
    border-color: #cbd5e1;
}

:deep(.p-select-label) {
    font-size: 13px;
    font-weight: 500;
    color: #334155;
}

:deep(.mobile-friendly-select .p-select-label) {
    white-space: normal !important;
    word-break: break-word !important;
    line-height: 1.4 !important;
    padding: 6px 12px !important;
}

:deep(.mobile-friendly-panel .p-select-option) {
    white-space: normal !important;
    word-break: break-word !important;
    line-height: 1.4 !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
}
</style>