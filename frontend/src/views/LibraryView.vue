<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from "primevue/usetoast"


import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import SelectButton from 'primevue/selectbutton'
import Card from 'primevue/card'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Avatar from 'primevue/avatar'

import AudioDetailModal from '../components/AudioDetailModal.vue'

const toast = useToast()
const props = defineProps({
    user: Object,
    isAdmin: Boolean
})


const tracks = ref([])
const loading = ref(false)
const searchQuery = ref('')
const selectedCategory = ref('all')
const selectedDept = ref('Все отделы')
const currentView = ref('all')
const displayMode = ref('grid') 

const selectedTrack = ref(null)
const isDetailModalOpen = ref(false)

const cache = {
    all: null,
    favorites: null
}


// Константы для CRM
const departments = ['Все отделы', 'Общий отдел', 'Аналитика', 'IT', 'Бухгалтерия', 'Руководство']
const viewOptions = [
    { label: 'Реестр', value: 'all', icon: 'pi pi-folder-open' },
    { label: 'Избранное', value: 'favorites', icon: 'pi pi-star' }
]
const categories = [
    { id: 'all', name: 'Все' },
    { id: 'concentration', name: 'Концентрация' },
    { id: 'pro', name: 'Проф. контент' },
    { id: 'meeting', name: 'Совещания' },
]

// Логика загрузки
const fetchTracks = async (forceRefresh = false) => {
    // 1. Проверка кеша
    if (!forceRefresh && cache[currentView.value]) {
        tracks.value = cache[currentView.value]
        return
    }

    loading.value = true
    try {
        const url = currentView.value === 'favorites'
            ? 'http://127.0.0.1:8000/api/favorites/'
            : 'http://127.0.0.1:8000/api/records/'

        const response = await axios.get(url)

        
        const incomingData = Array.isArray(response.data) ? response.data : []

        
        tracks.value = incomingData
        cache[currentView.value] = incomingData

    } catch (error) {
        console.error("Ошибка при загрузке:", error)
        toast.add({
            severity: 'error',
            summary: 'Ошибка сети',
            detail: 'Сервер РостовСтат недоступен или ошибка API',
            life: 3000
        })
    } finally {
        loading.value = false
    }
}

const handleGlobalUpload = () => {
    cache.all = null
    fetchTracks(true);
    toast.add({
        severity: 'success',
        summary: 'Обновление',
        detail: 'Список записей синхронизирован',
        life: 1000
    });
};

// CRM Фильтрация
const filteredTracks = computed(() => {
    const list = tracks.value;
    if (!list.length) return [];

    const query = searchQuery.value.trim().toLowerCase();
    const category = selectedCategory.value;
    const dept = selectedDept.value;

    const isAllDept = dept === 'Все отделы';
    const isAllCat = category === 'all';

    if (!query && isAllDept && isAllCat) return list;

   
    return list.filter(track => {
        const matchesSearch = !query || (track.title && track.title.toLowerCase().includes(query));
        const matchesCategory = isAllCat || track.category === category;
        const matchesDept = isAllDept || track.author_department === dept;
        return matchesSearch && matchesCategory && matchesDept;
    });
});

// Функции действий
const openTrackDetails = (track) => {
    selectedTrack.value = track
    isDetailModalOpen.value = true
}

