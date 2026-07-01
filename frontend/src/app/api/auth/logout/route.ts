import { NextRequest, NextResponse } from 'next/server';
import { cookies } from 'next/headers';

export async function GET(req: NextRequest) {
  // Clear the github token cookie
  (await cookies()).delete('github_token');
  
  // Redirect to home page
  return NextResponse.redirect(new URL('/', req.url));
}
