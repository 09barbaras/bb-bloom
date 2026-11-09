import { useQuery } from '@tanstack/react-query'

import { api } from './client'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: () => api.get<{ status: string }>('/api/health'),
    retry: false, // a down backend should show "unreachable" right away, not after retries
  })
}
