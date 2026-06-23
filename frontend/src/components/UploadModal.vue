<script setup>
import { ref } from 'vue'
import axios from 'axios'
import Swal from 'sweetalert2'

import InputText from 'primevue/inputtext'
import Textarea from 'primevue/textarea'
import Select from 'primevue/select'
import Button from 'primevue/button'
import Checkbox from 'primevue/checkbox'
import FileUpload from 'primevue/fileupload'

const emit = defineEmits(['close', 'uploaded'])

const title = ref('')
const description = ref('')
const category = ref('svod') // По умолчанию выставляем первый отдел
const tags = ref('')
const isPrivate = ref(false)
const file = ref(null)
const extraFiles = ref([])
const isUploading = ref(false)

// Структура отделов Ростовстата для классификации медиаматериалов
const categories = [
  { value: 'svod', label: 'Отдел сводных статических работ и общественных связей', icon: '📊' },
  { value: 'accounts', label: 'Отдел региональных счетов и балансов', icon: '📈' },
  { value: 'prices', label: 'Отдел статистики цен и финансов', icon: '💰' },
  { value: 'agriculture', label: 'Отдел статистики сельского хозяйства и окружающей среды', icon: '🌱' },
  { value: 'enterprises', label: 'Отдел статистики предприятий', icon: '🏢' },
  { value: 'services', label: 'Отдел статистики рыночных услуг', icon: '🛒' },
  { value: 'labor', label: 'Отдел статистики труда, образования, науки и инноваций', icon: '👥' },
  { value: 'living_stand', label: 'Отдел статистики уровня жизни и обследований ДХ', icon: '🏠' },
  { value: 'construction', label: 'Отдел статистики строительства, инвестиций и ЖКХ', icon: '🏗️' },
  { value: 'population', label: 'Отдел статистики населения, здравоохранения и переписей', icon: '🏥' },
]

const onFileSelect = (e) => {
  file.value = e.files[0]
}

// Корректное накопление дополнительных документов
const onExtraFilesSelect = (e) => {
  extraFiles.value = Array.from(e.files)
}

const removeExtraFile = (i) => {
  extraFiles.value.splice(i, 1)
}

const upload = async () => {
  if (!file.value || !title.value) {
    return Swal.fire({ icon: 'warning', title: 'Внимание', text: 'Укажите название и выберите MP4-файл', confirmButtonColor: '#3b82f6' })
  }

  if (!file.value.name.toLowerCase().endsWith('.mp4')) {
    return Swal.fire({ icon: 'error', title: 'Неверный формат', text: 'Допускается загрузка только файлов MP4 (.mp4)', confirmButtonColor: '#3b82f6' })
  }

  const formData = new FormData()
  const token = localStorage.getItem('user-token')

  formData.append('title', title.value)
  formData.append('description', description.value)
  formData.append('category', category.value)
  formData.append('tags', tags.value)
  formData.append('is_private', isPrivate.value ? '1' : '0')
  formData.append('file', file.value)

  // Добавление сопутствующих документов ведомства
  extraFiles.value.forEach(f => formData.append('documents', f))

  isUploading.value = true
  Swal.fire({ title: 'Загрузка на сервер...', didOpen: () => Swal.showLoading(), allowOutsideClick: false })

  try {
    await axios.post('http://127.0.0.1:8000/api/upload/', formData, {
      headers: { 'Content-Type': 'multipart/form-data', Authorization: `Token ${token}` }
    })
    await Swal.fire({ icon: 'success', title: 'Успешно опубликовано', timer: 1000, showConfirmButton: false })
    window.dispatchEvent(new CustomEvent('track-uploaded'))
    emit('uploaded')
    emit('close')
  } catch (err) {
    Swal.fire({
      icon: 'error',
      title: 'Ошибка загрузки',
      text: err.response?.data?.error || err.response?.data?.file?.[0] || 'Внутренняя ошибка сервера'
    })
  } finally {
    isUploading.value = false
  }
}
</script>

