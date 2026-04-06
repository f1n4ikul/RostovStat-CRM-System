<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'
import { useRouter } from 'vue-router'

// PrimeVue компоненты
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import SelectButton from 'primevue/selectbutton'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import Avatar from 'primevue/avatar'
import Badge from 'primevue/badge'
import { useToast } from "primevue/usetoast"

// Ваши компоненты
import Login from './components/Login.vue'
import Register from './components/Register.vue'
import UploadModal from './components/UploadModal.vue'
import Profile from './components/Profile.vue'
import AudioDetailModal from './components/AudioDetailModal.vue'
import AdminPanel from './components/AdminPanel.vue'

const router = useRouter()
const toast = useToast()

// Состояние
const tracks = ref([])
const searchQuery = ref('')
const selectedCategory = ref('all')
const currentView = ref('all')
const userProfile = ref(null)
const isAuthenticated = ref(false)
const isAuthMode = ref('login')
const showUploadModal = ref(false)
const showProfile = ref(false)
const currentPage = ref('library')

// Опции для вкладок
const viewOptions = [
  { label: 'Вся библиотека', value: 'all', icon: 'pi pi-database' },
  { label: 'Избранное', value: 'favorites', icon: 'pi pi-heart-fill' }
]

const categories = [
  { id: 'all', name: 'Все' },
  { id: 'concentration', name: 'Концентрация' },
  { id: 'pro', name: 'Проф. контент' },
  { id: 'meeting', name: 'Совещание' },
]

const isSystemAdmin = computed(() => {
  // Проверяем все возможные варианты, которые может прислать бэкенд
  return (
    userProfile.value?.role_code === 'admin' ||
    userProfile.value?.is_staff === true ||
    userProfile.value?.is_superuser === true ||
    userProfile.value?.permissions?.is_admin === true
  );
});

const canUpload = computed(() => {
  // Разрешаем загрузку админам или тем, у кого есть явное право
  return (
    userProfile.value?.permissions?.can_upload === true ||
    userProfile.value?.role_code === 'admin'
  );
});

const selectedTrack = ref(null)
const isDetailModalOpen = ref(false)

const fetchUserProfile = async () => {
  const token = localStorage.getItem('user-token')
  if (!token) return
  try {
    const response = await axios.get('http://127.0.0.1:8000/api/profile/')
    userProfile.value = response.data
    console.log("Мой профиль:", response.data)
  } catch (error) {
    if (error.response?.status === 401) handleGlobalLogout()
  }
}

const fetchTracks = async () => {
  const token = localStorage.getItem('user-token')
  if (!token) return
  try {
    const url = currentView.value === 'favorites'
      ? 'http://127.0.0.1:8000/api/favorites/'
      : 'http://127.0.0.1:8000/api/records/'
    const response = await axios.get(url)
    tracks.value = response.data
    if (selectedTrack.value) {
      const updated = tracks.value.find(t => t.id === selectedTrack.value.id);
      if (updated) {
        selectedTrack.value = updated;
      }
    }
  } catch (error) {
    console.error("Ошибка загрузки:", error)
  }
}

const handleDeleteTrack = async (deletedTrackId) => {

  console.log("Сигнал об удалении получен для ID:", deletedTrackId);

  // 1. Мгновенно убираем трек из локального списка (интерфейс обновится сразу)

  tracks.value = tracks.value.filter(t => t.id !== deletedTrackId);

  // 2. Закрываем модальное окно

  isDetailModalOpen.value = false;
  selectedTrack.value = null;

  // 3. На всякий случай обновляем данные с сервера
  await fetchTracks();

};

onMounted(async () => {
  const token = localStorage.getItem('user-token')
  if (token) {
    axios.defaults.headers.common['Authorization'] = `Token ${token}`
    isAuthenticated.value = true
    await fetchUserProfile()
    if (userProfile.value) {
      const storageData = {
        ...userProfile.value,
        is_staff: userProfile.value.role_code === 'admin' || userProfile.value.permissions?.is_admin
      }
      localStorage.setItem('user-info', JSON.stringify(storageData))
    }
    await fetchTracks()
  }
})

watch(currentView, () => fetchTracks())

const handleAuthSuccess = async () => {
  isAuthenticated.value = true
  await fetchUserProfile()

  if (userProfile.value) {
    const storageData = {
      ...userProfile.value,
      // Добавляем флаг is_staff для совместимости с проверкой в AdminPanel
      is_staff: userProfile.value.role_code === 'admin' || userProfile.value.permissions?.is_admin
    }
    localStorage.setItem('user-info', JSON.stringify(storageData))
  }
  fetchTracks()
  toast.add({ severity: 'success', summary: 'Успех', detail: `Добро пожаловать, ${userProfile.value.username}`, life: 3000 });
  
  // Маленькое уведомление в углу
  const Toast = Swal.mixin({

    toast: true,

    position: 'top-end',

    showConfirmButton: false,

    timer: 3000,

    timerProgressBar: true,
  })
  Toast.fire({

    icon: 'success',

    title: `Добро пожаловать, ${userProfile.value.username}!`

  })
}

