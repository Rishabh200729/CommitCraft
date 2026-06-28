import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(req: NextRequest) {
  const token = cookies().get('github_token')?.value;
  
  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }
  
  try {
    // Fetch user's repos
    const response = await fetch('https://api.github.com/user/repos?sort=updated&per_page=100', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!response.ok) {
      return NextResponse.json({ error: 'Failed to fetch repos' }, { status: response.status });
    }
    
    const repos = await response.json();
    
    // Map to a simpler structure
    const mappedRepos = repos.map((repo: any) => ({
      id: repo.id,
      name: repo.name,
      full_name: repo.full_name,
      owner: repo.owner.login,
      description: repo.description,
      private: repo.private,
      updated_at: repo.updated_at
    }));
    
    return NextResponse.json({ repos: mappedRepos });
    
  } catch (error) {
    console.error('Error fetching repos:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
