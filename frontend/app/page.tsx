'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userApi, roleApi } from '@/lib/api';
import { UserWithRoles } from '@/lib/types';
import { useState } from 'react';
import UserList from '@/components/UserList';
import AddUserModal from '@/components/AddUserModal';
import RoleEditor from '@/components/RoleEditor';

export default function Home() {
  const queryClient = useQueryClient();
  const [selectedUser, setSelectedUser] = useState<UserWithRoles | null>(null);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        <header className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            Role Management Portal
          </h1>
          <p className="text-slate-300">
            Manage users and their role configurations
          </p>
        </header>

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
