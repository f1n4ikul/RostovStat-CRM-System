<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import WaveSurfer from 'wavesurfer.js'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import axios from 'axios'

import Button from 'primevue/button'
import InputText from 'primevue/inputtext'

const props = defineProps({
    src: String,
    title: String,
    id: [Number, String]
})

const emit = defineEmits(['comment-added'])

const audioRef = ref(null)
const waveformRef = ref(null)
const wavesurfer = ref(null)
const player = ref(null)

const currentTimeText = ref('0:00')
const durationText = ref('0:00')
const newComment = ref('')
const isSubmitting = ref(false)

const formatTime = (seconds) => {
    if (seconds === null || isNaN(seconds)) return '0:00'
    const minutes = Math.floor(seconds / 60)
    const secondsRem = Math.floor(seconds % 60)
    return `${minutes}:${secondsRem < 10 ? '0' : ''}${secondsRem}`
}

// ФУНКЦИЯ СКАЧИВАНИЯ (СВОЯ)
const handleDownload = async () => {
    const downloadUrl = `http://127.0.0.1:8000/api/records/${props.id}/download/`
    const token = localStorage.getItem('user-token');

    try {
        const response = await fetch(downloadUrl, {
            headers: { 'Authorization': `Token ${token}` }
        });

        if (!response.ok) throw new Error('Download failed');

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${props.title || 'audio'}.mp3`;
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (err) {
        console.error('Ошибка при скачивании:', err);
    }
};

const initPlayer = () => {
    // 1. Инициализируем Plyr БЕЗ кнопки download внутри
    if (player.value) player.value.destroy()
    player.value = new Plyr(audioRef.value, {
        blankVideo: '',
        controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'settings'],
        speed: { selected: 1, options: [0.5, 1, 1.5, 2] }
    })

    // 2. Инициализируем WaveSurfer
    if (wavesurfer.value) wavesurfer.value.destroy()
    wavesurfer.value = WaveSurfer.create({
        container: waveformRef.value,
        media: audioRef.value,
        waveColor: '#cbd5e1',
        progressColor: '#3b82f6',
        barWidth: 2,
        height: 60,
        responsive: true,
        cursorColor: '#3b82f6'
    })

    wavesurfer.value.on('timeupdate', (time) => {
        currentTimeText.value = formatTime(time)
    })

    wavesurfer.value.on('ready', () => {
        durationText.value = formatTime(wavesurfer.value.getDuration())
    })
}

const submitComment = async () => {
    if (!newComment.value.trim() || isSubmitting.value) return
    isSubmitting.value = true
    const token = localStorage.getItem('user-token')
    const currentPos = wavesurfer.value ? Math.floor(wavesurfer.value.getCurrentTime()) : 0

    try {
        await axios.post(`http://127.0.0.1:8000/api/audio/${props.id}/add_comment/`, {
            text: newComment.value,
            timestamp: currentPos
        }, {
            headers: { 'Authorization': `Token ${token}` }
        })
        newComment.value = ''
        emit('comment-added')
    } catch (err) {
        console.error('Ошибка отправки комментария:', err)
    } finally {
        isSubmitting.value = false
    }
}

const seekTo = (seconds) => {
    if (wavesurfer.value) {
        wavesurfer.value.setTime(seconds)
        wavesurfer.value.play()
    }
}

defineExpose({ seekTo })

onMounted(() => initPlayer())
onUnmounted(() => {
    if (player.value) player.value.destroy()
    if (wavesurfer.value) wavesurfer.value.destroy()
})

watch(() => props.id, async () => {
    await nextTick()
    initPlayer()
})
</script>

<template>
    <div class="flex flex-col w-full bg-white rounded-[2rem] border border-slate-100 shadow-2xl shadow-slate-200/50">

        <div class="flex-shrink-0 px-6 py-4 border-b border-slate-50 flex items-center justify-between bg-slate-50/30">
            <div class="flex items-center gap-4">
                <div
                    class="w-10 h-10 rounded-xl bg-white flex items-center justify-center shadow-sm border border-slate-100">
                    <i class="pi pi-volume-up text-blue-600"></i>
                </div>
                <div class="flex flex-col overflow-hidden text-left">
                    <span class="text-[9px] font-bold text-blue-400 uppercase tracking-widest block mb-0.5">Панель
                        управления</span>
                    <h4 class="text-sm font-bold text-slate-700 truncate max-w-[200px]">{{ title || 'Аудиофайл' }}</h4>
                </div>
            </div>

            <Button icon="pi pi-download" @click="handleDownload"
                class="!p-2 !rounded-lg !bg-white !border-slate-200 !text-slate-600 hover:!text-blue-600 hover:!border-blue-200 shadow-sm transition-all" />
        </div>

        <div class="p-6 flex flex-col gap-6">
            <div class="bg-slate-50/50 rounded-2xl p-4 border border-slate-100/50">
                <div ref="waveformRef"></div>
                <div class="flex justify-between mt-2 text-[10px] font-mono font-bold">
                    <span class="text-blue-600">{{ currentTimeText }}</span>
                    <span class="text-slate-400">{{ durationText }}</span>
                </div>
            </div>

            <div class="plyr-wrapper">
                <audio ref="audioRef" :src="src" controls crossorigin="anonymous"></audio>
            </div>

            <div class="p-4 rounded-2xl bg-blue-50/30 border border-blue-100/50">
                <div class="flex items-center gap-1.5 mb-2 text-[10px] font-bold text-blue-500 uppercase px-1">
                    <i class="pi pi-clock"></i>
                    <span>Оставить заметку на {{ currentTimeText }}</span>
                </div>
                <div class="flex gap-2 text-left">
                    <InputText v-model="newComment" placeholder="Введите текст комментария..."
                        @keyup.enter="submitComment"
                        class="flex-1 !text-xs !rounded-xl !border-slate-200 !bg-white !py-2.5 !px-4 focus:!border-blue-400 transition-all !shadow-sm" />
                    <Button icon="pi pi-send" @click="submitComment" :loading="isSubmitting"
                        class="!rounded-xl !w-11 !bg-blue-600 !border-none !text-white shadow-lg shadow-blue-200" />
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
:deep(.plyr--audio .plyr__controls) {
    background: white !important;
    border-radius: 12px !important;
    border: 1px solid #f1f5f9 !important;
    padding: 8px !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
}
</style>