<template>
  <div class="sg-page" v-loading="loading">
    <template v-if="inc">
      <div class="page-header">
        <div class="page-heading">
          <h2 class="page-title">{{ inc.reference }} · {{ sg.studentLabel(inc.student, locale) }} <small>{{ inc.class_name_at_time }}</small></h2>
          <p class="subtitle">{{ t('safeguarding.confidential') }} · {{ t(`safeguarding.ring.${inc.ring}`) }}</p>
        </div>
        <div class="toolbar">
          <el-button @click="sg.toggleHideNames()">{{ sg.hideNames ? t('safeguarding.showNames') : t('safeguarding.hideNames') }}</el-button>
          <el-button @click="sg.showBlank()">{{ t('safeguarding.blankScreen') }}</el-button>
          <el-button v-if="p.can_export" @click="openExport">{{ t('safeguarding.detail.export') }}</el-button>
        </div>
      </div>

      <el-alert v-if="p.level === 'REPORTER'" type="info" :closable="false" :title="t('safeguarding.detail.reporterView')" style="margin-bottom: 12px" />

      <el-row :gutter="16">
        <el-col :span="16">
          <el-card shadow="never">
            <el-descriptions :column="2" size="small" border>
              <el-descriptions-item :label="t('safeguarding.list.status')">
                <el-tag size="small">{{ t(`safeguarding.status.${inc.status}`) }}</el-tag>
                <el-button v-if="p.can_change_status" link size="small" @click="statusDialog = true">{{ t('safeguarding.detail.changeStatus') }}</el-button>
              </el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.list.severity')">{{ t(`safeguarding.severity.${inc.severity}`) }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.list.categories')">
                <el-tag v-for="c in inc.categories" :key="c.id" size="small" :color="c.colour" effect="dark" style="margin-right: 4px; border: 0">{{ c.name_en }} {{ c.name_zh }}</el-tag>
              </el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.form.ring')">
                {{ t(`safeguarding.ring.${inc.ring}`) }}
                <el-button v-if="p.can_change_ring || (p.level === 'TEAM' && inc.ring !== 'DSL')" link size="small" @click="ringDialog = true">{{ t('safeguarding.detail.changeRing') }}</el-button>
              </el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.form.occurredAt')">{{ fmt(inc.occurred_at) }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.form.timeBand')">{{ inc.time_band_label }} {{ inc.period_number ? `P${inc.period_number}` : '' }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.form.location')">{{ inc.location_name }} {{ inc.location_detail }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.detail.lesson')">
                <template v-if="inc.lesson">{{ inc.lesson.subject_name || inc.lesson.course_name }} · {{ inc.lesson.teacher?.name }} · {{ inc.lesson.room_name }}</template>
                <template v-else>{{ inc.subject_name || '—' }}</template>
              </el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.form.section')">{{ t(`safeguarding.section.${inc.section}`) }}</el-descriptions-item>
              <el-descriptions-item v-if="inc.source" :label="t('safeguarding.form.source')">{{ t(`safeguarding.source.${inc.source}`) }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.detail.reporter')">{{ inc.reporter?.name || '—' }} · {{ fmt(inc.logged_at) }}</el-descriptions-item>
              <el-descriptions-item :label="t('safeguarding.list.assigned')">{{ inc.assigned_to?.name || '—' }}</el-descriptions-item>
              <el-descriptions-item v-if="inc.linked_students?.length" :label="t('safeguarding.form.linkedStudents')" :span="2">
                <span v-for="s in inc.linked_students" :key="s.id" style="margin-right: 8px">{{ sg.studentLabel(s, locale) }}</span>
              </el-descriptions-item>
              <el-descriptions-item v-if="inc.staff_present?.length" :label="t('safeguarding.form.staffPresent')" :span="2">{{ inc.staff_present.map((e) => e.name).join(', ') }}</el-descriptions-item>
              <el-descriptions-item v-if="inc.agency_involved" :label="t('safeguarding.form.agency')" :span="2">{{ inc.agency_involved }} {{ inc.agency_reference }}</el-descriptions-item>
            </el-descriptions>

            <h4>{{ t('safeguarding.detail.account') }}</h4>
            <p class="sg-body">{{ inc.body }}</p>

            <template v-if="inc.body_map_marks.length">
              <h4>{{ t('safeguarding.form.bodyMap') }}</h4>
              <ul>
                <li v-for="(m, i) in inc.body_map_marks" :key="m.id ?? i">
                  {{ i + 1 }}. {{ t(`safeguarding.bodyMap.${m.view.toLowerCase()}`) }} · {{ te(`safeguarding.regions.${m.region}`) ? t(`safeguarding.regions.${m.region}`) : m.region }} · {{ m.note }}
                </li>
              </ul>
            </template>

            <h4>{{ t('safeguarding.detail.attachments') }}</h4>
            <ul>
              <li v-for="a in inc.attachments" :key="a.id">
                <a :href="`${baseURL}${a.download_url}`" target="_blank" rel="noopener">{{ a.original_name }}</a> · {{ Math.round(a.size / 1024) }} KB · {{ a.uploaded_by_name }}
              </li>
            </ul>
            <el-upload v-if="p.can_upload" :show-file-list="false" :http-request="(o: UploadRequestOptions) => doUpload(o.file as File)">
              <el-button size="small">+ {{ t('safeguarding.form.files') }}</el-button>
            </el-upload>
          </el-card>

          <!-- Chronology -->
          <el-card v-if="p.sees_chronology" shadow="never" style="margin-top: 16px">
            <template #header>{{ t('safeguarding.detail.chronology') }}</template>
            <el-timeline>
              <el-timeline-item v-for="a in inc.actions" :key="a.id" :timestamp="`${fmt(a.created_at)} · ${a.author_name}`" placement="top" :type="a.ring === 'DSL' ? 'danger' : undefined">
                <strong>{{ t(`safeguarding.actionKind.${a.kind}`) }}</strong>
                <el-tag v-if="a.ring === 'DSL'" size="small" type="danger" style="margin-left: 6px">{{ t('safeguarding.detail.dslOnly') }}</el-tag>
                <p v-if="a.body" class="sg-body">{{ a.body }}</p>
                <small v-if="a.meta && Object.keys(a.meta).length" class="sg-meta">{{ metaText(a.meta) }}</small>
              </el-timeline-item>
            </el-timeline>
            <div v-if="p.can_add_action" class="sg-add-action">
              <el-select v-model="newAction.kind" style="width: 180px">
                <el-option v-for="k in ['NOTE', 'ACTION', 'PARENT_CONTACT', 'AGENCY', 'REFERRAL']" :key="k" :value="k" :label="t(`safeguarding.actionKind.${k}`)" />
              </el-select>
              <el-checkbox v-if="p.can_add_dsl_note" v-model="newAction.dsl">{{ t('safeguarding.detail.dslOnly') }}</el-checkbox>
              <el-input v-model="newAction.body" type="textarea" :rows="3" maxlength="20000" />
              <el-button type="primary" size="small" :disabled="!newAction.body.trim()" @click="addAction">{{ t('safeguarding.detail.addAction') }}</el-button>
            </div>
          </el-card>

          <!-- Reporter's own addendum -->
          <el-card v-else shadow="never" style="margin-top: 16px">
            <template #header>{{ t('safeguarding.detail.addNote') }}</template>
            <ul>
              <li v-for="a in inc.my_notes" :key="a.id">{{ fmt(a.created_at) }} · {{ a.body }}</li>
            </ul>
            <el-input v-model="newAction.body" type="textarea" :rows="3" maxlength="20000" />
            <el-button type="primary" size="small" style="margin-top: 6px" :disabled="!newAction.body.trim()" @click="addAction">{{ t('safeguarding.detail.addNote') }}</el-button>
          </el-card>
        </el-col>

        <el-col :span="8">
          <el-card v-if="p.sees_chronology" shadow="never">
            <template #header>{{ t('safeguarding.detail.alerts') }}</template>
            <ul class="sg-plain">
              <li v-for="a in inc.alerts" :key="a.id">{{ a.employee.name }} <small>· {{ fmt(a.created_at) }} · {{ a.read_at ? '✓' : '' }}</small></li>
            </ul>
            <template v-if="p.can_alert">
              <el-select v-model="alertPick.employees" multiple filterable size="small" style="width: 100%" :placeholder="t('safeguarding.form.assignToPlaceholder')">
                <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
              </el-select>
              <div class="sg-groups">
                <el-check-tag v-for="g in alertGroups" :key="g.id" :checked="alertPick.groups.includes(g.id)" @change="toggle(alertPick.groups, g.id)">{{ g.name_en }} {{ g.name_zh }}</el-check-tag>
              </div>
              <el-input v-model="alertPick.message" size="small" maxlength="255" :placeholder="t('safeguarding.form.alertMessage')" style="margin-top: 6px" />
              <el-button size="small" type="primary" style="margin-top: 6px" :disabled="!alertPick.employees.length && !alertPick.groups.length" @click="sendAlerts">{{ t('safeguarding.form.alertStaff') }}</el-button>
            </template>
          </el-card>

          <el-card v-if="p.can_grant" shadow="never" style="margin-top: 16px">
            <template #header>{{ t('safeguarding.detail.grants') }}</template>
            <ul class="sg-plain">
              <li v-for="g in inc.access_grants" :key="g.id" :class="{ 'sg-muted': !g.is_current }">
                {{ g.employee_summary.name }} · {{ g.reason }} <small>· {{ g.expires_at ? fmt(g.expires_at) : '∞' }}</small>
                <el-button v-if="g.is_current" link type="danger" size="small" @click="revoke(g.id)">{{ t('safeguarding.detail.revoke') }}</el-button>
              </li>
            </ul>
            <el-select v-model="grant.employee" filterable size="small" style="width: 100%" :placeholder="t('safeguarding.form.assignToPlaceholder')">
              <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
            </el-select>
            <el-input v-model="grant.reason" size="small" maxlength="255" :placeholder="t('safeguarding.detail.reason')" style="margin-top: 6px" />
            <el-date-picker v-model="grant.expires_at" type="datetime" size="small" value-format="YYYY-MM-DDTHH:mm:ss" :placeholder="t('safeguarding.detail.expires')" style="margin-top: 6px; width: 100%" />
            <el-button size="small" type="primary" style="margin-top: 6px" :disabled="!grant.employee || !grant.reason" @click="doGrant">{{ t('safeguarding.detail.grant') }}</el-button>
          </el-card>

          <el-card v-if="p.can_soft_delete" shadow="never" style="margin-top: 16px">
            <el-input v-model="deleteReason" size="small" maxlength="255" :placeholder="t('safeguarding.detail.softDeleteReason')" />
            <el-button size="small" type="danger" plain style="margin-top: 6px" :disabled="deleteReason.length < 5" @click="softDelete">{{ t('safeguarding.detail.softDelete') }}</el-button>
          </el-card>
        </el-col>
      </el-row>

      <el-dialog v-model="statusDialog" :title="t('safeguarding.detail.changeStatus')" width="420px">
        <el-select v-model="statusPick.status" style="width: 100%">
          <el-option v-for="s in ['ACTIVE', 'MONITORING', 'REFERRED', 'NFA', 'CLOSED']" :key="s" :value="s" :label="t(`safeguarding.status.${s}`)" />
        </el-select>
        <el-input v-model="statusPick.note" type="textarea" :rows="3" style="margin-top: 8px" />
        <template #footer><el-button type="primary" @click="setStatus">OK</el-button></template>
      </el-dialog>

      <el-dialog v-model="ringDialog" :title="t('safeguarding.detail.changeRing')" width="420px">
        <el-select v-model="ringPick.ring" style="width: 100%">
          <el-option v-for="r in ['PASTORAL', 'TEAM', 'DSL']" :key="r" :value="r" :label="t(`safeguarding.ring.${r}`)" :disabled="!p.can_lower_ring && r !== 'DSL'" />
        </el-select>
        <el-input v-model="ringPick.note" type="textarea" :rows="3" style="margin-top: 8px" />
        <template #footer><el-button type="primary" @click="setRing">OK</el-button></template>
      </el-dialog>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, type UploadRequestOptions } from 'element-plus'
import request from '@/api/request'
import { asList, sgApi, type AlertGroup, type EmployeeSummary, type IncidentDetail, type IncidentPermissions, type Ring } from '../api/safeguarding'
import { useSafeguardingStore } from '../composables/useSafeguarding'

const props = defineProps<{ id: string | number }>()
const { t, te, locale } = useI18n()
const router = useRouter()
const sg = useSafeguardingStore()
const baseURL = request.defaults.baseURL ?? '/api/v1'

const inc = ref<IncidentDetail | null>(null)
const loading = ref(false)
const employees = ref<EmployeeSummary[]>([])
const alertGroups = ref<AlertGroup[]>([])
const statusDialog = ref(false)
const ringDialog = ref(false)
const deleteReason = ref('')
const newAction = reactive({ kind: 'NOTE', body: '', dsl: false })
const alertPick = reactive({ employees: [] as number[], groups: [] as number[], message: '' })
const grant = reactive({ employee: null as number | null, reason: '', expires_at: null as string | null })
const statusPick = reactive({ status: 'ACTIVE', note: '' })
const ringPick = reactive({ ring: 'TEAM' as Ring, note: '' })

const p = computed<IncidentPermissions>(() => inc.value?.permissions ?? ({ level: 'NONE' } as IncidentPermissions))

function fmt(v: string | null) {
  return v ? v.replace('T', ' ').slice(0, 16) : '—'
}
function metaText(meta: Record<string, unknown>) {
  return Object.entries(meta).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(', ') : String(v)}`).join(' · ')
}
function toggle(arr: number[], id: number) {
  const i = arr.indexOf(id)
  i >= 0 ? arr.splice(i, 1) : arr.push(id)
}

async function load() {
  loading.value = true
  try {
    inc.value = await sgApi.getIncident(Number(props.id))
    statusPick.status = inc.value.status
    ringPick.ring = inc.value.ring
  } catch {
    ElMessage.error(t('forbiddenPage.title'))
    router.replace({ name: 'Safeguarding' })
  } finally {
    loading.value = false
  }
}
async function addAction() {
  await sgApi.addAction(Number(props.id), newAction.kind, newAction.body, newAction.dsl ? 'DSL' : 'TEAM')
  newAction.body = ''
  newAction.dsl = false
  await load()
}
async function setStatus() {
  await sgApi.setStatus(Number(props.id), statusPick.status as IncidentDetail['status'], statusPick.note)
  statusDialog.value = false
  statusPick.note = ''
  await load()
}
async function setRing() {
  const r = await sgApi.setRing(Number(props.id), ringPick.ring, ringPick.note)
  ringDialog.value = false
  if ((r as unknown as { visible_to_you?: boolean }).visible_to_you === false) {
    router.replace({ name: 'Safeguarding' })
    return
  }
  await load()
}
async function sendAlerts() {
  await sgApi.sendAlerts(Number(props.id), alertPick.employees, alertPick.groups, alertPick.message)
  alertPick.employees = []
  alertPick.groups = []
  alertPick.message = ''
  await load()
}
async function doGrant() {
  if (!grant.employee) return
  await sgApi.grantAccess(Number(props.id), grant.employee, grant.reason, grant.expires_at)
  grant.employee = null
  grant.reason = ''
  grant.expires_at = null
  await load()
}
async function revoke(gid: number) {
  await sgApi.revokeAccess(Number(props.id), gid)
  await load()
}
async function doUpload(file: File) {
  await sgApi.upload(Number(props.id), file)
  await load()
}
function openExport() {
  window.open(sgApi.exportUrl(Number(props.id)), '_blank', 'noopener')
}
async function softDelete() {
  await sgApi.softDelete(Number(props.id), deleteReason.value)
  router.replace({ name: 'Safeguarding' })
}

onMounted(async () => {
  await sg.load()
  await load()
  if (p.value.can_alert || p.value.can_grant) {
    const emp = await request.get('/users/employees/', { params: { page_size: 500, status: 'active' } })
    employees.value = asList<EmployeeSummary>(emp.data)
    alertGroups.value = asList(await sgApi.alertGroups())
  }
})
</script>

<style scoped>
.sg-page { padding: 16px; }
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 12px; gap: 12px; flex-wrap: wrap; }
.page-title small { color: #888; font-weight: normal; font-size: 13px; margin-left: 8px; }
.subtitle { color: #c0392b; font-size: 12px; margin: 2px 0 0; }
.toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
.sg-body { white-space: pre-wrap; line-height: 1.5; }
.sg-meta { color: #888; }
.sg-add-action { display: grid; gap: 8px; margin-top: 12px; }
.sg-plain { list-style: none; padding: 0; margin: 0 0 8px; }
.sg-plain li { padding: 3px 0; }
.sg-muted { color: #aaa; }
.sg-groups { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 6px; }
</style>
