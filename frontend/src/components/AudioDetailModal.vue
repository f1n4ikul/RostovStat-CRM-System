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

// Реф для управления плеером из этой модалки
const wavePlayerRef = ref(null)

const formatTime = (seconds) => {
  if (seconds === null || seconds === undefined || isNaN(seconds)) return '0:00'
  const minutes = Math.floor(seconds / 60)
  const secondsRem = Math.floor(seconds % 60)
  return `${minutes}:${secondsRem < 10 ? '0' : ''}${secondsRem}`
}

const handleSeek = (time) => {
  if (wavePlayerRef.value) {
    wavePlayerRef.value.seekTo(time)
  }
}

const handleDeleteTrack = async () => {
  const result = await Swal.fire({
    title: 'Вы уверены?',
    text: `Запись "${props.track.title}" будет удалена безвозвратно!`,
    icon: 'warning',
    target: document.querySelector('.custom-dialog'),
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#64748b',
    confirmButtonText: 'Да, удалить!',
    cancelButtonText: 'Отмена',
    background: '#ffffff',
    borderRadius: '20px'
  })

  if (result.isConfirmed) {
    try {
      const token = localStorage.getItem('user-token')
      await axios.delete(`http://127.0.0.1:8000/api/records/${props.track.id}/delete/`, {
        headers: { 'Authorization': `Token ${token}` }
      })

      await Swal.fire({
        title: 'Удалено!',
        icon: 'success',
        timer: 1500,
        showConfirmButton: false,
        target: document.querySelector('.custom-dialog'),
        borderRadius: '20px'
      })

      emit('track-deleted', props.track.id)
      emit('close')
    } catch (err) {
      Swal.fire({
        title: 'Ошибка!',
        text: err.response?.data?.error || 'Не удалось удалить файл.',
        icon: 'error'
      })
    }
  }
}

const handleEditTrack = () => {
  alert('Функция редактирования данных будет добавлена в следующем обновлении.')
}

const onCommentAdded = () => {
  emit('refresh')
}
</script>

<template>
  <Dialog :visible="isOpen" @update:visible="emit('close')" modal :closable="false" :showHeader="false"
    class="custom-dialog" contentClass="!p-0 !rounded-[2.5rem] !overflow-hidden"
    :style="{ width: '95vw', maxWidth: '1250px' }" breakPoint="960px">

    <div class="grid grid-cols-1 md:grid-cols-[240px_1fr_300px] h-full md:h-[85vh] bg-white overflow-hidden">

      <div class="bg-slate-50/80 p-6 border-r border-slate-100 flex flex-col gap-8">
        <Button icon="pi pi-arrow-left" label="Назад к списку" text @click="emit('close')"
          class="!text-slate-400 hover:!text-slate-600 !font-bold !text-xs !justify-start !p-0" />

        <div class="flex flex-col gap-6">
          <h3 class="text-[9px] font-black text-slate-400 uppercase tracking-widest">Служебная информация</h3>

          <div class="info-block">
            <span class="label">Автор загрузки</span>
            <span class="value">{{ track.author_name || 'Не указан' }}</span>
          </div>

          <div class="info-block">
            <span class="label">Дата создания</span>
            <span class="value text-[11px]">{{ new Date(track.created_at).toLocaleString('ru-RU') }}</span>
          </div>

          <div class="info-block">
            <span class="label">Уровень доступа</span>
            <div class="mt-1">
              <Tag :severity="track.is_private ? 'warn' : 'success'" :value="track.is_private ? 'Приватно' : 'Публично'"
                class="!text-[8px] !px-2" />
            </div>
          </div>
        </div>
      </div>

      <div class="p-8 flex flex-col overflow-y-auto bg-white custom-scrollbar relative">
        <div v-if="isAdmin" class="flex gap-3 mb-8 justify-center">
          <Button label="Редактировать" icon="pi pi-pencil" severity="info" outlined @click="handleEditTrack"
            class="!rounded-xl !text-xs !px-6" />
          <Button label="Удалить" icon="pi pi-trash" severity="danger" outlined @click="handleDeleteTrack"
            class="!rounded-xl !text-xs !px-6" />
        </div>

        <div class="mb-8 text-center">
          <Tag :value="track.category" severity="info"
            class="!bg-blue-50 !text-blue-600 !text-[10px] !font-black uppercase px-3" />
          <h2 class="text-3xl font-black text-slate-800 mt-3 tracking-tighter">{{ track.title }}</h2>
          <p class="text-slate-400 text-sm mt-2 max-w-md mx-auto italic">{{ track.description || 'Нет описания' }}</p>
        </div>

        <div class="flex-1 flex flex-col justify-start">
          <WavePlayer ref="wavePlayerRef" :id="track.id" :src="track.file" :title="track.title"
            @comment-added="onCommentAdded" />
        </div>
      </div>

      <div class="bg-slate-50/30 border-l border-slate-100 flex flex-col h-full overflow-hidden text-left">
        <div class="p-6 pb-2">
          <h3 class="text-[10px] font-black text-slate-800 uppercase tracking-widest flex items-center gap-2">
            <i class="pi pi-comments text-blue-500"></i>
            Хронология заметок ({{ track.comments?.length || 0 }})
          </h3>
        </div>

        <ScrollPanel class="flex-1 w-full px-6 custom-scroll" style= "height: 100%">
          <div v-if="track.comments && track.comments.length > 0" class="flex flex-col gap-3 py-4 pr-2">
            <div v-for="c in track.comments" :key="c.id"
              class="flex flex-col gap-2 p-3 bg-white rounded-xl border border-slate-100 hover:border-blue-200 transition-all shadow-sm group">

              <div class="flex items-center justify-between">
                <button @click="handleSeek(c.timestamp)"
                  class="shrink-0 text-[10px] font-mono font-bold bg-blue-50 px-2 py-1 rounded-lg text-blue-600 hover:bg-blue-600 hover:text-white transition-colors">
                  {{ formatTime(c.timestamp) }}
                </button>
                <i class="pi pi-bookmark text-slate-200 text-[10px] group-hover:text-blue-300 transition-colors"></i>
              </div>

              <span class="text-[11px] text-slate-600 leading-snug break-words font-medium">
                {{ c.text }}
              </span>
            </div>
          </div>

          <div v-else class="flex flex-col items-center justify-center py-20 text-slate-300">
            <i class="pi pi-inbox text-2xl mb-2 opacity-50"></i>
            <p class="text-[9px] font-bold uppercase tracking-widest text-center">Заметок пока нет</p>
          </div>
        </ScrollPanel>
      </div>

    </div>
  </Dialog>
</template>

<style scoped>
@reference "../style.css";

.info-block {
  @apply flex flex-col gap-0.5;
}

.label {
  @apply text-[8px] text-slate-400 font-bold uppercase tracking-widest;
}

.value {
  @apply text-xs font-bold text-slate-600;
}

:deep(.p-scrollpanel-bar) {
  background: #cbd5e1 !important;
  width: 4px !important;
  opacity: 1 !important;
  z-index: 10;
}
</style>