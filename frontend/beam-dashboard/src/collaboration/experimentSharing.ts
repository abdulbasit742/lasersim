export interface ExperimentSession {
  id: string;
  owner: string;
  collaborators: string[];
  status: 'active' | 'closed';
}

export function addCollaborator(session: ExperimentSession, user: string) {
  session.collaborators.push(user);
  return session;
}
