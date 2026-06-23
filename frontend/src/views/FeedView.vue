<template>
    <Toast />
    <ConfirmDialog />

    <div class="min-h-screen bg-slate-50/50 pb-12">
        <div class="bg-white border-b border-slate-100 shadow-sm mb-8">
            <div
                class="max-w-7xl mx-auto px-4 py-6 md:py-8 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                    <div class="flex items-center gap-2.5">
                        <span class="w-2.5 h-6 bg-blue-600 rounded-full"></span>
                        <h1 class="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">
                            Информационная лента <span class="text-blue-600">Ростовстат</span>
                        </h1>
                    </div>
                    <p class="text-sm text-slate-500 mt-1.5 font-medium pl-3">
                        Ведомственные объявления, регламенты модернизации и оперативные сводки по подразделениям
                    </p>
                </div>
            </div>
        </div>

        <div class="max-w-7xl mx-auto px-4 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">

            <aside class="lg:col-span-4 bg-white p-5 rounded-2xl border border-slate-100 shadow-sm sticky top-6">
                <div class="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                        <i class="pi pi-filter"></i> Фильтр по ведомствам
                    </h3>
                    <span class="text-[11px] font-mono bg-slate-100 text-slate-600 px-2 py-0.5 rounded-md font-bold">
                        {{ departments.length - 1 }}
                    </span>
                </div>

                <div class="flex flex-row overflow-x-auto lg:flex-col gap-1.5 pb-3 lg:pb-0 scrollbar-none">
                    <button v-for="dept in departments" :key="dept.id" @click="currentDepartment = dept.id" :class="[
                        'w-full text-left px-4 py-3 text-xs font-semibold rounded-xl whitespace-nowrap lg:whitespace-normal transition-all duration-200 flex items-center gap-3 shrink-0 lg:shrink',
                        currentDepartment === dept.id
                            ? 'bg-blue-50 text-blue-700 shadow-sm ring-1 ring-blue-100 font-bold'
                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                    ]">
                        <span class="text-sm opacity-80">{{ dept.id === 'all' ? '🏛️' : '📁' }}</span>
                        <span class="leading-relaxed">{{ dept.name }}</span>
                    </button>
                </div>
            </aside>

            <main class="lg:col-span-8 space-y-6">

                <div v-if="isAdminOrModerator"
                    class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 relative overflow-hidden">
                    <div class="absolute top-0 left-0 right-0 h-[3px] bg-gradient-to-r from-blue-500 to-indigo-600">
                    </div>
                    <div class="flex items-center gap-2 mb-4">
                        <i class="pi pi-pencil text-blue-500 text-sm"></i>
                        <h3 class="text-sm font-bold text-slate-800 uppercase tracking-wide">Создать официальное
                            уведомление</h3>
                    </div>

                    <form @submit.prevent="createPost" class="space-y-4">
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div class="md:col-span-2">
                                <InputText v-model="newPost.title" placeholder="Краткий заголовок публикации..."
                                    required
                                    class="w-full !rounded-xl !p-3 !text-sm !bg-slate-50 !border-slate-100 focus:!border-blue-500 transition-all" />
                            </div>
                            <div>
                                <select v-model="newPost.department"
                                    class="w-full p-3 bg-slate-50 border border-slate-100 rounded-xl text-xs text-slate-600 font-medium outline-none focus:border-blue-500 h-full transition-all">
                                    <option v-for="dept in departments.filter(d => d.id !== 'all')" :key="dept.id"
                                        :value="dept.id">
                                        Для: {{ dept.name }}
                                    </option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <Textarea v-model="newPost.content" rows="4"
                                placeholder="Введите текст сообщения, методологические изменения или повестку дня..."
                                required
                                class="w-full !p-4 !bg-slate-50 !border-slate-100 !rounded-xl !text-sm focus:!border-blue-500 transition-all resize-none !leading-relaxed" />
                        </div>

                        <div class="flex justify-end pt-1">
                            <Button type="submit" :loading="isSubmitting" label="Опубликовать в реестр"
                                icon="pi pi-send"
                                class="!px-6 !py-3 !bg-blue-600 hover:!bg-blue-700 !text-white !font-bold !text-xs !rounded-xl !transition-all !shadow-md !border-none tracking-wide" />
                        </div>
                    </form>
                </div>

                <div v-if="filteredPosts.length > 0" class="space-y-5">
                    <div v-for="post in filteredPosts" :key="post.id"
                        class="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 md:p-8 hover:shadow-md hover:border-slate-200/80 transition-all relative group">

                        <button v-if="isAdminOrModerator" @click="deletePost(post.id)"
                            class="absolute top-6 right-6 text-slate-300 hover:text-red-500 hover:bg-red-50 p-2 rounded-xl transition-all lg:opacity-0 group-hover:opacity-100">
                            <i class="pi pi-trash text-sm"></i>
                        </button>

                        <div
                            class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-5 pb-4 border-b border-slate-50">
                            <div class="flex items-center space-x-3.5">
                                <Avatar :label="getInitials(post.author_name)" shape="circle" size="large"
                                    class="bg-gradient-to-br from-blue-600 to-indigo-600 text-white font-bold text-xs shadow-inner shrink-0" />
                                <div>
                                    <h4 class="text-sm font-bold text-slate-800 tracking-tight">{{ post.author_name ||
                                        'Сотрудник RostovStat' }}</h4>
                                    <p class="text-[11px] text-slate-400 font-mono flex items-center gap-1 mt-0.5">
                                        <i class="pi pi-clock text-[10px]"></i> {{ formatDate(post.created_at) }}
                                    </p>
                                </div>
                            </div>

                            <span
                                class="self-start sm:self-center px-3 py-1.5 text-[10px] font-bold uppercase tracking-wider rounded-lg bg-slate-50 text-slate-500 border border-slate-200/60 max-w-[280px] truncate sm:mr-8">
                                {{ post.department_name || 'Общий отдел' }}
                            </span>
                        </div>

                        <h2 class="text-xl font-black text-slate-900 mb-3 tracking-tight leading-snug">{{ post.title }}
                        </h2>
                        <p class="text-slate-600 text-sm leading-relaxed whitespace-pre-line mb-6 font-medium">{{
                            post.content || post.text }}</p>

                        <div class="flex items-center gap-3 border-t border-slate-100 pt-4">
                            <button @click="toggleLike(post)"
                                :class="['flex items-center space-x-2 text-xs font-bold px-3 py-2 rounded-xl transition-all', post.is_liked ? 'bg-red-50 text-red-600' : 'bg-slate-50 text-slate-500 hover:bg-slate-100']">
                                <i :class="[post.is_liked ? 'pi pi-heart-fill' : 'pi pi-heart']"></i>
                                <span class="font-mono">{{ post.likes_count || 0 }}</span>
                            </button>

                            <button @click="openComments(post)"
                                class="flex items-center space-x-2 text-xs font-bold px-4 py-2 bg-slate-50 text-slate-500 hover:bg-blue-50 hover:text-blue-600 rounded-xl transition-all ml-1">
                                <i class="pi pi-comments"></i>
                                <span>Обсуждение ({{ post.comments?.length || 0 }})</span>
                            </button>
                        </div>
                    </div>
                </div>

                <div v-else
                    class="text-center py-20 bg-white rounded-2xl border border-dashed border-slate-200 shadow-inner p-6">
                    <div
                        class="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-100">
                        <i class="pi pi-folder-open text-slate-400 text-xl"></i>
                    </div>
                    <h4 class="text-slate-800 font-bold text-sm mb-1">Реестр пуст</h4>
                    <p class="text-slate-400 text-xs max-w-xs mx-auto leading-normal">
                        В выбранном ведомственном разделе пока нет опубликованных приказов или новостей.
                    </p>
                </div>
            </main>

        </div>
    </div>

    <Dialog v-model:visible="isCommentsVisible" modal :style="{ width: '38rem' }" :breakpoints="{ '960px': '95vw' }"
        class="custom-feed-dialog" :showHeader="false">
        <div v-if="selectedPost" class="p-6 md:p-8 flex flex-col h-full max-h-[85vh]">

            <div class="flex items-center justify-between mb-5 pb-3 border-b border-slate-100">
                <div>
                    <span
                        class="text-[9px] font-bold uppercase text-blue-600 bg-blue-50 px-2 py-0.5 rounded tracking-wide mb-1 inline-block">Комментарии</span>
                    <h3 class="font-black text-base text-slate-900 truncate max-w-[280px] md:max-w-[400px]">{{
                        selectedPost.title }}</h3>
                </div>
                <Button icon="pi pi-times" severity="secondary" rounded text @click="isCommentsVisible = false"
                    class="!w-8 !h-8" />
            </div>

            <div class="comments-container overflow-y-auto space-y-3.5 pr-2 flex-1 mb-6 max-h-[350px]">
                <div v-for="comment in selectedPost.comments" :key="comment.id"
                    class="bg-slate-50 p-4 rounded-xl border border-slate-100">
                    <div class="flex justify-between items-center mb-1.5">
                        <span class="text-xs font-bold text-slate-800">{{ comment.author }}</span>
                        <span class="text-[10px] text-slate-400 font-mono">{{ formatDate(comment.created_at) }}</span>
                    </div>
                    <p class="text-slate-600 text-xs leading-relaxed font-medium">{{ comment.text }}</p>
                </div>

                <div v-if="!selectedPost.comments?.length" class="text-center py-8">
                    <i class="pi pi-comment text-slate-200 text-3xl mb-2 block"></i>
                    <p class="text-slate-400 text-xs">Будьте первым, кто прокомментирует запись!</p>
                </div>
            </div>

            <div class="flex gap-2.5 items-center pt-3 border-t border-slate-100">
                <InputText v-model="newComment" placeholder="Ваш комментарий для коллег..." @keyup.enter="sendComment"
                    class="flex-1 !rounded-xl !p-3 !text-xs !bg-slate-50 !border-slate-100 focus:!border-blue-500 transition-all shadow-inner" />
                <Button @click="sendComment" icon="pi pi-send"
                    class="!w-10 !h-10 !rounded-xl !bg-blue-600 hover:!bg-blue-700 !text-white !border-none transition-all shadow-md shrink-0" />
            </div>
        </div>
    </Dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import InputText from 'primevue/inputtext'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog'
