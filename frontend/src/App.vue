<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter, useRoute } from 'vue-router'

// PrimeVue компоненты
import Button from 'primevue/button'
import Avatar from 'primevue/avatar'
import Toast from 'primevue/toast'
import { useToast } from "primevue/usetoast"

// Ваши компоненты
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import UploadModal from './components/UploadModal.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()

// Состояние авторизации
const userProfile = ref(null)
const isAuthenticated = ref(false)
const isResolvingAuth = ref(true)
const isAuthMode = ref('login')
const showUploadModal = ref(false)

// UX состояние: открыто ли мобильное меню
const isMobileMenuOpen = ref(false)

// Закрываем меню при смене маршрута
watch(() => route.path, () => {
  isMobileMenuOpen.value = false
})

// Права доступа
const isSystemAdmin = computed(() => {
  return (
    userProfile.value?.role_code === 'admin' ||
    userProfile.value?.is_staff === true ||
    userProfile.value?.is_superuser === true
  );
});

const showAdminButton = computed(() => {
  return isSystemAdmin.value && route.path !== '/admin';
});

const canUpload = computed(() => {
  return userProfile.value?.permissions?.can_upload === true || userProfile.value?.role_code === 'admin';
});

// Загрузка профиля
const fetchUserProfile = async () => {
  const token = localStorage.getItem('user-token')
  if (!token) {
    isResolvingAuth.value = false
    return
  }
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/profile/')
    userProfile.value = response.data
    isAuthenticated.value = true
  } catch (error) {
    console.error("Ошибка авторизации:", error)
    handleGlobalLogout()
  } finally {
    isResolvingAuth.value = false
  }
}

// Инициализация при загрузке страницы
onMounted(async () => {
  const token = localStorage.getItem('user-token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    await fetchUserProfile()
  } else {
    isResolvingAuth.value = false
  }
})

const onResourceUploaded = () => {
  showUploadModal.value = false
  window.dispatchEvent(new Event('track-uploaded'));

  toast.add({
    severity: 'success',
    summary: 'Загружено',
    detail: 'Файл успешно добавлен в систему',
    life: 3000
  });
}

// Обработка успешного входа
const handleAuthSuccess = async () => {
  isResolvingAuth.value = true
  const token = localStorage.getItem('user-token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
  }

  await fetchUserProfile()

  toast.add({
    severity: 'success',
    summary: 'Успех',
    detail: `Добро пожаловать, ${userProfile.value?.username || ''}`,
    life: 3000
  });

  router.push('/library')
}

// Глобальный выход
const handleGlobalLogout = () => {
  localStorage.removeItem('user-token')
  localStorage.removeItem('user-info')
  isAuthenticated.value = false
  userProfile.value = null
  delete axios.defaults.headers.common['Authorization']
  isResolvingAuth.value = false
  isMobileMenuOpen.value = false
  router.push('/')
}
</script>

