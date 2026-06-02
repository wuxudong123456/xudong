import request from './request'

export function getOverview() { return request.get('/dashboard/overview') }
export function getClassDistribution() { return request.get('/dashboard/class-distribution') }
export function getScoreTrend() { return request.get('/dashboard/score-trend') }
export function getEmploymentRate() { return request.get('/dashboard/employment-rate') }
export function getScoreDistribution() { return request.get('/dashboard/score-distribution') }