<template>
  <div class="fixed inset-0 bg-black/40 backdrop-blur-md flex items-center justify-center p-4 z-50 overflow-y-auto">
    <div class="bg-white p-8 rounded-3xl w-full max-w-md shadow-2xl border border-slate-100 my-auto">

      <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-black text-slate-800 tracking-tight">Новая запись</h3>
        <Button icon="pi pi-times" severity="secondary" rounded text @click="emit('close')" />
      </div>

      <div class="flex flex-col gap-5">
        <div class="flex flex-col gap-1">
          <label class="field-label">Название записи / Протокола</label>
          <InputText v-model="title" placeholder="Напр: Совещание по балансам региональных счетов"
            class="w-full !rounded-xl" />
        </div>

        <div class="flex flex-col gap-1">
          <label class="field-label">Отдел-инициатор (Категория)</label>
          <Select v-model="category" :options="categories" optionLabel="label" optionValue="value"
            placeholder="Выберите подразделение" class="w-full !rounded-xl text-xs">
            <template #option="{ option }">
              <div class="flex items-center gap-3 py-0.5 max-w-[320px]">
                <span class="text-base shrink-0">{{ option.icon }}</span>
                <span class="text-xs text-slate-700 leading-snug break-words">{{ option.label }}</span>
              </div>
            </template>
            <template #value="{ value }">
              <div v-if="value" class="flex items-center gap-2 max-w-[280px]">
                <span class="shrink-0">{{categories.find(c => c.value === value)?.icon}}</span>
                <span class="truncate text-xs text-slate-800">{{categories.find(c => c.value === value)?.label
                  }}</span>
              </div>
              <span v-else class="text-slate-400 text-xs">Выберите подразделение</span>
            </template>
          </Select>
        </div>

        <div class="flex flex-col gap-3">
          <InputText v-model="tags" placeholder="Ключевые слова (через запятую)" class="w-full !rounded-xl" />
          <Textarea v-model="description" rows="2" autoResize placeholder="Краткое содержание или повестка дня..."
            class="w-full !rounded-xl" />
        </div>

        <div class="flex flex-col gap-1">
          <label class="field-label">Медиафайл записи (.MP4)</label>
          <FileUpload mode="basic" @select="onFileSelect" accept=".mp4,audio/mp4,video/mp4" :maxFileSize="200000000"
            chooseLabel="Выбрать файл MP4" class="p-button-outlined p-button-secondary w-full !rounded-xl" />
          <div class="flex items-center justify-between mt-1 ml-1">
            <small v-if="file" class="text-blue-600 font-bold flex items-center gap-1 truncate max-w-[220px]">
              <i class="pi pi-check-circle"></i> {{ file.name }}
            </small>
            <small class="text-slate-400 text-[10px] ml-auto">Медиапоток MP4 · До 200 МБ</small>
          </div>
        </div>

        <div class="flex flex-col gap-1">
          <label class="field-label">Сопутствующие отчеты / нормативные акты</label>
          <FileUpload mode="basic" @select="onExtraFilesSelect" :multiple="true"
            accept=".pdf,.doc,.docx,.xls,.xlsx,.csv" chooseLabel="Прикрепить документы" severity="info"
            class="p-button-outlined w-full !rounded-xl" />

          <div v-if="extraFiles.length" class="flex flex-col gap-1.5 mt-2 max-h-[100px] overflow-y-auto p-0.5">
            <div v-for="(f, i) in extraFiles" :key="f.name"
              class="text-[10px] bg-slate-50 px-2.5 py-1.5 rounded-lg text-slate-600 border border-slate-200 flex items-center justify-between gap-2">
              <span class="truncate flex items-center gap-1">📎 {{ f.name }}</span>
              <i class="pi pi-times cursor-pointer text-slate-400 hover:text-red-500 text-[9px]"
                @click="removeExtraFile(i)" />
            </div>
          </div>
        </div>

        <div class="flex items-center gap-3 p-1">
          <Checkbox v-model="isPrivate" binary id="private-check" />
          <label for="private-check" class="text-sm font-semibold text-slate-600 cursor-pointer select-none">
            Ограничить доступ (только для сотрудников отдела)
          </label>
        </div>

        <div class="flex gap-3 pt-2">
          <Button @click="upload" :loading="isUploading" label="Опубликовать в архив"
            class="flex-[2] !py-4 !rounded-2xl !font-bold !bg-blue-600 !border-none" />
          <Button @click="emit('close')" label="Отмена" severity="secondary" text
            class="flex-1 !py-4 !rounded-2xl !font-bold" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@reference "../style.css";

.field-label {
  @apply text-[10px] font-bold uppercase text-slate-400 ml-1 tracking-wider;
}

:deep(.p-inputtext),
:deep(.p-select),
:deep(.p-textarea) {
  border-color: #f1f5f9 !important;
  background-color: #f8fafc !important;
}

:deep(.p-inputtext:focus),
:deep(.p-select:focus),
:deep(.p-textarea:focus) {
  box-shadow: 0 0 0 2px #3b82f633 !important;
  border-color: #3b82f6 !important;
}

:deep(.p-select-overlay) {
  max-width: 360px !important;
}

@media (max-height: 800px) {
  .fixed {
    align-items: flex-start;
  }
}
</style>