<template>
  <!--
    Tab on the student profile (StudentProfile.vue). Shows only what the viewer may
    see; staff without a role still get the "Log a concern" button.
    Usage: <el-tab-pane :label="t('safeguarding.studentTab.title')" name="safeguarding">
             <StudentSafeguardingTab :student-id="student.id" />
           </el-tab-pane>
  -->
  <div class="sg-tab" v-loading="loading">
    <div class="sg-tab-head">
      <span class="sg-conf">{{ t('safeguarding.confidential') }}</span>
      <el-button type="primary" size="small" @click="router.push({ name: 'SafeguardingNew', query: { student: studentId } })">
        + {{ t('safeguarding.studentTab.add') }}
      </el-button>
    </div>
    <p v-if="data && !data.has_role" class="sg-muted">{{ t('safeguarding.studentTab.noRole') }}</p>

    <el-table v-if="data?.incidents.length" :data="data.incidents" size="small" @row-click="(r: IncidentListItem) => router.push({ name: 'SafeguardingDetail', params: { id: r.id } })" row-class-name="sg-row">
      <el-table-column :label="t('safeguarding.list.reference')" prop="reference" width="130" />
      <el-table-column :label="t('safeguarding.list.categories')" min-width="200">
        <template #default="{ row }">
          <el-tag v-for="c in row.categories" :key="c.id" size="small" :color="c.colour" effect="dark" style="margin-right: 4px; border: 0">{{ locale.startsWith('zh') ? c.name_zh : c.name_en }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('safeguarding.list.status')" width="130">
        <template #default="{ row }">{{ t(`safeguarding.status.${row.status}`) }}</template>
      </el-table-column>
      <el-table-column :label="t('safeguarding.list.occurred')" width="140">
        <template #default="{ row }">{{ row.occurred_at.replace('T', ' ').slice(0, 16) }}</template>
      </el-table-column>
      <el-table-column :label="t('safeguarding.list.assigned')" width="130">
        <template #default="{ row }">{{ row.assigned_to?.name || '—' }}</template>
      </el-table-column>
    </el-table>
    <p v-else-if="data" class="sg-muted">{{ t('safeguarding.studentTab.none') }}</p>

    <template v-if="data?.linked.length">
      <h4>{{ t('safeguarding.studentTab.linked') }}</h4>
      <ul>
        <li v-for="r in data.linked" :key="r.id">
          <router-link :to="{ name: 'SafeguardingDetail', params: { id: r.id } }">{{ r.reference }}</router-link>
          · {{ r.occurred_at.slice(0, 10) }} · {{ t(`safeguarding.status.${r.status}`) }}
        </li>
      </ul>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { sgApi, type IncidentListItem, type StudentSummary } from '../api/safeguarding'

const props = defineProps<{ studentId: number }>()
const { t, locale } = useI18n()
const router = useRouter()
const loading = ref(false)
const data = ref<{ student: StudentSummary; incidents: IncidentListItem[]; linked: IncidentListItem[]; can_add: boolean; has_role: boolean } | null>(null)

async function load() {
  loading.value = true
  try {
    data.value = await sgApi.byStudent(props.studentId)
  } finally {
    loading.value = false
  }
}
onMounted(load)
watch(() => props.studentId, load)
</script>

<style scoped>
.sg-tab-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sg-conf { color: #c0392b; font-size: 12px; }
.sg-muted { color: #888; font-size: 13px; }
:deep(.sg-row) { cursor: pointer; }
</style>
