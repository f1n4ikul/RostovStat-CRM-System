<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'
import { useToast } from "primevue/usetoast"
import { useRouter } from 'vue-router'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'
import SelectButton from 'primevue/selectbutton'
import Tag from 'primevue/tag'
import DataTable from 'primevue/datatable'
import Column from 'primevue/column'
import Dropdown from 'primevue/dropdown'
import Avatar from 'primevue/avatar'

const router = useRouter()
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
const displayMode = ref('table')

const cache = { all: null, favorites: null }

const departments = [
    'Все отделы',
    'Отдел сводных статистических работ и общественных связей',
    'Отдел региональных счетов и балансов',
    'Отдел статистики цен и финансов',
    'Отдел статистики сельского хозяйства и окружающей природной среды',
    'Отдел статистики предприятий',
    'Отдел статистики рыночных услуг',
    'Отдел статистики труда, образования, науки и инноваций',
    'Отдел статистики уровня жизни и обследований домашних хозяйств',
    'Отдел статистики строительства, инвестиций и жилищно-коммунального хозяйства',
    'Отдел статистики населения и здравоохранения, организации и проведения переписей и обследований'
]
const viewOptions = [
    { label: 'Реестр записей', value: 'all' },
    { label: 'Избранные', value: 'favorites' }
]
const categories = [
    { id: 'all', name: 'Все отделы' },
    { id: 'svod', name: 'Отдел сводных статистических работ и общественных связей' },
    { id: 'accounts', name: 'Отдел региональных счетов и балансов' },
    { id: 'prices', name: 'Отдел статистики цен и финансов' },
    { id: 'agriculture', name: 'Отдел статистики сельского хозяйства и окружающей природной среды' },
    { id: 'enterprise', name: 'Отдел статистики предприятий' },
    { id: 'services', name: 'Отдел статистики рыночных услуг' },
    { id: 'labor', name: 'Отдел статистики труда, образования, науки и инноваций' },
    { id: 'living_standard', name: 'Отдел статистики уровня жизни и обследований домашних хозяйств' },
    { id: 'construction', name: 'Отдел статистики строительства, инвестиций и жилищно-коммунального хозяйства' },
    { id: 'population', name: 'Отдел статистики населения и здравоохранения, организации и проведения переписей и обследований' }
]

const openTrackPage = (trackId) => {
    if (!trackId) return
    router.push(`/library/${trackId}`)
}

const fetchTracks = async (forceRefresh = false) => {
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
        tracks.value = Array.isArray(response.data) ? response.data : []
        cache[currentView.value] = tracks.value
    } catch (error) {
        console.error("Ошибка API:", error)
        toast.add({ severity: 'error', summary: 'Ошибка связи', detail: 'Сервер недоступен', life: 3000 })
        tracks.value = []
    } finally {
        loading.value = false
    }
}

const handleGlobalUpload = () => {
    cache.all = null
    cache.favorites = null
    fetchTracks(true)
}

const filteredTracks = computed(() => {
    const list = tracks.value || []
    if (!list.length) return []

    const query = searchQuery.value.trim().toLowerCase()
    const category = selectedCategory.value
    const dept = selectedDept.value

    return list.filter(track => {
        if (!track) return false
        const matchesSearch = !query || (track.title && track.title.toLowerCase().includes(query))
        const matchesCategory = category === 'all' || track.category === category
        const matchesDept = dept === 'Все отделы' || track.author_department === dept
        return matchesSearch && matchesCategory && matchesDept
    })
})

