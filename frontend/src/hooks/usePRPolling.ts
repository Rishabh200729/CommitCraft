import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function usePRPolling(jobId: string | null) {
  const { data: jobStatus, isFetching, error } = useQuery({
    queryKey: ['prJob', jobId],
    queryFn: async () => {
      if (!jobId) return null;
      const res = await axios.get(`${API_URL}/api/pr/${jobId}`);
      return res.data;
    },
    enabled: !!jobId,
    refetchInterval: (query) => {
        const data = query.state.data as any;
        if (data?.status === 'completed' || data?.status === 'failed') {
            return false;
        }
        return 3000;
    },
  });

  const isProcessing = jobStatus?.status === 'processing' || (!jobStatus && !!jobId && isFetching);
  const verdict = jobStatus?.analysis?.verdict;
  const isCompleted = jobStatus?.status === 'completed';
  const isFailed = jobStatus?.status === 'failed';

  return {
    jobStatus,
    isProcessing,
    verdict,
    isCompleted,
    isFailed,
    isFetching,
    error: error || jobStatus?.error,
  };
}
