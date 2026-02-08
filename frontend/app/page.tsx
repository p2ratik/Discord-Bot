'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi, roleApi, adminRoleApi } from '@/lib/api';
import { UserWithRoles } from '@/lib/types';
import { useState } from 'react';
import UserList from '@/components/UserList';
import AddUserModal from '@/components/AddUserModal';
import RoleEditor from '@/components/RoleEditor';
import AdminList from '@/components/AdminList';
import AdminRoleEditor from '@/components/AdminRoleEditor';

type TabType = 'users' | 'admins';

interface AdminUser {
  user_id: string;
  role?: any;
}

export default function Home() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState<TabType>('users');
  const [selectedUser, setSelectedUser] = useState<UserWithRoles | null>(null);
  const [selectedAdmin, setSelectedAdmin] = useState<AdminUser | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [adminList, setAdminList] = useState<AdminUser[]>([]);

  const { data: users, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await userApi.getAll();
      return response.data as UserWithRoles[];
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: (userId: string) => userApi.delete(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      if (selectedUser) setSelectedUser(null);
    },
  });

  const handleSelectUser = async (user: UserWithRoles) => {
    try {
      const response = await userApi.getById(user.user_id);
      setSelectedUser(response.data);
    } catch (error) {
      console.error('Error fetching user details:', error);
    }
  };

  const handleSelectAdmin = async (admin: AdminUser) => {
    try {
      // Try to fetch existing admin role
      const response = await adminRoleApi.get(admin.user_id);
      setSelectedAdmin({
        user_id: admin.user_id,
        role: response.data.role,
      });

      // Add to admin list if not already there
      if (!adminList.find(a => a.user_id === admin.user_id)) {
        setAdminList([...adminList, admin]);
      }
    } catch (error) {
      // Admin doesn't have a role yet
      setSelectedAdmin(admin);

      // Add to admin list if not already there
      if (!adminList.find(a => a.user_id === admin.user_id)) {
        setAdminList([...adminList, admin]);
      }
    }
  };

  const handleAdminUpdate = async () => {
    if (selectedAdmin) {
      // Refresh the admin data
      try {
        const response = await adminRoleApi.get(selectedAdmin.user_id);
        setSelectedAdmin({
          user_id: selectedAdmin.user_id,
          role: response.data.role,
        });

        // Update admin in the list
        setAdminList(adminList.map(a =>
          a.user_id === selectedAdmin.user_id
            ? { ...a, role: response.data.role }
            : a
        ));
      } catch (error) {
        console.error('Error refreshing admin data:', error);
      }
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Role Management Portal
          </h1>
          <p className="text-slate-300">
            Manage users and admin role configurations
          </p>
        </header>

        {/* Tab Navigation */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${activeTab === 'users'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                : 'bg-white/10 text-slate-300 hover:bg-white/20'
              }`}
          >
            👥 User Management
          </button>
          <button
            onClick={() => setActiveTab('admins')}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${activeTab === 'admins'
                ? 'bg-gradient-to-r from-orange-600 to-red-600 text-white shadow-lg shadow-orange-500/50'
                : 'bg-white/10 text-slate-300 hover:bg-white/20'
              }`}
          >
            👑 Admin Management
          </button>
        </div>

        {/* User Management Section */}
        {activeTab === 'users' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Users List */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-semibold text-white">Users</h2>
                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  + Add User
                </button>
              </div>

              {isLoading && (
                <div className="text-white text-center py-8">Loading users...</div>
              )}

              {error && (
                <div className="text-red-400 text-center py-8">
                  Error loading users. Make sure the backend is running.
                </div>
              )}

              {users && (
                <UserList
                  users={users}
                  selectedUser={selectedUser}
                  onSelectUser={handleSelectUser}
                  onDeleteUser={(userId) => deleteUserMutation.mutate(userId)}
                />
              )}
            </div>

            {/* Role Editor */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
              <h2 className="text-2xl font-semibold text-white mb-4">
                Role Editor
              </h2>

              {selectedUser ? (
                <RoleEditor
                  user={selectedUser}
                  onUpdate={() => {
                    queryClient.invalidateQueries({ queryKey: ['users'] });
                    handleSelectUser(selectedUser);
                  }}
                />
              ) : (
                <div className="text-slate-400 text-center py-12">
                  Select a user to edit their roles
                </div>
              )}
            </div>
          </div>
        )}

        {/* Admin Management Section */}
        {activeTab === 'admins' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Admin List */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-orange-500/30">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-2xl font-semibold text-white flex items-center">
                  <span className="mr-2">👑</span>
                  Admins
                </h2>
              </div>

              <AdminList
                admins={adminList}
                selectedAdmin={selectedAdmin}
                onSelectAdmin={handleSelectAdmin}
              />
            </div>

            {/* Admin Role Editor */}
            <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-orange-500/30">
              <h2 className="text-2xl font-semibold text-white mb-4 flex items-center">
                <span className="mr-2">⚙️</span>
                Admin Role Editor
              </h2>

              <AdminRoleEditor
                adminUser={selectedAdmin}
                onUpdate={handleAdminUpdate}
              />
            </div>
          </div>
        )}
      </div>

      {isAddModalOpen && (
        <AddUserModal
          onClose={() => setIsAddModalOpen(false)}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['users'] });
            setIsAddModalOpen(false);
          }}
        />
      )}
    </div>
  );
}
