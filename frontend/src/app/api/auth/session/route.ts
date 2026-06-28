import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(req: NextRequest) {
  const token = cookies().get('github_token')?.value;
  
  if (!token) {
    return NextResponse.json({ authenticated: false }, { status: 401 });
  }
  
  try {
    // Verify token and get user info
    const userResponse = await fetch('https://api.github.com/user', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!userResponse.ok) {
      // Token might be invalid or expired
      cookies().delete('github_token');
      return NextResponse.json({ authenticated: false }, { status: 401 });
    }
    
    const userData = await userResponse.json();
    
    return NextResponse.json({
      authenticated: true,
      user: {
        name: userData.name,
        login: userData.login,
        avatar_url: userData.avatar_url
      }
    });
    
  } catch (error) {
    console.error('Session check error:', error);
    return NextResponse.json({ authenticated: false }, { status: 500 });
  }
}
