<template>
  <div class="sg-page">
    <div class="page-header">
      <div class="page-heading">
        <h2 class="page-title">{{ mine ? t('safeguarding.myConcerns') : t('safeguarding.title') }}</h2>
        <p class="subtitle">{{ t('safeguarding.confidential') }}</p>
      </div>
      <div class="toolbar">
        <el-button @click="sg.toggleHideNames()">{{ sg.hideNames ? t('safeguarding.showNames') : t('safeguarding.hideNames') }}</el-button>
        <el-button @click="sg.showBlank()">{{ t('safeguarding.blankScreen') }}</el-button>
        <el-button v-if="sg.isDsl" @click="router.push({ name: 'SafeguardingAccess' })">{{ t('safeguarding.accessRoles') }}</el-button>
        <el-button type="primary" @click="router.push({ name: 'SafeguardingNew' })">+ {{ t('safeguarding.addIncident') }}</el-button>
      </div>
    </div>

    <el-card v-if="!mine && sg.isTeam && dash" class="sg-dash" shadow="never">
      <div class="sg-dash-grid">
        <div><div class="n">{{ dash.open }}</div><div class="l">{{ t('safeguarding.status.ACTIVE') }} / {{ t('safeguarding.status.MONITORING') }}</div></div>
        <div><div class="n warn">{{ dash.overdue }}</div><div class="l">{{ t('safeguarding.list.overdue', { days: dash.overdue_days }) }}</div></div>
        <div><div class="n">{{ dash.my_assigned }}</div><div class="l">{{ t('safeguarding.list.assigned') }}</div></div>
        <div><div class="n">{{ dash.logged_last_7_days }}</div><div class="l">7d</div></div>
        <div><div class="n">{{ dash.unread_alerts }}</div><div class="l">{{ t('safeguarding.detail.alerts') }}</div></div>
      </div>
    </el-card>

    <el-card shadow="never">
      <div v-if="!mine" class="sg-filters">
        <el-input v-model="filters.q" :placeholder="t('safeguarding.list.search')" clearable style="width: 240px" @change="load" />
        <el-select v-model="filters.status" multiple collapse-tags :placeholder="t('safeguarding.list.status')" style="width: 220px" @change="load">
          <el-option v-for="s in statuses" :key="s" :label="t(`safeguarding.status.${s}`)" :value="s" />
        </el-select>
        <el-select v-model="filters.category" multiple collapse-tags :placeholder="t('safeguarding.list.categories')" style="width: 240px" @change="load">
          <el-option v-for="c in categories" :key="c.id" :label="`${c.name_en} ${c.name_zh}`" :value="c.code" />
        </el-select>
        <el-select v-model="filters.severity" multiple collapse-tags :placeholder="t('safeguarding.list.severity')" style="width: 160px" @change="load">
          <el-option v-for="s in severities" :key="s" :label="t(`safeguarding.severity.${s}`)" :value="s" />
        </el-select>
        <el-date-picker v-model="range" type="daterange" value-format="YYYY-MM-DD" style="width: 260px" @change="load" />
        <el-checkbox v-model="filters.open" @change="load">{{ t('safeguarding.list.open') }}</el-checkbox>
      </div>

      <el-table :data="rows" v-loading="loading" :empty-text="t('safeguarding.list.none')" @row-click="(r: IncidentListItem) => router.push({ name: 'SafeguardingDetail', params: { id: r.id } })" row-class-name="sg-row">
        <el-table-column :label="t('safeguarding.list.reference')" prop="reference" width="140" />
        <el-table-column :label="t('safeguarding.list.student')" min-width="180">
          <template #default="{ row }">{{ sg.studentLabel(row.student, locale) }}</template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.list.class')" prop="class_name_at_time" width="90" />
        <el-table-column :label="t('safeguarding.list.categories')" min-width="220">
          <template #default="{ row }">
            <el-tag v-for="c in row.categories" :key="c.id" size="small" :color="c.colour" effect="dark" style="margin-right: 4px; border: 0">{{ locale.startsWith('zh') ? c.name_zh : c.name_en }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.list.status')" width="130">
          <template #default="{ row }"><el-tag :type="statusType(row.status)" size="small">{{ t(`safeguarding.status.${row.status}`) }}</el-tag></template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.list.severity')" width="100">
          <template #default="{ row }">{{ t(`safeguarding.severity.${row.severity}`) }}</template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.form.ring')" width="140">
          <template #default="{ row }">{{ t(`safeguarding.ring.${row.ring}`) }}</template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.list.occurred')" width="150">
          <template #default="{ row }">{{ fmt(row.occurred_at) }}</template>
        </el-table-column>
        <el-table-column v-if="!mine" :label="t('safeguarding.list.lastAction')" width="150">
          <template #default="{ row }">{{ fmt(row.last_action_at) }}</template>
        </el-table-column>
        <el-table-column v-if="!mine" :label="t('safeguarding.list.assigned')" width="140">
          <template #default="{ row }">{{ row.assigned_to?.name || '—' }}</template>
        </el-table-column>
      </el-table>
      <el-pagination v-if="total > pageSize" layout="prev, pager, next" :total="total" :page-size="pageSize" :current-page="page" @current-change="(p: number) => { page = p; load() }" style="margin-top: 12px" />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { asList, sgApi, type Category, type IncidentListItem } from '../api/safeguarding'
import { useSafeguardingStore } from '../composables/useSafeguarding'

const props = defineProps<{ mine?: boolean }>()
const { t, locale } = useI18n()
const router = useRouter()
const sg = useSafeguardingStore()

const statuses = ['ACTIVE', 'MONITORING', 'REFERRED', 'NFA', 'CLOSED']
const severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
const rows = ref<IncidentListItem[]>([])
const categories = ref<Category[]>([])
const dash = ref<Record<string, number> | null>(null)
const loading = ref(false)
const total = ref(0)
const page = ref(1)
const pageSize = 20
const range = ref<[string, string] | null>(null)
const filters = reactive({ q: '', status: [] as string[], category: [] as string[], severity: [] as string[], open: true })

function statusType(s: string) {
  return s === 'ACTIVE' ? 'danger' : s === 'MONITORING' ? 'warning' : s === 'REFERRED' ? 'info' : 'success'
}
function fmt(v: string | null) {
  return v ? v.replace('T', ' ').slice(0, 16) : '—'
}

async function load() {
  loading.value = true
  try {
    if (props.mine) {
      const data = await sgApi.myIncidents()
      rows.value = asList(data as IncidentListItem[])
      total.value = rows.value.length
    } else {
      const data = await sgApi.listIncidents({
        page: page.value, page_size: pageSize, q: filters.q || undefined,
        status: filters.status.join(',') || undefined, category: filters.category.join(',') || undefined,
        severity: filters.severity.join(',') || undefined, open: filters.open ? 1 : undefined,
        date_from: range.value?.[0], date_to: range.value?.[1],
      })
      rows.value = data.results
      total.value = data.count
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await sg.load()
  categories.value = asList(await sgApi.categories())
  if (!props.mine && sg.isTeam) dash.value = (await sgApi.dashboard()) as Record<string, number>
  await load()
})
</script>

<style scoped>
.sg-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; flex-wrap: wrap; }
.subtitle { color: #c0392b; font-size: 12px; margin: 2px 0 0; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
.sg-dash { margin-bottom: 12px; }
.sg-dash-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; text-align: center; }
.sg-dash-grid .n { font-size: 26px; font-weight: 700; }
.sg-dash-grid .n.warn { color: #e6a23c; }
.sg-dash-grid .l { font-size: 12px; color: #666; }
.sg-filters { display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; align-items: center; }
:deep(.sg-row) { cursor: pointer; }
</style>
