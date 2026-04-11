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
    if (player.value) player.value.destroy()
    if (wavesurfer.value) wavesurfer.value.destroy()

    player.value = new Plyr(audioRef.value, {
        controls: ['play', 'progress', 'current-time', 'mute', 'volume', 'settings'],
        speed: { selected: 1, options: [0.5, 1, 1.5, 2] }
    })

    wavesurfer.value = WaveSurfer.create({
        container: waveformRef.value,
        media: audioRef.value,
        waveColor: '#e2e8f0', // Светло-серый для неактивной части
        progressColor: '#2563eb', // Насыщенный синий для прогресса
        barWidth: 2, // Чуть тоньше линии
        barGap: 3,
        barRadius: 4,
        height: 80,
        responsive: true,
        cursorColor: '#2563eb',
        cursorWidth: 2
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
        const response = await axios.post(`http://127.0.0.1:8000/api/audio/${props.id}/add_comment/`, {
            text: newComment.value,
            timestamp: currentPos
        }, {
            headers: { 'Authorization': `Token ${token}` }
        })
        newComment.value = ''
        emit('comment-added', response.data)
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

const skip = (amount) => {
    if (wavesurfer.value) {
        wavesurfer.value.skip(amount)
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
    <div
        class="flex flex-col w-full bg-white rounded-[2.5rem] border border-slate-100 p-10 shadow-2xl shadow-blue-900/10">

        <div class="flex items-center justify-between mb-10">
            <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-2xl bg-blue-50 flex items-center justify-center">
                    <i class="pi pi-volume-up text-blue-600"></i>
                </div>
                <div class="flex flex-col text-left">
                    <span class="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Режим
                        прослушивания</span>
                    <h4 class="text-base font-black text-slate-800">{{ title }}</h4>
                </div>
            </div>

            <div class="flex items-center gap-2">
                <span class="text-sm font-mono font-black text-blue-600">{{ currentTimeText }}</span>
                <span class="text-sm font-mono text-slate-300">/</span>
                <span class="text-sm font-mono text-slate-400">{{ durationText }}</span>
            </div>
        </div>

        <div class="relative mb-10 bg-gradient-to-b from-slate-50 to-white rounded-[2rem] p-8 border border-slate-50">
            <div ref="waveformRef" class="cursor-pointer"></div>
        </div>

        <div class="flex flex-col gap-10">
            <audio ref="audioRef" :src="src" crossorigin="anonymous" class="hidden"></audio>

            <div class="flex items-center gap-6">
                <div class="flex items-center gap-3 bg-slate-50 p-2 rounded-2xl border border-slate-100 shadow-sm">
                    <Button text rounded @click="skip(-10)"
                        class="!flex !items-center !justify-center !gap-1 !px-3 !py-2 !text-slate-400 hover:!text-blue-600 hover:!bg-white hover:shadow-sm transition-all">
                        <i class="pi pi-angle-left text-xs font-bold"></i>
                        <span class="text-[10px] font-black tracking-tighter">10с</span>
                    </Button>

                    <div class="w-[1px] h-4 bg-slate-200"></div>

                    <Button text rounded @click="skip(10)"
                        class="!flex !items-center !justify-center !gap-1 !px-3 !py-2 !text-slate-400 hover:!text-blue-600 hover:!bg-white hover:shadow-sm transition-all">
                        <span class="text-[10px] font-black tracking-tighter">10с</span>
                        <i class="pi pi-angle-right text-xs font-bold"></i>
                    </Button>
                </div>

                <div class="flex-1 custom-plyr-container">
                </div>

                <Button icon="pi pi-cloud-download" @click="handleDownload"
                    class="!text-[10px] !font-black !bg-slate-900 !border-none !text-white !px-8 !py-4 !rounded-2xl hover:!bg-blue-600 shadow-xl shadow-slate-200 transition-all"
                    label="ЭКСПОРТ" />
            </div>

            <div class="mt-8 pt-8 border-t border-slate-100">
                <div class="flex flex-col gap-2 text-left">
                    <span class="ml-2 text-[9px] font-black text-slate-400 uppercase tracking-widest">
                        Новая заметка на {{ currentTimeText }}
                    </span>

                    <div class="relative w-full flex items-center">
                        <InputText v-model="newComment" placeholder="Введите текст замечания..."
                            @keyup.enter="submitComment"
                            class="w-full !rounded-[1.25rem] !pl-6 !pr-14 !py-5 !border-slate-100 !bg-slate-50 focus:!bg-white focus:!border-blue-400 focus:!ring-4 focus:!ring-blue-50/50 transition-all !text-sm !font-medium" />

                        <Button @click="submitComment" :loading="isSubmitting"
                            class="!absolute right-2 !w-11 !h-11 !rounded-xl !bg-blue-600 !border-none !text-white hover:!bg-blue-700 active:scale-95 transition-all shadow-md shadow-blue-200">
                            <i class="pi pi-send text-sm"></i>
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Стилизация Plyr под CRM Ростовстата (белый, светлый) */
:deep(.plyr--audio .plyr__controls) {
    background: #f8fafc !important;
    /* Slate-50 */
    border-radius: 1.25rem !important;
    border: 1px solid #f1f5f9 !important;
    padding: 10px 15px !important;
    box-shadow: inset 0 2px 4px 0 rgb(0 0 0 / 0.03) !important;
}

:deep(.plyr--audio) {
    --plyr-color-main: #2563eb;
    /* Blue-600 */
}

/* Скрываем прогресс-бар Plyr, так как WaveSurfer — наш основной прогресс-бар */
:deep(.plyr__progress__container) {
    display: none !important;
}

:deep(.plyr__time) {
    font-size: 11px;
    font-family: monospace;
}

:deep(.p-button) {
    margin: 0;
}

:deep(.p-inputtext:enabled:focus) {
    box-shadow: none;
}
</style>