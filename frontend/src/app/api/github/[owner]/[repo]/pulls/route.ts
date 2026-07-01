import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ owner: string; repo: string }> }
) {
  const token = (await cookies()).get('github_token')?.value;
  
  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  const { owner, repo } = await params;
  
  try {
    // Fetch repo's open PRs
    const response = await fetch(`https://api.github.com/repos/${owner}/${repo}/pulls?state=open`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to fetch PRs' }, { status: response.status });
    }
    
    const pulls = await response.json();
    
    // Map to a simpler structure
    const mappedPulls = pulls.map((pr: any) => ({
      number: pr.number,
      title: pr.title,
      state: pr.state,
      author: pr.user.login,
      created_at: pr.created_at,
      updated_at: pr.updated_at,
      html_url: pr.html_url
    }));
    
    return NextResponse.json({ pulls: mappedPulls });
    
  } catch (error) {
    console.error(`Error fetching PRs for ${owner}/${repo}:`, error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
