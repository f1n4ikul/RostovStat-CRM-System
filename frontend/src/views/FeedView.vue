<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import Button from 'primevue/button'
import Textarea from 'primevue/textarea'
import Avatar from 'primevue/avatar'
import Dialog from 'primevue/dialog';

const isCommentsVisible = ref(false);
const selectedPost = ref(null);
const newComment = ref('');

const mainNews = ref(null)
const regionalStats = ref([])

const fetchPortalData = async () => {
    try {
        // Загружаем важную новость
        const newsRes = await axios.get('http://127.0.0.1:8000/api/news/latest/')
        mainNews.value = newsRes.data

        // Загружаем стат. показатели
        const statsRes = await axios.get('http://127.0.0.1:8000/api/stats-widget/')
        regionalStats.value = statsRes.data
    } catch (err) {
        console.error("Ошибка при загрузке данных портала", err)
    }
}

onMounted(() => {
    fetchPosts()
    fetchPortalData()
})

const openComments = (post) => {
    selectedPost.value = post;
    isCommentsVisible.value = true;
    // Здесь можно вызвать axios.get для подгрузки комментов, если их нет в объекте post
};

const sendComment = async () => {
    if (!newComment.value.trim()) return;
    try {
        // Добавляем полный путь к API
        const response = await axios.post(`http://127.0.0.1:8000/api/posts/${selectedPost.value.id}/comments/`, {
            text: newComment.value
        });

        // Проверяем, существует ли массив комментариев в объекте поста
        if (!selectedPost.value.comments) {
            selectedPost.value.comments = [];
        }

        // Добавляем новый комментарий в начало списка
        selectedPost.value.comments.unshift(response.data);

        // Очищаем поле ввода
        newComment.value = '';
    } catch (err) {
        console.error("Ошибка при отправке комментария:", err);
        // Можно добавить уведомление для пользователя, если есть Toast
    }
};

const posts = ref([])
const newPostContent = ref('')
const isSubmitting = ref(false)

const fetchPosts = async () => {
    try {
        const response = await axios.get('http://127.0.0.1:8000/api/posts/')
        posts.value = response.data
    } catch (err) {
        console.error("Ошибка загрузки ленты", err)
    }
}

const createPost = async () => {
    if (!newPostContent.value.trim()) return
    isSubmitting.value = true
    try {
        await axios.post('http://127.0.0.1:8000/api/posts/', { text: newPostContent.value })
        newPostContent.value = ''
        await fetchPosts()
    } finally {
        isSubmitting.value = false
    }
}

// ФУНКЦИЯ ЛАЙКА
const toggleLike = async (post) => {
    try {
        // Мы используем эндпоинт, который создали в Django
        const response = await axios.post(`http://127.0.0.1:8000/api/posts/${post.id}/like/`)

        // Обновляем локальное состояние поста, чтобы не перекачивать всю ленту
        post.is_liked = response.data.is_liked
        if (post.is_liked) {
            post.likes_count++
        } else {
            post.likes_count--
        }
    } catch (err) {
        console.error("Ошибка при лайке", err)
    }
}



onMounted(fetchPosts)
</script>

