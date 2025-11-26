import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import DeploymentView from '../views/DeploymentView.vue'
import ProjectsView from '../views/ProjectsView.vue'
import LibraryView from '../views/LibraryView.vue'
import HistoryView from '../views/HistoryView.vue'
import ReportsView from '../views/ReportsView.vue'
import ExportView from '../views/ExportView.vue'
import AnalysisView from '../views/AnalysisView.vue'
import SettingsView from '../views/SettingsView.vue'
import AboutView from '../views/AboutView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/deployment',
  },
  {
    path: '/deployment',
    name: 'Deployment',
    component: DeploymentView,
    meta: { title: 'Deployment' },
  },
  {
    path: '/projects',
    name: 'Projects',
    component: ProjectsView,
    meta: { title: 'Projects' },
  },
  {
    path: '/library',
    name: 'Library',
    component: LibraryView,
    meta: { title: 'Library' },
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { title: 'History' },
  },
  {
    path: '/reports',
    name: 'Reports',
    component: ReportsView,
    meta: { title: 'Reports' },
  },
  {
    path: '/export',
    name: 'Export',
    component: ExportView,
    meta: { title: 'Export' },
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: AnalysisView,
    meta: { title: 'Analysis' },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { title: 'Settings' },
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView,
    meta: { title: 'About' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  const title = to.meta?.title as string | undefined
  if (title) {
    document.title = `${title} - chklst`
  }
  next()
})

export default router
