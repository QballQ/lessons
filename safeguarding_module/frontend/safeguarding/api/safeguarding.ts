/**
 * Safeguarding API client. Uses the same axios instance as the rest of SIMS
 * (baseURL /api/v1, Bearer token, refresh interceptor). Adjust the import path
 * to wherever the shared instance lives (src/api/request.ts in most builds).
 */
import request from '@/api/request'

export type Ring = 'PASTORAL' | 'TEAM' | 'DSL'
export type Section = 'WHOLE' | 'LOWER' | 'UPPER' | 'BOARDING'
export type IncidentStatus = 'ACTIVE' | 'MONITORING' | 'REFERRED' | 'NFA' | 'CLOSED'
export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
export type Source = 'STAFF_OBSERVED' | 'STUDENT_DISCLOSURE' | 'PEER_REPORT' | 'PARENT' | 'EXTERNAL' | 'OTHER'

export interface StudentSummary {
  id: number
  student_id: string
  name_en: string
  name_zh: string
  class_name: string
  grade_name: string
  gender: string
  enrollment_status: string
}
export interface EmployeeSummary { id: number; employee_no: string; name: string; position_type: string }
export interface Category { id: number; code: string; name_en: string; name_zh: string; ring: Ring; uses_body_map: boolean; colour: string; sort_order: number; is_active: boolean }
export interface Location { id: number; name_en: string; name_zh: string; kind: string; room: number | null; room_name: string; section: Section; sort_order: number; is_active: boolean }
export interface TimeBand { id: number; code: string; label_en: string; label_zh: string; start_time: string; end_time: string; period_number: number | null; applies_to: string; sort_order: number; is_active: boolean }
export interface AlertGroup { id: number; code: string; name_en: string; name_zh: string; members: number[]; member_summaries: EmployeeSummary[]; sort_order: number; is_active: boolean }
export interface BodyMapMark { id?: number; view: 'FRONT' | 'BACK'; x: number | string; y: number | string; region: string; note: string; created_at?: string; created_by_name?: string }
export interface Attachment { id: number; original_name: string; content_type: string; size: number; sha256: string; created_at: string; uploaded_by_name: string; download_url: string }
export interface Action { id: number; kind: string; body: string; ring: Ring; meta: Record<string, unknown>; author_name: string; created_at: string }
export interface Alert { id: number; employee: EmployeeSummary; message: string; grants_access: boolean; created_at: string; read_at: string | null; alerted_by_name: string }
export interface AccessGrant { id: number; employee: number; employee_summary: EmployeeSummary; reason: string; created_at: string; expires_at: string | null; revoked_at: string | null; granted_by_name: string; is_current: boolean }
export interface Lesson { schedule_id: number; subject_id: number | null; subject_name: string; course_name: string; teacher: EmployeeSummary | null; room_id: number | null; room_name: string; period: number; day_of_week: number }
export interface IncidentPermissions {
  level: 'NONE' | 'REPORTER' | 'PASTORAL' | 'GRANTED' | 'TEAM' | 'DSL'
  can_view: boolean; can_edit: boolean; can_change_status: boolean; can_change_ring: boolean; can_lower_ring: boolean
  can_alert: boolean; can_grant: boolean; can_add_action: boolean; can_add_dsl_note: boolean; can_upload: boolean
  can_edit_body_map: boolean; can_export: boolean; can_soft_delete: boolean; sees_chronology: boolean; sees_dsl_notes: boolean
}
export interface IncidentListItem {
  id: number; reference: string; student: StudentSummary; class_name_at_time: string; section: Section
  categories: Category[]; status: IncidentStatus; ring: Ring; severity: Severity
  occurred_at: string; logged_at: string; last_action_at: string | null
  assigned_to: EmployeeSummary | null; reporter: EmployeeSummary | null
  location_name: string; time_band_label: string; period_number: number | null; alert_count: number
}
export interface IncidentDetail extends IncidentListItem {
  body: string; source: Source; linked_students: StudentSummary[]; staff_present: EmployeeSummary[]
  time_band: number | null; location: number | null; location_detail: string; subject: number | null; subject_name: string
  schedule: number | null; lesson: Lesson | null; agency_involved: string; agency_reference: string
  body_map_marks: BodyMapMark[]; attachments: Attachment[]; actions?: Action[]; alerts?: Alert[]; access_grants?: AccessGrant[]
  my_notes?: Action[]; closed_at: string | null; closed_by_name?: string; updated_at?: string; permissions: IncidentPermissions
}
export interface IncidentCreatePayload {
  student: number; body: string; categories: number[]; linked_students?: number[]; occurred_at: string
  time_band?: number | null; period_number?: number | null; location?: number | null; location_detail?: string
  subject?: number | null; schedule?: number | null; staff_present?: number[]; severity?: Severity; source?: Source
  status?: 'ACTIVE' | 'NFA'; assigned_to?: number | null; agency_involved?: string; agency_reference?: string
  section?: Section; ring?: Ring; body_map_marks?: BodyMapMark[]; alert_employees?: number[]; alert_groups?: number[]; alert_message?: string
}
export interface SafeguardingMe {
  employee: EmployeeSummary | null; roles: string[]; is_dsl: boolean; is_team: boolean; is_pastoral: boolean
  deputy_sections: Section[]; pastoral_scope: { sections: Section[]; class_ids: number[]; grade_ids: number[]; house_ids: number[] }
  unread_alerts: number; settings: { reporter_sees_own: boolean; idle_timeout_minutes: number; overdue_days: number }
}
export interface RoleAssignment {
  id?: number; employee: number; employee_summary?: EmployeeSummary; role: 'DSL' | 'DEPUTY' | 'PASTORAL'; section: Section
  class_ids: number[]; grade_ids: number[]; house_ids: number[]; is_active: boolean; starts_on: string | null; ends_on: string | null; note: string
}
export interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[] }

