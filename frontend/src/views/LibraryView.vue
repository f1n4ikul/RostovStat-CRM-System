<script>

import { ref } from 'vue'
const cachedTracks = ref([]) 
</script>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from "primevue/usetoast"


// PrimeVue компоненты
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import SelectButton from 'primevue/selectbutton'
import Card from 'primevue/card'
import Tag from 'primevue/tag'

// Твои компоненты
import AudioDetailModal from '../components/AudioDetailModal.vue'
import AdminPanel from '../components/AdminPanel.vue'

const toast = useToast()

const props = defineProps({
    user: Object,
    isAdmin: Boolean
})



// Состояние
const tracks = ref(cachedTracks.value)

const searchQuery = ref('')
const selectedCategory = ref('all')
const currentView = ref('all')
const selectedTrack = ref(null)
const isDetailModalOpen = ref(false)

// Опции для табов (SelectButton)
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

// Загрузка данных
const fetchTracks = async () => {
    const token = localStorage.getItem('user-token')
    
    if (!token) return
    try {
        const url = currentView.value === 'favorites'
            ? 'http://127.0.0.1:8000/api/favorites/'
            : 'http://127.0.0.1:8000/api/records/'

        const response = await axios.get(url)
        const data = Array.isArray(response.data) ? response.data : []
        
        

        tracks.value = data
        cachedTracks.value = data
        // Защита: если пришел не массив, делаем массивом
        tracks.value = Array.isArray(response.data) ? response.data : []
    } catch (error) {
        console.error("Ошибка загрузки:", error)
        tracks.value = []
    }
}

// Фильтрация (с защитой от undefined)
const filteredTracks = computed(() => {
    const list = tracks.value || []
    return list.filter(track => {
        const title = track.title || ''
        const matchesSearch = title.toLowerCase().includes(searchQuery.value.toLowerCase())
        const matchesCategory = selectedCategory.value === 'all' || track.category === selectedCategory.value
        return matchesSearch && matchesCategory
    })
})

const openTrackDetails = (track) => {
    selectedTrack.value = track
    isDetailModalOpen.value = true
}

const handleExternalUpload = () => {
    fetchTracks(); // Перезагружаем список
};

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

onMounted(() => {
    fetchTracks();
    // Слушаем событие "обновить-данные"
    window.addEventListener('track-uploaded', handleExternalUpload);
});

onUnmounted(() => {
    // Убираем слушатель, чтобы не было утечек памяти
    window.removeEventListener('track-uploaded', handleExternalUpload);
});

watch(currentView, () => fetchTracks())
</script>

<template>
    <div class="animate-in fade-in duration-500">
        <div class="flex flex-col items-center gap-6 mb-10">

            <SelectButton v-model="currentView" :options="viewOptions" optionLabel="label" optionValue="value"
                class="custom-tabs">
                <template #option="slotProps">
                    <div class="flex items-center gap-2 px-2">
                        <i :class="slotProps.option.icon"></i>
                        <span>{{ slotProps.option.label }}</span>
                    </div>
                </template>
            </SelectButton>

            <div class="w-full max-w-2xl relative group">
                <i class="pi pi-search absolute left-5 top-1/2 -translate-y-1/2 text-slate-400"></i>
                <InputText v-model="searchQuery" placeholder="Поиск по архиву записей..."
                    class="!w-full !pl-14 !py-4 !rounded-2xl !border-none !shadow-sm focus:!shadow-xl transition-all" />
            </div>

            <div class="flex flex-wrap justify-center gap-2">
                <Button v-for="cat in categories" :key="cat.id" :label="cat.name"
                    :severity="selectedCategory === cat.id ? 'info' : 'secondary'"
                    :outlined="selectedCategory !== cat.id" @click="selectedCategory = cat.id"
                    class="!rounded-full !text-xs !font-bold !px-5" />
            </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            <div v-for="track in filteredTracks" :key="track.id" @click="openTrackDetails(track)"
                class="group relative">
                <Card
                    class="!rounded-[2rem] !border-none !shadow-sm hover:!shadow-2xl hover:!-translate-y-2 transition-all cursor-pointer overflow-hidden !bg-white">
                    <template #header>
                        <div class="h-40 bg-slate-100 flex items-center justify-center relative overflow-hidden">
                            <i
                                :class="[track.is_private ? 'pi pi-lock text-amber-500' : 'pi pi-volume-up text-blue-500/40', 'text-4xl']"></i>

                            <Button :icon="track.is_favorite ? 'pi pi-heart-fill' : 'pi pi-heart'" rounded
                                @click.stop="toggleLike(track)" class="favorite-button"
                                :class="{ 'is-active': track.is_favorite }" />
                        </div>
                    </template>
                    <template #title>
                        <div class="pt-2 text-sm font-black text-slate-800 line-clamp-1 px-1">{{ track.title }}</div>
                    </template>
                    <template #subtitle>
                        <p class="text-[11px] font-medium text-slate-400 line-clamp-2 px-1">
                            {{ track.description || 'Описание отсутствует' }}
                        </p>
                    </template>
                </Card>
            </div>
        </div>

        <div v-if="filteredTracks.length === 0" class="flex flex-col items-center justify-center py-24 text-slate-300">
            <i class="pi pi-cloud-download text-6xl mb-4 opacity-20"></i>
            <p class="text-xl font-bold">Ничего не найдено</p>
        </div>

        <AudioDetailModal v-if="selectedTrack" :track="selectedTrack" :is-open="isDetailModalOpen" :is-admin="isAdmin"
            @close="isDetailModalOpen = false" @refresh="fetchTracks" />
    </div>
</template>

<style scoped>
/* Кнопка лайка */
.favorite-button {
    position: absolute !important;
    top: 1rem;
    right: 1rem;
    opacity: 0;
    transition: all 0.3s ease;
    z-index: 10;
}

.group:hover .favorite-button,
.favorite-button.is-active {
    opacity: 1;
}

.favorite-button.is-active {
    color: #ef4444 !important;
    background: #fef2f2 !important;
}

/* Стили табов ( SelectButton ) */
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
}

:deep(.custom-tabs .p-highlight) {
    background: white !important;
    color: #2563eb !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05) !important;
}
</style>