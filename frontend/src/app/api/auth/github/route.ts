import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const clientId = process.env.GITHUB_CLIENT_ID;
  
  if (!clientId) {
    return NextResponse.json({ error: 'GitHub Client ID not configured' }, { status: 500 });
  }
  
  // Use 'repo' scope to access private repos, 'read:user' for profile info
  const scope = 'repo read:user';
  
  const githubAuthUrl = `https://github.com/login/oauth/authorize?client_id=${clientId}&scope=${encodeURIComponent(scope)}`;
  
  return NextResponse.redirect(githubAuthUrl);
}