import Toast from 'primevue/toast'
import { useToast } from "primevue/usetoast"
import ConfirmDialog from 'primevue/confirmdialog'
import { useConfirm } from "primevue/useconfirm"

const toast = useToast()
const confirm = useConfirm()

// Дефолтные стартовые посты, если localStorage пустой
const defaultPosts = [
    {
        id: 991,
        title: "Переход на СУБД PostgreSQL завершен",
        content: "Уважаемые коллеги! Техническая служба ИТ-отдела успешно завершила миграцию баз данных корпоративных сервисов RostovStat на отечественную СУБД PostgreSQL в рамках комплексной программы модернизации.\n\nВсе учетные записи сотрудников, логи безопасности и сессии авторизации сохранены в штатном режиме. Скорость обработки аналитических реестров увеличена на 35%. В случае фиксации сбоев незамедлительно направляйте тикет в техподдержку.",
        author_name: "Администратор системы",
        department: "common",
        department_name: "Общий отдел",
        created_at: new Date().toISOString(),
        likes_count: 8,
        is_liked: false,
        comments: [
            { id: 1, author: "Смирнова Е.В.", text: "Отличная новость, медиатека теперь подгружается мгновенно!", created_at: new Date().toISOString() }
        ]
    },
    {
        id: 992,
        title: "Сбор квартальной статотчетности по региону",
        content: "Напоминаем начальникам аналитических подразделений о подготовке к выгрузке отчетных макроэкономических показателей Ростовской области за текущий рабочий период.\n\nСводные таблицы, методологические изменения и аудиозаписи внутренних совещаний по согласованию статистических критериев необходимо структурировать и загрузить в локальное хранилище системы до пятницы включительно.",
        author_name: "Модератор ленты",
        department: "svod",
        department_name: "Отдел сводных статических работ и общественных связей",
        created_at: new Date(Date.now() - 7200000).toISOString(),
        likes_count: 4,
        is_liked: false,
        comments: []
    }
]

