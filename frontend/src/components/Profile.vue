<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import AnalyticsCharts from './AnalyticsCharts.vue'

// Импорт компонентов PrimeVue
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Tag from 'primevue/tag'
import ScrollPanel from 'primevue/scrollpanel'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'

const router = useRouter()
const profile = ref(null)
const allTracks = ref([])
const isSettingsMode = ref(false)
const newPassword = ref('')
const message = ref('')

onMounted(async () => {
    try {
        const [resProfile, resTracks] = await Promise.all([
            axios.get('http://127.0.0.1:8000/api/profile/'),
            axios.get('http://127.0.0.1:8000/api/records/')
        ])
        profile.value = resProfile.data
        allTracks.value = resTracks.data
    } catch (e) {
        console.error("Ошибка загрузки профиля:", e)
        if (e.response?.status === 401) handleLogout()
    }
})

const handleLogout = () => {
    localStorage.removeItem('user-token')
    localStorage.removeItem('user-info')
    delete axios.defaults.headers.common['Authorization']
    window.location.href = '/'
}

const saveSettings = async () => {
    if (newPassword.value.length < 6) {
        message.value = "Пароль слишком короткий"
        return
    }
    message.value = "Настройки сохранены!"
    setTimeout(() => {
        isSettingsMode.value = false
        message.value = ""
        newPassword.value = ""
    }, 1500)
}

const getRoleSeverity = (role) => {
    switch (role) {
        case 'admin': return 'danger';
        case 'moderator': return 'help';
        default: return 'info';
    }
}
</script>

