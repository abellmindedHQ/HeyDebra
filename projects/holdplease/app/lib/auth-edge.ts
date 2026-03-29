/**
 * Lightweight auth config for Edge middleware.
 * Does NOT import the DB (SQLite) — only JWT-based session check.
 */
import NextAuth from 'next-auth';

export const { auth } = NextAuth({
  providers: [], // No providers needed for middleware (JWT session check only)
  session: {
    strategy: 'jwt',
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) token.userId = user.id;
      return token;
    },
    async session({ session, token }) {
      if (token.userId) {
        session.user.id = token.userId as string;
      }
      return session;
    },
  },
});
