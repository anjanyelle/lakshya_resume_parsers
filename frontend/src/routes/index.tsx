import type { RouteObject } from 'react-router-dom'
import DashboardPage from '../pages/DashboardPage'
import ResumeAnalyzerPage from '../pages/ResumeAnalyzerPage'
import CandidatesPage from '../pages/CandidatesPage'
import CandidateDetailPage from '../pages/CandidateDetailPage'
import JobPostingsPage from '../pages/JobPostingsPage'
import AnalyticsPage from '../pages/AnalyticsPage'
import SettingsPage from '../pages/SettingsPage'
import AuthPage from '../pages/AuthPage'
import TaxonomyPage from '../pages/TaxonomyPage'
import CorrectionsPage from '../pages/CorrectionsPage'
import AccuracyPage from '../pages/AccuracyPage'

export const appRoutes: RouteObject[] = [
  {
    path: '/',
    element: <DashboardPage />,
  },
  {
    path: '/upload',
    element: <ResumeAnalyzerPage />,
  },
  {
    path: '/candidates',
    element: <CandidatesPage />,
  },
  {
    path: '/candidates/:id',
    element: <CandidateDetailPage />,
  },
  {
    path: '/job-postings',
    element: <JobPostingsPage />,
  },
  {
    path: '/analytics',
    element: <AnalyticsPage />,
  },
  {
    path: '/settings',
    element: <SettingsPage />,
  },
  {
    path: '/taxonomy',
    element: <TaxonomyPage />,
  },
  {
    path: '/corrections',
    element: <CorrectionsPage />,
  },
  {
    path: '/accuracy',
    element: <AccuracyPage />,
  },
  {
    path: '/auth',
    element: <AuthPage />,
  },
]