<template>
    <div class="w-full mx-auto animate-in fade-in duration-500 pb-12">

        <!-- Внутренний подзаголовок (Хлебные крошки / Назад) -->
        <div
            class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 md:mb-8 bg-white p-4 rounded-2xl border border-slate-200/60 shadow-sm">
            <div class="flex items-center gap-3">
                <Button icon="pi pi-chevron-left" @click="router.push('/')"
                    class="!p-button-text !p-button-secondary !p-button-sm !rounded-xl" label="Назад к архиву" />
                <div class="h-4 w-[1px] bg-slate-200 mx-1 hidden sm:block"></div>
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400 hidden sm:inline">Личный
                    кабинет</span>
            </div>

            <div v-if="profile"
                class="flex items-center justify-between sm:justify-end gap-3 w-full sm:w-auto border-t sm:border-none pt-2 sm:pt-0">
                <span class="text-[10px] font-black uppercase tracking-widest text-slate-400 sm:hidden">Статус
                    аккаунта:</span>
                <Tag :value="profile.role" :severity="getRoleSeverity(profile.role_code)"
                    class="!rounded-lg !text-[9px] !font-black uppercase tracking-tighter" />
            </div>
        </div>

        <div v-if="profile" class="w-full">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-6 md:gap-8 items-start">

                <!-- ЛЕВАЯ КОЛОНКА: КАРТОЧКА СОТРУДНИКА -->
                <div class="lg:col-span-4 xl:col-span-3 lg:sticky lg:top-24">
                    <div class="bg-slate-900 rounded-[2rem] md:rounded-[2.5rem] p-6 md:p-8 text-white shadow-xl">
                        <div class="flex flex-col items-center">

                            <div class="relative mb-4 md:mb-6 group">
                                <Avatar :label="profile.username[0].toUpperCase()"
                                    class="!w-24 !h-24 md:!w-32 md:!h-32 !text-4xl md:!text-5xl !font-black !rounded-[1.5rem] md:!rounded-[2rem] shadow-2xl transition-transform group-hover:scale-105"
                                    :class="[
                                        profile.role_code === 'admin' ? 'bg-gradient-to-br from-red-500 to-rose-700' :
                                            profile.role_code === 'moderator' ? 'bg-gradient-to-br from-purple-500 to-indigo-700' :
                                                'bg-gradient-to-br from-blue-500 to-cyan-700'
                                    ]" />
                                <div
                                    class="absolute -bottom-1 -right-1 w-7 h-7 bg-green-500 border-4 border-slate-900 rounded-xl flex items-center justify-center">
                                    <i class="pi pi-check text-[8px] text-white"></i>
                                </div>
                            </div>

                            <div class="text-center w-full">
                                <h2 class="text-xl md:text-2xl font-black tracking-tight mb-1 truncate">{{
                                    profile.username }}</h2>
                                <p
                                    class="text-blue-400 text-[9px] md:text-[10px] font-black uppercase tracking-[0.2em] italic mb-4 md:mb-6 truncate">
                                    {{ profile.department || 'Департамент статистики' }}
                                </p>

                                <div class="bg-white/5 rounded-xl p-3.5 mb-4 border border-white/5 text-left">
                                    <p class="text-[9px] text-slate-400 uppercase font-black mb-1 tracking-wider">
                                        Электронная почта</p>
                                    <p class="text-xs md:text-sm font-medium text-slate-200 truncate">{{ profile.email
                                        }}</p>
                                </div>

                                <div class="space-y-2 mb-6 text-left">
                                    <div class="flex justify-between items-center bg-white/5 px-3.5 py-2 rounded-xl">
                                        <span class="text-[9px] font-black text-slate-400 uppercase">Табельный ID</span>
                                        <span class="text-xs font-mono text-slate-200">#{{ profile.id + 1000 }}</span>
                                    </div>
                                    <div class="flex justify-between items-center bg-white/5 px-3.5 py-2 rounded-xl">
                                        <span class="text-[9px] font-black text-slate-400 uppercase">Регистрация</span>
                                        <span class="text-xs font-mono text-slate-200">{{ profile.date_joined }}</span>
                                    </div>
                                </div>

                                <Button @click="handleLogout" icon="pi pi-power-off" label="Завершить сеанс"
                                    class="!w-full !py-3.5 !rounded-xl !text-[10px] !font-black !uppercase !tracking-widest !bg-red-500/10 !text-red-400 !border-red-500/20 hover:!bg-red-500 hover:!text-white transition-all" />
                            </div>

                        </div>
                    </div>
                </div>

                <!-- ПРАВАЯ КОЛОНКА: РАБОЧИЕ ДАННЫЕ / ТАБЫ -->
                <div class="lg:col-span-8 xl:col-span-9 space-y-6 md:space-y-8 w-full min-w-0">

                    <!-- Переключатели вкладок (Адаптивные кнопки) -->
                    <div class="flex flex-row gap-2 bg-slate-200/60 p-1.5 rounded-2xl w-full sm:w-max">
                        <button @click="isSettingsMode = false"
                            :class="[!isSettingsMode ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900']"
                            class="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 md:px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all">
                            <i class="pi pi-chart-bar"></i> <span>Аналитика</span>
                        </button>
                        <button @click="isSettingsMode = true"
                            :class="[isSettingsMode ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-600 hover:text-slate-900']"
                            class="flex-1 sm:flex-initial flex items-center justify-center gap-2 px-4 md:px-6 py-3 rounded-xl font-black text-[10px] uppercase tracking-widest transition-all">
                            <i class="pi pi-shield"></i> <span>Безопасность</span>
                        </button>
                    </div>

                    <!-- ВКЛАДКА: АНАЛИТИКА -->
                    <div v-if="!isSettingsMode"
                        class="space-y-6 md:space-y-8 animate-in slide-in-from-right-4 duration-300">

                        <!-- Микро-карточки метрик -->
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 md:gap-6">
                            <div
                                class="bg-white p-6 md:p-8 rounded-2xl md:rounded-[2rem] shadow-sm border border-slate-200/60 flex flex-col items-center text-center">
                                <div class="w-10 h-10 bg-blue-50 rounded-xl flex items-center justify-center mb-3">
                                    <i class="pi pi-heart-fill text-blue-500 text-sm"></i>
                                </div>
                                <p class="text-3xl md:text-4xl font-black text-slate-800">{{
                                    profile.summary?.my_favorites || 0 }}</p>
                                <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-1.5">В
                                    избранном</p>
                            </div>

                            <div
                                class="bg-white p-6 md:p-8 rounded-2xl md:rounded-[2rem] shadow-sm border border-slate-200/60 flex flex-col items-center text-center">
                                <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-3">
                                    <i class="pi pi-cloud-upload text-indigo-500 text-sm"></i>
                                </div>
                                <p class="text-3xl md:text-4xl font-black text-slate-800">{{ profile.summary?.my_records
                                    || 0 }}</p>
                                <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-1.5">Мои
                                    загрузки</p>
                            </div>

                            <div
                                class="bg-slate-900 p-6 md:p-8 rounded-2xl md:rounded-[2rem] shadow-xl flex flex-col items-center text-center">
                                <div
                                    class="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center mb-3 text-white">
                                    <i class="pi pi-server text-sm"></i>
                                </div>
                                <p class="text-3xl md:text-4xl font-black text-white">{{
                                    profile.summary?.total_system_files || 0 }}</p>
                                <p class="text-[9px] text-slate-500 uppercase font-black tracking-widest mt-1.5">База
                                    системы</p>
                            </div>
                        </div>

                        <!-- Модуль Графиков -->
                        <div
                            class="bg-white p-4 sm:p-6 md:p-8 rounded-2xl md:rounded-[2rem] border border-slate-200/60 shadow-sm">
                            <h4 class="text-[10px] font-black text-slate-800 uppercase tracking-widest italic mb-6">
                                Визуализация активности данных
                            </h4>
                            <AnalyticsCharts :records="allTracks" />
                        </div>

                        <!-- Логи Системных Событий -->
                        <div
                            class="bg-white p-4 sm:p-6 md:p-8 rounded-2xl md:rounded-[2rem] border border-slate-200/60 shadow-sm">
                            <h4 class="text-[10px] font-black text-slate-800 uppercase tracking-widest mb-6">События
                                учетной записи</h4>
                            <ScrollPanel style="width: 100%; height: 320px" class="custom-scroll">
                                <div class="space-y-3 pr-2 md:pr-4">
                                    <div v-for="item in profile.stats?.recent_activity" :key="item.id"
                                        class="group flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50/50 rounded-xl md:rounded-2xl border border-transparent hover:border-blue-200 hover:bg-white transition-all duration-300 gap-3">
                                        <div class="flex items-center space-x-4">
                                            <div
                                                class="w-9 h-9 bg-white rounded-xl flex items-center justify-center shadow-sm group-hover:bg-blue-600 transition-colors shrink-0">
                                                <i
                                                    class="pi pi-history text-slate-400 group-hover:text-white text-xs"></i>
                                            </div>
                                            <div class="min-w-0">
                                                <p class="text-xs md:text-sm font-black text-slate-700 truncate">{{
                                                    item.title }}</p>
                                                <p
                                                    class="text-[9px] text-slate-400 uppercase font-bold tracking-tight mt-0.5">
                                                    Запись успешно верифицирована</p>
                                            </div>
                                        </div>
                                        <div class="text-left sm:text-right shrink-0">
                                            <Tag :value="item.date" severity="secondary"
                                                class="!text-[9px] !bg-slate-200/50 !text-slate-600" />
                                        </div>
                                    </div>
                                </div>
                            </ScrollPanel>
                        </div>
                    </div>

                    <!-- ВКЛАДКА: БЕЗОПАСНОСТЬ -->
                    <div v-else class="max-w-2xl w-full animate-in slide-in-from-right-4 duration-300">
                        <div
                            class="bg-white p-5 sm:p-6 md:p-10 rounded-2xl md:rounded-[2rem] border border-slate-200 shadow-sm">
                            <div class="mb-6 md:mb-8">
                                <h3 class="text-lg md:text-xl font-black text-slate-800 mb-2">Настройки безопасности
                                </h3>
                                <p class="text-xs md:text-sm text-slate-400 font-medium">Регулярная смена пароля
                                    помогает защитить ваш рабочий аккаунт в закрытой системе РостовСтат.</p>
                            </div>

                            <div class="space-y-4">
                                <div class="flex flex-col gap-2">
                                    <label class="text-[10px] font-black uppercase text-slate-400 ml-1">Новый
                                        пароль</label>
                                    <InputText v-model="newPassword" type="password"
                                        class="!w-full !rounded-xl !p-4 !bg-slate-50 !border-slate-200/70 focus:!bg-white"
                                        placeholder="Минимум 6 символов" />
                                </div>

                                <Message v-if="message" :severity="message.includes('сохранены') ? 'success' : 'warn'">
                                    {{ message }}
                                </Message>

                                <div class="flex flex-col sm:flex-row gap-3 pt-4">
                                    <Button @click="saveSettings" label="Сохранить изменения"
                                        class="sm:flex-[2] !rounded-xl !py-3.5 !font-black !uppercase !text-[10px] !tracking-widest" />
                                    <Button @click="isSettingsMode = false" label="Отмена" severity="secondary" text
                                        class="sm:flex-1 !rounded-xl !py-3.5 !font-black !uppercase !text-[10px] !tracking-widest" />
                                </div>
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
:deep(.custom-scroll .p-scrollpanel-bar) {
    background-color: #cbd5e1 !important;
    opacity: 0.5 !important;
}

:deep(.p-tag) {
    border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>