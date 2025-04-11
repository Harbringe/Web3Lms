import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  // Get the pathname of the request (e.g. /, /protected, /api/protected)
  const path = request.nextUrl.pathname

  // If it's an API route, let the request pass through
  if (path.startsWith('/api/')) {
    return NextResponse.next()
  }

  // Allow the request to continue
  return NextResponse.next()
}

// Configure which paths middleware will run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
} 