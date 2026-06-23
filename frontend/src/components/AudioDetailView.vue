<script setup>
import { ref, nextTick, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import Swal from 'sweetalert2'

import Button from 'primevue/button'
import ScrollPanel from 'primevue/scrollpanel'
import Tag from 'primevue/tag'
import Avatar from 'primevue/avatar'

import VideoPlayer from './VideoPlayer.vue'

const props = defineProps({
  user: Object,
  isAdmin: Boolean
})

const route = useRoute()
const router = useRouter()

const track = ref(null)
const loading = ref(true)
const videoPlayerRef = ref(null)
const activeMobileTab = ref('protocol') // 'protocol' | 'info'

const trackId = route.params.id

const fetchTrackData = async () => {
  try {
    loading.value = true
    const token = localStorage.getItem('user-token')
    const response = await axios.get(`http://127.0.0.1:8000/api/records/${trackId}/`, {
      headers: { Authorization: `Token ${token}` }
    })
    track.value = response.data
  } catch (err) {
    Swal.fire({ title: 'Ошибка доступа', text: 'Запись не найдена', icon: 'error' })
    router.push('/library')
  } finally {
    loading.value = false
  }
}

onMounted(() => fetchTrackData())

const formatTime = (s) => (s && !isNaN(s)) ? `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}` : '0:00'
const formatDate = (d) => d ? new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' }) : '—'
const parsedTags = computed(() => (track.value?.tags || '').split(',').map(t => t.trim()).filter(Boolean))

const handleSeek = (time) => {
  videoPlayerRef.value?.seekTo(time)
  // На мобилках при клике на таймкод скроллим вверх к плееру
  if (window.innerWidth < 768) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const onCommentAdded = async (newComment) => {
  if (!newComment) return
  track.value.comments.push(newComment)
  await nextTick()
  const scrollEl = document.querySelector('.events-scroll .p-scrollpanel-content')
  scrollEl?.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' })
}
</script>

<template>
  <div v-if="loading"
    class="fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-slate-950 text-slate-500">
    <i class="pi pi-spin pi-spinner text-xl mb-2 text-blue-500"></i>
    <p class="text-[10px] font-mono uppercase tracking-widest">Инициализация холста...</p>
  </div>

  <!-- FIXED INSET-0 вырывает интерфейс из любого родительского контейнера и Grid-сетки шаблона -->
  <div v-else-if="track"
    class="fixed inset-0 z-[999] flex flex-col bg-slate-950 text-slate-100 font-sans antialiased overflow-hidden select-none">

    <!-- Шапка плеера: На мобайле прячем лишнее, оставляя только кнопку назад и ID -->
    <header
      class="shrink-0 bg-slate-900 border-b border-slate-950 px-4 md:px-6 h-12 flex items-center justify-between gap-4">
      <div class="flex items-center gap-2 min-w-0">
        <Button icon="pi pi-arrow-left" text @click="router.push('/library')"
          class="!text-slate-400 hover:!text-white hover:!bg-slate-800 !w-8 !h-8 !rounded shrink-0" />
        <span class="font-mono text-xs font-bold text-slate-500 tracking-wider">#{{ track.id }}</span>
        <div class="h-3 w-[1px] bg-slate-800 shrink-0 hidden md:block" />
        <h1 class="text-xs md:text-sm font-medium text-slate-200 truncate hidden sm:block">
          {{ track.title }}
        </h1>
      </div>

      <div class="flex items-center gap-2">
        <Tag :value="track.category" severity="secondary"
          class="!bg-blue-950/60 !border !border-blue-900/40 !text-blue-400 !text-[9px] !font-bold !rounded !px-2" />
        <span
          class="text-[10px] font-mono bg-slate-800 px-2 py-0.5 rounded text-slate-400 border border-slate-700 hidden md:inline-block">
          {{ track.security_level || 'Служебный' }}
        </span>
      </div>
    </header>

    <!-- Основной рабочий конвейер -->
    <!-- На десктопе: 3 панели. На мобильных: Вертикальный стек, где плеер зафиксирован, а панели переключаются табами -->
    <div class="flex-1 flex flex-col md:flex-row overflow-hidden w-full relative">

      <!-- ЛЕВАЯ ПАНЕЛЬ (Десктоп: параметры / Мобильный: скрыта под таб) -->
      <aside class="w-[260px] bg-slate-900/40 border-r border-slate-950 flex flex-col overflow-hidden hidden xl:flex">
        <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-5 sidebar-scroll">

          <div class="flex items-center gap-2.5 bg-slate-950/40 p-2.5 rounded border border-slate-900">
            <Avatar :label="track.author_name?.charAt(0)" class="!bg-slate-800 !text-slate-300 !text-xs !font-bold" />
            <div class="min-w-0">
              <p class="text-slate-300 font-medium text-xs truncate">{{ track.author_name }}</p>
              <p class="text-slate-500 text-[9px] tracking-wide uppercase truncate">{{ track.author_department }}</p>
            </div>
          </div>

          <div>
            <p class="panel-label">Тех-паспорт</p>
            <div class="space-y-2 mt-2.5 text-[11px] font-mono text-slate-400">
              <div class="flex justify-between border-b border-slate-900/60 pb-1"><span>Поток</span><span
                  class="text-slate-200">MP4 / H.264</span></div>
              <div class="flex justify-between border-b border-slate-900/60 pb-1"><span>Битрейт</span><span
                  class="text-slate-200">{{ track.bitrate || '—' }}</span></div>
              <div class="flex justify-between border-b border-slate-900/60 pb-1"><span>Вес</span><span
                  class="text-slate-200">{{ track.file_size || '—' }}</span></div>
            </div>
          </div>

          <div>
            <p class="panel-label">Аннотация</p>
            <p
              class="text-[11px] text-slate-400 leading-relaxed mt-2 bg-slate-950/20 p-2.5 rounded border border-slate-900">
              {{ track.description || 'Официальное описание документа отсутствует.' }}
            </p>
          </div>
        </div>
      </aside>

      <!-- ЦЕНТР: Плеер (На мобайле занимает верхнюю треть экрана жестко) -->
      <main class="flex-1 flex flex-col bg-black overflow-hidden aspect-video md:aspect-auto">
        <VideoPlayer ref="videoPlayerRef" :id="track.id" :src="track.file" :title="track.title"
          @comment-added="onCommentAdded" />
      </main>

      <!-- МОБИЛЬНЫЙ ПЕРЕКЛЮЧАТЕЛЬ ТАБОВ (Виден только на смартфонах) -->
      <div class="md:hidden flex bg-slate-900 border-b border-slate-950 h-10 shrink-0">
        <button @click="activeMobileTab = 'protocol'"
          :class="['flex-1 text-[10px] font-bold uppercase tracking-wider transition-all', activeMobileTab === 'protocol' ? 'text-blue-400 border-b-2 border-blue-500 bg-slate-950/40' : 'text-slate-500']">
          Протокол событий ({{ track.comments?.length || 0 }})
        </button>
        <button @click="activeMobileTab = 'info'"
          :class="['flex-1 text-[10px] font-bold uppercase tracking-wider transition-all', activeMobileTab === 'info' ? 'text-blue-400 border-b-2 border-blue-500 bg-slate-950/40' : 'text-slate-500']">
          Инфо и Справка
        </button>
      </div>

      <!-- ПРАВАЯ ПАНЕЛЬ: Лента хронометража событий -->
      <aside
        :class="['w-full md:w-[320px] bg-slate-900/20 md:border-l border-slate-950 flex flex-col overflow-hidden', 'md:flex', activeMobileTab === 'protocol' ? 'flex' : 'hidden']">
        <div
          class="shrink-0 px-4 py-2.5 bg-slate-900/40 border-b border-slate-950 hidden md:flex items-center justify-between">
          <span class="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Хронологический журнал</span>
          <span
            class="text-[10px] font-mono text-blue-500 bg-blue-950/60 px-1.5 py-0.5 rounded border border-blue-900/40">{{
              track.comments?.length || 0 }}</span>
        </div>

        <ScrollPanel class="flex-1 w-full events-scroll bg-slate-950/10">
          <div class="p-3 flex flex-col gap-1.5">
            <div v-for="c in track.comments" :key="c.id"
              class="group flex flex-col gap-1 p-2.5 bg-slate-900/40 border border-slate-900 hover:border-blue-950 hover:bg-slate-900/80 rounded transition-all cursor-pointer"
              @click="handleSeek(c.timestamp)">

              <div class="flex items-center justify-between">
                <span
                  class="text-[10px] font-mono font-bold text-blue-400 bg-blue-950/40 px-1.5 py-0.5 rounded border border-blue-900/30">
                  {{ formatTime(c.timestamp) }}
                </span>
                <span
                  class="text-[8px] text-slate-600 group-hover:text-slate-400 uppercase font-mono tracking-wider">Фокус</span>
              </div>
              <p class="text-xs text-slate-300 font-medium leading-normal">{{ c.text }}</p>
              <div
                class="text-[8px] text-slate-500 font-mono text-right mt-1 opacity-0 group-hover:opacity-100 transition-opacity">
                Фиксатор: {{ c.author_name || 'Система' }}
              </div>
            </div>

            <div v-if="!track.comments?.length"
              class="text-center py-16 text-slate-600 text-[10px] uppercase tracking-widest font-mono">
              Отметки не обнаружены
            </div>
          </div>
        </ScrollPanel>
      </aside>

      <!-- МОБИЛЬНЫЙ ИНФО-БЛОК (Контент левого сайдбара для смартфонов при переключении таба) -->
      <div
        :class="['flex-1 bg-slate-950 p-4 overflow-y-auto flex flex-col gap-4 md:hidden', activeMobileTab === 'info' ? 'flex' : 'hidden']">
        <h2 class="text-xs font-bold text-slate-200 uppercase tracking-wider">{{ track.title }}</h2>
        <div class="bg-slate-900/60 p-3 rounded border border-slate-800 text-xs text-slate-400 space-y-1">
          <p><span class="text-slate-600">Исполнитель:</span> {{ track.author_name }}</p>
          <p><span class="text-slate-600">Подразделение:</span> {{ track.author_department }}</p>
          <p><span class="text-slate-600">Дата фиксации:</span> {{ formatDate(track.created_at) }}</p>
        </div>
        <div>
          <span class="panel-label">Описание записи</span>
          <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">{{ track.description || 'Нет описания.' }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
@reference "../style.css";

.panel-label {
  @apply text-[9px] font-bold uppercase tracking-widest text-slate-500;
}

.sidebar-scroll::-webkit-scrollbar {
  width: 2px;
}

.sidebar-scroll::-webkit-scrollbar-thumb {
  background: #1e293b;
}

:deep(.events-scroll .p-scrollpanel-bar) {
  background: #1e293b !important;
}
</style>