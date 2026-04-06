<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

// Импорт компонентов PrimeVue
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Tag from 'primevue/tag'
import ScrollPanel from 'primevue/scrollpanel'
import InputText from 'primevue/inputtext'
import Message from 'primevue/message'

const profile = ref(null)
const emit = defineEmits(['close', 'logout'])

const isSettingsMode = ref(false)
const newPassword = ref('')
const message = ref('')

const handleLogout = () => {
    localStorage.removeItem('user-token')
    delete axios.defaults.headers.common['Authorization']
    emit('logout')
    emit('close')
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

onMounted(async () => {
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/profile/')
        profile.value = response.data
    } catch (e) {
        console.error("Ошибка загрузки профиля:", e)
    }
})

// Хелпер для определения цвета роли
const getRoleSeverity = (role) => {
    switch (role) {
        case 'admin': return 'danger';
        case 'moderator': return 'help';
        default: return 'info';
    }
}
</script>

<template>
    <div v-if="profile" @click="emit('close')"
        class="fixed inset-0 bg-slate-900/60 backdrop-blur-md flex items-center justify-center z-[100] p-4">

        <div @click.stop
            class="bg-white w-full max-w-4xl rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col md:flex-row h-auto max-h-[90vh] border border-white/20">

            <div class="md:w-80 bg-slate-900 p-8 text-white flex flex-col items-center border-r border-slate-800">
                <div class="relative mb-6">
                    <Avatar :label="profile.username[0].toUpperCase()"
                        class="!w-28 !h-28 !text-4xl !font-black !rounded-3xl shadow-2xl" :class="[
                            profile.role_code === 'admin' ? 'bg-gradient-to-br from-red-600 to-orange-700' :
                                profile.role_code === 'moderator' ? 'bg-gradient-to-br from-purple-600 to-indigo-700' :
                                    'bg-gradient-to-br from-blue-600 to-cyan-700'
                        ]" />
                    <div
                        class="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 border-4 border-slate-900 rounded-full">
                    </div>
                </div>

                <div class="text-center mb-8">
                    <h2 class="text-2xl font-black tracking-tight">{{ profile.username }}</h2>
                    <p class="text-blue-400 text-[10px] font-black uppercase tracking-[0.15em] mt-1 italic">
                        {{ profile.department }}
                    </p>
                    <p class="text-slate-500 text-xs mt-2 opacity-60">{{ profile.email }}</p>

                    <div class="mt-5">
                        <Tag :value="profile.role" :severity="getRoleSeverity(profile.role_code)"
                            class="!px-4 !py-1.5 !rounded-full !text-[10px] !font-black uppercase tracking-widest" />
                    </div>
                </div>

                <div class="w-full space-y-5 pt-6 border-t border-slate-800/50">
                    <div class="flex justify-between items-center">
                        <span class="text-[9px] uppercase font-black text-slate-500 tracking-widest">Табельный №</span>
                        <span class="text-xs font-mono text-slate-300">#{{ profile.id + 1000 }}</span>
                    </div>
                    <div>
                        <p class="text-[9px] uppercase font-black text-slate-500 tracking-widest mb-1">В системе с</p>
                        <p class="text-xs font-mono text-slate-300">{{ profile.date_joined }}</p>
                    </div>
                </div>

                <Button @click="handleLogout" icon="pi pi-power-off" label="Завершить сессию" severity="danger" text
                    class="mt-auto w-full !rounded-2xl !text-[10px] !font-black !uppercase !tracking-widest !bg-slate-800/50 hover:!bg-red-500/10" />
            </div>

            <div class="flex-1 p-10 flex flex-col bg-slate-50/50">
                <div class="flex justify-between items-center mb-8">
                    <h3 class="text-3xl font-black text-slate-800 uppercase tracking-tighter italic">
                        {{ isSettingsMode ? 'Безопасность' : 'Личный кабинет' }}
                    </h3>
                    <Button icon="pi pi-times" severity="secondary" rounded text @click="emit('close')" />
                </div>

                <div v-if="!isSettingsMode" class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">

                    <div class="grid grid-cols-3 gap-4">
                        <div
                            class="bg-white p-5 rounded-[2rem] border border-slate-100 shadow-sm transition-all hover:shadow-md">
                            <p class="text-3xl font-black text-blue-600">{{ profile.summary.my_favorites }}</p>
                            <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-1">Избранное</p>
                        </div>
                        <div
                            class="bg-white p-5 rounded-[2rem] border border-slate-100 shadow-sm transition-all hover:shadow-md">
                            <p class="text-3xl font-black text-indigo-600">{{ profile.summary.my_records }}</p>
                            <p class="text-[9px] text-slate-400 uppercase font-black tracking-widest mt-1">Мои файлы</p>
                        </div>
                        <div class="bg-slate-900 p-5 rounded-[2rem] shadow-xl">
                            <p class="text-3xl font-black text-white">{{ profile.summary.total_system_files }}</p>
                            <p class="text-[9px] text-slate-500 uppercase font-black tracking-widest mt-1">Архив КИС</p>
                        </div>
                    </div>

                    <div>
                        <h4 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4 px-2">Последние
                            события</h4>
                        <ScrollPanel style="width: 100%; height: 250px">
                            <div class="space-y-2 pr-4">
                                <div v-for="item in profile.stats.recent_activity" :key="item.id"
                                    class="flex items-center justify-between p-4 bg-white rounded-2xl border border-slate-50 hover:border-blue-100 transition-all group">
                                    <div class="flex items-center space-x-4">
                                        <div
                                            class="w-10 h-10 bg-slate-50 rounded-xl flex items-center justify-center text-slate-400 group-hover:text-blue-500 transition-colors">
                                            <i class="pi pi-file-audio"></i>
                                        </div>
                                        <div>
                                            <p class="text-sm font-black text-slate-700 line-clamp-1">{{ item.title }}
                                            </p>
                                            <p class="text-[10px] text-slate-400 font-mono italic">Аудиопоток загружен
                                            </p>
                                        </div>
                                    </div>
                                    <Tag :value="item.date" severity="secondary" class="!text-[9px] !bg-slate-50" />
                                </div>
                            </div>
                        </ScrollPanel>
                    </div>

                    <Button @click="isSettingsMode = true" label="Настройки аккаунта" icon="pi pi-cog" outlined
                        class="w-full !py-4 !rounded-[2rem] !font-black !text-xs !uppercase !tracking-widest !border-2" />
                </div>

                <div v-else class="space-y-6 animate-in slide-in-from-right-4 duration-500">
                    <div class="p-6 bg-white rounded-3xl border border-slate-100 shadow-sm">
                        <label class="text-[10px] font-black uppercase text-slate-400 block mb-2">Новый пароль</label>
                        <InputText v-model="newPassword" type="password" class="w-full !rounded-xl"
                            placeholder="••••••••" />

                        <Message v-if="message" :severity="message.includes('сохранены') ? 'success' : 'warn'"
                            class="mt-4">
                            {{ message }}
                        </Message>
                    </div>

                    <div class="flex gap-4">
                        <Button @click="saveSettings" label="Сохранить" class="flex-1 !rounded-2xl !font-bold" />
                        <Button @click="isSettingsMode = false" label="Назад" severity="secondary" text
                            class="flex-1 !rounded-2xl !font-bold" />
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Плавный скроллбар для ScrollPanel */
:deep(.p-scrollpanel-bar) {
    background: #e2e8f0;
    opacity: 1;
}

:deep(.p-tag) {
    border: 1px solid rgba(0, 0, 0, 0.05);
}
</style>