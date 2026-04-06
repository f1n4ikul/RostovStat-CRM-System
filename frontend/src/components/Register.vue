<script setup>
import { ref } from 'vue'
import axios from 'axios'

// Компоненты PrimeVue
import InputText from 'primevue/inputtext'
import Password from 'primevue/password'
import Button from 'primevue/button'
import Message from 'primevue/message'

const employeeCode = ref('')
const email = ref('')
const password = ref('')
const role = ref('user') // По умолчанию 'user'
const errorMessage = ref('')
const isLoading = ref(false)

const emit = defineEmits(['register-success', 'go-to-login'])

const register = async () => {
    if (!employeeCode.value || !email.value || !password.value) {
        errorMessage.value = "Заполните все обязательные поля"
        return
    }

    isLoading.value = true
    errorMessage.value = ""

    try {
        const response = await axios.post('http://127.0.0.1:8000/api/register/', {
            employee_code: employeeCode.value,
            email: email.value,
            password: password.value,
            role: role.value
        })

        const token = response.data.token
        localStorage.setItem('user-token', token)
        axios.defaults.headers.common['Authorization'] = `Token ${token}`
        emit('register-success')
    } catch (error) {
        errorMessage.value = error.response?.data?.error || "Ошибка регистрации"
    } finally {
        isLoading.value = false
    }
}
</script>

<template>
    <div class="flex items-center justify-center min-h-screen bg-slate-50 p-4">
        <div class="bg-white w-full max-w-[420px] rounded-[2.5rem] shadow-2xl border border-slate-100 overflow-hidden">

            <div class="bg-slate-900 p-10 text-center relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 bg-blue-600/20 rounded-full -mr-16 -mt-16 blur-3xl"></div>
                <h2 class="text-3xl font-black text-white uppercase tracking-tighter italic">Регистрация</h2>
                <p class="text-slate-500 text-[10px] mt-2 uppercase tracking-[0.2em] font-bold">
                    Личный кабинет сотрудника Росстата
                </p>
            </div>

            <div class="p-10 space-y-6">
                <Message v-if="errorMessage" severity="error" variant="simple" class="!text-[11px] font-bold">
                    {{ errorMessage }}
                </Message>

                <div class="space-y-5">
                    <div class="flex flex-col gap-1.5">
                        <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">
                            Табельный номер
                        </label>
                        <div class="relative">
                            <i class="pi pi-id-card absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 z-10"></i>
                            <InputText v-model="employeeCode" placeholder="Например: 770123"
                                class="w-full !pl-11 !py-4 !rounded-2xl !bg-slate-50 !border-transparent focus:!border-blue-500 transition-all !font-bold" />
                        </div>
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">
                            Рабочий Email
                        </label>
                        <div class="relative">
                            <i class="pi pi-envelope absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 z-10"></i>
                            <InputText v-model="email" type="email" placeholder="name@rosstat.gov.ru"
                                class="w-full !pl-11 !py-4 !rounded-2xl !bg-slate-50 !border-transparent focus:!border-blue-500 transition-all !font-bold" />
                        </div>
                    </div>

                    <div class="flex flex-col gap-1.5">
                        <label class="text-[9px] font-black text-slate-400 uppercase tracking-widest ml-1">
                            Защитный пароль
                        </label>
                        <Password v-model="password" placeholder="••••••••" :feedback="true" toggleMask
                            promptLabel="Придумайте пароль" weakLabel="Слишком простой" mediumLabel="Средний"
                            strongLabel="Надежный" class="w-full"
                            inputClass="w-full !py-4 !pl-5 !rounded-2xl !bg-slate-50 !border-transparent focus:!border-blue-500 transition-all !font-bold" />
                    </div>
                </div>

                <div class="pt-2">
                    <Button @click="register" label="Создать аккаунт" :loading="isLoading"
                        class="w-full !py-5 !rounded-2xl !bg-slate-900 hover:!bg-blue-600 !border-none !text-[12px] !font-black !uppercase !tracking-widest !shadow-xl" />
                </div>

                <p class="text-center text-[11px] text-slate-400 font-bold uppercase tracking-tight">
                    Уже в системе?
                    <span @click="emit('go-to-login')"
                        class="text-blue-600 hover:text-blue-700 cursor-pointer transition-colors underline decoration-2 underline-offset-4 ml-1">
                        Авторизоваться
                    </span>
                </p>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Анимация появления */
.bg-white {
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Стилизация индикатора сложности пароля PrimeVue */
:deep(.p-password-overlay) {
    background: #ffffff;
    border-radius: 1rem;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
    padding: 1rem;
}

:deep(.p-password-meter) {
    height: 4px;
    border-radius: 2px;
}
</style>