const downloadFile = async (track) => {
    try {
        const response = await axios({
            url: `http://127.0.0.1:8000/api/records/${track.id}/download/`,
            method: 'GET',
            responseType: 'blob',
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${track.title}.mp3`)
        document.body.appendChild(link)
        link.click()
        toast.add({ severity: 'success', summary: 'Загрузка', detail: 'Файл подготовлен', life: 2000 })
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Файл не найден на сервере' })
    }
}

const toggleLike = async (track) => {
    try {
        const response = await axios.post(`http://127.0.0.1:8000/api/tracks/${track.id}/toggle-favorite/`)
        track.is_favorite = response.data.is_favorite
        if (currentView.value === 'favorites' && !track.is_favorite) {
            tracks.value = tracks.value.filter(t => t.id !== track.id)
        }
    } catch (e) {
        toast.add({ severity: 'warn', detail: 'Ошибка обновления статуса' })
    }
}

const handleTrackDeleted = () => {
    cache[currentView.value] = null
    fetchTracks(true);
    toast.add({
        severity: 'info',
        summary: 'Удаление',
        detail: 'Запись успешно удалена из системы',
        life: 3000
    });
};

watch(currentView, () => {
    searchQuery.value = ''
    selectedCategory.value = 'all'
    fetchTracks()
})

onMounted(() => {
    fetchTracks();
    
    window.addEventListener('track-uploaded', handleGlobalUpload);
});

onUnmounted(() => {
   
    window.removeEventListener('track-uploaded', handleGlobalUpload);
});

</script>

<template>
    <div class="crm-container p-2">
        <div class="bg-white rounded-3xl p-6 shadow-sm border border-slate-100 mb-8">
            <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-6">

                <div class="flex items-center gap-4">
                    <SelectButton v-model="currentView" :options="viewOptions" optionLabel="label" optionValue="value"
                        class="crm-tabs" />
                    <div class="h-8 w-[1px] bg-slate-200 mx-2 hidden sm:block"></div>
                    <div class="flex bg-slate-100 p-1 rounded-xl">
                        <Button icon="pi pi-th-large" @click="displayMode = 'grid'" :text="displayMode !== 'grid'"
                            class="!p-2" size="small" />
                        <Button icon="pi pi-list" @click="displayMode = 'table'" :text="displayMode !== 'table'"
                            class="!p-2" size="small" />
                    </div>
                </div>

                <div class="flex flex-col md:flex-row items-center gap-3 w-full lg:w-auto">
                    <div
                        class="relative flex items-center w-full lg:w-80 h-12 bg-white border border-slate-200 rounded-xl px-4 shadow-sm focus-within:border-blue-400 transition-all">
                        <i class="pi pi-search text-slate-400 mr-3 flex-shrink-0" />

                        <InputText v-model="searchQuery" placeholder="Поиск по реестру..."
                            class="w-full !border-none !p-0 !bg-transparent !ring-0 text-sm text-slate-700" />
                    </div>

                    <Dropdown v-model="selectedDept" :options="departments"
                        class="w-full md:w-56 !h-12 !rounded-xl !border-slate-200 shadow-sm flex items-center" />
                </div>
            </div>
            

            <div class="flex gap-2 mt-6 overflow-x-auto pb-2">
                <Button v-for="cat in categories" :key="cat.id" :label="cat.name"
                    :severity="selectedCategory === cat.id ? 'info' : 'secondary'" @click="selectedCategory = cat.id"
                    class="!rounded-full !text-[11px] !px-4" size="small" />
            </div>
        
        </div>

        <div v-if="loading" class="flex justify-center py-20">
            <i class="pi pi-spin pi-spinner text-4xl text-blue-500"></i>
        </div>

        <div v-else>
            <div v-show="displayMode === 'table'"
                class="bg-white rounded-3xl shadow-sm overflow-hidden border border-slate-100">
                <DataTable :value="filteredTracks" responsiveLayout="scroll" class="crm-table text-sm" hoverSelection
                    @row-click="(e) => openTrackDetails(e.data)">
                    <Column field="title" header="Документ" sortable>
                        <template #body="{ data }">
                            <div class="flex items-center gap-3">
                                <i
                                    :class="[data.is_private ? 'pi pi-lock text-amber-500' : 'pi pi-file-audio text-blue-500', 'text-lg']"></i>
                                <span class="font-bold text-slate-700">{{ data.title }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="author_name" header="Автор">
                        <template #body="{ data }">
                            <div class="flex flex-col">
                                <span class="font-medium">{{ data.author_name }}</span>
                                <span class="text-[10px] text-slate-400">{{ data.author_department }}</span>
                            </div>
                        </template>
                    </Column>
                    <Column field="category" header="Категория">
                        <template #body="{ data }">
                            <Tag :value="data.category" severity="secondary" class="!text-[10px]" />
                        </template>
                    </Column>
                    <Column field="created_at" header="Дата" sortable>
                        <template #body="{ data }">
                            <span class="text-slate-500 text-xs">{{ new Date(data.created_at).toLocaleDateString()
                                }}</span>
                        </template>
                    </Column>
                    <Column header="Действия">
                        <template #body="{ data }">
                            <div class="flex gap-1" @click.stop>
                                <Button icon="pi pi-heart" :severity="data.is_favorite ? 'danger' : 'secondary'" text
                                    rounded @click="toggleLike(data)" />
                                <Button icon="pi pi-download" severity="secondary" text rounded
                                    @click="downloadFile(data)" />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </div>

            <div v-show="displayMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                <div v-for="track in filteredTracks" :key="track.id" @click="openTrackDetails(track)" class="group">
                    <Card
                        class="!rounded-[2rem] !border-none !shadow-sm hover:!shadow-xl transition-all cursor-pointer overflow-hidden">
                        <template #header>
                            <div class="h-32 bg-slate-50 flex items-center justify-center relative">
                                <div class="absolute inset-0 opacity-[0.03] pointer-events-none">
                                    <i class="pi pi-database text-[10rem] -rotate-12"></i>
                                </div>

                                <Avatar v-if="track.author_name" :label="track.author_name[0]" size="xlarge"
                                    shape="circle" class="!bg-blue-100 !text-blue-500 !shadow-sm" />
                                <Avatar v-else icon="pi pi-user" size="xlarge" shape="circle" />

                                <Button :icon="track.is_favorite ? 'pi pi-heart-fill' : 'pi pi-heart'" rounded
                                    @click.stop="toggleLike(track)" class="favorite-float-btn"
                                    :class="{ 'is-active': track.is_favorite }" />
                            </div>
                        </template>
                        <template #title>
                            <div class="text-sm font-black text-slate-800 line-clamp-1 mb-1">{{ track.title }}</div>
                        </template>
                        <template #content>
                            <div class="flex flex-col gap-3">
                                <p class="text-[11px] text-slate-400 line-clamp-2 leading-relaxed h-8">
                                    {{ track.description || 'Нет описания' }}
                                </p>

                                <div class="flex items-center justify-between border-t border-slate-50 pt-3 mt-1">

                                    <div class="flex flex-col gap-0.5">
                                        <div class="text-[10px] font-bold text-slate-700 leading-none">
                                            {{ track.author_name }}
                                        </div>
                                        <div class="text-[9px] text-blue-500 font-medium uppercase tracking-wider">
                                            {{ track.author_department }}
                                        </div>
                                    </div>

                                    <Button icon="pi pi-download" text rounded size="small"
                                        class="!text-slate-400 hover:!text-blue-600 hover:!bg-blue-50 transition-colors"
                                        @click.stop="downloadFile(track)" />
                                </div>

                            </div>
                        </template>
                    </Card>
                </div>
            </div>
        </div>

        <div v-if="filteredTracks.length === 0 && !loading"
            class="flex flex-col items-center justify-center py-24 text-slate-300">
            <i class="pi pi-folder-open text-6xl mb-4 opacity-20"></i>
            <p class="text-xl font-bold italic">Записи не найдены</p>
        </div>

        <AudioDetailModal v-if="selectedTrack" :track="selectedTrack" :is-open="isDetailModalOpen" :is-admin="isAdmin"
            @close="isDetailModalOpen = false" @refresh="fetchTracks" @track-deleted="handleTrackDeleted" />
    </div>
</template>

<style scoped>

:deep(.crm-tabs) {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 3px;
    border-radius: 14px;
}

:deep(.crm-tabs .p-button) {
    border: none;
    border-radius: 10px;
    background: transparent;
    color: #64748b;
    font-size: 0.8rem;
    font-weight: 700;
}

:deep(.crm-tabs .p-highlight) {
    background: white !important;
    color: #3b82f6 !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06) !important;
}

/* Стилизация таблицы */
:deep(.crm-table .p-datatable-thead > tr > th) {
    background: #f8fafc;
    color: #64748b;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1rem;
}

:deep(.crm-table .p-datatable-tbody > tr) {
    cursor: pointer;
    transition: background 0.2s;
}


.favorite-float-btn {
    position: absolute !important;
    top: 0.75rem;
    right: 0.75rem;
    background: rgba(255, 255, 255, 0.9) !important;
    /* Полупрозрачный фон */
    backdrop-filter: blur(4px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    opacity: 0;
    /* Делаем видимой всегда */
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    
    z-index: 20;
    border: 1px solid #f1f5f9 !important;
}

.favorite-float-btn:hover {
    transform: scale(1.1);
    background: white !important;
    opacity: 1;
}

/* Состояние, когда лайк уже стоит */
.favorite-float-btn.is-active {
    color: #ef4444 !important;
    background: #fff1f2 !important;
    border-color: #fecdd3 !important;
    opacity: 1;
}   
.group {
    perspective: 1000px;
}
.group:hover .favorite-float-btn {
    opacity: 1;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

:deep(.p-inputtext) {
    box-shadow: none !important;
    background: transparent !important;
    border: none !important;
}


:deep(.p-dropdown-label) {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
}


.pi-search {
    line-height: 0;
    
}
</style>