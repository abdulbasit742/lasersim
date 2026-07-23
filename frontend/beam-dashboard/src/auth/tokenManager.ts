export interface SessionToken {
  token: string;
  expiresAt: number;
}

export function isTokenValid(session: SessionToken) {
  return Date.now() < session.expiresAt;
}

export function clearSession() {
  return null;
}
