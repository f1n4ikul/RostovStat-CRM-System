<script setup>
import { computed } from 'vue'
import {
    Chart as ChartJS,
    Title,
    Tooltip,
    Legend,
    BarElement,
    CategoryScale,
    LinearScale,
    ArcElement
} from 'chart.js'
import { Bar, Pie } from 'vue-chartjs'

// Регистрируем модули Chart.js
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

const props = defineProps({
    stats: Object,
    records: Array
})
const someData = (props.records?.filter(r => r.status === 'ok')) || []

// 1. Логика для круговой диаграммы (Распределение по категориям)
const categoryData = computed(() => {
    const list = props.records || [] // Защита
    const counts = {}
    list.forEach(r => {
        counts[r.category] = (counts[r.category] || 0) + 1
    })

    // Красивые названия категорий для легенды
    const labelsMap = {
        'concentration': 'Концентрация',
        'pro': 'Проф. контент',
        'meeting': 'Совещания',
        'all': 'Общее'
    }

    return {
        labels: Object.keys(counts).map(k => labelsMap[k] || k),
        datasets: [{
            backgroundColor: ['#3b82f6', '#8b5cf6', '#f59e0b', '#10b981'],
            data: Object.values(counts)
        }]
    }
})

// 2. Логика для столбчатой диаграммы (Активность по дням)
const activityData = computed(() => {
    const list = props.records || [] // Защита
    const last7Days = [...Array(7)].map((_, i) => {
        const d = new Date()
        d.setDate(d.getDate() - i)
        return d.toISOString().split('T')[0]
    }).reverse()

    const counts = last7Days.map(date => {
        // Добавлен опциональный поиск
        return list.filter(r => r.created_at?.startsWith(date)).length
    })

    return {
        labels: last7Days.map(d => new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })),
        datasets: [{
            label: 'Загружено файлов',
            backgroundColor: '#3b82f6',
            borderRadius: 8,
            data: counts
        }]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Позволяет графику подстраиваться под размер контейнера
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                boxWidth: 10,
                usePointStyle: true,
                padding: 15, // Отступ между легендой и графиком
                font: { weight: 'bold', size: 10 }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            padding: 12,
            borderRadius: 10
        }
    },
    // Важно для Pie: отступы внутри самого холста
    layout: {
        padding: {
            top: 10,
            bottom: 10
        }
    }
}
</script>

<template>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm h-64 flex flex-col">
            <h5 class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-4">Активность (7 дней)</h5>
            <div class="bg-slate-50/50 p-4 rounded-3xl border border-slate-100 h-[280px] overflow-hidden">
                <Bar :data="activityData" :options="chartOptions" />
            </div>
        </div>
        <div class="flex flex-col">
            <h5 class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-4 italic ml-2">
                Типы контента
            </h5>
            <div
                class="bg-slate-50/50 p-4 rounded-3xl border border-slate-100 h-[280px] relative overflow-hidden flex justify-center">
                <Pie :data="categoryData" :options="chartOptions" />
            </div>
        </div>

        <!-- <div class="bg-white p-6 rounded-[2rem] border border-slate-100 shadow-sm h-64 flex flex-col">
            <h5 class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-4">По категориям</h5>
            <div class="flex-1 flex justify-center">
                <Pie :data="categoryData" :options="chartOptions" />
            </div>
        </div> -->
    </div>
</template>