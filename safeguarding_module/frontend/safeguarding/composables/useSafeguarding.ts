/**
 * Safeguarding Pinia store: who I am inside the module, plus the Hide Names
 * display toggle. Roles come only from `/safeguarding/me/`; the SIMS admin
 * flag is never consulted here.
 */
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import { sgApi, type SafeguardingMe, type StudentSummary } from '../api/safeguarding'

export const useSafeguardingStore = defineStore('safeguarding', () => {
  const me = ref<SafeguardingMe | null>(null)
  const loaded = ref(false)
  const hideNames = ref(false)
  const blank = ref(false)

  const isDsl = computed(() => !!me.value?.is_dsl)
  const isTeam = computed(() => !!me.value?.is_team)
  const hasRole = computed(() => (me.value?.roles.length ?? 0) > 0)
  const unread = computed(() => me.value?.unread_alerts ?? 0)

  async function load(force = false) {
    if (loaded.value && !force) return me.value
    try {
      me.value = await sgApi.me()
    } catch {
      me.value = null
    }
    loaded.value = true
    return me.value
  }

  /** Student label for lists; initials and the last digits of the ID when Hide Names is on. */
  function studentLabel(s: StudentSummary | null | undefined, locale = 'en'): string {
    if (!s) return ''
    const en = s.name_en || ''
    const zh = s.name_zh || ''
    if (hideNames.value) {
      const initials = en.split(/\s+/).filter(Boolean).map((p) => p[0]?.toUpperCase()).join('')
      return `${initials || '**'} (${s.student_id?.slice(-3) || '***'})`
    }
    return locale.startsWith('zh') ? [zh || en, en && zh ? en : ''].join(' ').trim() : [en || zh, en && zh ? zh : ''].join(' ').trim()
  }

  function toggleHideNames() {
    hideNames.value = !hideNames.value
  }
  function showBlank() {
    blank.value = true
  }
  function hideBlank() {
    blank.value = false
  }

  return { me, loaded, hideNames, blank, isDsl, isTeam, hasRole, unread, load, studentLabel, toggleHideNames, showBlank, hideBlank }
})
