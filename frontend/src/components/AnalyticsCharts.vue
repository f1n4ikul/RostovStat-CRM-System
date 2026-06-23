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

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement)

const props = defineProps({
    stats: Object,
    records: Array
})

// Логика распределения по категориям
const categoryData = computed(() => {
    const list = props.records || []
    const counts = {}
    list.forEach(r => {
        counts[r.category] = (counts[r.category] || 0) + 1
    })

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

// Столбчатая диаграмма активности по дням
const activityData = computed(() => {
    const list = props.records || []
    const last7Days = [...Array(7)].map((_, i) => {
        const d = new Date()
        d.setDate(d.getDate() - i)
        return d.toISOString().split('T')[0]
    }).reverse()

    const counts = last7Days.map(date => {
        return list.filter(r => r.created_at?.startsWith(date)).length
    })

    return {
        labels: last7Days.map(d => new Date(d).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })),
        datasets: [{
            label: 'Загружено файлов',
            backgroundColor: '#3b82f6',
            borderRadius: 6,
            data: counts
        }]
    }
})

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false, // Разрешаем кастомизацию контейнером
    plugins: {
        legend: {
            position: 'bottom',
            labels: {
                boxWidth: 8,
                usePointStyle: true,
                padding: 12,
                font: { weight: 'bold', size: 10 }
            }
        },
        tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.9)',
            padding: 10,
            borderRadius: 8
        }
    },
    layout: {
        padding: { top: 5, bottom: 5 }
    }
}
</script>

<template>
    <!-- Изменили на grid-cols-1 lg:grid-cols-2 для лучшего распределения пространства -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">

        <!-- График 1: Активность -->
        <div class="bg-slate-50/60 p-4 rounded-2xl border border-slate-100 flex flex-col w-full">
            <h5 class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-3">Активность (7 дней)</h5>
            <!-- Контейнер с явной высотой для корректного рендеринга ChartJS -->
            <div class="h-[240px] md:h-[280px] w-full relative">
                <Bar :data="activityData" :options="chartOptions" />
            </div>
        </div>

        <!-- График 2: Типы контента -->
        <div class="bg-slate-50/60 p-4 rounded-2xl border border-slate-100 flex flex-col w-full">
            <h5 class="text-[10px] font-black uppercase text-slate-400 tracking-widest mb-3 italic">Типы контента</h5>
            <div class="h-[240px] md:h-[280px] w-full relative flex justify-center">
                <Pie :data="categoryData" :options="chartOptions" />
            </div>
        </div>

    </div>
</template>