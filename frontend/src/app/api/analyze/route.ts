import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

export async function POST(req: NextRequest) {
  const token = (await cookies()).get('github_token')?.value;
  
  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    const body = await req.json();
    const { owner, repo, pr_number } = body;
    
    if (!owner || !repo || !pr_number) {
      return NextResponse.json({ error: 'Missing required fields' }, { status: 400 });
    }
    
    // Forward to FastAPI backend
    const response = await fetch(`${BACKEND_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ owner, repo, pr_number })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: 'Backend analysis failed', details: errorData }, 
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error starting analysis:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(req: NextRequest) {
  const searchParams = req.nextUrl.searchParams;
  const jobId = searchParams.get('job_id');
  
  if (!jobId) {
    return NextResponse.json({ error: 'No job_id provided' }, { status: 400 });
  }
  
  try {
    // Poll FastAPI backend for status
    const response = await fetch(`${BACKEND_URL}/api/pr/${jobId}`, {
      method: 'GET'
    });
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to fetch job status' }, { status: response.status });
    }
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error fetching analysis status:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