const posts = ref([])
const selectedPost = ref(null)
const isCommentsVisible = ref(false)
const newComment = ref('')
const isSubmitting = ref(false)

const currentUser = ref({
    username: 'Администратор системы',
    role: 'admin',
    department: 'common'
})

const isAdminOrModerator = computed(() => {
    return currentUser.value.role === 'admin' || currentUser.value.role === 'moderator';
})

const currentDepartment = ref('all')
const departments = ref([
    { id: 'all', name: 'Все отделы' },
    { id: 'common', name: 'Общий отдел' },
    { id: 'svod', name: 'Отдел сводных статических работ и общественных связей' },
    { id: 'balance', name: 'Отдел региональных счетов и балансов' },
    { id: 'finance', name: 'Отдел статистики цен и финансов' },
    { id: 'agro', name: 'Отдел статистики сельского хозяйства и окружающей природной среды' },
    { id: 'enterprise', name: 'Отдел статистики предприятий' },
    { id: 'services', name: 'Отдел статистики рыночных услуг' },
    { id: 'labor', name: 'Отдел статистики труда, образования, науки и инноваций' },
    { id: 'living', name: 'Отдел статистики уровня жизни и обследований домашних хозяйств' },
    { id: 'building', name: 'Отдел статистики строительства, инвестиций и жилищно-коммунального хозяйства' },
    { id: 'population', name: 'Отдел статистики населения и здравоохранения, организации и проведения переписей и обследований' }
])

