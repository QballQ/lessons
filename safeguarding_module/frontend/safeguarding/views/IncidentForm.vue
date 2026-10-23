<template>
  <!-- The CPOMS-style "Add Incident" form. Any active staff member can submit. -->
  <div class="sg-page">
    <div class="page-header">
      <div class="page-heading">
        <h2 class="page-title">{{ t('safeguarding.addIncident') }}</h2>
        <p class="subtitle">{{ t('safeguarding.confidential') }}</p>
      </div>
    </div>

    <el-card shadow="never">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="200px" label-position="left">
        <!-- Student (SIMS typeahead) -->
        <el-form-item :label="t('safeguarding.form.student')" prop="student">
          <el-select v-model="form.student" filterable remote :remote-method="searchStudents" :loading="searching" :placeholder="t('safeguarding.form.studentPlaceholder')" style="width: 100%" @change="onStudentChange">
            <el-option v-for="s in studentOptions" :key="s.id" :value="s.id" :label="`${s.name_en} ${s.name_zh} · ${s.student_id} · ${s.class_name}`" />
          </el-select>
        </el-form-item>

        <!-- Account -->
        <el-form-item :label="t('safeguarding.form.incident')" prop="body">
          <el-input v-model="form.body" type="textarea" :rows="8" maxlength="20000" show-word-limit :placeholder="t('safeguarding.form.incidentPlaceholder')" />
        </el-form-item>

        <!-- Categories (bilingual) -->
        <el-form-item :label="t('safeguarding.form.categories')" prop="categories">
          <el-checkbox-group v-model="form.categories">
            <el-checkbox v-for="c in categories" :key="c.id" :value="c.id" :label="c.id">{{ c.name_en }} {{ c.name_zh }}</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- Linked students -->
        <el-form-item :label="t('safeguarding.form.linkedStudents')">
          <el-select v-model="form.linked_students" multiple filterable remote :remote-method="searchLinked" :placeholder="t('safeguarding.form.studentPlaceholder')" style="width: 100%">
            <el-option v-for="s in linkedOptions" :key="s.id" :value="s.id" :label="`${s.name_en} ${s.name_zh} · ${s.student_id} · ${s.class_name}`" />
          </el-select>
          <div class="hint">{{ t('safeguarding.form.linkedStudentsHint') }}</div>
        </el-form-item>

        <!-- Body map marks: see docs/01 for the clickable-figure component this replaces -->
        <el-form-item v-if="showBodyMap" :label="t('safeguarding.form.bodyMap')">
          <div class="sg-marks">
            <div v-for="(m, i) in form.body_map_marks" :key="i" class="sg-mark-row">
              <el-select v-model="m.view" style="width: 110px">
                <el-option value="FRONT" :label="t('safeguarding.bodyMap.front')" />
                <el-option value="BACK" :label="t('safeguarding.bodyMap.back')" />
              </el-select>
              <el-select v-model="m.region" filterable style="width: 180px" :placeholder="t('safeguarding.bodyMap.region')">
                <el-option v-for="r in regionCodes" :key="r" :value="r" :label="t(`safeguarding.regions.${r}`)" />
              </el-select>
              <el-input v-model="m.note" maxlength="500" :placeholder="t('safeguarding.bodyMap.notePlaceholder')" />
              <el-button link type="danger" @click="form.body_map_marks.splice(i, 1)">{{ t('safeguarding.bodyMap.remove') }}</el-button>
            </div>
            <el-button size="small" @click="form.body_map_marks.push({ view: 'FRONT', x: 50, y: 50, region: 'other', note: '' })">+ {{ t('safeguarding.bodyMap.marks') }}</el-button>
            <div class="hint">{{ t('safeguarding.form.bodyMapHint') }}</div>
          </div>
        </el-form-item>

        <!-- When -->
        <el-form-item :label="t('safeguarding.form.occurredAt')" prop="occurred_at">
          <el-date-picker v-model="form.occurred_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" format="YYYY-MM-DD HH:mm" @change="refreshContext" />
          <div class="hint">{{ t('safeguarding.form.occurredAtHint') }}</div>
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.timeBand')">
          <el-select v-model="form.time_band" clearable style="width: 320px" @change="onBandChange">
            <el-option v-for="b in timeBands" :key="b.id" :value="b.id" :label="`${b.label_en} ${b.label_zh} (${b.start_time.slice(0, 5)}-${b.end_time.slice(0, 5)})`" />
          </el-select>
          <el-input-number v-model="form.period_number" :min="1" :max="12" controls-position="right" style="width: 110px; margin-left: 8px" :placeholder="t('safeguarding.form.period')" @change="refreshContext" />
        </el-form-item>

        <!-- Timetable lookup result -->
        <el-form-item v-if="form.student && form.occurred_at" :label="t('safeguarding.form.subject')">
          <div v-if="lessons.length" class="sg-lessons">
            <div class="hint">{{ t('safeguarding.form.lessonFound') }}:</div>
            <el-radio-group v-model="form.schedule" @change="onLessonPick">
              <el-radio v-for="l in lessons" :key="l.schedule_id" :value="l.schedule_id" :label="l.schedule_id">
                {{ l.subject_name || l.course_name }} · {{ l.teacher?.name || '' }} · {{ l.room_name }}
              </el-radio>
            </el-radio-group>
          </div>
          <div v-else class="hint">{{ t('safeguarding.form.lessonNone') }}</div>
        </el-form-item>

        <!-- Where -->
        <el-form-item :label="t('safeguarding.form.location')" prop="location">
          <el-select v-model="form.location" clearable style="width: 320px">
            <el-option v-for="l in locations" :key="l.id" :value="l.id" :label="`${l.name_en} ${l.name_zh}`" />
          </el-select>
          <el-input v-model="form.location_detail" maxlength="120" style="width: 320px; margin-left: 8px" :placeholder="t('safeguarding.form.locationDetailPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.section')">
          <el-select v-model="form.section" style="width: 200px">
            <el-option v-for="s in ['LOWER', 'UPPER', 'BOARDING', 'WHOLE']" :key="s" :value="s" :label="t(`safeguarding.section.${s}`)" />
          </el-select>
        </el-form-item>

        <!-- Context -->
        <el-form-item :label="t('safeguarding.form.source')">
          <el-select v-model="form.source" style="width: 260px">
            <el-option v-for="s in sources" :key="s" :value="s" :label="t(`safeguarding.source.${s}`)" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.severity')">
          <el-radio-group v-model="form.severity">
            <el-radio-button v-for="s in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']" :key="s" :value="s" :label="s">{{ t(`safeguarding.severity.${s}`) }}</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.status')">
          <el-select v-model="form.status" style="width: 260px">
            <el-option value="ACTIVE" :label="t('safeguarding.status.ACTIVE')" />
            <el-option value="NFA" :label="t('safeguarding.status.NFA')" />
          </el-select>
          <div class="hint">{{ t('safeguarding.form.statusHint') }}</div>
        </el-form-item>
        <el-form-item v-if="sg.isTeam" :label="t('safeguarding.form.ring')">
          <el-checkbox v-model="dslOnly">{{ t('safeguarding.form.ringDslOnly') }}</el-checkbox>
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.assignTo')">
          <el-select v-model="form.assigned_to" clearable filterable style="width: 320px" :placeholder="t('safeguarding.form.assignToPlaceholder')">
            <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('safeguarding.form.staffPresent')">
          <el-select v-model="form.staff_present" multiple filterable style="width: 100%">
            <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
          </el-select>
        </el-form-item>

        <!-- Files: uploaded after creation (needs the incident id) -->
        <el-form-item :label="t('safeguarding.form.files')">
          <el-upload :auto-upload="false" :on-change="(f: UploadFile) => pending.push(f)" :on-remove="(f: UploadFile) => pending.splice(pending.indexOf(f), 1)" multiple drag>
            <div>{{ t('safeguarding.form.filesHint') }}</div>
          </el-upload>
        </el-form-item>

        <!-- Alerts -->
        <el-form-item :label="t('safeguarding.form.alertStaff')">
          <el-select v-model="form.alert_employees" multiple filterable style="width: 100%" :placeholder="t('safeguarding.form.assignToPlaceholder')">
            <el-option v-for="e in employees" :key="e.id" :value="e.id" :label="`${e.name} (${e.employee_no})`" />
          </el-select>
          <div class="sg-groups">
            <el-check-tag v-for="g in alertGroups" :key="g.id" :checked="form.alert_groups.includes(g.id)" @change="toggleGroup(g.id)">{{ g.name_en }} {{ g.name_zh }}</el-check-tag>
          </div>
          <el-input v-model="form.alert_message" maxlength="255" :placeholder="t('safeguarding.form.alertMessage')" style="margin-top: 6px" />
          <div class="hint">{{ t('safeguarding.form.alertStaffHint') }}</div>
        </el-form-item>

        <el-form-item :label="t('safeguarding.form.agency')">
          <el-input v-model="form.agency_involved" maxlength="120" style="width: 320px" />
          <el-input v-model="form.agency_reference" maxlength="60" style="width: 200px; margin-left: 8px" :placeholder="t('safeguarding.form.agencyReference')" />
        </el-form-item>

        <el-form-item :label="t('safeguarding.form.loggedAt')">
          <span>{{ now }}</span>
          <div class="hint">{{ t('safeguarding.form.loggedAtHint') }}</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="submitting" @click="submit">{{ t('safeguarding.form.submit') }}</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, type FormInstance, type UploadFile } from 'element-plus'