const handleGlobalLogout = () => {
  localStorage.removeItem('user-token')
  localStorage.removeItem('user-info')
  isAuthenticated.value = false
  userProfile.value = null
  currentPage.value = 'library'
  delete axios.defaults.headers.common['Authorization']
  if (router) router.push('/')
}

const toggleLike = async (track) => {
  try {
    const response = await axios.post(`http://127.0.0.1:8000/api/tracks/${track.id}/toggle-favorite/`)
    track.is_favorite = response.data.is_favorite
    if (currentView.value === 'favorites' && !track.is_favorite) {
      tracks.value = tracks.value.filter(t => t.id !== track.id)
    }
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Не удалось обновить статус', life: 2000 });
  }
}

// Логика редактирования (пока заглушка или вызов формы)

const handleEditTrack = () => {

  alert('Функция редактирования в разработке (здесь можно открыть форму изменения названия/категории)')

}

const openTrackDetails = (track) => {
  selectedTrack.value = track
  isDetailModalOpen.value = true
}

const filteredTracks = computed(() => {
  return tracks.value.filter(track => {
    const title = track.title || ''
    const matchesSearch = title.toLowerCase().includes(searchQuery.value.toLowerCase())
    const matchesCategory = selectedCategory.value === 'all' || track.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})
</script>

<template>
  <span class="text-[10px] text-red-500">Admin: {{ isSystemAdmin }}</span>
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
            @click="currentPage = 'library'">
            <i class="pi pi-bolt text-blue-600 text-2xl"></i>
            Media<span class="text-blue-600 font-light text-sm tracking-widest ml-1">Archive</span>
          </h1>

          <div class="items-center gap-2 bg-slate-100 p-1 rounded-xl">
            <Button v-if="canUpload" label="Загрузить" icon="pi pi-plus" size="small" @click="showUploadModal = true"
              class="!rounded-lg !bg-blue-600 !border-none" />
            <Button v-if="isSystemAdmin" :label="currentPage === 'admin-panel' ? 'В библиотеку' : 'Админ-панель'"
              :icon="currentPage === 'admin-panel' ? 'pi pi-home' : 'pi pi-shield'" size="small"
              :severity="currentPage === 'admin-panel' ? 'info' : 'warn'" :text="currentPage !== 'admin-panel'"
              @click="currentPage = (currentPage === 'admin-panel' ? 'library' : 'admin-panel')" />
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="hidden sm:flex flex-col items-end border-r pr-4 border-slate-200">
            <span class="text-[10px] font-black text-slate-400 uppercase tracking-widest">{{ userProfile?.department
              }}</span>
            <span class="text-[11px] font-bold text-slate-700 italic">{{ userProfile?.role }}</span>
          </div>

          <Avatar icon="pi pi-user" class="cursor-pointer hover:ring-2 hover:ring-blue-500 transition-all"
            shape="circle" size="large" @click="showProfile = true" />
          <Button icon="pi pi-power-off" severity="danger" text rounded @click="handleGlobalLogout" />
        </div>
      </div>
    </nav>

    <div class="max-w-[1400px] mx-auto p-6 mt-4">
      <div v-if="currentPage === 'admin-panel' && isSystemAdmin">
        <AdminPanel />
      </div>

      <div v-else>
        <div class="flex flex-col items-center gap-6 mb-10">
          <SelectButton v-model="currentView" :options="viewOptions" optionValue="value" dataKey="value"
            class="custom-tabs">
            <template #option="slotProps">
              <div class="flex items-center gap-2">
                <i :class="slotProps.option.icon"></i>
                <span>{{ slotProps.option.label }}</span>
              </div>
            </template>
          </SelectButton>

          <div class="w-full max-w-2xl relative group">
            <i
              class="pi pi-search absolute left-5 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-blue-500 transition-colors"></i>
            <InputText v-model="searchQuery" placeholder="Поиск по архиву записей..."
              class="!w-full !pl-14 !py-4 !rounded-2xl !bg-white !border-none !shadow-sm !text-lg focus:!shadow-xl transition-all" />
          </div>

          <div class="flex flex-wrap justify-center gap-2">
            <Button v-for="cat in categories" :key="cat.id" :label="cat.name"
              :severity="selectedCategory === cat.id ? 'info' : 'secondary'" :outlined="selectedCategory !== cat.id"
              @click="selectedCategory = cat.id" class="!rounded-full !text-xs !font-bold !px-5" />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          <div v-for="track in filteredTracks" :key="track.id" @click="openTrackDetails(track)" class="group relative">
            <Card
              class="!rounded-[2rem] !border-none !shadow-sm hover:!shadow-2xl hover:!-translate-y-2 transition-all duration-300 cursor-pointer !overflow-hidden !bg-white">
              <template #header>
                <div class="h-40 bg-slate-100 flex items-center justify-center relative overflow-hidden group/header">

                  <div
                    class="absolute inset-0 bg-gradient-to-br from-blue-600/5 to-indigo-600/10 group-hover/header:scale-110 transition-transform duration-500">
                  </div>

                  <div class="relative z-10 flex flex-col items-center gap-2">
                    <i :class="[
                      track.is_private ? 'pi pi-lock text-amber-500' : 'pi pi-volume-up text-blue-500/40',
                      'text-4xl transition-all duration-300 group-hover:scale-110 group-hover:text-blue-600'
                    ]"></i>
                  </div>

                  <Button :icon="track.is_favorite ? 'pi pi-heart-fill' : 'pi pi-heart'" rounded
                    @click.stop="toggleLike(track)" class="favorite-button"
                    :class="{ 'is-active': track.is_favorite }" />

                  <div v-if="track.is_private" class="absolute top-4 left-4 z-10">
                    <Tag value="PRIVATE" severity="warn" class="!text-[8px] !font-black !px-2 !bg-amber-400/90" />
                  </div>
                </div>
              </template>

              <template #title>
                <div class="pt-2">
                  <span
                    class="text-sm font-black text-slate-800 line-clamp-1 leading-tight group-hover:text-blue-600 transition-colors">
                    {{ track.title }}
                  </span>
                </div>
              </template>

              <template #subtitle>
                <p class="text-[11px] font-medium text-slate-400 line-clamp-2 mt-1 min-h-[2rem]">
                  {{ track.description || 'Описание отсутствует' }}
                </p>
              </template>

              <template #footer>
                <div class="flex justify-between items-center border-t border-slate-50 pt-4 mt-2">
                  <div class="flex items-center gap-1.5">
                    <i class="pi pi-calendar text-[10px] text-slate-300"></i>
                    <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tight">
                      {{ new Date(track.created_at).toLocaleDateString() }}
                    </span>
                  </div>

                  <div class="flex items-center gap-2">
                    <div class="flex items-center gap-1 bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full">
                      <i class="pi pi-comments text-[9px]"></i>
                      <span class="text-[9px] font-black">{{ track.comments?.length || 0 }}</span>
                    </div>
                  </div>
                </div>
              </template>
            </Card>
          </div>
        </div>

        <div v-if="filteredTracks.length === 0" class="flex flex-col items-center justify-center py-24 text-slate-300">
          <i class="pi pi-cloud-download text-6xl mb-4 opacity-20"></i>
          <p class="text-xl font-bold tracking-tight">Ничего не найдено</p>
        </div>
      </div>
    </div>

    <UploadModal v-if="showUploadModal" @close="showUploadModal = false" @uploaded="fetchTracks" />
    <Profile v-if="showProfile" @close="showProfile = false" @logout="handleGlobalLogout" />
    <AudioDetailModal v-if="selectedTrack" :track="selectedTrack" :is-open="isDetailModalOpen" :is-admin="isSystemAdmin"
      @close="isDetailModalOpen = false" @refresh="fetchTracks" @track-deleted="handleTrackDeleted" />
  </div>
</template>

<style scoped>
:deep(.p-card-header) {
  position: relative !important;
}

.favorite-button {
  position: absolute !important;
  top: 1rem !important;
  right: 1rem !important;
  z-index: 30 !important;
  width: 2.5rem !important;
  height: 2.5rem !important;
  background: rgba(255, 255, 255, 0.6) !important;
  backdrop-filter: blur(4px) !important;
  border: none !important;
  color: #94a3b8 !important;
  /* slate-400 */
  transition: all 0.3s ease !important;
  opacity: 0;
  /* Скрыта по умолчанию */
}

/* Показываем кнопку при наведении на всю карточку */
.group:hover .favorite-button {
  opacity: 1;
}

/* Стили для уже лайкнутой кнопки */
.favorite-button.is-active {
  opacity: 1 !important;
  background: #fef2f2 !important;
  /* red-50 */
  color: #ef4444 !important;
  /* red-500 */
}

.favorite-button:hover {
  transform: scale(1.1);
  background: white !important;
  color: #ef4444 !important;
}

:deep(.custom-tabs) {
  background: #f1f5f9;
  padding: 4px;
  border-radius: 1rem;
  border: none;
}

:deep(.custom-tabs .p-button) {
  border: none;
  border-radius: 0.75rem;
  background: transparent;
  color: #64748b;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.5rem 1.5rem;
}

:deep(.custom-tabs .p-highlight) {
  background: white !important;
  color: #2563eb !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}

/* :deep(.p-card) {
  --p-card-body-padding: 1.25rem;
} */

</style>