<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

// PrimeVue
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import Tag from 'primevue/tag'
import ScrollPanel from 'primevue/scrollpanel'

import WavePlayer from './WavePlayer.vue'

const props = defineProps(['track', 'isOpen', 'isAdmin'])
const emit = defineEmits(['close', 'refresh', 'track-deleted'])

const wavePlayerRef = ref(null)

const formatTime = (seconds) => {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return '0:00'
  const minutes = Math.floor(seconds / 60)
  const secondsRem = Math.floor(seconds % 60)
  return `${minutes}:${secondsRem < 10 ? '0' : ''}${secondsRem}`
}

const handleSeek = (time) => {
  wavePlayerRef.value?.seekTo(time)
}

const handleDeleteTrack = async () => {
  const result = await Swal.fire({
    title: 'Удалить запись?',
    text: `Файл "${props.track.title}" будет стерт из архива безвозвратно.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    confirmButtonText: 'Да, удалить',
    cancelButtonText: 'Отмена',
    customClass: { popup: 'rounded-3xl' }
  })

  if (result.isConfirmed) {
    try {
      const token = localStorage.getItem('user-token')
      await axios.delete(`http://127.0.0.1:8000/api/records/${props.track.id}/delete/`, {
        headers: { 'Authorization': `Token ${token}` }
      })
      emit('track-deleted', props.track.id)
      emit('close')
    } catch (err) {
      Swal.fire('Ошибка', err.response?.data?.error || 'Доступ запрещен', 'error')
    }
  }
}

const downloadDoc = async (doc) => {
  const token = localStorage.getItem('user-token')
  try {
    const response = await fetch(`http://127.0.0.1:8000/api/documents/${doc.id}/download/`, {
      headers: { 'Authorization': `Token ${token}` }
    })
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', doc.file_name)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (err) {
    console.error('Download error:', err)
  }
}

const onCommentAdded = async (newCommentFromPlayer) => {
  emit('refresh')
  if (newCommentFromPlayer) {
    props.track.comments.push(newCommentFromPlayer)

    // Ждем, пока Vue отрисует новый элемент в DOM
    await nextTick()

    // Находим контейнер скролла и крутим вниз
    const scrollEl = document.querySelector('.custom-scroll .p-scrollpanel-content')
    if (scrollEl) {
      scrollEl.scrollTo({ top: scrollEl.scrollHeight, behavior: 'smooth' })
    }
  }
}


</script>