import request from '@/api/request'
import { asList, sgApi, type AlertGroup, type Category, type EmployeeSummary, type IncidentCreatePayload, type Lesson, type Location, type StudentSummary, type TimeBand } from '../api/safeguarding'
import { useSafeguardingStore } from '../composables/useSafeguarding'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const sg = useSafeguardingStore()

const formRef = ref<FormInstance>()
const categories = ref<Category[]>([])
const locations = ref<Location[]>([])
const timeBands = ref<TimeBand[]>([])
const alertGroups = ref<AlertGroup[]>([])
const employees = ref<EmployeeSummary[]>([])
const studentOptions = ref<StudentSummary[]>([])
const linkedOptions = ref<StudentSummary[]>([])
const lessons = ref<Lesson[]>([])
const pending = reactive<UploadFile[]>([])
const searching = ref(false)
const submitting = ref(false)
const dslOnly = ref(false)
const sources = ['STAFF_OBSERVED', 'STUDENT_DISCLOSURE', 'PEER_REPORT', 'PARENT', 'EXTERNAL', 'OTHER']
const regionCodes = ['head', 'face', 'neck', 'chest', 'abdomen', 'back_upper', 'back_lower', 'left_shoulder', 'right_shoulder', 'left_upper_arm', 'right_upper_arm', 'left_forearm', 'right_forearm', 'left_hand', 'right_hand', 'pelvis', 'buttocks', 'left_thigh', 'right_thigh', 'left_lower_leg', 'right_lower_leg', 'left_foot', 'right_foot', 'other']
const now = new Date().toISOString().replace('T', ' ').slice(0, 16)