const base = '/safeguarding'
const unwrap = <T>(p: Promise<{ data: T }>) => p.then((r) => r.data)

export const sgApi = {
  me: () => unwrap<SafeguardingMe>(request.get(`${base}/me/`)),
  dashboard: () => unwrap<Record<string, unknown>>(request.get(`${base}/dashboard/`)),
  lookupStudents: (q: string, limit = 15) => unwrap<StudentSummary[]>(request.get(`${base}/students/lookup/`, { params: { q, limit } })),
  context: (student: number, at: string, period?: number | null) =>
    unwrap<{ student: StudentSummary; section: Section; time_band: TimeBand | null; period_number: number | null; lessons: Lesson[] }>(
      request.get(`${base}/context/`, { params: { student, at, period: period ?? undefined } }),
    ),

  categories: () => unwrap<Category[] | Paginated<Category>>(request.get(`${base}/categories/`, { params: { page_size: 200 } })),
  locations: () => unwrap<Location[] | Paginated<Location>>(request.get(`${base}/locations/`, { params: { page_size: 200 } })),
  timeBands: () => unwrap<TimeBand[] | Paginated<TimeBand>>(request.get(`${base}/time-bands/`, { params: { page_size: 200 } })),
  alertGroups: () => unwrap<AlertGroup[] | Paginated<AlertGroup>>(request.get(`${base}/alert-groups/`, { params: { page_size: 200 } })),

  listIncidents: (params: Record<string, unknown>) => unwrap<Paginated<IncidentListItem>>(request.get(`${base}/incidents/`, { params })),
  myIncidents: () => unwrap<Paginated<IncidentListItem> | IncidentListItem[]>(request.get(`${base}/incidents/mine/`)),
  byStudent: (student: number) =>
    unwrap<{ student: StudentSummary; incidents: IncidentListItem[]; linked: IncidentListItem[]; can_add: boolean; has_role: boolean }>(
      request.get(`${base}/incidents/by-student/`, { params: { student } }),
    ),
  getIncident: (id: number) => unwrap<IncidentDetail>(request.get(`${base}/incidents/${id}/`)),
  createIncident: (payload: IncidentCreatePayload) => unwrap<IncidentDetail>(request.post(`${base}/incidents/`, payload)),
  updateIncident: (id: number, payload: Partial<IncidentCreatePayload>) => unwrap<IncidentDetail>(request.patch(`${base}/incidents/${id}/`, payload)),
  setStatus: (id: number, status: IncidentStatus, note = '') => unwrap<IncidentDetail>(request.post(`${base}/incidents/${id}/status/`, { status, note })),
  setRing: (id: number, ring: Ring, note = '') => unwrap<IncidentDetail>(request.post(`${base}/incidents/${id}/ring/`, { ring, note })),
  addAction: (id: number, kind: string, body: string, ring: Ring = 'TEAM') => unwrap<Action>(request.post(`${base}/incidents/${id}/actions/`, { kind, body, ring })),
  sendAlerts: (id: number, employees: number[], groups: number[], message = '', grants_access = true) =>
    unwrap<Alert[]>(request.post(`${base}/incidents/${id}/alerts/`, { employees, groups, message, grants_access })),
  grantAccess: (id: number, employee: number, reason: string, expires_at: string | null = null) =>
    unwrap<AccessGrant>(request.post(`${base}/incidents/${id}/grants/`, { employee, reason, expires_at })),
  revokeAccess: (id: number, grantId: number) => unwrap<AccessGrant>(request.post(`${base}/incidents/${id}/grants/${grantId}/revoke/`)),
  addMark: (id: number, mark: BodyMapMark) => unwrap<BodyMapMark>(request.post(`${base}/incidents/${id}/body-map/`, mark)),
  removeMark: (id: number, markId: number) => request.post(`${base}/incidents/${id}/body-map/${markId}/remove/`),
  upload: (id: number, file: File) => {
    const fd = new FormData()
    fd.append('file', file)
    return unwrap<Attachment>(request.post(`${base}/incidents/${id}/attachments/`, fd, { headers: { 'Content-Type': 'multipart/form-data' } }))
  },
  exportUrl: (id: number) => `${request.defaults.baseURL}${base}/incidents/${id}/export/`,
  softDelete: (id: number, reason: string) => request.post(`${base}/incidents/${id}/soft-delete/`, { reason }),

  myAlerts: (unread = true) => unwrap<Array<{ id: number; incident_id: number; incident_reference: string; student: StudentSummary; message: string; created_at: string; read_at: string | null; alerted_by_name: string }>>(
    request.get(`${base}/alerts/mine/`, { params: { unread: unread ? 1 : 0 } }),
  ),
  markAlertsRead: (ids: number[]) => request.post(`${base}/alerts/mine/`, { ids }),

  roles: () => unwrap<RoleAssignment[] | Paginated<RoleAssignment>>(request.get(`${base}/roles/`, { params: { page_size: 200 } })),
  createRole: (r: RoleAssignment) => unwrap<RoleAssignment>(request.post(`${base}/roles/`, r)),
  updateRole: (id: number, r: Partial<RoleAssignment>) => unwrap<RoleAssignment>(request.patch(`${base}/roles/${id}/`, r)),
  deleteRole: (id: number) => request.delete(`${base}/roles/${id}/`),
}

/** Lists come back paginated or plain depending on the project pagination setting. */
export function asList<T>(data: T[] | Paginated<T>): T[] {
  return Array.isArray(data) ? data : data.results
}