<template>
  <Toast />

  <div v-if="isResolvingAuth" class="min-h-screen flex flex-col items-center justify-center bg-[#f8fafc]">
    <i class="pi pi-spin pi-spinner text-4xl text-blue-600 mb-4"></i>
    <p class="text-slate-500 font-medium text-sm animate-pulse">Загрузка профиля RostovStat...</p>
  </div>

  <div v-else-if="!isAuthenticated">
    <Login v-if="isAuthMode === 'login'" @login-success="handleAuthSuccess" @go-to-register="isAuthMode = 'register'" />
    <Register v-else @register-success="handleAuthSuccess" @go-to-login="isAuthMode = 'login'" />
  </div>

  <div v-else class="min-h-screen bg-[#f8fafc] flex flex-col w-full overflow-x-hidden">

    <nav
      class="sticky top-0 z-50 bg-white/90 backdrop-blur-md border-b border-slate-200 px-4 md:px-6 py-3.5 md:py-4 transition-all w-full shrink-0">
      <div class="max-w-[1400px] mx-auto flex justify-between items-center w-full">

        <div class="flex items-center gap-4 lg:gap-8 min-w-0">
          <h1
            class="text-lg md:text-xl font-black text-slate-900 tracking-tighter uppercase flex items-center gap-2 cursor-pointer shrink-0 select-none"
            @click="router.push('/library')">
            <i class="pi pi-chart-bar text-blue-600 text-xl md:text-2xl"></i>
            <span>Rostov<span class="text-blue-600 font-light text-xs md:text-sm tracking-widest ml-1">Stat
                </span></span>
          </h1>

          <div class="hidden md:flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
            <Button label="Лента" icon="pi pi-home" text size="small" @click="router.push('/')"
              :class="['!text-xs !font-semibold', route.path === '/' ? '!bg-white !shadow-sm !text-blue-600' : '!text-slate-600']" />

            <Button label="Медиатека" icon="pi pi-images" text size="small" @click="router.push('/library')"
              :class="['!text-xs !font-semibold', route.path === '/library' || route.path.startsWith('/library/') ? '!bg-white !shadow-sm !text-blue-600' : '!text-slate-600']" />

            <Button v-if="canUpload" label="Загрузить" icon="pi pi-plus" size="small" @click="showUploadModal = true"
              class="!rounded-lg !bg-blue-600 !border-none !text-xs !font-semibold" />

            <Button v-if="showAdminButton" label="Админ-панель" icon="pi pi-shield" size="small" severity="warn" text
              class="!text-xs !font-semibold" @click="router.push('/admin')" />
          </div>
        </div>

        <div class="flex items-center gap-2 md:gap-4 shrink-0">

          <div class="hidden sm:flex flex-col items-end border-r pr-4 border-slate-200">
            <span class="text-[9px] font-black text-slate-400 uppercase tracking-widest truncate max-w-[180px]">
              {{ userProfile?.department || 'Общий отдел' }}
            </span>
            <span class="text-[11px] font-bold text-slate-600 italic truncate max-w-[150px]">
              {{ userProfile?.role || 'Пользователь' }}
            </span>
          </div>

          <Avatar icon="pi pi-user"
            class="hidden sm:inline-flex cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all shadow-sm !bg-slate-100 !text-slate-600"
            shape="circle" size="large" @click="router.push('/profile')" />

          <Button icon="pi pi-power-off" severity="danger" text rounded class="hidden sm:inline-flex"
            @click="handleGlobalLogout" />

          <button @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="md:hidden w-10 h-10 flex items-center justify-center rounded-xl bg-slate-50 border border-slate-200/70 text-slate-700 active:bg-slate-100 transition-all"
            aria-label="Навигация">
            <i
              :class="['pi text-base transition-transform duration-200', isMobileMenuOpen ? 'pi-times rotate-90 text-blue-600' : 'pi-bars']"></i>
          </button>

        </div>
      </div>

      <div v-if="isMobileMenuOpen"
        class="block md:hidden absolute top-[61px] left-0 right-0 w-full bg-white border-b border-slate-200 shadow-xl animate-dropdown">
        <div class="p-4 flex flex-col gap-2 bg-white">

          <div class="text-[10px] font-bold uppercase tracking-wider text-slate-400 px-2 mb-1">Навигация по CRM</div>

          <button @click="router.push('/'); isMobileMenuOpen = false"
            :class="['w-full flex items-center gap-3 p-3 rounded-xl text-sm font-semibold transition-colors text-left', route.path === '/' ? 'bg-blue-50 text-blue-600' : 'text-slate-600 active:bg-slate-50']">
            <i class="pi pi-home text-sm"></i>
            <span>Лента обновлений</span>
          </button>

          <button @click="router.push('/library'); isMobileMenuOpen = false"
            :class="['w-full flex items-center gap-3 p-3 rounded-xl text-sm font-semibold transition-colors text-left', route.path.startsWith('/library') ? 'bg-blue-50 text-blue-600' : 'text-slate-600 active:bg-slate-50']">
            <i class="pi pi-images text-sm"></i>
            <span>Медиатека записей</span>
          </button>

          <button v-if="canUpload" @click="showUploadModal = true; isMobileMenuOpen = false"
            class="w-full flex items-center gap-3 p-3 rounded-xl text-sm font-semibold bg-blue-600 text-white shadow-md active:bg-blue-700 text-left">
            <i class="pi pi-plus text-sm"></i>
            <span>Загрузить новый файл</span>
          </button>

          <button v-if="showAdminButton" @click="router.push('/admin'); isMobileMenuOpen = false"
            class="w-full flex items-center gap-3 p-3 rounded-xl text-sm font-semibold bg-amber-500 text-white active:bg-amber-600 text-left">
            <i class="pi pi-shield text-sm"></i>
            <span>Админ-панель контроля</span>
          </button>

          <div class="mt-2 pt-3 border-t border-slate-100 flex items-center justify-between px-2">
            <div class="flex flex-col min-w-0" @click="router.push('/profile'); isMobileMenuOpen = false">
              <span class="text-[11px] font-bold text-slate-800 truncate">{{ userProfile?.username || 'Профиль'
                }}</span>
              <span class="text-[9px] font-medium text-slate-400 uppercase tracking-wide truncate mt-0.5">{{
                userProfile?.department || 'Общий отдел' }}</span>
            </div>

            <button @click="handleGlobalLogout"
              class="h-9 px-3 text-xs font-semibold text-red-600 bg-red-50 rounded-xl flex items-center gap-1.5 active:bg-red-100 transition-colors">
              <i class="pi pi-power-off text-xs"></i>
              <span>Выйти</span>
            </button>
          </div>

        </div>
      </div>
    </nav>

    <main class="w-full max-w-[1400px] mx-auto p-4 md:p-6 flex-1 box-border flex flex-col justify-start">
      <router-view :user="userProfile" :is-admin="isSystemAdmin" />
    </main>

    <UploadModal v-if="showUploadModal" @close="showUploadModal = false" @uploaded="onResourceUploaded" />
  </div>
</template>

<style>
/* Сбросы и базовые анимации */
html,
body {
  margin: 0;
  padding: 0;
  width: 100%;
  overflow-x: hidden;
  background-color: #f8fafc;
}

*,
::before,
::after {
  box-sizing: border-box;
}

/* Анимация раскрытия мобильного меню */
@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-dropdown {
  animation: dropdownSlide 0.22s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>