const downloadFile = async (track) => {
    if (!track?.id) return
    try {
        const response = await axios({
            url: `http://127.0.0.1:8000/api/records/${track.id}/download/`,
            method: 'GET',
            responseType: 'blob',
        })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${track.title || 'audio_record'}.mp3`)
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
    } catch (e) {
        toast.add({ severity: 'error', summary: 'Ошибка', detail: 'Файл не найден' })
    }
}

const toggleLike = async (track) => {
    if (!track?.id) return
    try {
        const response = await axios.post(`http://127.0.0.1:8000/api/records/${track.id}/toggle-favorite/`)
        const newFavoriteStatus = response.data.is_favorite

        // Элегантно обновляем элемент в массиве реактивно для Vue
        tracks.value = tracks.value.map(t => {
            if (t.id === track.id) {
                return { ...t, is_favorite: newFavoriteStatus }
            }
            return t
        })

        // Логика поведения в зависимости от текущей открытой вкладки
        if (currentView.value === 'favorites') {
            // Если мы на вкладке избранного и сняли звездочку — убираем трек из экрана
            if (!newFavoriteStatus) {
                tracks.value = tracks.value.filter(t => t.id !== track.id)
            }
            cache.favorites = tracks.value
            cache.all = null // Заставляем общую ленту обновиться при переходе
        } else {
            // Если мы на общей вкладке — обновляем кэш текущей и сбрасываем кэш избранного
            cache.all = tracks.value
            cache.favorites = null
        }

        // Выводим красивое уведомление сотруднику
        toast.add({
            severity: 'success',
            summary: newFavoriteStatus ? 'Добавлено' : 'Удалено',
            detail: newFavoriteStatus ? 'Запись добавлена в избранное' : 'Запись удалена из избранного',
            life: 2000
        })

    } catch (e) {
        console.error("Ошибка toggle-favorite:", e)
        toast.add({ severity: 'warn', summary: 'Ошибка', detail: 'Не удалось обновить статус избранного', life: 3000 })
    }
}

watch(currentView, () => {
    searchQuery.value = ''
    selectedCategory.value = 'all'
    fetchTracks()
})

onMounted(() => {
    fetchTracks()
    window.addEventListener('track-uploaded', handleGlobalUpload)
})

onUnmounted(() => {
    window.removeEventListener('track-uploaded', handleGlobalUpload)
})
</script>