const form = reactive<IncidentCreatePayload & { body_map_marks: NonNullable<IncidentCreatePayload['body_map_marks']>; alert_employees: number[]; alert_groups: number[]; linked_students: number[]; staff_present: number[] }>({
  student: Number(route.query.student) || 0,
  body: '',
  categories: [],
  linked_students: [],
  occurred_at: new Date(Date.now() - new Date().getTimezoneOffset() * 60000).toISOString().slice(0, 19),
  time_band: null,
  period_number: null,
  location: null,
  location_detail: '',
  subject: null,
  schedule: null,
  staff_present: [],
  severity: 'MEDIUM',
  source: 'STAFF_OBSERVED',
  status: 'ACTIVE',
  assigned_to: null,
  agency_involved: '',
  agency_reference: '',
  section: 'UPPER',
  body_map_marks: [],
  alert_employees: [],
  alert_groups: [],
  alert_message: '',
})

const rules = {
  student: [{ required: true, message: t('safeguarding.form.student'), trigger: 'change' }],
  body: [{ required: true, min: 10, message: t('safeguarding.form.minBody'), trigger: 'blur' }],
  categories: [{ type: 'array', required: true, min: 1, message: t('safeguarding.form.minCategory'), trigger: 'change' }],
  occurred_at: [{ required: true, message: t('safeguarding.form.occurredAt'), trigger: 'change' }],
}

