export type UserRole = 'admin' | 'researcher' | 'operator' | 'viewer';

export const permissions = {
  admin: ['manage_users', 'control_experiments', 'view_data'],
  researcher: ['create_experiment', 'view_data'],
  operator: ['run_experiment', 'monitor_system'],
  viewer: ['view_dashboard']
};

export function hasPermission(role: UserRole, permission: string) {
  return permissions[role]?.includes(permission) ?? false;
}
