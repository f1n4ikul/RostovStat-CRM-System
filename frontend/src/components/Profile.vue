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

// Загрузка данных при входе на страницу
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
        // Если токен протух — отправляем на логин
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
    // Здесь будет твой реальный запрос к API для смены пароля
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
    <div class="min-h-screen bg-[#f1f5f9] pb-12">
        <div class="sticky top-0 z-10 bg-white/80 backdrop-blur-md border-b border-slate-200 mb-8">
            <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <Button icon="pi pi-chevron-left" @click="router.push('/')"
                        class="!p-button-text !p-button-secondary !p-button-sm !rounded-xl" label="Назад к архиву" />
                    <div class="h-4 w-[1px] bg-slate-200 mx-2"></div>
                    <span class="text-xs font-black uppercase tracking-widest text-slate-400">Личный кабинет</span>
                </div>

                <div class="flex items-center gap-3">
                    <Tag v-if="profile" :value="profile.role" :severity="getRoleSeverity(profile.role_code)"
                        class="!rounded-lg !text-[9px] !font-black uppercase tracking-tighter" />
                </div>
            </div>
        </div>

        <div v-if="profile" class="max-w-7xl mx-auto px-6 animate-in fade-in duration-700">
            <div class="grid grid-cols-1 lg:grid-cols-12 gap-8">

                <div class="lg:col-span-4 xl:col-span-3">
                    <div class="bg-slate-900 rounded-[2.5rem] p-8 text-white shadow-2xl sticky top-24">
                        <div class="flex flex-col items-center">
                            <div class="relative mb-6 group">
                                <Avatar :label="profile.username[0].toUpperCase()"
                                    class="!w-32 !h-32 !text-5xl !font-black !rounded-[2rem] shadow-2xl transition-transform group-hover:scale-105"
                                    :class="[
                                        profile.role_code === 'admin' ? 'bg-gradient-to-br from-red-500 to-rose-700' :
                                            profile.role_code === 'moderator' ? 'bg-gradient-to-br from-purple-500 to-indigo-700' :
                                                'bg-gradient-to-br from-blue-500 to-cyan-700'
                                    ]" />
                                <div
                                    class="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 border-4 border-slate-900 rounded-2xl flex items-center justify-center">
                                    <i class="pi pi-check text-[10px] text-white"></i>
                                </div>
                            </div>

                            <div class="text-center w-full">
                                <h2 class="text-2xl font-black tracking-tight mb-1">{{ profile.username }}</h2>
                                <p class="text-blue-400 text-[10px] font-black uppercase tracking-[0.2em] italic mb-4">
                                    {{ profile.department || 'Департамент статистики' }}
                                </p>

                                <div class="bg-white/5 rounded-2xl p-4 mb-6 border border-white/5">
                                    <p class="text-[10px] text-slate-400 uppercase font-black mb-1">Электронная почта
                                    </p>
                                    <p class="text-sm font-medium text-slate-200 truncate">{{ profile.email }}</p>
                                </div>

                                <div class="space-y-3 mb-8">
                                    <div class="flex justify-between items-center bg-white/5 px-4 py-2 rounded-xl">
                                        <span class="text-[9px] font-black text-slate-500 uppercase">ID</span>
                                        <span class="text-xs font-mono">#{{ profile.id + 1000 }}</span>
                                    </div>
                                    <div class="flex justify-between items-center bg-white/5 px-4 py-2 rounded-xl">
                                        <span class="text-[9px] font-black text-slate-500 uppercase">Стаж</span>
                                        <span class="text-xs font-mono">{{ profile.date_joined }}</span>
                                    </div>
                                </div>

                                <Button @click="handleLogout" icon="pi pi-power-off" label="Завершить сеанс"
                                    class="!w-full !py-4 !rounded-2xl !text-[10px] !font-black !uppercase !tracking-widest !bg-red-500/10 !text-red-400 !border-red-500/20 hover:!bg-red-500 hover:!text-white transition-all" />
                            </div>
                        </div>
                    </div>
                </div>

                <div class="lg:col-span-8 xl:col-span-9 space-y-8">

                    <div class="flex gap-4">
                        <button @click="isSettingsMode = false"
                            :class="[!isSettingsMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-slate-500']"
                            class="px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all">
                            <i class="pi pi-chart-bar mr-2"></i> Аналитика
                        </button>
                        <button @click="isSettingsMode = true"
                            :class="[isSettingsMode ? 'bg-blue-600 text-white shadow-lg' : 'bg-white text-slate-500']"
                            class="px-8 py-4 rounded-2xl font-black text-[10px] uppercase tracking-widest transition-all">
                            <i class="pi pi-shield mr-2"></i> Безопасность
                        </button>
                    </div>

                    <div v-if="!isSettingsMode" class="space-y-8 animate-in slide-in-from-right-4 duration-500">
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
                            <div
                                class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-200/60 flex flex-col items-center text-center">
                                <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
                                    <i class="pi pi-heart-fill text-blue-500"></i>
                                </div>
                                <p class="text-4xl font-black text-slate-800">{{ profile.summary.my_favorites }}</p>
                                <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-2">В
                                    избранном</p>
                            </div>
                            <div
                                class="bg-white p-8 rounded-[2rem] shadow-sm border border-slate-200/60 flex flex-col items-center text-center">
                                <div class="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-4">
                                    <i class="pi pi-cloud-upload text-indigo-500"></i>
                                </div>
                                <p class="text-4xl font-black text-slate-800">{{ profile.summary.my_records }}</p>
                                <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-2">Мои
                                    загрузки</p>
                            </div>
                            <div
                                class="bg-slate-900 p-8 rounded-[2rem] shadow-xl flex flex-col items-center text-center">
                                <div
                                    class="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center mb-4 text-white">
                                    <i class="pi pi-server"></i>
                                </div>
                                <p class="text-4xl font-black text-white">{{ profile.summary.total_system_files }}</p>
                                <p class="text-[9px] text-slate-500 uppercase font-black tracking-widest mt-2">База
                                    системы</p>
                            </div>
                        </div>

                        <div class="bg-white p-10 rounded-[3rem] border border-slate-200/60 shadow-sm">
                            <div class="flex items-center justify-between mb-8">
                                <h4 class="text-xs font-black text-slate-800 uppercase tracking-widest italic">
                                    Визуализация активности данных
                                </h4>
                            </div>
                            <AnalyticsCharts :records="allTracks" />
                        </div>

                        <div class="bg-white p-10 rounded-[3rem] border border-slate-200/60 shadow-sm">
                            <h4 class="text-xs font-black text-slate-800 uppercase tracking-widest mb-8">События учетной
                                записи</h4>
                            <ScrollPanel style="width: 100%; height: 300px" class="custom-scroll">
                                <div class="space-y-4 pr-6">
                                    <div v-for="item in profile.stats.recent_activity" :key="item.id"
                                        class="group flex items-center justify-between p-5 bg-slate-50/50 rounded-3xl border border-transparent hover:border-blue-200 hover:bg-white transition-all duration-300">
                                        <div class="flex items-center space-x-5">
                                            <div
                                                class="w-10 h-10 bg-white rounded-2xl flex items-center justify-center shadow-sm group-hover:bg-blue-600 transition-colors">
                                                <i class="pi pi-history text-slate-400 group-hover:text-white"></i>
                                            </div>
                                            <div>
                                                <p class="text-sm font-black text-slate-700">{{ item.title }}</p>
                                                <p
                                                    class="text-[10px] text-slate-400 uppercase font-bold tracking-tighter">
                                                    Запись успешно верифицирована</p>
                                            </div>
                                        </div>
                                        <div class="text-right">
                                            <Tag :value="item.date" severity="secondary"
                                                class="!text-[9px] !bg-slate-200/50 !text-slate-600" />
                                        </div>
                                    </div>
                                </div>
                            </ScrollPanel>
                        </div>
                    </div>

                    <div v-else class="max-w-xl animate-in slide-in-from-right-4 duration-500">
                        <div class="bg-white p-10 rounded-[3rem] border border-slate-200 shadow-sm">
                            <div class="mb-8">
                                <h3 class="text-xl font-black text-slate-800 mb-2">Настройки безопасности</h3>
                                <p class="text-sm text-slate-400 font-medium">Регулярная смена пароля помогает защитить
                                    ваш рабочий аккаунт в РостовСтат.</p>
                            </div>

                            <div class="space-y-4">
                                <div class="flex flex-col gap-2">
                                    <label class="text-[10px] font-black uppercase text-slate-400 ml-1">Новый
                                        пароль</label>
                                    <InputText v-model="newPassword" type="password"
                                        class="!w-full !rounded-2xl !p-5 !bg-slate-50 !border-slate-100 focus:!bg-white"
                                        placeholder="Минимум 6 символов" />
                                </div>

                                <Message v-if="message" :severity="message.includes('сохранены') ? 'success' : 'warn'">
                                    {{ message }}
                                </Message>

                                <div class="flex gap-4 pt-4">
                                    <Button @click="saveSettings" label="Сохранить изменения"
                                        class="flex-[2] !rounded-2xl !py-4 !font-black !uppercase !text-[10px] !tracking-widest" />
                                    <Button @click="isSettingsMode = false" label="Отмена" severity="secondary" text
                                        class="flex-1 !rounded-2xl !font-black !uppercase !text-[10px] !tracking-widest" />
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
/* Кастомный скролл для PrimeVue */
:deep(.custom-scroll .p-scrollpanel-bar) {
    background-color: #cbd5e1 !important;
    opacity: 0.5 !important;
}

:deep(.p-tag) {
    border: 1px solid rgba(0, 0, 0, 0.05);
}

/* Улучшение читаемости на больших экранах */
.max-w-7xl {
    max-width: 1400px;
}
</style>