const newPost = ref({
    title: '',
    content: '',
    department: 'common'
})

// Синхронизация данных с localStorage
const saveToStorage = () => {
    localStorage.setItem('rostovstat_posts', JSON.stringify(posts.value))
}

const filteredPosts = computed(() => {
    if (currentDepartment.value === 'all') return posts.value;
    return posts.value.filter(post => post.department === currentDepartment.value);
});

const loadPosts = () => {
    const saved = localStorage.getItem('rostovstat_posts')
    if (saved) {
        try {
            posts.value = JSON.parse(saved)
        } catch (e) {
            posts.value = defaultPosts
        }
    } else {
        posts.value = defaultPosts
        saveToStorage()
    }
}

const createPost = () => {
    if (!isAdminOrModerator.value || !newPost.value.content.trim() || !newPost.value.title.trim()) return

    isSubmitting.value = true

    // Имитируем небольшую задержку сети для реалистичности анимации кнопки (loading)
    setTimeout(() => {
        const targetDept = departments.value.find(d => d.id === newPost.value.department)

        const created = {
            id: Date.now(),
            title: newPost.value.title,
            content: newPost.value.content,
            author_name: currentUser.value.username,
            department: newPost.value.department,
            department_name: targetDept ? targetDept.name : 'Общий отдел',
            created_at: new Date().toISOString(),
            likes_count: 0,
            is_liked: false,
            comments: []
        }

        posts.value.unshift(created)
        saveToStorage()

        // Очищаем форму
        newPost.value.title = ''
        newPost.value.content = ''
        newPost.value.department = 'common'

        isSubmitting.value = false
        toast.add({ severity: 'success', summary: 'Успех', detail: 'Сообщение успешно добавлено в реестр', life: 3000 });
    }, 600)
}

const toggleLike = (post) => {
    post.is_liked = !post.is_liked
    post.likes_count = post.is_liked ? (post.likes_count + 1) : (post.likes_count - 1)
    saveToStorage()
}

const openComments = (post) => {
    selectedPost.value = post
    isCommentsVisible.value = true
}

const sendComment = () => {
    if (!newComment.value.trim() || !selectedPost.value) return

    if (!selectedPost.value.comments) selectedPost.value.comments = []

    selectedPost.value.comments.unshift({
        id: Date.now(),
        author: currentUser.value.username,
        text: newComment.value,
        created_at: new Date().toISOString()
    })

    newComment.value = ''
    saveToStorage()
}

const deletePost = (postId) => {
    confirm.require({
        message: 'Вы уверены, что хотите безвозвратно удалить это сообщение из ленты?',
        header: 'Подтверждение удаления',
        icon: 'pi pi-exclamation-triangle',
        rejectLabel: 'Отмена',
        acceptLabel: 'Удалить',
        rejectClass: 'p-button-secondary p-button-text',
        acceptClass: 'p-button-danger',
        accept: () => {
            posts.value = posts.value.filter(post => post.id !== postId)
            saveToStorage()
            toast.add({ severity: 'success', summary: 'Удалено', detail: 'Запись стерта из локальной системы', life: 3000 });
        }
    });
}

const getInitials = (name) => {
    if (!name) return 'РС';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
}

const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
        return new Date(dateString).toLocaleString('ru-RU', {
            day: 'numeric',
            month: 'short',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return dateString;
    }
}

onMounted(() => {
    loadPosts()
})
</script>

<style scoped>
.scrollbar-none::-webkit-scrollbar {
    display: none;
}

.scrollbar-none {
    -ms-overflow-style: none;
    scrollbar-width: none;
}

:deep(.custom-feed-dialog) {
    border-radius: 1.25rem !important;
    border: none !important;
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15) !important;
}

:deep(.p-dialog-content) {
    padding: 0 !important;
}

.comments-container::-webkit-scrollbar {
    width: 4px;
}

.comments-container::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 10px;
}
</style>