<template>
    <div class="max-w-[1400px] mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">

            <div class="lg:col-span-8 space-y-6">

                <div class="bg-gradient-to-r from-blue-700 to-blue-500 rounded-[2rem] p-8 text-white shadow-lg">
                    <div class="flex justify-between items-start">
                        <div>
                            <span
                                class="bg-white/20 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-widest">Важное</span>
                            <h2 class="text-3xl font-black mt-4 mb-2">Отчетность за I квартал 2026</h2>
                            <p class="text-blue-50 opacity-90">Всем отделам необходимо загрузить актуальные данные до 15
                                апреля. Инструкции доступны в медиатеке.</p>
                        </div>
                        <i class="pi pi-megaphone text-5xl opacity-20"></i>
                    </div>
                    <Button label="Подробнее"
                        class="mt-6 !bg-white !text-blue-700 !border-none !rounded-xl font-bold" />
                </div>

                <h3 class="text-xl font-black text-slate-800 flex items-center gap-2 px-2">
                    <i class="pi pi- list text-blue-600"></i> Активность сотрудников
                </h3>

                <div v-for="post in posts" :key="post.id"
                    class="bg-white rounded-[2rem] border border-slate-100 shadow-sm overflow-hidden hover:shadow-md transition-shadow">
                    <div class="p-6">
                        <div class="flex items-center gap-3 mb-4">
                            <Avatar :label="post.author_name?.[0]" shape="circle" class="bg-blue-100 text-blue-600" />
                            <div class="flex flex-col">
                                <span class="font-bold text-slate-800">{{ post.author_name }}</span>
                                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                    {{ new Date(post.created_at).toLocaleString() }}
                                </span>
                            </div>
                        </div>
                        <p class="text-slate-600 leading-relaxed whitespace-pre-wrap">{{ post.text }}</p>
                    </div>

                    <div class="px-6 py-3 bg-slate-50/50 border-t border-slate-50 flex gap-4">
                        <Button :icon="post.is_liked ? 'pi pi-heart-fill' : 'pi pi-heart'" text
                            :severity="post.is_liked ? 'danger' : 'secondary'" :label="String(post.likes_count || 0)"
                            class="!text-xs transition-colors" @click="toggleLike(post)" />
                        <Button icon="pi pi-comment" label="Обсудить" class="p-button-text"
                            @click="openComments(post)" />
                    </div>
                </div>
            </div>

            <div class="lg:col-span-4 space-y-6">

                <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
                    <h4 class="font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <i class="pi pi-pencil text-blue-500"></i> Написать сообщение
                    </h4>
                    <div class="flex flex-col gap-3">
                        <Textarea v-model="newPostContent" autoResize rows="3" placeholder="Поделитесь новостью..."
                            class="!w-full !border-none !bg-slate-50 !rounded-2xl !p-4 focus:!ring-2 focus:!ring-blue-100 transition-all text-sm" />
                        <Button label="Опубликовать" icon="pi pi-send" @click="createPost" :loading="isSubmitting"
                            class="!rounded-xl !bg-blue-600 !border-none w-full" />
                    </div>
                </div>

                <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
                    <h4 class="font-bold text-slate-800 mb-4">Показатели региона</h4>
                    <div class="space-y-4">
                        <div class="flex justify-between items-center p-3 bg-green-50 rounded-2xl">
                            <span class="text-sm text-green-700 font-medium">Инфляция (мес)</span>
                            <span class="font-black text-green-600">+0.4%</span>
                        </div>
                        <div class="flex justify-between items-center p-3 bg-blue-50 rounded-2xl">
                            <span class="text-sm text-blue-700 font-medium">ВРП рост</span>
                            <span class="font-black text-blue-600">+2.1%</span>
                        </div>
                    </div>
                </div>

                <div class="bg-white p-6 rounded-[2rem] shadow-sm border border-slate-100">
                    <h4 class="font-bold text-slate-800 mb-4">Быстрые ссылки</h4>
                    <div class="flex flex-col gap-2">
                        <a href="https://61.rosstat.gov.ru/"
                            class="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-xl transition-all text-sm text-slate-600">
                            <i class="pi pi-external-link text-blue-500"></i> Сайт Росстата
                        </a>
                        <a href="#"
                            class="flex items-center gap-3 p-2 hover:bg-slate-50 rounded-xl transition-all text-sm text-slate-600">
                            <i class="pi pi-file-pdf text-red-500"></i> Регламент 2026
                        </a>
                    </div>
                </div>

            </div>

        </div>

        <Dialog v-model:visible="isCommentsVisible" header="Обсуждение" :modal="true" class="custom-dialog"
            :style="{ width: '90vw', maxWidth: '600px' }">
        </Dialog>
    </div>
</template>
<style scoped>
/* Стили для скругления самой модалки PrimeVue */
:deep(.custom-dialog) {
    border-radius: 2rem !important;
    overflow: hidden;
    border: none !important;
}

:deep(.custom-dialog .p-dialog-header) {
    padding: 1.5rem 1.5rem 0.5rem 1.5rem;
    background: white;
    border: none;
}

:deep(.custom-dialog .p-dialog-content) {
    padding: 0 1.5rem 1.5rem 1.5rem;
    background: white;
}

/* Красивый скроллбар для списка комментов */
.comments-container::-webkit-scrollbar {
    width: 4px;
}

.comments-container::-webkit-scrollbar-track {
    background: transparent;
}

.comments-container::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
}
</style>