<template>
    <div class="crm-wrapper w-full flex flex-col items-center justify-start bg-transparent min-h-screen">

        <div class="crm-container w-full max-w-[1200px] px-4 py-4 md:py-6 mx-auto box-border">

            <div
                class="w-full flex flex-col gap-3 mb-5 md:bg-white md:p-5 md:border md:border-slate-200 md:rounded-2xl md:shadow-sm">

                <div class="w-full">
                    <SelectButton v-model="currentView" :options="viewOptions" optionLabel="label" optionValue="value"
                        class="crm-tabs-mobile w-full flex text-center" />
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 w-full">
                    <div
                        class="relative flex items-center w-full h-11 bg-white border border-slate-200 rounded-xl px-3 focus-within:border-blue-500 transition-all shadow-sm md:shadow-none">
                        <i class="pi pi-search text-slate-400 mr-2 text-sm shrink-0" />
                        <InputText v-model="searchQuery" placeholder="Поиск по названию..."
                            class="w-full !border-none !p-0 !bg-transparent !ring-0 text-sm" />
                    </div>

                    <Dropdown v-model="selectedDept" :options="departments"
                        class="w-full !h-11 !rounded-xl !border-slate-200 flex items-center text-sm shadow-sm md:shadow-none" />
                </div>

                <div
                    class="flex gap-1.5 overflow-x-auto pb-1 pt-1 scroller-hidden -mx-4 px-4 sm:mx-0 sm:px-0 w-[calc(100%+2rem)] sm:w-full">
                    <Button v-for="cat in categories" :key="cat.id" :label="cat.name" :class="[
                        '!rounded-full !text-xs !px-4 !py-2 shrink-0 transition-all !font-medium',
                        selectedCategory === cat.id
                            ? '!bg-blue-600 !border-blue-600 !text-white'
                            : '!bg-white !border-slate-200 !text-slate-600 shadow-sm'
                    ]" @click="selectedCategory = cat.id" />
                </div>
            </div>

            <div v-if="loading"
                class="w-full flex flex-col items-center justify-center py-20 bg-white rounded-2xl border border-slate-200">
                <i class="pi pi-spin pi-spinner text-xl text-blue-600 mb-2"></i>
                <span class="text-xs text-slate-400">Загрузка данных...</span>
            </div>

            <div v-else-if="filteredTracks.length > 0" class="w-full">

                <div
                    class="hidden md:block w-full bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                    <DataTable :value="filteredTracks" responsiveLayout="scroll" class="crm-table text-sm w-full"
                        @row-click="(e) => openTrackPage(e.data?.id)">
                        <Column field="title" header="Название записи">
                            <template #body="{ data }">
                                <div class="flex items-center gap-3">
                                    <i
                                        :class="[data?.is_private ? 'pi pi-lock text-amber-500' : 'pi pi-file-audio text-slate-400', 'text-base']"></i>
                                    <span class="font-medium text-slate-900 truncate max-w-md">{{ data?.title || 'Без названия' }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="author_name" header="Исполнитель">
                            <template #body="{ data }">
                                <div class="flex flex-col">
                                    <span class="font-medium text-slate-800 text-xs">{{ data?.author_name || 'Система'
                                        }}</span>
                                    <span
                                        class="text-[10px] text-slate-400 font-medium uppercase tracking-wider mt-0.5">{{
                                            data?.author_department || 'Общий отдел' }}</span>
                                </div>
                            </template>
                        </Column>
                        <Column field="category" header="Категория">
                            <template #body="{ data }">
                                <Tag :value="data?.category || 'all'" severity="secondary"
                                    class="!text-[10px] !rounded !px-2" />
                            </template>
                        </Column>
                        <Column field="created_at" header="Дата">
                            <template #body="{ data }">
                                <span class="text-slate-500 text-xs">{{ data?.created_at ? new
                                    Date(data.created_at).toLocaleDateString('ru-RU') : '—' }}</span>
                            </template>
                        </Column>
                        <Column class="text-right">
                            <template #body="{ data }">
                                <div class="flex justify-end gap-1" @click.stop>
                                    <Button :icon="data?.is_favorite ? 'pi pi-star-fill' : 'pi pi-star'"
                                        :severity="data?.is_favorite ? 'warning' : 'secondary'" text rounded
                                        @click="toggleLike(data)" />
                                    <Button icon="pi pi-download" severity="secondary" text rounded
                                        @click="downloadFile(data)" />
                                </div>
                            </template>
                        </Column>
                    </DataTable>
                </div>

                <div class="block md:hidden space-y-3 w-full">
                    <div v-for="track in filteredTracks" :key="'mob-' + track?.id" @click="openTrackPage(track?.id)"
                        class="w-full bg-white rounded-2xl border border-slate-100 p-4 active:scale-[0.99] active:bg-slate-50 transition-all shadow-sm flex flex-col gap-3 box-border">

                        <div class="flex items-start justify-between gap-2 w-full">
                            <div class="flex items-center gap-2.5 min-w-0">
                                <Avatar :label="track?.author_name ? track.author_name[0] : 'U'"
                                    class="!bg-slate-100 !text-slate-600 !w-8 !h-8 !text-xs !font-bold !rounded-xl shrink-0" />
                                <div class="flex flex-col min-w-0">
                                    <span class="text-xs font-bold text-slate-900 truncate">{{ track?.author_name ||
                                        'Аноним' }}</span>
                                    <span
                                        class="text-[10px] text-slate-400 font-medium uppercase tracking-wide truncate">{{
                                            track?.author_department || 'Общий отдел' }}</span>
                                </div>
                            </div>

                            <div class="flex items-center gap-1 -mt-1 -mr-1 shrink-0" @click.stop>
                                <button @click="toggleLike(track)"
                                    class="w-11 h-11 flex items-center justify-center rounded-full text-lg transition-colors active:bg-slate-100">
                                    <i
                                        :class="[track?.is_favorite ? 'pi pi-star-fill text-amber-500' : 'pi pi-star text-slate-400']"></i>
                                </button>
                            </div>
                        </div>

                        <div class="text-sm font-semibold text-slate-800 leading-snug flex items-start gap-2 w-full">
                            <i
                                :class="[track?.is_private ? 'pi pi-lock text-amber-500' : 'pi pi-file-audio text-slate-400', 'mt-0.5 text-sm shrink-0']"></i>
                            <span class="break-words flex-1 min-w-0">{{ track?.title || 'Без наименования' }}</span>
                        </div>

                        <p v-if="track?.description"
                            class="text-[11px] text-slate-500 line-clamp-2 leading-relaxed bg-slate-50 p-2 rounded-xl border border-slate-100/60 w-full box-border">
                            {{ track.description }}
                        </p>

                        <div class="flex items-center justify-between border-t border-slate-100 pt-3 mt-1 w-full">
                            <div class="flex items-center gap-2">
                                <Tag :value="track?.category || 'all'" severity="secondary"
                                    class="!text-[10px] !bg-slate-100 !text-slate-500 !rounded-md !px-2.5 !py-1" />
                                <span class="text-[11px] text-slate-400 font-mono">
                                    {{ track?.created_at ? new Date(track.created_at).toLocaleDateString('ru-RU') : '—'
                                    }}
                                </span>
                            </div>

                            <button @click.stop="downloadFile(track)"
                                class="h-9 px-3.5 bg-slate-50 hover:bg-slate-100 active:bg-slate-200 rounded-xl flex items-center gap-1.5 text-xs font-semibold text-slate-600 transition-colors border border-slate-200/60 shrink-0">
                                <i class="pi pi-download text-xs"></i>
                                <span>Файл</span>
                            </button>
                        </div>

                    </div>
                </div>

            </div>

            <div v-else
                class="w-full flex flex-col items-center justify-center py-16 bg-white rounded-2xl border border-slate-200 text-slate-400">
                <i class="pi pi-folder-open text-2xl mb-2 opacity-50"></i>
                <p class="text-xs font-medium">Ничего не найдено</p>
            </div>

        </div>
    </div>
</template>

<style scoped>
@reference "../style.css";

/* Скрытие системного скроллбара категорий */
.scroller-hidden::-webkit-scrollbar {
    display: none;
}

.scroller-hidden {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

/* Фикс для предотвращения вываливания flex-элементов */
.crm-wrapper * {
    box-sizing: border-box;
}

/* Кастомный стиль кнопок вкладок для мобильных */
:deep(.crm-tabs-mobile) {
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    padding: 3px;
    border-radius: 12px;
}

:deep(.crm-tabs-mobile .p-button) {
    flex: 1;
    border: none;
    border-radius: 9px;
    background: transparent;
    color: #64748b;
    font-size: 13px;
    font-weight: 600;
    padding: 10px 0;
    transition: all 0.15s ease;
}

:deep(.crm-tabs-mobile .p-highlight) {
    background: white !important;
    color: #2563eb !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06) !important;
}

/* Таблица */
:deep(.crm-table .p-datatable-thead > tr > th) {
    background: #f8fafc;
    color: #64748b;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 14px 16px;
    border-bottom: 1px solid #e2e8f0;
}

:deep(.crm-table .p-datatable-tbody > tr:hover) {
    background: #f8fafc !important;
}

/* Сбросы базовых инпутов */
:deep(.p-inputtext) {
    box-shadow: none !important;
    background: transparent !important;
    border: none !important;
}

:deep(.p-dropdown) {
    box-shadow: none !important;
}

:deep(.p-dropdown-label) {
    font-size: 13px;
    color: #334155;
    padding-left: 12px;
}
</style>