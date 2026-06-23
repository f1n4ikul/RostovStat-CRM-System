<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import axios from 'axios'
import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const props = defineProps({ src: String, title: String, id: [Number, String] })
const emit = defineEmits(['comment-added'])

const videoRef = ref(null)
const player = ref(null)
const currentTimeText = ref('0:00')
const durationText = ref('0:00')
const newComment = ref('')
const isSubmitting = ref(false)

// Новые стейты для работы с Blob
const blobUrl = ref('')
const isVideoLoading = ref(false)

const formatTime = (s) => (s && !isNaN(s)) ? `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}` : '0:00'

// Метод предварительной загрузки видео в Blob
const loadVideoAsBlob = async (videoUrl) => {
  if (!videoUrl) return

  // Освобождаем старую память перед загрузкой нового видео
  if (blobUrl.value) {
    URL.revokeObjectURL(blobUrl.value)
    blobUrl.value = ''
  }

  isVideoLoading.value = true
  try {
    // Скачиваем файл целиком в бинарном виде
    const response = await axios.get(videoUrl, { responseType: 'blob' })
    // Создаем локальную ссылку на этот кусок памяти
    blobUrl.value = URL.createObjectURL(response.data)
  } catch (err) {
    console.error("Ошибка кэширования видео во фронтенде:", err)
    // Фолбэк на оригинальный url, если что-то пошло не так
    blobUrl.value = videoUrl
  } finally {
    isVideoLoading.value = false
  }
}

const initPlayer = () => {
  if (!videoRef.value || !blobUrl.value) return

  // Если инстанс уже есть — обновляем источник через встроенное API Plyr
  if (player.value) {
    player.value.source = {
      type: 'video',
      title: props.title || 'Video',
      sources: [{ src: blobUrl.value, type: 'video/mp4' }]
    }
    return
  }

  // Самая первая инициализация
  player.value = new Plyr(videoRef.value, {
    controls: ['play', 'progress', 'current-time', 'duration', 'mute', 'volume', 'fullscreen'],
    keyboard: { focused: true, global: true },
    tooltips: { controls: false, seek: true }
  })

  player.value.on('timeupdate', () => {
    currentTimeText.value = formatTime(player.value.currentTime)
  })

  player.value.on('loadedmetadata', () => {
    durationText.value = formatTime(player.value.duration)
  })
}

// Перемотка из заметок по таймингам
const seekTo = (seconds) => {
  if (!player.value) return
  player.value.currentTime = Number(seconds)
  player.value.play().catch(() => { })
}

// Шаг вперед/назад (-10s / 10s)
const skip = (amount) => {
  if (!player.value) return
  let targetTime = player.value.currentTime + amount
  player.value.currentTime = Math.max(0, Math.min(player.value.duration, targetTime))
}

const submitComment = async () => {
  if (!newComment.value.trim() || isSubmitting.value) return
  isSubmitting.value = true
  const token = localStorage.getItem('user-token')
  const timestamp = Math.floor(player.value?.currentTime ?? 0)
  try {
    const { data } = await axios.post(
      `http://127.0.0.1:8000/api/audio/${props.id}/add_comment/`,
      { text: newComment.value, timestamp },
      { headers: { Authorization: `Token ${token}` } }
    )
    newComment.value = ''
    emit('comment-added', data)
  } catch (err) {
    console.error(err)
  } finally {
    isSubmitting.value = false
  }
}

defineExpose({ seekTo })

onMounted(async () => {
  if (props.src) {
    await loadVideoAsBlob(props.src)
    initPlayer()
  }
})

onUnmounted(() => {
  if (player.value) player.value.destroy()
  if (blobUrl.value) URL.revokeObjectURL(blobUrl.value)
})

// Наблюдатель за сменой медиафайла
watch(() => props.src, async (newSrc) => {
  if (!newSrc) return
  await loadVideoAsBlob(newSrc)
  await nextTick()
  initPlayer()
})
</script>

<template>
  <div class="flex-1 flex flex-col bg-black h-full w-full relative overflow-hidden">

    <div class="flex-1 relative flex items-center justify-center min-h-0 bg-black">

      <div v-if="isVideoLoading"
        class="absolute inset-0 flex flex-col items-center justify-center bg-slate-950/80 z-30 gap-3">
        <i class="pi pi-spin pi-spinner text-3xl text-blue-500"></i>
        <span class="text-xs text-slate-400 font-mono">Буферизация медиапотока...</span>
      </div>

      <video ref="videoRef" :src="blobUrl" crossorigin="anonymous" playsinline class="w-full h-full object-contain">
      </video>
    </div>

    <div
      class="shrink-0 bg-slate-900 border-t border-slate-950 px-4 py-3 md:px-6 md:py-4 flex flex-col gap-2.5 md:gap-3">

      <div class="flex items-center justify-between gap-4">
        <div class="flex items-center gap-0.5 bg-slate-950 p-0.5 rounded border border-slate-800">
          <Button :disabled="isVideoLoading" text size="small" @click="skip(-10)"
            class="!text-slate-500 hover:!text-slate-300 !px-3 !py-1 !text-[11px] !font-mono !border-none">
            <i class="pi pi-angle-left mr-1"></i>-10s
          </Button>
          <div class="w-[1px] h-3 bg-slate-800" />
          <Button :disabled="isVideoLoading" text size="small" @click="skip(10)"
            class="!text-slate-500 hover:!text-slate-300 !px-3 !py-1 !text-[11px] !font-mono !border-none">
            10s<i class="pi pi-angle-right ml-1"></i>
          </Button>
        </div>

        <div
          class="text-[10px] md:text-[11px] font-mono text-slate-400 bg-slate-950 px-2.5 py-1 rounded border border-slate-800/60">
          <span class="font-bold text-blue-500">{{ currentTimeText }}</span>
          <span class="text-slate-800">/</span>
          {{ durationText }}
        </div>
      </div>

      <div class="relative flex items-center">
        <span
          class="absolute left-2.5 text-[9px] font-mono font-bold text-blue-400 bg-blue-950/50 border border-blue-900/60 px-1.5 py-0.5 rounded z-10 select-none">
          {{ currentTimeText }}
        </span>
        <InputText :disabled="isVideoLoading" v-model="newComment"
          placeholder="Зафиксировать событие на этом таймкоде..." @keyup.enter="submitComment"
          class="w-full !rounded !pl-14 !pr-10 !py-2 !border-slate-800 !bg-slate-950 !text-slate-300 focus:!border-blue-900/80 transition-all !text-xs placeholder:!text-slate-600 shadow-inner" />
        <Button :disabled="isVideoLoading" @click="submitComment" :loading="isSubmitting" icon="pi pi-plus"
          class="!absolute right-1 !w-7 !h-7 !rounded !bg-slate-900 !text-slate-400 hover:!text-white hover:!bg-blue-600 !border-none transition-all" />
      </div>

    </div>
  </div>
</template>

<style scoped>
:deep(.plyr) {
  --plyr-color-main: #2563eb;
  --plyr-video-background: #000000;
  width: 100%;
  height: 100%;
}

:deep(.plyr__video-wrapper) {
  height: 100%;
}

:deep(.plyr__controls) {
  padding: 24px 12px 4px !important;
  z-index: 20;
}

:deep(.p-inputtext) {
  box-shadow: none !important;
}
</style>