/**
 * Routes for the safeguarding module. Add to the children of MainLayout in src/router.
 *
 * Guard: the existing beforeEach checks `adminOnly` and `requiredPosition` through
 * the user store, where isAdmin short-circuits to true. Safeguarding must NOT use
 * that path. Add a separate meta key `sgRole` and this check in beforeEach:
 *
 *   import { useSafeguardingStore } from '@/modules/safeguarding/composables/useSafeguarding'
 *   ...
 *   if (to.meta?.sgRole) {
 *     const sg = useSafeguardingStore(); await sg.load()
 *     const roles = sg.me?.roles ?? []
 *     if (!(to.meta.sgRole as string[]).some((r) => roles.includes(r))) { next('/forbidden'); return }
 *   }
 *
 * No `adminOnly` fallback: a SIMS super admin without a safeguarding role gets /forbidden.
 */
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: 'safeguarding',
    name: 'Safeguarding',
    component: () => import('../views/IncidentList.vue'),
    meta: { title: '安全保障', icon: 'Lock', sgRole: ['DSL', 'DEPUTY', 'PASTORAL'] },
  },
  {
    path: 'safeguarding/new',
    name: 'SafeguardingNew',
    component: () => import('../views/IncidentForm.vue'),
    meta: { title: '添加事件', parent: 'Safeguarding', hideInSidebar: true }, // any active staff
  },
  {
    path: 'safeguarding/mine',
    name: 'SafeguardingMine',
    component: () => import('../views/IncidentList.vue'),
    props: { mine: true },
    meta: { title: '我提交的关注', parent: 'Safeguarding', hideInSidebar: true }, // any active staff
  },
  {
    path: 'safeguarding/:id(\\d+)',
    name: 'SafeguardingDetail',
    component: () => import('../views/IncidentDetail.vue'),
    props: true,
    meta: { title: '事件详情', parent: 'Safeguarding', hideInSidebar: true }, // visibility decided by the API
  },
  {
    path: 'safeguarding/access',
    name: 'SafeguardingAccess',
    component: () => import('../views/AccessRoles.vue'),
    meta: { title: '安全保障访问权限', parent: 'Safeguarding', hideInSidebar: true, sgRole: ['DSL'] },
  },
]

export default routes