<template>
  <Dialog :visible="isOpen" @update:visible="emit('close')" modal :closable="false" :showHeader="false"
    class="custom-dialog" contentClass="!p-0 !rounded-[2.5rem] !overflow-hidden !border-none"
    :style="{ width: '95vw', maxWidth: '1350px' }">

    <div class="grid grid-cols-1 md:grid-cols-[320px_1fr_340px] h-[92vh] bg-slate-50">

      <aside class="bg-white border-r border-slate-100 flex flex-col overflow-hidden">
        <div class="p-8 flex flex-col gap-5 h-full overflow-y-auto custom-scrollbar">
          <Button icon="pi pi-arrow-left" label="НАЗАД К РЕЕСТРУ" text @click="emit('close')" class="!text-blue-600 !font-black !text-[10px] !tracking-[0.2em] !p-5 !justify-start 
         transition-all duration-200 
         hover:!text-blue-800 hover:!bg-slate-100/50 active:scale-95" />

          <section class="flex flex-col gap-5">
            <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">Информация</h3>

            <div class="bg-slate-50 p-5 rounded-3xl border border-slate-100 flex flex-col gap-4">
              <div class="info-card">
                <span class="label">Идентификатор</span>
                <span class="value font-mono text-blue-600">#{{ track.id?.toString().padStart(6, '0') }}</span>
              </div>

              <div class="info-card">
                <span class="label">Ответственное лицо</span>
                <div class="flex items-center gap-3 mt-1">
                  <div
                    class="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center text-[10px] text-white font-bold">
                    {{ track.author_name?.substring(0, 1) }}
                  </div>
                  <div class="flex flex-col">
                    <span class="value text-slate-900">{{ track.author_name }}</span>
                    <span class="text-[9px] text-slate-400 font-bold uppercase">{{ track.author_department ||
                      'Департамент' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h3 class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-4">Документация</h3>
            <div v-if="track.documents?.length" class="space-y-2">
              <div v-for="doc in track.documents" :key="doc.id"
                class="group flex items-center justify-between p-3 bg-white rounded-2xl border border-slate-100 hover:border-blue-200 hover:shadow-sm transition-all">
                <div class="flex items-center gap-3 overflow-hidden">
                  <div class="w-8 h-8 rounded-lg bg-red-50 flex items-center justify-center">
                    <i class="pi pi-file-pdf text-red-400 text-xs"></i>
                  </div>
                  <span class="text-[11px] font-bold text-slate-700 truncate max-w-[140px]">{{ doc.file_name }}</span>
                </div>
                <Button icon="pi pi-download" text rounded @click="downloadDoc(doc)"
                  class="!w-8 !h-8 !text-slate-400 group-hover:!text-blue-600" />
              </div>
            </div>
          </section>

          <div v-if="isAdmin" class="mt-auto pt-6 flex flex-col gap-3">
            <Button label="Правка данных" icon="pi pi-pencil" severity="secondary"
              class="!text-[10px] !font-bold !py-4 !rounded-2xl !bg-slate-100 !border-none !text-slate-700 hover:!bg-slate-200" />
            <Button label="Удалить протокол" icon="pi pi-trash" severity="danger" text
              class="!text-[10px] !font-bold !py-4 !rounded-2xl" />
          </div>
        </div>
      </aside>

      <main class="flex flex-col overflow-hidden">
        <div class="p-5 overflow-y-auto custom-scrollbar flex-1 flex flex-col">
          <header class="mb-5">
            <div class="flex items-center gap-4 mb-5">
              <span
                class="bg-blue-600 text-white text-[9px] font-black px-3 py-1.5 rounded-lg uppercase tracking-wider">
                {{ track.category }}
              </span>
              <span class="text-[11px] text-slate-400 font-bold uppercase tracking-widest">
                {{ new Date(track.created_at).toLocaleDateString('ru-RU', {
                  day: 'numeric', month: 'long', year:
                'numeric' }) }}
              </span>
            </div>
            <h2 class="text-2xl font-black text-slate-900 tracking-tighter leading-none mb-8">{{ track.title }}</h2>
            <p class="text-slate-400 text-l leading-relaxed font-medium max-w-3xl">
              {{ track.description || 'Описание отсутствует.' }}
            </p>
          </header>

          <div class="mt-auto mb-8">
            <WavePlayer ref="wavePlayerRef" :id="track.id" :src="track.file" :title="track.title"
              @comment-added="onCommentAdded" />
          </div>
        </div>
      </main>

      <section class="bg-white border-l border-slate-100 flex flex-col">
        <div class="p-8 border-b border-slate-50 flex items-center justify-between">
          <h3 class="text-[10px] font-black text-slate-900 uppercase tracking-[0.2em]">События записи</h3>
          <div class="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-[10px] font-black">
            {{ track.comments?.length || 0 }}
          </div>
        </div>

        <ScrollPanel class="flex-1 w-full h-full p-4">
          <div v-if="track.comments?.length" class="flex flex-col gap-3 p-4">
            <div v-for="c in track.comments" :key="c.id"
              class="group flex flex-col gap-3 p-5 bg-slate-50 rounded-[1.5rem] border border-transparent hover:border-blue-100 hover:bg-white hover:shadow-xl hover:shadow-blue-900/5 transition-all cursor-pointer"
              @click="handleSeek(c.timestamp)">
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-black text-white bg-blue-600 px-3 py-1 rounded-full">
                  {{ formatTime(c.timestamp) }}
                </span>
                <i class="pi pi-play text-[10px] text-slate-300 group-hover:text-blue-600"></i>
              </div>
              <p class="text-[13px] text-slate-700 leading-snug font-semibold">{{ c.text }}</p>
            </div>
          </div>
        </ScrollPanel>
      </section>

    </div>
  </Dialog>
</template>

<style scoped>
@reference "../style.css";

.info-card {
  @apply flex flex-col gap-0.5;
}

.label {
  @apply text-[9px] text-slate-400 font-black uppercase tracking-wider;
}

.value {
  @apply text-xs font-bold text-slate-800;
}

.tech-badge {
  @apply p-4 rounded-2xl border flex flex-col gap-1;
}

.badge-label {
  @apply text-[9px] uppercase font-black tracking-widest;
}

.badge-value {
  @apply text-[11px] font-bold;
}

/* Кастомный скролл */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-slate-200 rounded-full;
}

:deep(.p-dialog-content) {
  @apply shadow-2xl;
}
</style>