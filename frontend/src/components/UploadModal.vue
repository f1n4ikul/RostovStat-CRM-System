<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

// Импортируем компоненты PrimeVue
import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import FileUpload from 'primevue/fileupload'

const title = ref('')
const description = ref('')
const category = ref('other')
const isPrivate = ref(false)
const file = ref(null)
const tags = ref('')
const isUploading = ref(false)

const emit = defineEmits(['close', 'uploaded'])

const categories = [
    { value: 'other', label: 'Прочее', icon: '📁' },
    { value: 'concentration', label: 'Музыка для концентрации', icon: '🎧' },
    { value: 'pro', label: 'Профессиональный контент', icon: '💼' },
    { value: 'relax', label: 'Психологическая разгрузка', icon: '🍃' },
    { value: 'meeting', label: 'Совещание', icon: '👥' }
]

// Метод для обработки выбора файла (через кастомное событие PrimeVue)
const onFileSelect = (event) => {
    file.value = event.files[0]
}

const upload = async () => {
    if (!file.value || !title.value) {
        return Swal.fire({
            icon: 'warning',
            title: 'Внимание',
            text: 'Укажите название и выберите файл',
            confirmButtonColor: '#3b82f6'
        })
    }

    const formData = new FormData()
    const token = localStorage.getItem('user-token')

    formData.append('title', title.value)
    formData.append('description', description.value)
    formData.append('category', category.value)
    formData.append('tags', tags.value)
    formData.append('is_private', isPrivate.value ? 'true' : 'false')
    formData.append('file', file.value)

    isUploading.value = true
    Swal.fire({
        title: 'Загрузка...',
        didOpen: () => Swal.showLoading(),
        allowOutsideClick: false
    })

    try {
        await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
                'Authorization': `Token ${token}`
            }
        })
        await Swal.fire({ icon: 'success', title: 'Готово', timer: 1500, showConfirmButton: false })
        emit('uploaded')
        emit('close')
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Ошибка', text: error.response?.data?.error || 'Ошибка сервера' })
    } finally {
        isUploading.value = false
    }
}
</script>

<template>
    <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-center justify-center p-4 z-50">
        <div
            class="bg-white p-8 rounded-3xl w-full max-w-md shadow-2xl animate-in fade-in zoom-in duration-300 border border-slate-100">

            <div class="flex justify-between items-center mb-6">
                <h3 class="text-2xl font-black text-slate-800 tracking-tight">Новая запись</h3>
                <Button icon="pi pi-times" severity="secondary" rounded text @click="emit('close')" />
            </div>

            <div class="flex flex-col gap-5">
                <div class="flex flex-col gap-1">
                    <label class="text-[10px] font-bold uppercase text-slate-400 ml-1">Название</label>
                    <InputText v-model="title" placeholder="Напр: Отчет за март" class="w-full !rounded-xl" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-[10px] font-bold uppercase text-slate-400 ml-1">Категория</label>
                    <Select v-model="category" :options="categories" optionLabel="label" optionValue="value"
                        placeholder="Выберите категорию" class="w-full !rounded-xl">
                        <template #option="slotProps">
                            <div class="flex items-center gap-3">
                                <span>{{ slotProps.option.icon }}</span>
                                <span>{{ slotProps.option.label }}</span>
                            </div>
                        </template>
                        <template #value="slotProps">
                            <div v-if="slotProps.value" class="flex items-center gap-2">
                                <span>{{categories.find(c => c.value === slotProps.value)?.icon}}</span>
                                <span>{{categories.find(c => c.value === slotProps.value)?.label}}</span>
                            </div>
                            <span v-else>{{ slotProps.placeholder }}</span>
                        </template>
                    </Select>
                </div>

                <div class="flex flex-col gap-4">
                    <InputText v-model="tags" placeholder="Теги через запятую" class="w-full !rounded-xl" />
                    <Textarea v-model="description" rows="2" autoResize placeholder="Описание записи..."
                        class="w-full !rounded-xl" />
                </div>

                <div class="flex flex-col gap-1">
                    <label class="text-[10px] font-bold uppercase text-slate-400 ml-1">Аудиофайл</label>
                    <FileUpload mode="basic" @select="onFileSelect" accept="audio/*" :maxFileSize="50000000"
                        chooseLabel="Выбрать файл" class="p-button-outlined p-button-secondary w-full !rounded-xl" />
                    <small v-if="file" class="text-blue-600 font-bold ml-1 mt-1">✓ {{ file.name }}</small>
                </div>

                <div class="flex items-center gap-3 p-1">
                    <Checkbox v-model="isPrivate" binary id="private-check" />
                    <label for="private-check" class="text-sm font-semibold text-slate-600 cursor-pointer">Приватный
                        доступ</label>
                </div>

                <div class="flex gap-3 pt-2">
                    <Button @click="upload" :loading="isUploading" label="Опубликовать"
                        class="flex-[2] !py-4 !rounded-2xl !font-bold !bg-blue-600 !border-none" />
                    <Button @click="emit('close')" label="Отмена" severity="secondary" text
                        class="flex-1 !py-4 !rounded-2xl !font-bold" />
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
/* Убираем стандартные синие обводки, если они конфликтуют с Tailwind */
:deep(.p-inputtext),
:deep(.p-select),
:deep(.p-textarea) {
    border-color: #f1f5f9 !important;
    background-color: #f8fafc !important;
}

:deep(.p-inputtext:focus),
:deep(.p-select:focus) {
    box-shadow: 0 0 0 2px #3b82f6 !important;
}
</style>