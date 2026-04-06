<script setup>
import { ref } from 'vue'
import axios from 'axios'

// Импорт компонентов PrimeVue
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const emit = defineEmits(['login-success', 'go-to-register'])

const login = async () => {
    error.value = ""
    isLoading.value = true
    try {
        const response = await axios.post('http://127.0.0.1:8000/api/login/', {
            employee_code: username.value,
            password: password.value
        })
        const token = response.data.token
        localStorage.setItem('user-token', token)
        axios.defaults.headers.common['Authorization'] = `Token ${token}`
        emit('login-success')
    } catch (err) {
        error.value = "Неверный логин или пароль"
    } finally {
        isLoading.value = false
    }
}
</script>

<template>
    <div class="flex items-center justify-center min-h-screen bg-slate-50 p-4">
        <div
            class="bg-white w-full max-w-[400px] rounded-[2.5rem] shadow-2xl shadow-slate-200/50 overflow-hidden border border-slate-100 transition-all">

            <div class="bg-slate-900 p-10 text-center relative overflow-hidden">
                <div class="absolute top-0 left-0 w-32 h-32 bg-blue-600/20 rounded-full -ml-16 -mt-16 blur-3xl"></div>
                <h2 class="text-3xl font-black text-white uppercase tracking-tighter italic">Авторизация</h2>
                <p class="text-slate-500 text-[10px] mt-2 uppercase tracking-[0.2em] font-bold px-4">
                    Доступ к архиву аудиозаписей
                </p>
            </div>

            <div class="p-10 space-y-6">
                <Message v-if="error" severity="error" variant="simple" class="!text-[11px] font-bold">
                    {{ error }}
                </Message>

                <div class="space-y-5">
                    <div class="flex flex-col gap-1.5">
                        <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">
                            Имя пользователя / Табельный №
                        </label>
                        <div class="relative flex items-center">
                            <i class="pi pi-user absolute left-4 text-slate-400 z-10"></i>
                            <InputText v-model="username" placeholder="Введите логин" @keyup.enter="login"
                                class="w-full !pl-11 !py-4 !rounded-2xl !bg-slate-50 !border-transparent focus:!border-blue-500 transition-all !font-bold" />
                        </div>
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">
                            Пароль доступа
                        </label>
                        <Password v-model="password" placeholder="••••••••" :feedback="false" toggleMask
                            @keyup.enter="login" class="w-full"
                            inputClass="w-full !py-4 !pl-5 !rounded-2xl !bg-slate-50 !border-transparent focus:!border-blue-500 transition-all !font-bold" />
                    </div>
                </div>

                <div class="pt-2">
                    <Button @click="login" :loading="isLoading" label="Войти в систему" icon="pi pi-sign-in"
                        class="w-full !py-5 !rounded-2xl !bg-slate-900 hover:!bg-blue-600 !border-none !text-[12px] !font-black !uppercase !tracking-widest !shadow-xl" />
                </div>

                <div class="flex flex-col space-y-3 items-center">
                    <p class="text-[11px] text-slate-400 font-bold uppercase tracking-tight text-center">
                        Новый сотрудник?
                        <br>
                        <span @click="emit('go-to-register')"
                            class="text-blue-600 hover:text-blue-700 cursor-pointer transition-colors underline decoration-2 underline-offset-4">
                            Зарегистрироваться
                        </span>
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.bg-white {
    animation: slideIn 0.7s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: scale(0.95) translateY(10px);
    }

    to {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
</style>