const showBodyMap = computed(() => {
  const chosen = categories.value.filter((c) => form.categories.includes(c.id))
  return chosen.length === 0 || chosen.some((c) => c.uses_body_map) || form.body_map_marks.length > 0
})

async function searchStudents(q: string) {
  if (q.length < 2) return
  searching.value = true
  try {
    studentOptions.value = await sgApi.lookupStudents(q)
  } finally {
    searching.value = false
  }
}
async function searchLinked(q: string) {
  if (q.length >= 2) linkedOptions.value = await sgApi.lookupStudents(q)
}

async function refreshContext() {
  if (!form.student || !form.occurred_at) return
  const ctx = await sgApi.context(form.student, form.occurred_at, form.period_number)
  form.section = ctx.section
  if (ctx.time_band && form.time_band == null) form.time_band = ctx.time_band.id
  if (ctx.period_number && form.period_number == null) form.period_number = ctx.period_number
  lessons.value = ctx.lessons
  if (lessons.value.length === 1) {
    form.schedule = lessons.value[0].schedule_id
    onLessonPick()
  }
}
function onStudentChange() {
  refreshContext()
}
function onBandChange(id: number | null) {
  const band = timeBands.value.find((b) => b.id === id)
  form.period_number = band?.period_number ?? null
  refreshContext()
}
function onLessonPick() {
  const l = lessons.value.find((x) => x.schedule_id === form.schedule)
  if (!l) return
  form.subject = l.subject_id
  if (l.room_id && form.location == null) {
    const loc = locations.value.find((x) => x.room === l.room_id)
    if (loc) form.location = loc.id
    else form.location_detail = form.location_detail || l.room_name
  }
}
function toggleGroup(id: number) {
  const i = form.alert_groups.indexOf(id)
  i >= 0 ? form.alert_groups.splice(i, 1) : form.alert_groups.push(id)
}

async function submit() {
  const ok = await formRef.value?.validate().catch(() => false)
  if (!ok) return
  submitting.value = true
  try {
    const payload: IncidentCreatePayload = { ...form, ring: dslOnly.value ? 'DSL' : undefined }
    const created = await sgApi.createIncident(payload)
    for (const f of pending) if (f.raw) await sgApi.upload(created.id, f.raw)
    ElMessage.success(t('safeguarding.form.submitted', { reference: created.reference }))
    router.push(created.permissions.level === 'REPORTER' ? { name: 'SafeguardingMine' } : { name: 'SafeguardingDetail', params: { id: created.id } })
  } catch (e: unknown) {
    const detail = (e as { response?: { data?: unknown } })?.response?.data
    ElMessage.error(typeof detail === 'string' ? detail : JSON.stringify(detail ?? e))
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await sg.load()
  ;[categories.value, locations.value, timeBands.value, alertGroups.value] = await Promise.all([
    sgApi.categories().then(asList), sgApi.locations().then(asList), sgApi.timeBands().then(asList), sgApi.alertGroups().then(asList),
  ])
  // Staff list for assign / alerts / staff present: the existing SIMS employees endpoint.
  const emp = await request.get('/users/employees/', { params: { page_size: 500, status: 'active' } })
  employees.value = asList<EmployeeSummary>(emp.data)
  if (form.student) {
    const s = await request.get(`/users/students/${form.student}/`)
    studentOptions.value = [{ id: s.data.id, student_id: s.data.student_id, name_en: `${s.data.first_name_en ?? ''} ${s.data.last_name_en ?? ''}`.trim(), name_zh: `${s.data.last_name_zh ?? ''}${s.data.first_name_zh ?? ''}`, class_name: s.data.class_name ?? '', grade_name: '', gender: s.data.gender ?? '', enrollment_status: s.data.enrollment_status ?? '' }]
    refreshContext()
  }
})
</script>

<style scoped>
.sg-page { padding: 16px; }
.page-header { margin-bottom: 12px; }
.subtitle { color: #c0392b; font-size: 12px; margin: 2px 0 0; }
.hint { color: #888; font-size: 12px; line-height: 1.4; margin-top: 4px; width: 100%; }
.sg-marks { width: 100%; }
.sg-mark-row { display: grid; grid-template-columns: 110px 180px 1fr auto; gap: 8px; margin-bottom: 6px; }
.sg-groups { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }
.sg-lessons { width: 100%; }
</style>
