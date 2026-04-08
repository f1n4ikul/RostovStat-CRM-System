<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

// PrimeVue компоненты
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Toast from 'primevue/toast'
import { useToast } from "primevue/usetoast"

// Ваши компоненты
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import UploadModal from './components/UploadModal.vue'

const router = useRouter()
const toast = useToast()

// Состояние авторизации
const userProfile = ref(null)
const isAuthenticated = ref(false)
const isAuthMode = ref('login')
const showUploadModal = ref(false)

// Права доступа
const isSystemAdmin = computed(() => {
  return (
    userProfile.value?.role_code === 'admin' ||
    userProfile.value?.is_staff === true ||
    userProfile.value?.is_superuser === true
  );
});

const canUpload = computed(() => {
  return userProfile.value?.permissions?.can_upload === true || userProfile.value?.role_code === 'admin';
});

// Загрузка профиля
const fetchUserProfile = async () => {
  const token = localStorage.getItem('user-token')
  if (!token) return
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/profile/')
    userProfile.value = response.data
  } catch (error) {
    if (error.response?.status === 401) handleGlobalLogout()
  }
}

// Инициализация при загрузке
onMounted(async () => {
  const token = localStorage.getItem('user-token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    isAuthenticated.value = true
    await fetchUserProfile()
  }
})

// Обработка входа
const handleAuthSuccess = async () => {
  isAuthenticated.value = true
  await fetchUserProfile()

  toast.add({
    severity: 'success',
    summary: 'Успех',
    detail: `Добро пожаловать, ${userProfile.value?.username}`,
    life: 3000
  });

  router.push('/') // После входа всегда на главную
}

// Выход
const handleGlobalLogout = () => {
  localStorage.removeItem('user-token')
  localStorage.removeItem('user-info')
  isAuthenticated.value = false
  userProfile.value = null
  delete axios.defaults.headers.common['Authorization']
  router.push('/')
}

// Навигация в админку (если используешь currentPage для админки, иначе лучше через роуты)
const goToAdmin = () => {
  // Если админка — это отдельная страница, используй router.push('/admin')
  // Если админка — это переключатель внутри Library, передавай это через пропсы
}
</script>

<template>
  <Toast />

  <div v-if="!isAuthenticated">
    <Login v-if="isAuthMode === 'login'" @login-success="handleAuthSuccess" @go-to-register="isAuthMode = 'register'" />
    <Register v-else @register-success="handleAuthSuccess" @go-to-login="isAuthMode = 'login'" />
  </div>

  <div v-else class="min-h-screen bg-[#f8fafc] pb-24">

    <nav class="sticky top-0 z-40 bg-white/80 backdrop-blur-md border-b border-slate-200 px-6 py-4">
      <div class="max-w-[1400px] mx-auto flex justify-between items-center">

        <div class="flex items-center gap-8">
          <h1
            class="text-xl font-black text-slate-900 tracking-tighter uppercase flex items-center gap-2 cursor-pointer"
            @click="router.push('/')">
            <i class="pi pi-bolt text-blue-600 text-2xl"></i>
            Media<span class="text-blue-600 font-light text-sm tracking-widest ml-1">Archive</span>
          </h1>

          <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
            <Button v-if="canUpload" label="Загрузить" icon="pi pi-plus" size="small" @click="showUploadModal = true"
              class="!rounded-lg !bg-blue-600 !border-none" />

            <Button v-if="isSystemAdmin" label="Админ-панель" icon="pi pi-shield" size="small" severity="warn" text
              @click="router.push('/admin')" />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="hidden sm:flex flex-col items-end border-r pr-4 border-slate-200">
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">
              {{ userProfile?.department }}
            </span>
            <span class="text-[11px] font-bold text-slate-700 italic">
              {{ userProfile?.role }}
            </span>
          </div>

          <Avatar icon="pi pi-user" class="cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all shadow-sm"
            shape="circle" size="large" @click="router.push('/profile')" />

          <Button icon="pi pi-power-off" severity="danger" text rounded @click="handleGlobalLogout" />
        </div>
      </div>
    </nav>

    <main class="max-w-[1400px] mx-auto p-6">
      <router-view :user="userProfile" :is-admin="isSystemAdmin" />
    </main>

    <UploadModal v-if="showUploadModal" @close="showUploadModal = false" @uploaded="onResourceUploaded" />
  </div>
</template>

<style>
/* Глобальные стили анимации переходов, если нужно */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>