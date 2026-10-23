<template>
  <!-- DSL only: who holds safeguarding access. The SIMS permission matrix does not control this. -->
  <div class="sg-page">
    <div class="page-header">
      <div class="page-heading">
        <h2 class="page-title">{{ t('safeguarding.roles.title') }}</h2>
        <p class="hint">{{ t('safeguarding.roles.hint') }}</p>
      </div>
      <el-button type="primary" @click="openNew">+ {{ t('safeguarding.roles.add') }}</el-button>
    </div>

    <el-card shadow="never">
      <el-table :data="rows" v-loading="loading">
        <el-table-column :label="t('safeguarding.roles.employee')" min-width="180">
          <template #default="{ row }">{{ row.employee_summary?.name }} <small>({{ row.employee_summary?.employee_no }})</small></template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.roles.role')" width="220">
          <template #default="{ row }">{{ t(`safeguarding.role.${row.role}`) }}</template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.roles.section')" width="130">
          <template #default="{ row }">{{ t(`safeguarding.section.${row.section}`) }}</template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.roles.scope')" min-width="200">
          <template #default="{ row }">
            <span v-if="row.role === 'PASTORAL'">classes {{ row.class_ids.join(', ') || '—' }} · grades {{ row.grade_ids.join(', ') || '—' }} · houses {{ row.house_ids.join(', ') || '—' }}</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.roles.active')" width="90">
          <template #default="{ row }"><el-switch :model-value="row.is_active" @change="(v: boolean) => toggleActive(row, v)" /></template>
        </el-table-column>
        <el-table-column :label="t('safeguarding.roles.from')" prop="starts_on" width="110" />
        <el-table-column :label="t('safeguarding.roles.to')" prop="ends_on" width="110" />
        <el-table-column :label="t('safeguarding.roles.note')" prop="note" min-width="160" />
      </el-table>
    </el-card>

    <el-dialog v-model="dialog" :title="t('safeguarding.roles.add')" width="560px">
      <el-form :model="draft" label-width="140px">
        <el-form-item :label="t('safeguarding.roles.employee')">
          <el-select v-model="draft.employee" filterable style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('safeguarding.roles.role')">
          <el-select v-model="draft.role" style="width: 100%">
            <el-option v-for="r in ['DSL', 'DEPUTY', 'PASTORAL']" :key="r" :value="r" :label="t(`safeguarding.role.${r}`)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('safeguarding.roles.section')">
          <el-select v-model="draft.section" style="width: 100%">
            <el-option v-for="s in ['WHOLE', 'LOWER', 'UPPER', 'BOARDING']" :key="s" :value="s" :label="t(`safeguarding.section.${s}`)" />
          </el-select>
        </el-form-item>
        <template v-if="draft.role === 'PASTORAL'">
          <el-form-item :label="t('class.title')">
            <el-select v-model="draft.class_ids" multiple filterable style="width: 100%">
              <el-option v-for="c in classes" :key="c.id" :value="c.id" :label="c.name" />
            </el-select>
          </el-form-item>
          <el-form-item :label="t('class.grade')">
            <el-select v-model="draft.grade_ids" multiple filterable style="width: 100%">
              <el-option v-for="g in grades" :key="g.id" :value="g.id" :label="g.name" />
            </el-select>
          </el-form-item>
        </template>
        <el-form-item :label="t('safeguarding.roles.from')"><el-date-picker v-model="draft.starts_on" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item :label="t('safeguarding.roles.to')"><el-date-picker v-model="draft.ends_on" type="date" value-format="YYYY-MM-DD" /></el-form-item>
        <el-form-item :label="t('safeguarding.roles.note')"><el-input v-model="draft.note" maxlength="255" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :disabled="!draft.employee" @click="save">{{ t('common.save') }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import request from '@/api/request'
import { asList, sgApi, type EmployeeSummary, type RoleAssignment } from '../api/safeguarding'

const { t } = useI18n()
const rows = ref<RoleAssignment[]>([])
const employees = ref<EmployeeSummary[]>([])
const classes = ref<Array<{ id: number; name: string }>>([])
const grades = ref<Array<{ id: number; name: string }>>([])
const loading = ref(false)
const dialog = ref(false)
const draft = reactive<RoleAssignment>({ employee: 0, role: 'DEPUTY', section: 'WHOLE', class_ids: [], grade_ids: [], house_ids: [], is_active: true, starts_on: null, ends_on: null, note: '' })

async function load() {
  loading.value = true
  try {
    rows.value = asList(await sgApi.roles())
  } finally {
    loading.value = false
  }
}
function openNew() {
  Object.assign(draft, { employee: 0, role: 'DEPUTY', section: 'WHOLE', class_ids: [], grade_ids: [], house_ids: [], is_active: true, starts_on: null, ends_on: null, note: '' })
  dialog.value = true
}
async function save() {
  try {
    await sgApi.createRole({ ...draft })
    dialog.value = false
    await load()
  } catch (e: unknown) {
    ElMessage.error(JSON.stringify((e as { response?: { data?: unknown } })?.response?.data ?? e))
  }
}
async function toggleActive(row: RoleAssignment, v: boolean) {
  try {
    await sgApi.updateRole(row.id as number, { is_active: v })
  } catch (e: unknown) {
    ElMessage.error(JSON.stringify((e as { response?: { data?: unknown } })?.response?.data ?? e))
  }
  await load()
}
onMounted(async () => {
  await load()
  const [emp, cls, grd] = await Promise.all([
    request.get('/users/employees/', { params: { page_size: 500, status: 'active' } }),
    request.get('/academic/classes/', { params: { page_size: 500 } }),
    request.get('/academic/grades/', { params: { page_size: 100 } }),
  ])
  employees.value = asList<EmployeeSummary>(emp.data)
  classes.value = asList(cls.data)
  grades.value = asList(grd.data)
})
</script>

<style scoped>
.sg-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; }
.hint { color: #888; font-size: 12px; margin: 2px 0 0; max-width: 720px; }
</style>
